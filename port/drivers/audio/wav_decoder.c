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
#include "wav_decoder.h"
#include "vfs_lfs2.h"
#include "audio_board.h"
#include "audio.h"
#include "player.h"
#include "stream_out.h"

static const char *TAG = "wav_decoder";
#define TAG(a, b, c, d) (((a) << 24) | ((b) << 16) | ((c) << 8) | (d))
wav_decoder_t *wav_decoder = NULL;

static uint32_t read_tag(void) {
	uint32_t tag = 0;
	uint8_t data;

	lfs2_file_read(&wav_decoder->lfs2_file->vfs->lfs, &wav_decoder->lfs2_file->file, &data, 1);
	tag = (tag << 8) | data;
	lfs2_file_read(&wav_decoder->lfs2_file->vfs->lfs, &wav_decoder->lfs2_file->file, &data, 1);
	tag = (tag << 8) | data;
	lfs2_file_read(&wav_decoder->lfs2_file->vfs->lfs, &wav_decoder->lfs2_file->file, &data, 1);
	tag = (tag << 8) | data;
	lfs2_file_read(&wav_decoder->lfs2_file->vfs->lfs, &wav_decoder->lfs2_file->file, &data, 1);
	tag = (tag << 8) | data;
	return tag;
}

static uint32_t read_int32(void) {
	uint32_t value = 0;
	uint8_t data;

	lfs2_file_read(&wav_decoder->lfs2_file->vfs->lfs, &wav_decoder->lfs2_file->file, &data, 1);
	value |= data <<  0;
	lfs2_file_read(&wav_decoder->lfs2_file->vfs->lfs, &wav_decoder->lfs2_file->file, &data, 1);
	value |= data <<  8;
	lfs2_file_read(&wav_decoder->lfs2_file->vfs->lfs, &wav_decoder->lfs2_file->file, &data, 1);
	value |= data << 16;
	lfs2_file_read(&wav_decoder->lfs2_file->vfs->lfs, &wav_decoder->lfs2_file->file, &data, 1);
	value |= data << 24;
	return value;
}

static uint16_t read_int16(void) {
	uint8_t data;
	
	uint16_t value = 0;
	lfs2_file_read(&wav_decoder->lfs2_file->vfs->lfs, &wav_decoder->lfs2_file->file, &data, 1);
	value |= data << 0;
	lfs2_file_read(&wav_decoder->lfs2_file->vfs->lfs, &wav_decoder->lfs2_file->file, &data, 1);
	value |= data << 8;
	return value;
}

esp_err_t wav_file_open(const char *path_in)
{
	if(!wav_decoder){
		ESP_LOGE(TAG, "wav_decoder is null.");
		return ESP_FAIL;
	}

	wav_decoder->lfs2_file = vfs_lfs2_file_open(path_in);
	if(!wav_decoder->lfs2_file){
		ESP_LOGE(TAG, "fiel open fault.");
		return ESP_FAIL;
	}

	uint32_t tag, tag2, length;
	tag = read_tag(); // 4字节
	length = read_int32(); // 4字节
	if (tag != TAG('R', 'I', 'F', 'F') || length < 4) {
		return ESP_FAIL;	
	}

	tag2 = read_tag();
	if (tag2 != TAG('W', 'A', 'V', 'E')) { // 4字节
		return ESP_FAIL;
	}

	uint32_t subtag, sublength;
	subtag = read_tag();  // 4字节
	sublength = read_int32();
	if (subtag != TAG('f', 'm', 't', ' ') || sublength < 16) {
		return ESP_FAIL;
	}
	wav_decoder->wav_info.format          = read_int16();
	wav_decoder->wav_info.channels        = read_int16();
	wav_decoder->wav_info.sample_rate     = read_int32();
	wav_decoder->wav_info.byte_rate       = read_int32();
	wav_decoder->wav_info.block_align     = read_int16();
	wav_decoder->wav_info.bits_per_sample = read_int16();
	ESP_LOGE(TAG, "wav format: %d, channels: %d sample rate: %d, bits per sample: %d", wav_decoder->wav_info.format, wav_decoder->wav_info.channels, 
		wav_decoder->wav_info.sample_rate, wav_decoder->wav_info.bits_per_sample);

	subtag = read_tag();  // 4字节
	if (subtag != TAG('d', 'a', 't', 'a')) {
		return ESP_FAIL;
	}
	sublength = read_int32(); // 读完后，文件定位在data首址
	wav_decoder->data_length = sublength;
	// ESP_LOGE(TAG, "data pos: %ld, data_len: %ld\n", lfs2_file_tell(&wav_decoder->lfs2_file->vfs->lfs, &wav_decoder->lfs2_file->file), wav_decoder->data_length);

	return ESP_OK;
}

