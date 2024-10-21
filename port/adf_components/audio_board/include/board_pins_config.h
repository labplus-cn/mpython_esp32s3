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

#ifndef _BOARD_PINS_CONFIG_H_
#define _BOARD_PINS_CONFIG_H_

#include "driver/i2c.h"
#include "driver/spi_common.h"
#include "driver/spi_master.h"
#include "driver/spi_slave.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief                  Board i2s pin definition
 */
typedef struct {
    int mck_io_num;         /*!< MCK pin, output */
    int bck_io_num;         /*!< BCK pin, input in slave role, output in master role */
    int ws_io_num;          /*!< WS pin, input in slave role, output in master role */
    int data_out_num;       /*!< DATA pin, output */
    int data_in_num;        /*!< DATA pin, input */
} board_i2s_pin_t;

/**
 * @brief                  Get i2c pins configuration
 *
 * @param      port        i2c port number to get configuration
 * @param      i2c_config  i2c configuration parameters
 *
 * @return
 *     - ESP_OK
 *     - ESP_FAIL
 */
esp_err_t get_i2c_pins(i2c_port_t port, i2c_config_t *i2c_config);

/**
 * @brief                  Get i2s pins configuration
 *
 * @param      port        i2s port number to get configuration
 * @param      i2s_config  i2s configuration parameters
 *
 * @return
 *     - ESP_OK
 *     - ESP_FAIL
 */
esp_err_t get_i2s_pins(int port, board_i2s_pin_t *i2s_config);

#ifdef __cplusplus
}
#endif

#endif
