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

#ifndef WAV_DECODER_H
#define WAV_DECODER_H

#ifdef __cplusplus
extern "C" {
#endif

#include "audio/fatfs/src/ff.h"

typedef struct wav_decoder {
	FATFS *fs;
	FIL *file;
	uint32_t data_length;

	int format;
	int sample_rate;
	int bits_per_sample;
	int channels;
	int byte_rate;
	int block_align;
} wav_decoder_t;

void* wav_decoder_init(const char* filename);
void wav_decoder_deinit(void* obj);
int wav_decoder_get_header(void* obj, int* format, int* channels, int* sample_rate, int* bits_per_sample, unsigned int* data_length);
int wav_decoder_get_sample_rate(void* obj);
int wav_decoder_get_channel(void* obj);
int wav_decoder_get_data_length(void* obj);

esp_err_t wav_file_open(void* obj, const char *filename);
void wav_file_close(void* obj);
int wav_file_read(void* obj, unsigned char* data, unsigned int length);

#ifdef __cplusplus
}
#endif

#endif

