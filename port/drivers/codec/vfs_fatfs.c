/*
 * ESPRESSIF MIT License
 *
 * Copyright (c) 2019 <ESPRESSIF SYSTEMS (SHANGHAI) CO., LTD>
 *
 * Permission is hereby granted for use on all ESPRESSIF SYSTEMS products, in which case,
 * it is free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the Software is furnished
 * to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or
 * substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 * FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 * IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 */

#include "errno.h"
#include <string.h>

#include "esp_log.h"
#include "vfs_fatfs.h"
#include "audio_mem.h"
#include "extmod/vfs.h"

#include "extmod/vfs_fat.h"
#include "py/builtin.h"
#include "py/objstr.h"
#include "py/runtime.h"
#include "py/stream.h"

static const char *TAG = "VFS_FATFS";

typedef struct vfs_stream {
    int block_size;
    bool is_open;
    FIL file;
    FATFS *fatfs;
} vfs_stream_t;

vfs_stream_t *vfs = NULL;

esp_err_t vfs_fat_file_open(mp_obj_t path_in, mp_obj_t mode_in)
{
    mp_vfs_mount_t *existing_mount = MP_STATE_VM(vfs_mount_table);
    if (existing_mount == MP_VFS_NONE){
        ESP_LOGE(TAG, "fs none.............");
        return ESP_FAIL;
    }
    fs_user_mount_t *user_mount = MP_OBJ_TO_PTR(existing_mount->obj);
    if (user_mount == NULL) {
        ESP_LOGE(TAG, "No user mount");
        return ESP_FAIL;
    }
    
    if(!vfs){
        vfs = audio_calloc(1, sizeof(vfs_stream_t));
        if(!vfs)
            return ESP_FAIL;
        vfs->fatfs = &user_mount->fatfs;
        if(!vfs->fatfs){
            ESP_LOGE(TAG, "can not get fatfs......");
            return ESP_FAIL;
        }
    }

    const char *path =  mp_obj_str_get_str(path_in);
    int mode = 0;
    const char *mode_s = mp_obj_str_get_str(mode_in);
    // TODO make sure only one of r, w, x, a, and b, t are specified
    while (*mode_s) {
        switch (*mode_s++) {
            case 'r':
                mode |= FA_READ;
                break;
            case 'w':
                mode |= FA_WRITE | FA_CREATE_ALWAYS;
                break;
            case 'x':
                mode |= FA_WRITE | FA_CREATE_NEW;
                break;
            case 'a':
                mode |= FA_WRITE | FA_OPEN_ALWAYS;
                break;
            case '+':
                mode |= FA_READ | FA_WRITE;
                break;
            // case 'b':
            //     type = &mp_type_vfs_fat_fileio;
            //     break;
            // case 't':
            //     type = &mp_type_vfs_fat_textio;
                break;
        }
    }

    if (f_open(vfs->fatfs, &vfs->file, path, mode) == FR_OK) {
        vfs->is_open = true;
    }else{

    }

    FILINFO fno;    
    f_stat (vfs->fatfs, path, &fno);
    ESP_LOGE(TAG, "file size: %d, name: %s", (int)fno.fsize, (char *)fno.fname);

    return ESP_OK;
}

void vfs_fat_file_close(void)
{
    if(!vfs){
        f_close (&vfs->file);
        audio_free(vfs);
    }
}




