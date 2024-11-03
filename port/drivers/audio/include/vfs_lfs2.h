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

#ifndef _VFS_LFS2_H_
#define _VFS_LFS2_H_

#include "esp_err.h"
#include "py/runtime.h"
#include "lib/littlefs/lfs2.h"
#include "extmod/vfs.h"
#include "py/stream.h"
#include "py/builtin.h"

#ifdef __cplusplus
extern "C" {
#endif

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

mp_obj_vfs_lfs2_file_t* vfs_lfs2_file_open(const char *path_in);

#ifdef __cplusplus
}
#endif

#endif
