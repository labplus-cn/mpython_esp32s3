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
#include "py/runtime.h"
#include "esp_log.h"
#include "vfs_lfs2.h"
#include "extmod/vfs_lfs.h"
#include "shared/timeutils/timeutils.h"
#include "py/mphal.h"

static const char *TAG = "VFS_LFS2";

#define LFS_ATTR_MTIME (1) // 64-bit little endian, nanoseconds since 1970/1/1

static void lfs_get_mtime(uint8_t buf[8]) {
    // On-disk storage of timestamps uses 1970 as the Epoch, so convert from host's Epoch.
    uint64_t ns = timeutils_nanoseconds_since_epoch_to_nanoseconds_since_1970(mp_hal_time_ns());
    // Store "ns" to "buf" in little-endian format (essentially htole64).
    for (size_t i = 0; i < 8; ++i) {
        buf[i] = ns;
        ns >>= 8;
    }
}

mp_obj_vfs_lfs2_file_t* vfs_lfs2_file_open(const char *path_in)
{
    mp_vfs_mount_t *existing_mount = MP_STATE_VM(vfs_mount_table);

    if (existing_mount == MP_VFS_NONE){
        ESP_LOGE(TAG, "No root.");
        return mp_const_none;
    }

    mp_obj_vfs_lfs2_t *mp_obj_lfs2 = MP_OBJ_TO_PTR(existing_mount->obj);
    if (mp_obj_lfs2 == NULL) {
        ESP_LOGE(TAG, "No root lfs2 file system.");
        return mp_const_none;
    }

    const mp_obj_type_t *type = &mp_type_vfs_lfs2_textio;

    mp_obj_vfs_lfs2_file_t *mp_obj_lfs2_file = calloc(sizeof(mp_obj_vfs_lfs2_file_t) + mp_obj_lfs2->lfs.cfg->cache_size, sizeof(uint8_t));
    mp_obj_lfs2_file->base.type = type;

    mp_obj_lfs2_file->vfs = mp_obj_lfs2;
    mp_obj_lfs2_file->cfg.buffer = &mp_obj_lfs2_file->file_buffer[0];

    if (mp_obj_lfs2->enable_mtime) {
        lfs_get_mtime(&mp_obj_lfs2_file->mtime[0]);
        mp_obj_lfs2_file->attrs[0].type = LFS_ATTR_MTIME;
        mp_obj_lfs2_file->attrs[0].buffer = &mp_obj_lfs2_file->mtime[0];
        mp_obj_lfs2_file->attrs[0].size = sizeof(mp_obj_lfs2_file->mtime);
        mp_obj_lfs2_file->cfg.attrs = &mp_obj_lfs2_file->attrs[0];
        mp_obj_lfs2_file->cfg.attr_count = MP_ARRAY_SIZE(mp_obj_lfs2_file->attrs);
    }

    int ret = lfs2_file_opencfg(&mp_obj_lfs2->lfs, &mp_obj_lfs2_file->file, path_in, LFS2_O_RDONLY, &mp_obj_lfs2_file->cfg);
    if (ret < 0) {
        mp_obj_lfs2_file->vfs = NULL;
        mp_raise_OSError(-ret);
    }

    // struct lfs2_fsinfo fsinfo = { 0 };
    // lfs2_fs_stat(&mp_obj_lfs2->lfs, &fsinfo);
    // ESP_LOGE(TAG, "block size: %d byte, block count: %d", (int)fsinfo.block_size, (int)fsinfo.block_count); 
    // ESP_LOGE(TAG, "file size: %ld byte",lfs2_file_size(&mp_obj_lfs2_file->vfs->lfs, &mp_obj_lfs2_file->file));   

    return mp_obj_lfs2_file;
}




