/*
 * audio_recorder.c
 *
 *  Created on: 2019.02.03
 *      Author: zhaohuijiang
 */

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <ctype.h>
#include <math.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "esp_system.h"
#include "esp_log.h"
#include "py/stream.h"
#include "py/reader.h"
#include "py/runtime.h"

#include "wave_head.h"
#include "mpconfigboard.h"
#include "recorder.h"
#include "player.h"
#include "msg.h"

#include "sc.h"
#include "bsp_audio.h"

#define ABS(x) ((x) < 0 ? -(x) : (x))
// #define TAG "recorder"

recorder_handle_t *recorder = NULL;
bool is_record_open = false;
int8_t *stream_buff = NULL;

/*
static void example_disp_buf(uint8_t* buf, int length)
{
    printf("======\n");
    for (int i = 0; i < length; i++) {
        printf("%02x ", buf[i]);
        if ((i + 1) % 8 == 0) {
            printf("\n");
        }
    }
    printf("======\n");
}
*/

void recorder_init()
{}

void recorder_record(const char *filename, wav_fmt_t fmt, int time)
{
    if(!recorder){
        recorder = calloc(1, sizeof(recorder_handle_t));
        recorder->recorder_event = xEventGroupCreate(); 
        recorder->record_ringbuff = rb_create(READ_RINGBUF_BLOCK_SIZE, READ_RINGBUF_BLOCK_NUM);   
    }

    recorder->time = time;
    if ( recorder->time > 5){
        mp_warning(NULL, "Record time too long, will limit to 5s.");
        recorder->time = 5;
    }

    recorder->wav_fmt.bits_per_sample = fmt.bits_per_sample;
    recorder->wav_fmt.channels = fmt.channels;
    recorder->wav_fmt.sampleRate = fmt.sampleRate;
    // data_size = sample_rate * (bits_per_sampe / 8) * channels * time;
    recorder->total_frames = recorder->time * (recorder->wav_fmt.sampleRate * recorder->wav_fmt.channels * recorder->wav_fmt.bits_per_sample / 8) / READ_RINGBUF_BLOCK_SIZE;
    // ESP_LOGE(TAG, "record total frame: %d, time: %d", recorder->total_frames, recorder->time);
    recorder->file_uri = filename;

    sc_stop_flag = 1;
    bsp_codec_dev_delete();
    bsp_codec_dev_create();

    xBinarySemaphore = xSemaphoreCreateBinary();
    xTaskCreatePinnedToCore(&stream_i2s_read_task, "stream_i2s_read_task", 4 * 1024, (void*)recorder, 8, NULL, CORE_NUM1);
    xSemaphoreTake(xBinarySemaphore, portMAX_DELAY);
    sc_stop_flag = 0;
    vSemaphoreDelete(xBinarySemaphore);
}

void record_deinit(void)
{

}

uint16_t record_loudness(void)
{
    double loudness = 0.0;

    if(!stream_buff){
        stream_buff = calloc(100, sizeof(int8_t));
    }

    sc_stop_flag = 1;
    if(!is_record_open){
        bsp_codec_dev_open(8000, 1, 16);
        bsp_audio_set_play_vol(0);
        is_record_open = true;
    }
    
    bsp_get_feed_data(true, stream_buff, 100);
    for(int i = 0; i < 50; i++){
        // loudness += *((int16_t *)stream_buff + i) < 0 ? -*((int16_t *)stream_buff + i) : *((int16_t *)stream_buff + i);
        loudness += (double)(pow(*((int16_t *)stream_buff + i), 2));
    }
    return (uint16_t)(20 * log10(sqrt(loudness / 50) * 5)); //+ 1e-9)); // 5 is the gain of the microphone,校正倍数
}

void record_loudness_stop(void)
{
    if(is_record_open){
        bsp_codec_dev_close();
        is_record_open = false;
        sc_stop_flag = 0;
    }

    if(stream_buff){
        free(stream_buff);
        stream_buff = NULL;
    }
}
