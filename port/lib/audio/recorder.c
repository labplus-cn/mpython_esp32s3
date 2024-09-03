#include "stdio.h"
#include "stdlib.h"
#include <string.h>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/timers.h"
#include "freertos/queue.h"
#include <sys/stat.h>
#include "audio/include/esp_board_init.h"
#include "audio/include/wav_encoder.h"
#include "audio/include/recorder.h"
#include <dirent.h>

#define CODEC_CHANNEL 2
#define CODEC_SAMPLE_RATE 16000
#define FRAME_BUF_SIZE 2048
#define TAG    "recorder"

static void rec_timer_cb(void *arg)
{
    recorder_handle_t* recorder = (recorder_handle_t*) pvTimerGetTimerID(arg);
    recorder->recorder_state = 4;
}

static void stream_in_task(void *arg)
{
    recorder_handle_t *recorder = arg;
    int16_t* buffer = malloc(recorder->frame_size * sizeof(int16_t));
    ESP_LOGE(TAG, "create stream in running.");

    while (1) {
        switch (recorder->recorder_state) {
        case 1: // recorder
            esp_get_feed_data(false, buffer, recorder->frame_size);
            xQueueSend(recorder->recorder_queue, buffer, portMAX_DELAY);
            // vTaskDelay(5 / portTICK_PERIOD_MS);
            // ESP_LOGD(TAG, "stream in.");
            break;
        case 2: // pause or stop
            vTaskDelay(16 / portTICK_PERIOD_MS);
            break;

        case 3: // continue
            recorder->recorder_state = 1;
            break;

        case 4: // exit
            vTaskDelay(2000 / portTICK_PERIOD_MS);
            ESP_LOGE(TAG, "stream read end.\n");
            free(buffer);
            // return;
            vTaskDelete(NULL);

        default: // exit
            vTaskDelay(16 / portTICK_PERIOD_MS);
        }
    }
}

static void stream_out_task(void *arg)
{
    recorder_handle_t *recorder = arg;
    unsigned char* buffer = malloc(recorder->frame_size * sizeof(unsigned char));
    unsigned char* zero_buffer = calloc(recorder->frame_size, sizeof(unsigned char));
    ESP_LOGE(TAG, "stream_out is running.\n");
    void *ww = NULL;
    ww = wav_encoder_open(recorder->audio_file, recorder->sample_rate, recorder->bits_per_sample, recorder->channels);

    int count = 0;
    while (1) {
        count++;
        switch (recorder->recorder_state) {
        case 1: // play
            xQueueReceive(recorder->recorder_queue, buffer, portMAX_DELAY);
            wav_encoder_run(ww, buffer, recorder->frame_size);
            break;

        case 2: // pause or stop
            break;

        case 3: // continue
            recorder->recorder_state = 1;
            // vTaskDelay(16 / portTICK_PERIOD_MS);
            break;

        case 4: // exit
            ESP_LOGE(TAG, "recorder end.\n");
            vTaskDelay(2000 / portTICK_PERIOD_MS);
            free(buffer);
            while(1){
                 vTaskDelay(200 / portTICK_PERIOD_MS);
            }

        default: // exit
            // i2s_zero_dma_buffer(0);
            vTaskDelay(16 / portTICK_PERIOD_MS);

        }
    }
}

void *recorder_create(const char *file, uint8_t rec_time, int ringbuf_size, unsigned int core_num)
{
    if (ringbuf_size < FRAME_BUF_SIZE)
        ringbuf_size = FRAME_BUF_SIZE;
    else
        ringbuf_size = (ringbuf_size / FRAME_BUF_SIZE + 1) * FRAME_BUF_SIZE; //取FRAME_BUF_SIZE整数倍

    if (core_num > 1)
        core_num = 1;

    recorder_handle_t *recorder = malloc(sizeof(recorder_handle_t));

    recorder->frame_size = FRAME_BUF_SIZE;
    recorder->rb_size = ringbuf_size;
    recorder->recorder_queue = xQueueCreate(ringbuf_size / recorder->frame_size, recorder->frame_size);
    recorder->recorder_state = 0;
    recorder->audio_file = file;
    recorder->sample_rate = 16000;
    recorder->bits_per_sample = 16;
    recorder->channels = 2;

    recorder->rec_Timer =  xTimerCreate(	"rec_timer",
								(rec_time * 60000) / portTICK_PERIOD_MS,
								pdFALSE,
								recorder,
								&rec_timer_cb); 

    xTaskCreatePinnedToCore(&stream_in_task, "stream_in", 2 * 1024, (void*)recorder, 8, NULL, core_num);
    xTaskCreatePinnedToCore(&stream_out_task, "stream_out", 2 * 1024, (void*)recorder, 8, NULL, core_num);

    return recorder;
}

void recorder_play(void *handle, const char *path)
{
    recorder_handle_t *recorder = handle;
    recorder->recorder_state = 1;
}

void recorder_pause(void *handle)
{
    recorder_handle_t *recorder = handle;
    recorder->recorder_state = 2;
    // ESP_LOGE(TAG, "pause\n");
}

void recorder_continue(void *handle)
{
    recorder_handle_t *recorder = handle;
    recorder->recorder_state = 3;
    // ESP_LOGE(TAG, "play\n");
}

void recorder_exit(void *handle)
{
    recorder_handle_t *recorder = handle;
    recorder->recorder_state = 4;
}

int recorder_get_state(void *handle)
{
    recorder_handle_t *recorder = handle;
    return recorder->recorder_state;
}

