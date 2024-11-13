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
#include "recorder.h"

static const char *TAG = "wav_codec";

wav_codec_t *wav_file_open(const char *path_in, int mode)
{
	size_t len;
	uint8_t data[44] = {0};

	wav_codec_t *wav_codec = (wav_codec_t*) calloc(1, sizeof(wav_codec_t));
	if(!wav_codec){
		ESP_LOGE(TAG, "wav_codec is null.");
		return NULL;
	}

	wav_codec->lfs2_file = vfs_lfs2_file_open(path_in, mode);
	if(!wav_codec->lfs2_file){
		ESP_LOGE(TAG, "fiel open fault.");
		goto failt;
	}

	if(mode == LFS2_O_RDONLY){ //decoder
		len = lfs2_file_read(&wav_codec->lfs2_file->vfs->lfs, &wav_codec->lfs2_file->file, &data, 44); //read wav head
		if(len < 44){
			ESP_LOGE(TAG, "Bad file.");
			goto failt;;
		}

		wav_head_parser(data, &wav_codec->wav_info);
		if(wav_codec->wav_info.fileChunkID != 0X46464952 && wav_codec->wav_info.fileFormat != 0X45564157){
			ESP_LOGE(TAG, "Not wave file");
			goto failt;;
		}
		// ESP_LOGE(TAG, "wav format: %d, channels: %d sample rate: %ld, bits per sample: %d, data lenght: %ld", wav_codec->wav_info.audioFormat, wav_codec->wav_info.channels, 
		// 	wav_codec->wav_info.sampleRate, wav_codec->wav_info.bits_per_sample, wav_codec->wav_info.dataSize);
	}else if((mode & LFS2_O_WRONLY) == LFS2_O_WRONLY){ //encoder

	}

	return wav_codec;
failt:
	free(wav_codec);
	return NULL;
}

void wav_file_close(wav_codec_t *wav_codec)
{
	vfs_lfs2_file_close(wav_codec->lfs2_file);
	if(wav_codec){
		free(wav_codec);
	}
}
		
