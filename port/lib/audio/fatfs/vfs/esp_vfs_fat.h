/*
 * SPDX-FileCopyrightText: 2015-2023 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once
#include <stddef.h>
#include "esp_err.h"
#include "driver/gpio.h"
#include "audio/fatfs/src/ff.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Convenience function to initialize read-only FAT filesystem and register it in VFS
 *
 * This is an all-in-one function which does the following:
 *
 * - finds the partition with defined partition_label. Partition label should be
 *   configured in the partition table.
 * - mounts FAT partition using FATFS library
 * - registers FATFS library with VFS, with prefix given by base_prefix variable
 *
 * @note Wear levelling is not used when FAT is mounted in read-only mode using this function.
 *
 * @param base_path        path where FATFS partition should be mounted (e.g. "/spiflash")
 * @param partition_label  label of the partition which should be used
 * @param mount_config     pointer to structure with extra parameters for mounting FATFS
 * @return
 *      - ESP_OK on success
 *      - ESP_ERR_NOT_FOUND if the partition table does not contain FATFS partition with given label
 *      - ESP_ERR_INVALID_STATE if esp_vfs_fat_spiflash_mount_ro was already called for the same partition
 *      - ESP_ERR_NO_MEM if memory can not be allocated
 *      - ESP_FAIL if partition can not be mounted
 *      - other error codes from SPI flash driver, or FATFS drivers
 */
esp_err_t esp_vfs_fat_spiflash_mount(const char* partition_label);

/**
 * @brief Unmount FAT filesystem and release resources acquired using esp_vfs_fat_spiflash_mount_ro
 *
 * @param base_path  path where partition should be registered (e.g. "/spiflash")
 * @param partition_label  label of partition to be unmounted
 *
 * @return
 *      - ESP_OK on success
 *      - ESP_ERR_INVALID_STATE if esp_vfs_fat_spiflash_mount_rw_wl hasn't been called
 */
esp_err_t esp_vfs_fat_spiflash_unmount(const char* partition_label);

void* esp_vfs_fat_spiflash_get_fs(void);

#ifdef __cplusplus
}
#endif