void wav_file_close(void)
{
	if(wav_decoder){
		if(wav_decoder->lfs2_file){
			lfs2_file_close(&wav_decoder->lfs2_file->vfs->lfs, &wav_decoder->lfs2_file->file);
			free(wav_decoder->lfs2_file);
		}
	}
}

void wav_get_info(wav_info_t *wav_info) {
	if(wav_decoder){
		wav_info->format = wav_decoder->wav_info.format;
		wav_info->channels = wav_decoder->wav_info.channels;
		wav_info->sample_rate = wav_decoder->wav_info.sample_rate;
		wav_info->bits_per_sample = wav_decoder->wav_info.bits_per_sample;
		wav_info->byte_rate       = read_int32();
		wav_info->block_align     = read_int16();
	}
}

void wav_file_read_task(void *arg)
{
	ESP_LOGE(TAG, "wav decodec task begin, RAM left: %ld", esp_get_free_heap_size());
    player_handle_t *player = arg;
	size_t len = 0;
	EventBits_t uxBits;
	size_t ringBufFreeBytes = 0;

    unsigned char* buffer = malloc(FRAME_SIZE * sizeof(unsigned char));
	if(!buffer){
		return;
	}
	// if(!wav_decoder){
	// 	wav_decoder = (wav_decoder_t*) malloc(sizeof(*wav_decoder));
	// 	if (!wav_decoder) {
	// 		free(buffer);
	// 		return;
	// 	}
	// }

	// if(wav_file_open(player->file_uri) == ESP_OK){
	// 	player->wav_info = wav_decoder->wav_info;
	// }

	// while(1){
	// 	ringBufFreeBytes = xRingbufferGetCurFreeSize(player->stream_out_ringbuff);
	// 	if( ringBufFreeBytes >= FRAME_SIZE){
	// 		len = lfs2_file_read(&wav_decoder->lfs2_file->vfs->lfs, &wav_decoder->lfs2_file->file, buffer, FRAME_SIZE);
	// 		fill_ringbuf(player->stream_out_ringbuff, buffer, len);
	// 	}else{
	// 		break;
	// 	}
	// }

	xTaskCreatePinnedToCore(&stream_out_task, "stream_out", 5 * 1024, (void*)player, 8, &player->stream_out_task, CORE_NUM1);

    while (1) {
		// ringBufFreeBytes = xRingbufferGetCurFreeSize(player->stream_out_ringbuff);
		// if( ringBufFreeBytes >= FRAME_SIZE){
			// len = lfs2_file_read(&wav_decoder->lfs2_file->vfs->lfs, &wav_decoder->lfs2_file->file, buffer, FRAME_SIZE);
			vTaskDelay(500 / portTICK_PERIOD_MS);
			goto exit;
		// 	// fill_ringbuf(player->stream_out_ringbuff, buffer, len);
		// 	if(len > 0){
		// 		xRingbufferSend(player->stream_out_ringbuff, (const void *)buffer, len, 100/portTICK_PERIOD_MS);
		// 	}
		// 	ESP_LOGE(TAG, "read len: %d", len);
		// 	if(len < FRAME_SIZE){  //文件读完了
		// 		xEventGroupSetBits(
		// 			player->player_event,    // The event group being updated.
		// 			EV_DEL_STREAM_OUT_TASK );// The bits being set.
		// 		break;
		// 	}
		// }
		// uxBits = xEventGroupWaitBits(    
		// 			player->player_event,    // The event group being tested.
		// 			EV_DEL_FILE_READ_TASK,  // The bits within the event group to wait for.
		// 			pdTRUE,         // BIT_0 and BIT_4 should be cleared before returning.
		// 			pdFALSE,         // not wait for both bits, either bit will do.
		// 			10 / portTICK_PERIOD_MS ); // Wait a maximum of 100ms for either bit to be set.
		// if(uxBits & EV_DEL_FILE_READ_TASK){ //Has get stop event.
		// 	goto exit;
		// }
    }
exit:
	// wav_file_close();
	free(buffer);
	// free(wav_decoder);
	ESP_LOGE(TAG, "wav decodec task end, RAM left: %ld", esp_get_free_heap_size());
	player->wav_file_read_task = NULL;
	vTaskDelete(NULL);	
}