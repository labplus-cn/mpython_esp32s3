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
#include "vfs_lfs2.h"
#include "audio_mem.h"
#include "extmod/vfs.h"

// #include "extmod/vfs_fat.h"
#include "lib/littlefs/lfs2.h"
#include "py/builtin.h"
#include "py/objstr.h"
#include "py/runtime.h"
#include "py/stream.h"

static const char *TAG = "VFS_LFS2";

typedef struct _mp_obj_vfs_lfs2_t {
    mp_obj_base_t base;
    mp_vfs_blockdev_t blockdev;
    bool enable_mtime;
    vstr_t cur_dir;
    struct lfs2_config config;
    lfs2_t lfs;
} mp_obj_vfs_lfs2_t;

typedef struct _mp_obj_vfs_lfs2_file_t {
    mp_obj_base_t base;
    mp_obj_vfs_lfs2_t *vfs;
    uint8_t mtime[8];
    lfs2_file_t file;
    struct lfs2_file_config cfg;
    struct lfs2_attr attrs[1];
    uint8_t file_buffer[0];
} mp_obj_vfs_lfs2_file_t;

mp_obj_vfs_lfs2_t *mp_obj_lfs2;
mp_obj_vfs_lfs2_file_t *mp_obj_lfs2_file;
extern mp_obj_t mp_vfs_lfs2_file_open(mp_obj_t self_in, mp_obj_t path_in, mp_obj_t mode_in);

esp_err_t vfs_lfs2_open(mp_obj_t path_in, mp_obj_t mode_in)
{
    if(!mp_obj_lfs2){
        // mp_obj_vfs_lfs2_t mp_obj_lfs2 = audio_calloc(1, sizeof(mp_obj_vfs_lfs2_t));
        mp_vfs_mount_t *existing_mount = MP_STATE_VM(vfs_mount_table);

        if (existing_mount == MP_VFS_NONE){
            ESP_LOGE(TAG, "fs none.");
            return -1;
        }
        mp_obj_lfs2 = MP_OBJ_TO_PTR(existing_mount->obj);
        if (mp_obj_lfs2 == NULL) {
            ESP_LOGE(TAG, "No user mount");
        }
    }

    mp_obj_lfs2_file = mp_vfs_lfs2_file_open(mp_obj_lfs2, path_in, mode_in);
    if(!mp_obj_lfs2_file){      
        // struct lfs2_fsinfo fsinfo = { 0 };
        // lfs2_fs_stat(&mp_obj_lfs2->lfs, &fsinfo);
        // ESP_LOGE(TAG, "block size: %d byte, block count: %d", (int)fsinfo.block_size, (int)fsinfo.block_count); 
        // ESP_LOGE(TAG, "file size: %ld byte",lfs2_file_size(&mp_obj_lfs2->lfs, &mp_obj_lfs2_file->file));   
            return -1;    
    }

    return ESP_OK;
}




