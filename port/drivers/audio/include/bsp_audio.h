/**
 * 
 * @copyright Copyright 2021 Espressif Systems (Shanghai) Co. Ltd.
 *
 *      Licensed under the Apache License, Version 2.0 (the "License");
 *      you may not use this file except in compliance with the License.
 *      You may obtain a copy of the License at
 *
 *               http://www.apache.org/licenses/LICENSE-2.0
 *
 *      Unless required by applicable law or agreed to in writing, software
 *      distributed under the License is distributed on an "AS IS" BASIS,
 *      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *      See the License for the specific language governing permissions and
 *      limitations under the License.
 */

#pragma once

#include <stdbool.h>
#include "esp_err.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "driver/i2s_std.h"
#include "driver/i2s_tdm.h"

/**
 * @brief Add dev board pin defination and check target.
 * 
 */

#if CONFIG_ESP32_S3_BOX_BOARD
    #include "esp32_s3_box_board.h"
#elif CONFIG_LABPLUS_CLASSROOM_KIT_NANJING_BOARD
    #include "audio/driver/labplus_classroom_kit_nanjing/bsp_board.h"
#elif CONFIG_LABPLUS_LEDONG_PRO_BOARD
    #include "labplus_Ledong_pro/bsp_audio_board.h"
#else 
    #error "Please select type of dev board"
#endif

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Power module of dev board. This can be expanded in the future.
 * 
 */
typedef enum {
    POWER_MODULE_LCD = 1,       /*!< LCD power control */
    POWER_MODULE_AUDIO,         /*!< Audio PA power control */
    POWER_MODULE_ALL = 0xff,    /*!< All module power control */
} power_module_t;

esp_err_t bsp_i2s_init(uint32_t sample_rate, int channel_format, int bits_per_sample);
esp_err_t bsp_i2s_deinit(bool is_rx_handle);
esp_err_t bsp_codec_dev_create(void);
esp_err_t bsp_codec_dev_delete(void);
esp_err_t bsp_codec_dev_open(int sample_rate, int channel_format, int bits_per_sample);
esp_err_t bsp_codec_dev_close(void);

esp_err_t bsp_audio_play(const int16_t* data, int length, TickType_t ticks_to_wait);

/**
 * @brief Get the record pcm data.
 * 
 * @param is_get_raw_channel Whether to get the recording data of the original number of channels. 
 *                           Otherwise, the corresponding number of channels will be filtered based on the board.
 * @param buffer The buffer where the data is stored.
 * @param buffer_len The buffer length.
 * @return
 *    - ESP_OK                  Success
 *    - Others                  Fail
 */
esp_err_t bsp_get_feed_data(bool is_get_raw_channel, int16_t *buffer, int buffer_len);

int bsp_get_feed_channel(void);

/**
 * @brief Set play volume
 * 
 * @return
 *    - ESP_OK: Success
 *    - Others: Fail
 */
esp_err_t bsp_audio_set_play_vol(int volume);

/**
 * @brief Get play volume
 * 
 * @return
 *    - ESP_OK: Success
 *    - Others: Fail
 */
esp_err_t bsp_audio_get_play_vol(int *volume);


#ifdef __cplusplus
}
#endif
