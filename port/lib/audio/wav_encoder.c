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

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include "audio/fatfs/src/ff.h"
#include "audio/fatfs/vfs/esp_vfs_fat.h"
#include "audio/include/wav_encoder.h"

struct wav_encoder {
	FATFS *fs;
	FIL *file;
	int data_length;

	int sample_rate;
	int bits_per_sample;
	int channels;
};

static void write_string(struct wav_encoder* ww, const char *str) {
	unsigned int n;

	fs_write(ww->file, &str[0], 1, &n);
	fs_write(ww->file, &str[1], 1, &n);
	fs_write(ww->file, &str[2], 1, &n);
	fs_write(ww->file, &str[3], 1, &n);
}

static void write_int32(struct wav_encoder* ww, int value) {
	uint8_t tmp;
	unsigned int n;

	tmp =(value >>  0) & 0xff;
	fs_write(ww->file, &tmp, 1, &n);
	tmp = (value >>  8) & 0xff;
	fs_write(ww->file, &tmp, 1, &n);
	tmp =  (value >> 16) & 0xff;
	fs_write(ww->file, &tmp, 1, &n);
	tmp = (value >> 24) & 0xff;
	fs_write(ww->file, &tmp, 1, &n);
}

static void write_int16(struct wav_encoder* ww, int value) {
	uint8_t tmp;
	unsigned int n;

	tmp = (value >> 0) & 0xff;
	fs_write(ww->file, &tmp, 1, &n);
	tmp = (value >> 8) & 0xff;
	fs_write(ww->file, &tmp, 1, &n);
}

static void write_header(struct wav_encoder* ww, int length) {
	int bytes_per_frame, bytes_per_sec;
	write_string(ww, "RIFF");
	write_int32(ww, 4 + 8 + 16 + 8 + length);
	write_string(ww, "WAVE");

	write_string(ww, "fmt ");
	write_int32(ww, 16);

	bytes_per_frame = ww->bits_per_sample/8*ww->channels;
	bytes_per_sec   = bytes_per_frame*ww->sample_rate;
	write_int16(ww, 1);                   // Format
	write_int16(ww, ww->channels);        // Channels
	write_int32(ww, ww->sample_rate);     // Samplerate
	write_int32(ww, bytes_per_sec);       // Bytes per sec
	write_int16(ww, bytes_per_frame);     // Bytes per frame
	write_int16(ww, ww->bits_per_sample); // Bits per sample

	write_string(ww, "data");
	write_int32(ww, length);
}

void* wav_encoder_open(const char *filename, int sample_rate, int bits_per_sample, int channels) {
	struct wav_encoder* ww = (struct wav_encoder*) malloc(sizeof(*ww));
	memset(ww, 0, sizeof(*ww));

	esp_vfs_fat_spiflash_mount("vfs");
	ww->fs = esp_vfs_fat_spiflash_get_fs();
	ww->file = (FIL*) malloc(sizeof(FIL));
	if (ww->fs == NULL || fs_open(ww->fs, ww->file, filename, FA_READ) != FR_OK) {
		free(ww);
		return NULL;
	}

	ww->data_length = 0;
	ww->sample_rate = sample_rate;
	ww->bits_per_sample = bits_per_sample;
	ww->channels = channels;

	write_header(ww, ww->data_length);
	return ww;
}

void wav_encoder_close(void* obj) {
	struct wav_encoder* ww = (struct wav_encoder*) obj;
	if (ww->file == NULL) {
		free(ww);
		return;
	}
	fs_lseek(ww->file, 0);
	write_header(ww, ww->data_length);
	fs_close(ww->file);
	free(ww);
}

void wav_encoder_run(void* obj, unsigned char* data, int length) {
	struct wav_encoder* ww = (struct wav_encoder*) obj;
	unsigned int n;
	if (ww->file == NULL)
		return;
	fs_write(ww->file, data, length, &n);
	ww->data_length += length;
}

