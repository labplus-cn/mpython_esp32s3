/*
 * SPDX-FileCopyrightText: 2015-2022 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <stdlib.h>
#include <string.h>
#include "esp_log.h"
#include "esp_err.h"
#include "esp_vfs_fat.h"
#include "audio/fatfs/src/diskio_impl.h"
#include "audio/fatfs/src/diskio_rawflash.h"
#include "audio/fatfs/src/ff.h"

static const char* TAG = "vfs_fat_spiflash";
static FATFS *fs;
esp_err_t esp_vfs_fat_spiflash_mount(const char* partition_label)
{
    esp_err_t result = ESP_OK;

    const esp_partition_t *data_partition = esp_partition_find_first(ESP_PARTITION_TYPE_DATA,
            ESP_PARTITION_SUBTYPE_DATA_FAT, partition_label);
    if (data_partition == NULL) {
        ESP_LOGE(TAG, "Failed to find FATFS partition (type='data', subtype='fat', partition_label='%s'). Check the partition table.", partition_label);
        return ESP_ERR_NOT_FOUND;
    }

    // connect driver to FATFS
    BYTE pdrv = 0xFF;
    if (diskio_get_drive(&pdrv) != ESP_OK) {
        ESP_LOGD(TAG, "the maximum count of volumes is already mounted");
        return ESP_ERR_NO_MEM;
    }
    ESP_LOGD(TAG, "using pdrv=%i", pdrv);

    result = diskio_register_raw_partition(pdrv, data_partition); //把pdrv跟文件系统分区关联起来。
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "diskio_register_raw_partition failed pdrv=%i, error - 0x(%x)", pdrv, result);
        goto fail;
    }

    if(!fs){
        fs = ffs_memalloc(sizeof(FATFS));
        // ESP_LOGE(TAG, "FATFS size %d.", sizeof(FATFS));
    }

    // Try to mount partition
    // char drv[3] = {(char)('0' + pdrv), ':', 0};
    fs->drv = pdrv;
    FRESULT fresult = fs_mount(fs);
    if (fresult != FR_OK) {
        result = ESP_FAIL;
        goto fail;
    }
    // ESP_LOGE(TAG, "fs_mount sucess.\n");
    return ESP_OK;

fail:
    diskio_unregister_raw_partition(pdrv);
    return result;
}

esp_err_t esp_vfs_fat_spiflash_unmount(const char* partition_label)
{
    const esp_partition_t *data_partition = esp_partition_find_first(ESP_PARTITION_TYPE_DATA,
            ESP_PARTITION_SUBTYPE_DATA_FAT, partition_label);

    if (data_partition == NULL) {
        ESP_LOGE(TAG, "Failed to find FATFS partition (type='data', subtype='fat', partition_label='%s'). Check the partition table.", partition_label);
        return ESP_ERR_NOT_FOUND;
    }

    BYTE pdrv = ffs_diskio_get_pdrv_raw(data_partition);
    if (pdrv == 0xff) {
        return ESP_ERR_INVALID_STATE;
    }

    // char drv[3] = {(char)('0' + pdrv), ':', 0};
    fs_umount(fs);
    if(fs){
        ffs_memfree(fs);
    }

    diskio_unregister_raw_partition(pdrv);
    return ESP_OK;
}

void* esp_vfs_fat_spiflash_get_fs(void)
{
    return fs;
}
