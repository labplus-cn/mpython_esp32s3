/* ------------------------------------------------------------------
 * Copyright (C) 2009 Martin Storsjo
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied.
 * See the License for the specific language governing permissions
 * and limitations under the License.
 * -------------------------------------------------------------------
 */
#include "esp_err.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "vfs_lfs2.h"
#include "bsp_audio.h"
#include "audio.h"
#include "player.h"

static const char *TAG = "wav_decoder";

wav_decoder_t *wav_file_open(const char *path_in)
{
	size_t len;
	uint8_t data[44] = {0};

	wav_decoder_t *wr = (wav_decoder_t*) calloc(1, sizeof(wav_decoder_t));
	if(!wr){
		ESP_LOGE(TAG, "wr is null.");
		return NULL;
	}

	wr->lfs2_file = vfs_lfs2_file_open(path_in, LFS2_O_RDONLY);
	if(!wr->lfs2_file){
		ESP_LOGE(TAG, "fiel open fault.");
		goto failt;
	}

	len = lfs2_file_read(&wr->lfs2_file->vfs->lfs, &wr->lfs2_file->file, &data, 44); //read wav head
	if(len < 44){
		ESP_LOGE(TAG, "Bad file.");
		goto failt;;
	}

	wav_head_parser(data, &wr->wav_info);
	if(wr->wav_info.fileChunkID != 0X46464952 && wr->wav_info.fileFormat != 0X45564157){
		ESP_LOGE(TAG, "Not wave file");
		goto failt;;
	}
	// ESP_LOGE(TAG, "wav format: %d, channels: %d sample rate: %ld, bits per sample: %d, data lenght: %ld", wr->wav_info.audioFormat, wr->wav_info.channels, 
	// 	wr->wav_info.sampleRate, wr->wav_info.bits_per_sample, wr->wav_info.dataSize);

	return wr;
failt:
	free(wr);
	return NULL;
}

void wav_file_close(wav_decoder_t *wr)
{
	vfs_lfs2_file_close(wr->lfs2_file);
	if(wr){
		free(wr);
	}
}
		
void wav_file_read_task(void *arg)
{
	// ESP_LOGE(TAG, "wav decodec task begin, RAM left: %ld", esp_get_free_heap_size());
    player_handle_t *player = arg;
	size_t len = 0;
	EventBits_t uxBits;
	size_t ringBufFreeBytes = 0;

    unsigned char* buffer = calloc(FRAME_SIZE, sizeof(unsigned char));
	if(!buffer){
		return;
	}

	wav_decoder_t *wav_decoder = wav_file_open(player->file_uri);
	if(!wav_decoder){
		ESP_LOGE(TAG, "Wave file open failt.");
		return;
	}
	player->wav_decoder = wav_decoder;

	len = lfs2_file_read(&wav_decoder->lfs2_file->vfs->lfs, &wav_decoder->lfs2_file->file, buffer, FRAME_SIZE);
	fill_ringbuf(player->stream_out_ringbuff, buffer, len);

	xTaskCreatePinnedToCore(&stream_i2s_out_task, "stream_out", 5 * 1024, (void*)player, 8, &player->stream_i2s_out_task, CORE_NUM1);
	int i = 0;

    while (1) {
		ringBufFreeBytes = xRingbufferGetCurFreeSize(player->stream_out_ringbuff);
		if( ringBufFreeBytes >= FRAME_SIZE){
			len = lfs2_file_read(&wav_decoder->lfs2_file->vfs->lfs, &wav_decoder->lfs2_file->file, buffer, FRAME_SIZE);
			if(len > 0){
				xRingbufferSend(player->stream_out_ringbuff, (const void *)buffer, len, 100/portTICK_PERIOD_MS);
			}
			
			if(len < FRAME_SIZE){  //文件读完了
				xEventGroupSetBits(
					player->player_event,    // The event group being updated.
					EV_DEL_STREAM_OUT_TASK );// The bits being set.
				break;
			}
		}
		uxBits = xEventGroupWaitBits(    
					player->player_event,    // The event group being tested.
					EV_DEL_FILE_READ_TASK,  // The bits within the event group to wait for.
					pdTRUE,         // BIT_0 and BIT_4 should be cleared before returning.
					pdFALSE,         // not wait for both bits, either bit will do.
					10 / portTICK_PERIOD_MS ); // Wait a maximum of 100ms for either bit to be set.
		if(uxBits & EV_DEL_FILE_READ_TASK){ //Has get stop event.
			goto exit;
		}
    }
exit:
	wav_file_close(wav_decoder);
	free(buffer);
	// ESP_LOGE(TAG, "wav decodec task end, RAM left: %ld", esp_get_free_heap_size());
	// player->wav_file_read_task = NULL;
	vTaskDelete(NULL);	
}

void stream_i2s_out_task(void *arg)
{
    // ESP_LOGE(TAG, "stream out task begin, RAM left: %ld", esp_get_free_heap_size());
    player_handle_t *player = arg;
    uint16_t len;
    EventBits_t uxBits;

    uint8_t *stream_out_buff = malloc(FRAME_SIZE * sizeof(uint8_t) + 1024);
    if(!stream_out_buff){
        return;
    }

    bsp_codec_dev_open(player->wav_decoder->wav_info.sampleRate, player->wav_decoder->wav_info.channels, player->wav_decoder->wav_info.bits_per_sample);
	//  bsp_codec_dev_open(16000, 2, 16);

    while (1) {
        len = read_ringbuf(player->stream_out_ringbuff, FRAME_SIZE, stream_out_buff);
        // ESP_LOGE(TAG, "ring buffer read len: %d", len);
        if(len > 0){
            if(player->audio_type == AUDIO_WAV_FILE_PLAY){
                bsp_audio_play((int16_t *)stream_out_buff, len, portMAX_DELAY);
            }else if(player->audio_type == AUDIO_WAV_FILE_RECORD){
                //write data to file
            }
        }else{
            memset(stream_out_buff, 0, FRAME_SIZE);
            bsp_audio_play((int16_t *)stream_out_buff, FRAME_SIZE / 2, portMAX_DELAY);
            vTaskDelay(200 / portTICK_PERIOD_MS);
            goto exit;
        }
        uxBits = xEventGroupWaitBits(
                    player->player_event,    // The event group being tested.
                    EV_DEL_STREAM_OUT_TASK,  // The bits within the event group to wait for.
                    pdTRUE,         // BIT_0 and BIT_4 should be cleared before returning.
                    pdFALSE,         // not wait for both bits, either bit will do.
                    5 / portTICK_PERIOD_MS ); // Wait a maximum of 100ms for either bit to be set.
		if(uxBits & EV_DEL_STREAM_OUT_TASK){
            vTaskDelay(200 / portTICK_PERIOD_MS);
			goto exit;
        }
    }

exit:
    bsp_codec_dev_close();
    if(stream_out_buff){
        free(stream_out_buff);
    }
    // ESP_LOGE(TAG, "stream out task end, RAM left: %ld", esp_get_free_heap_size());
    player->stream_i2s_out_task = NULL;
    vTaskDelete(NULL);
}