/*
 * SPDX-FileCopyrightText: 2015-2022 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <string.h>
#include "diskio_impl.h"
#include "ffconf.h"
#include "ff.h"
#include "esp_log.h"
#include "diskio_rawflash.h"
#include "esp_compiler.h"
#include "spi_flash_mmap.h"

static const char* TAG = "diskio_rawflash";

const esp_partition_t* ffs_raw_handles[FF_VOLUMES];


DSTATUS ffs_raw_initialize (BYTE pdrv)
{
    return 0;
}

DSTATUS ffs_raw_status (BYTE pdrv)
{
    return 0;
}

DRESULT ffs_raw_read (BYTE pdrv, BYTE *buff, DWORD sector, UINT count)
{
    ESP_LOGV(TAG, "ffs_raw_read - pdrv=%i, sector=%i, count=%in", (unsigned int)pdrv, (unsigned int)sector, (unsigned int)count);
    const esp_partition_t* part = ffs_raw_handles[pdrv];
    assert(part);
    esp_err_t err = esp_partition_read(part, sector * SPI_FLASH_SEC_SIZE, buff, count * SPI_FLASH_SEC_SIZE);
    if (unlikely(err != ESP_OK)) {
        ESP_LOGE(TAG, "esp_partition_read failed (0x%x)", err);
        return RES_ERROR;
    }
    return RES_OK;
}


DRESULT ffs_raw_write (BYTE pdrv, const BYTE *buff, DWORD sector, UINT count)
{
    return RES_ERROR;
}

DRESULT ffs_raw_ioctl (BYTE pdrv, BYTE cmd, void *buff)
{
    const esp_partition_t* part = ffs_raw_handles[pdrv];
    ESP_LOGV(TAG, "ffs_raw_ioctl: cmd=%in", cmd);
    assert(part);
    switch (cmd) {
        case IOCTL_INIT:
            *((BYTE *) buff) = 0x0;
            return RES_OK;
        case IOCTL_STATUS:
        case CTRL_TRIM:
        case CTRL_SYNC:
            return RES_OK;
        case GET_SECTOR_COUNT:
            *((DWORD *) buff) = part->size / SPI_FLASH_SEC_SIZE;
            return RES_OK;
        case GET_SECTOR_SIZE:
            *((WORD *) buff) = SPI_FLASH_SEC_SIZE;
            return RES_OK;
        case GET_BLOCK_SIZE:
            return RES_ERROR;
    }
    return RES_ERROR;
}


esp_err_t diskio_register_raw_partition(BYTE pdrv, const esp_partition_t* part_handle)
{
    if (pdrv >= FF_VOLUMES) {
        return ESP_ERR_INVALID_ARG;
    }
    static const diskio_impl_t raw_impl = {
        .init = &ffs_raw_initialize,
        .status = &ffs_raw_status,
        .read = &ffs_raw_read,
        .write = &ffs_raw_write,
        .ioctl = &ffs_raw_ioctl
    };
    diskio_register(pdrv, &raw_impl);
    ffs_raw_handles[pdrv] = part_handle;
    return ESP_OK;

}


BYTE ffs_diskio_get_pdrv_raw(const esp_partition_t* part_handle)
{
    for (int i = 0; i < FF_VOLUMES; i++) {
        if (part_handle == ffs_raw_handles[i]) {
            return i;
        }
    }
    return 0xff;
}
