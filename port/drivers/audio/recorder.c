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

#define TAG "recorder"

recorder_handle_t *recorder = NULL;

void example_disp_buf(uint8_t* buf, int length)
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

void recorder_init()
{

}

void recorder_record(const char *filename, int time)
{
    if(!recorder){
        recorder = calloc(1, sizeof(recorder_handle_t));
        recorder->recorder_event = xEventGroupCreate(); 
        recorder->stream_in_ringbuff = xRingbufferCreate(RINGBUF_SIZE, RINGBUF_TYPE_BYTEBUF);    
    }else{
        clear_ringbuf(recorder->stream_in_ringbuff);
    }

    recorder->time = time;
    if ( recorder->time > 5){
        mp_warning(NULL, "Record time too long, will limit to 5s.");
        recorder->time = 5;
    }

    xTaskCreatePinnedToCore(&stream_i2s_read_task, "stream_i2s_read_task", 2 * 1024, (void*)recorder, 8, NULL, CORE_NUM1);
}

uint32_t recorder_loudness()
{
    // // renderer_config_t *renderer = renderer_get();
    // uint32_t len = 32; //320bytes: record 10ms
    // int16_t *d_buff = calloc(len/2, sizeof(uint16_t));
    // uint8_t *read_buff = calloc(len, sizeof(uint8_t)); 
    
    // renderer_read_raw(read_buff, len);

    // i2s_adc_data_scale1(d_buff, read_buff, len);
    // audio_recorder_quicksort((uint16_t *)d_buff, len/2, 0, len/2 - 1);

    // // uint32_t sum = d_buff[len/2-2] - d_buff[1];
    // uint16_t loudness = d_buff[len/2 - 2];
    // free(read_buff);
    // free(d_buff);

    // #if MICROPY_BUILDIN_ADC
    // return loudness;
    // #else          
    // return loudness >> 4;
    // #endif
    
    return 0;
}

void recorder_deinit()
{

}

/********************************
 *函数名：swap
 *作用：交换两个数的值
 *参数：交换的两个数
 *返回值：无
 ********************************/
static void swap(uint16_t *a, uint16_t *b)  
{
    uint16_t temp;
    temp = *a;
    *a = *b;
    *b = temp;
}

/************************************
 *函数名：quicksort
 *作用：快速排序算法
 *参数：
 *返回值：无
 ************************************/
void audio_recorder_quicksort(uint16_t *buff, uint32_t maxlen, uint32_t begin, uint32_t end)
{
    int i, j;
    if(begin < end)
    {
        i = begin + 1;  // buff[begin]作为基准数，因此从array[begin+1]开始与基准数比较！
        j = end;        // buff[end]是数组的最后一位

        while(i < j)
        {
            if(buff[i] > buff[begin])  // 如果比较的数组元素大于基准数，则交换位置。
            {
                swap(&buff[i], &buff[j]);  // 交换两个数
                j--;
            }
            else
            {
                i++;  // 将数组向后移一位，继续与基准数比较。
            }
        }

        /* 跳出while循环后，i = j。
         * 此时数组被分割成两个部分  -->  buff[begin+1] ~ buff[i-1] < buff[begin]
         *                           -->  buff[i+1] ~ buff[end] > buff[begin]
         * 这个时候将数组buff分成两个部分，再将buff[i]与buff[begin]进行比较，决定buff[i]的位置。
         * 最后将buff[i]与buff[begin]交换，进行两个分割部分的排序！以此类推，直到最后i = j不满足条件就退出！
         */
        if(buff[i] >= buff[begin])  // 这里必须要取等“>=”，否则数组元素由相同的值时，会出现错误！
        {
            i--;
        }
        swap(&buff[begin], &buff[i]);  // 交换buff[i]与buff[begin]
        audio_recorder_quicksort(buff, maxlen, begin, i);
        audio_recorder_quicksort(buff, maxlen, j, end);
    }
}
