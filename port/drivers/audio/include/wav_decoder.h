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

#include "vfs_lfs2.h"
#include "py/obj.h"
#include "wave_head.h"

#ifdef __cplusplus
extern "C" {
#endif
typedef struct{
    mp_obj_vfs_lfs2_file_t *lfs2_file;
	wav_info_t wav_info;
} wav_decoder_t;


wav_decoder_t *wav_file_open(const char *path_in);
void wav_file_close(wav_decoder_t *wr);

void wav_file_read_task(void *arg);
void stream_i2s_out_task(void *arg);

#ifdef __cplusplus
}
#endif

#endif

