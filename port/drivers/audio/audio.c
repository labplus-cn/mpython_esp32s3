#include "stdio.h"
#include "stdlib.h"
#include <string.h>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "audio.h"
#include "audio_board.h"

audio_handle_t *audio_handle = NULL;

void fill_ringbuf(RingbufHandle_t ring_buff, uint8_t *buffer, uint16_t len)
{
    int free_size;

    free_size = xRingbufferGetCurFreeSize(ring_buff); //get ringbuf free size
    if(free_size >= len){
        xRingbufferSend(ring_buff, (const void *)buffer, (size_t)len, 100/portTICK_PERIOD_MS);
    }else{
        if(free_size > 0){
            xRingbufferSend(ring_buff, (const void *)buffer, (size_t)free_size, 100/portTICK_PERIOD_MS);
        }
        
    }
}

uint16_t read_ringbuf(RingbufHandle_t ring_buff, uint16_t supply_bytes, uint8_t *buffer)
{
    int ringBufRemainBytes = 0;
    size_t len = 0;
    void *temp = NULL;

    ringBufRemainBytes = RINGBUF_SIZE - xRingbufferGetCurFreeSize(ring_buff); 

    /* 1 从ringbuf中读解码器需要的数据量 */
    if (ringBufRemainBytes > 0)
    {
        if(ringBufRemainBytes >= supply_bytes)  //ring buffer remain data enough for decoder need
        { 
            if(supply_bytes != 0){
                temp = xRingbufferReceiveUpTo(ring_buff,  &len, 500 / portTICK_PERIOD_MS, supply_bytes);
            }
        }
        else{ 
            temp = xRingbufferReceiveUpTo(ring_buff,  &len, 50 / portTICK_PERIOD_MS, ringBufRemainBytes);     
        }  

        if(temp != NULL){
            memcpy(buffer, temp, len);
            vRingbufferReturnItem(ring_buff, (void *)temp);
        }
    }
    // ESP_LOGE(TAG, "ringBufRemainBytes = %d, supply_bytes = %d, left bytes: %d", ringBufRemainBytes, supply_bytes, *bytes_left);
    return len;
}

void audio_init(void)
{
    if(!audio_handle){
        esp_board_codec_dev_create();
        audio_handle->stream_out_ringbuff = xRingbufferCreate(RINGBUF_SIZE, RINGBUF_TYPE_BYTEBUF);
        audio_handle->stream_out_buff = calloc(BUFFER_SIZE, sizeof(uint8_t));
        audio_handle->stream_out_zero_buff = calloc(BUFFER_SIZE, sizeof(uint8_t));
    }
}

void audio_deinit(void)
{
    if(audio_handle){
        esp_board_codec_dev_delete();
        vRingbufferDelete(audio_handle->stream_out_ringbuff);
        if(audio_handle->stream_out_buff){
            free(audio_handle->stream_out_buff);
        }
        if(audio_handle->stream_out_zero_buff){
            free(audio_handle->stream_out_zero_buff);
        }
    }
}