void wav_file_read_task(void *arg)
{
	// ESP_LOGE(TAG, "wav decodec task begin, RAM left: %ld", esp_get_free_heap_size());
    player_handle_t *player = arg;
	size_t len = 0;
	EventBits_t uxBits;
	size_t ringBufFreeBytes = 0;

    int8_t *buffer = calloc(STREAM_OUT_FRAME_SIZE, sizeof(int8_t));
	if(!buffer){
		return;
	}

	wav_codec_t *wav_codec = wav_file_open(player->file_uri, LFS2_O_RDONLY);
	if(!wav_codec){
		ESP_LOGE(TAG, "Wave file open failt.");
		return;
	}
	player->wav_codec = wav_codec;

	// len = lfs2_file_read(&wav_codec->lfs2_file->vfs->lfs, &wav_codec->lfs2_file->file, buffer, STREAM_OUT_FRAME_SIZE);
	// xRingbufferSend(player->stream_out_ringbuff, buffer, len, 100/portTICK_PERIOD_MS);

	xTaskCreatePinnedToCore(&stream_i2s_write_task, "stream_out", 5 * 1024, (void*)player, 8, &player->stream_i2s_write_task, CORE_NUM1);

    while (1) {
		ringBufFreeBytes = xRingbufferGetCurFreeSize(player->stream_out_ringbuff);
		if( ringBufFreeBytes >= STREAM_OUT_FRAME_SIZE){
			len = lfs2_file_read(&wav_codec->lfs2_file->vfs->lfs, &wav_codec->lfs2_file->file, buffer, STREAM_OUT_FRAME_SIZE);
			if(len > 0){
				xRingbufferSend(player->stream_out_ringbuff, (const void *)buffer, len, 100/portTICK_PERIOD_MS);
			}
			
			if(len < STREAM_OUT_FRAME_SIZE){  //文件读完了
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
	wav_file_close(wav_codec);
	free(buffer);
	// ESP_LOGE(TAG, "wav decodec task end, RAM left: %ld", esp_get_free_heap_size());
	vTaskDelete(NULL);	
}

void stream_i2s_write_task(void *arg)
{
    // ESP_LOGE(TAG, "stream out task begin, RAM left: %ld", esp_get_free_heap_size());
    player_handle_t *player = arg;
    uint16_t len;
    EventBits_t uxBits;

    int8_t *stream_buff = calloc(STREAM_OUT_FRAME_SIZE, sizeof(int8_t));
    if(!stream_buff){
        return;
    }

    bsp_codec_dev_open(player->wav_codec->wav_info.sampleRate, player->wav_codec->wav_info.channels, player->wav_codec->wav_info.bits_per_sample);
    while (1) {
        len = read_ringbuf(player->stream_out_ringbuff, STREAM_OUT_RINGBUF_SIZE, STREAM_OUT_FRAME_SIZE, stream_buff);
        // ESP_LOGE(TAG, "ring buffer read len: %d", len);
        if(len > 0){
            if(player->audio_type == AUDIO_WAV_FILE_PLAY){
                bsp_audio_play(stream_buff, len, portMAX_DELAY);
            }else if(player->audio_type == AUDIO_WAV_FILE_RECORD){
                //write data to file
            }
        }else{
            memset(stream_buff, 0, STREAM_OUT_FRAME_SIZE);
            bsp_audio_play(stream_buff, STREAM_OUT_FRAME_SIZE, portMAX_DELAY);
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
    if(stream_buff){
        free(stream_buff);
    }
    // ESP_LOGE(TAG, "stream out task end, RAM left: %ld", esp_get_free_heap_size());
    player->stream_i2s_write_task = NULL;
    vTaskDelete(NULL);
}

void wav_file_write_task(void *arg)
{
	ESP_LOGE(TAG, "wav file write task begin, RAM left: %ld", esp_get_free_heap_size());
    recorder_handle_t *recorder = arg;
	EventBits_t uxBits;
	uint16_t len = 0;

    int8_t *buffer = calloc(RECORD_FRAME_SIZE * 2, sizeof(int8_t));
	if(!buffer){
		ESP_LOGE(TAG, "buffer calloc failt.");
		return;
	}

	wav_codec_t *wav_codec = wav_file_open(recorder->file_uri, LFS2_O_WRONLY | LFS2_O_CREAT);
	if(!wav_codec){
		free(buffer);
		ESP_LOGE(TAG, "Wave file open failt.");
		return;
	}
	recorder->wav_codec = wav_codec;

	// write wav header to file.
	wav_header_t *wav_header = calloc(1, sizeof(wav_header_t));
	if (!wav_header){
		free(buffer);
		wav_file_close(wav_codec);
		ESP_LOGE(TAG, "Wave head calloc failt.");
		return;
	}
		
	wav_head_init(wav_header, recorder->wav_fmt.sampleRate, recorder->wav_fmt.bits_per_sample, recorder->wav_fmt.channels, recorder->total_frames * RECORD_FRAME_SIZE);
	lfs2_file_write(&wav_codec->lfs2_file->vfs->lfs, &wav_codec->lfs2_file->file, (uint8_t *)wav_header, sizeof(wav_header_t));
	// lfs2_file_sync(&wav_codec->lfs2_file->vfs->lfs, &wav_codec->lfs2_file->file);
	free(wav_header);

    while (1) {
		len = read_ringbuf(recorder->stream_in_ringbuff, RECORD_RINGBUF_SIZE, RECORD_FRAME_SIZE * 2, buffer);
		if(len > 0){
			lfs2_file_write(&wav_codec->lfs2_file->vfs->lfs, &wav_codec->lfs2_file->file, buffer, len);
			// lfs2_file_sync(&wav_codec->lfs2_file->vfs->lfs, &wav_codec->lfs2_file->file);
		}
		uxBits = xEventGroupWaitBits(    
					recorder->recorder_event,    // The event group being tested.
					EV_DEL_FILE_WRITE_TASK,  // The bits within the event group to wait for.
					pdTRUE,         // BIT_0 and BIT_4 should be cleared before returning.
					pdFALSE,         // not wait for both bits, either bit will do.
					2 / portTICK_PERIOD_MS ); // Wait a maximum of 100ms for either bit to be set.
		if(uxBits & EV_DEL_FILE_WRITE_TASK){ //Has get stop event.
			goto exit;
		}
    }

exit:
	wav_file_close(wav_codec);
	free(buffer);
	ESP_LOGE(TAG, "wav file write task end, RAM left: %ld", esp_get_free_heap_size());
	vTaskDelete(NULL);	
}

void stream_i2s_read_task(void *arg)
{
    ESP_LOGE(TAG, "stream in task begin, RAM left: %ld", esp_get_free_heap_size());
    recorder_handle_t *recorder = arg;
	uint16_t frame_cnt = 0;

    int8_t *stream_buff = calloc(RECORD_FRAME_SIZE, sizeof(int8_t));
    if(!stream_buff){
        return;
    }

    bsp_codec_dev_open(recorder->wav_fmt.sampleRate, recorder->wav_fmt.channels, recorder->wav_fmt.bits_per_sample);
	xTaskCreatePinnedToCore(&wav_file_write_task, "wav_file_write_task", 4 * 1024, (void*)recorder, 8, NULL, CORE_NUM1);

    while (1) {
        while(xRingbufferGetCurFreeSize(recorder->stream_in_ringbuff) >= RECORD_FRAME_SIZE){
			bsp_get_feed_data(true, stream_buff, RECORD_FRAME_SIZE);
			// bsp_audio_play(stream_buff, RECORD_FRAME_SIZE, portMAX_DELAY);
			xRingbufferSend(recorder->stream_in_ringbuff, stream_buff, RECORD_FRAME_SIZE, 100/portTICK_PERIOD_MS);
			frame_cnt++;
			// ESP_LOGE(TAG, "freme cnt: %d", frame_cnt);
			if(frame_cnt > recorder->total_frames){
				xEventGroupSetBits(
					recorder->recorder_event,    // The event group being updated.
					EV_DEL_FILE_WRITE_TASK );// The bits being set.
				goto exit;
			}
		}
		vTaskDelay(2 / portTICK_PERIOD_MS);
    }
exit:
    bsp_codec_dev_close();
    if(stream_buff){
        free(stream_buff);
    }
    ESP_LOGE(TAG, "stream in task end, RAM left: %ld", esp_get_free_heap_size());
    vTaskDelete(NULL);
}