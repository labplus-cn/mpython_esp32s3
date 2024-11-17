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

#define TAG "recorder"

recorder_handle_t *recorder = NULL;

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

void recorder_record(const char *filename, int time)
{
    if(!recorder){
        recorder = calloc(1, sizeof(recorder_handle_t));
        recorder->record_queue = xQueueCreate(1, sizeof(msg_t));
        recorder->record_ringbuff = rb_create(READ_RINGBUF_BLOCK_SIZE, READ_RINGBUF_BLOCK_NUM);   
    }

    recorder->time = time;
    if ( recorder->time > 5){
        mp_warning(NULL, "Record time too long, will limit to 5s.");
        recorder->time = 5;
    }

    recorder->wav_fmt.bits_per_sample = 16;
    recorder->wav_fmt.channels = 2;
    recorder->wav_fmt.sampleRate = 16000;
    // data_size = sample_rate * (bits_per_sampe / 8) * channels * time;
    recorder->total_frames = recorder->time * (recorder->wav_fmt.sampleRate * recorder->wav_fmt.channels * recorder->wav_fmt.bits_per_sample / 8) / READ_RINGBUF_BLOCK_SIZE;
    ESP_LOGE(TAG, "record total frame: %d, time: %d", recorder->total_frames, recorder->time);
    recorder->file_uri = filename;
    xTaskCreatePinnedToCore(&stream_i2s_read_task, "stream_i2s_read_task", 4 * 1024, (void*)recorder, 8, NULL, CORE_NUM1);
}

void record_deinit(void)
{

}
