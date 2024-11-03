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

static const char *TAG = "wav_decoder";
#define TAG(a, b, c, d) (((a) << 24) | ((b) << 16) | ((c) << 8) | (d))

static uint32_t read_tag(wav_decoder_t* wr) {
	uint32_t tag = 0;
	uint8_t data;

	lfs2_file_read(&wr->lfs2_file->vfs->lfs, &wr->lfs2_file->file, &data, 1);
	tag = (tag << 8) | data;
	lfs2_file_read(&wr->lfs2_file->vfs->lfs, &wr->lfs2_file->file, &data, 1);
	tag = (tag << 8) | data;
	lfs2_file_read(&wr->lfs2_file->vfs->lfs, &wr->lfs2_file->file, &data, 1);
	tag = (tag << 8) | data;
	lfs2_file_read(&wr->lfs2_file->vfs->lfs, &wr->lfs2_file->file, &data, 1);
	tag = (tag << 8) | data;
	return tag;
}

static uint32_t read_int32(wav_decoder_t* wr) {
	uint32_t value = 0;
	uint8_t data;

	lfs2_file_read(&wr->lfs2_file->vfs->lfs, &wr->lfs2_file->file, &data, 1);
	value |= data <<  0;
	lfs2_file_read(&wr->lfs2_file->vfs->lfs, &wr->lfs2_file->file, &data, 1);
	value |= data <<  8;
	lfs2_file_read(&wr->lfs2_file->vfs->lfs, &wr->lfs2_file->file, &data, 1);
	value |= data << 16;
	lfs2_file_read(&wr->lfs2_file->vfs->lfs, &wr->lfs2_file->file, &data, 1);
	value |= data << 24;
	return value;
}

static uint16_t read_int16(wav_decoder_t* wr) {
	uint8_t data;
	
	uint16_t value = 0;
	lfs2_file_read(&wr->lfs2_file->vfs->lfs, &wr->lfs2_file->file, &data, 1);
	value |= data << 0;
	lfs2_file_read(&wr->lfs2_file->vfs->lfs, &wr->lfs2_file->file, &data, 1);
	value |= data << 8;
	return value;
}

void* wav_decoder_init(void) {
	wav_decoder_t* wr = (wav_decoder_t*) malloc(sizeof(*wr));
	memset(wr, 0, sizeof(*wr));

	return wr;
}

void wav_decoder_deinit(void* obj) {
	wav_decoder_t* wr = (wav_decoder_t*) obj;
	free(wr);
}

esp_err_t wav_file_open(void* obj, const char *path_in)
{
	wav_decoder_t* wr = (wav_decoder_t*) obj;
	if(!wr){
		ESP_LOGE(TAG, "wr is null.");
		return ESP_FAIL;
	}

	wr->lfs2_file = vfs_lfs2_file_open(path_in);
	if(!wr->lfs2_file){
		ESP_LOGE(TAG, "fiel open fault.");
		return ESP_FAIL;
	}

	uint32_t tag, tag2, length;
	tag = read_tag(wr); // 4字节
	length = read_int32(wr); // 4字节
	if (tag != TAG('R', 'I', 'F', 'F') || length < 4) {
		return ESP_FAIL;	
	}

	tag2 = read_tag(wr);
	if (tag2 != TAG('W', 'A', 'V', 'E')) { // 4字节
		return ESP_FAIL;
	}

	uint32_t subtag, sublength;
	subtag = read_tag(wr);  // 4字节
	sublength = read_int32(wr);
	if (subtag != TAG('f', 'm', 't', ' ') || sublength < 16) {
		return ESP_FAIL;
	}
	wr->format          = read_int16(wr);
	wr->channels        = read_int16(wr);
	wr->sample_rate     = read_int32(wr);
	wr->byte_rate       = read_int32(wr);
	wr->block_align     = read_int16(wr);
	wr->bits_per_sample = read_int16(wr);
	ESP_LOGE(TAG, "wav format: %d, channels: %d sample rate: %d, bits per sample: %d", wr->format, wr->channels, wr->sample_rate, wr->bits_per_sample);

	subtag = read_tag(wr);  // 4字节
	if (subtag != TAG('d', 'a', 't', 'a')) {
		return ESP_FAIL;
	}
	sublength = read_int32(wr); // 读完后，文件定位在data首址
	wr->data_length = sublength;
	// ESP_LOGE(TAG, "data pos: %ld, data_len: %ld\n", lfs2_file_tell(&wr->lfs2_file->vfs->lfs, &wr->lfs2_file->file), wr->data_length);

	return ESP_OK;
}

void wav_file_close(void* obj)
{
	wav_decoder_t* wr = (wav_decoder_t*) obj;
	if(wr->lfs2_file){
		lfs2_file_close(&wr->lfs2_file->vfs->lfs, &wr->lfs2_file->file);
		free(wr->lfs2_file);
	}
}

int wav_decoder_get_header(void* obj, int* format, int* channels, int* sample_rate, int* bits_per_sample, unsigned int* data_length) {
	wav_decoder_t* wr = (wav_decoder_t*) obj;
	if (format)
		*format = wr->format;
	if (channels)
		*channels = wr->channels;
	if (sample_rate)
		*sample_rate = wr->sample_rate;
	if (bits_per_sample)
		*bits_per_sample = wr->bits_per_sample;
	if (data_length)
		*data_length = wr->data_length;
	return wr->format && wr->sample_rate;
}


int wav_decoder_get_channel(void* obj) {

	wav_decoder_t* wr = (wav_decoder_t*) obj;
	return wr->channels;
}

int wav_decoder_get_sample_rate(void* obj) {

	wav_decoder_t* wr = (wav_decoder_t*) obj;
	return wr->sample_rate;
}

int wav_decoder_get_data_length(void* obj) {

	wav_decoder_t* wr = (wav_decoder_t*) obj;
	return wr->data_length;
}