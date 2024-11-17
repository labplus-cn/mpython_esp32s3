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

#ifndef __WAV_CODEC_H_
#define __WAV_CODEC_H_

#include "vfs_lfs2.h"
#include "py/obj.h"
#include "freertos/ringbuf.h"
#include "wave_head.h"

#ifdef __cplusplus
extern "C" {
#endif

#define CORE_NUM0 0
#define CORE_NUM1 1
typedef struct {
    uint16_t channels;             // Number of channel;1: 1 channel;2: 2 channels;
    uint32_t bitRate;               // bit sample rate
    uint32_t sampleRate;            // sample rate
    uint16_t bits_per_sample;                   // bit length 16bit,24bit,32bit
} wav_fmt_t;
typedef struct{
    mp_obj_vfs_lfs2_file_t *lfs2_file;
	wav_info_t wav_info;
} wav_codec_t;


wav_codec_t *wav_file_open(const char *path_in, int mode);
void wav_file_close(wav_codec_t *wav_codec);

// void wav_file_read_task(void *arg);
// void stream_i2s_write_task(void *arg);
void stream_i2s_read_task(void *arg);

#ifdef __cplusplus
}
#endif

#endif

