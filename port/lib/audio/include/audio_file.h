/*
 * audio_file.h
 *
 *  Created on: 2024.08.03
 *      Author: zhaohuijiang
 */

#ifndef MICROPY_INCLUDED_AUDIO_FILE_H
#define MICROPY_INCLUDED_AUDIO_FILE_H

#include <string.h>
#include <stdio.h>
#include "py/runtime.h"
#include "esp_err.h"

mp_obj_t audio_file_open(const char *filename, const char *mode);
void audio_file_close(mp_obj_t File);
int audio_file_read(mp_obj_t File, int *read_bytes, uint8_t *buf, uint32_t len);
int audio_file_write(mp_obj_t File, int *write_bytes, uint8_t *buf, uint32_t len);
void audio_chdir(const char *path);
void audio_feof(mp_obj_t File);
int audio_file_seek(mp_obj_t File, long offset, int whence);
mp_off_t audio_file_tell(mp_obj_t File);

#endif // MICROPY_INCLUDED_AUDIO_FILE_H
