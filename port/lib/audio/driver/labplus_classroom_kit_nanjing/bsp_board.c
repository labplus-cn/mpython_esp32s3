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

#include "string.h"
#include "es8388_codec.h"
#include "bsp_board.h"
#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
#include "driver/i2s_std.h"
#include "driver/i2s_tdm.h"
#include "soc/soc_caps.h"
#else
#include "driver/i2s.h"
#endif
#include "driver/gpio.h"
#include "esp_err.h"
#include "esp_log.h"
#include "driver/i2c.h"
#include "esp_rom_sys.h"
#include "esp_check.h"
// #include "audio/fatfs/audio_file.h"
#if ((SOC_SDMMC_HOST_SUPPORTED) && (FUNC_SDMMC_EN))
#include "driver/sdmmc_host.h"
#endif /* ((SOC_SDMMC_HOST_SUPPORTED) && (FUNC_SDMMC_EN)) */

#define GPIO_MUTE_NUM   GPIO_NUM_1
#define GPIO_MUTE_LEVEL 1
#define ACK_CHECK_EN   0x1     /*!< I2C master will check ack from slave*/
#define ADC_I2S_CHANNEL 4
static const char *TAG = "board";
#define I2S_NUM I2S_NUM_1


#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
static i2s_chan_handle_t                tx_handle = NULL;        // I2S tx channel handler
static i2s_chan_handle_t                rx_handle = NULL;        // I2S rx channel handler
#endif
static const audio_codec_data_if_t *record_data_if = NULL;
static const audio_codec_ctrl_if_t *record_ctrl_if = NULL;
static const audio_codec_if_t *record_codec_if = NULL;
static esp_codec_dev_handle_t record_dev = NULL;

static const audio_codec_data_if_t *play_data_if = NULL;
static const audio_codec_ctrl_if_t *play_ctrl_if = NULL;
static const audio_codec_gpio_if_t *play_gpio_if = NULL;
static const audio_codec_if_t *play_codec_if = NULL;
static esp_codec_dev_handle_t play_dev = NULL;

static esp_err_t bsp_i2s_init(uint32_t sample_rate, int channel_format, int bits_per_sample)
{
    esp_err_t ret_val = ESP_OK;

#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
    i2s_slot_mode_t channel_fmt = I2S_SLOT_MODE_STEREO;
    if (channel_format == 1) {
        channel_fmt = I2S_SLOT_MODE_MONO;
    } else if (channel_format == 2) {
        channel_fmt = I2S_SLOT_MODE_STEREO;
    } else {
        ESP_LOGE(TAG, "Unable to configure channel_format %d", channel_format);
        channel_format = 1;
        channel_fmt = I2S_SLOT_MODE_MONO;
    }

    if (bits_per_sample != 16 && bits_per_sample != 32) {
        ESP_LOGE(TAG, "Unable to configure bits_per_sample %d", bits_per_sample);
        bits_per_sample = 16;
    }

    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM, I2S_ROLE_MASTER);

    ret_val |= i2s_new_channel(&chan_cfg,  &tx_handle, &rx_handle);
    i2s_std_config_t std_cfg = I2S_CONFIG_DEFAULT(sample_rate, channel_fmt, bits_per_sample);
    ret_val |= i2s_channel_init_std_mode(tx_handle, &std_cfg);
    ret_val |= i2s_channel_init_std_mode(rx_handle, &std_cfg);
    ret_val |= i2s_channel_enable(tx_handle);
    ret_val |= i2s_channel_enable(rx_handle);
    ESP_LOGE(TAG, "I2S rx init end.");

    return ESP_OK;
}
/* 创建rx_handle，初始化并便能。*/
static esp_err_t bsp_i2s_rx_init(uint32_t sample_rate, int channel_format, int bits_per_sample)
{
    esp_err_t ret_val = ESP_OK;

#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
    i2s_slot_mode_t channel_fmt = I2S_SLOT_MODE_STEREO;
    if (channel_format == 1) {
        channel_fmt = I2S_SLOT_MODE_MONO;
    } else if (channel_format == 2) {
        channel_fmt = I2S_SLOT_MODE_STEREO;
    } else {
        ESP_LOGE(TAG, "Unable to configure channel_format %d", channel_format);
        channel_format = 1;
        channel_fmt = I2S_SLOT_MODE_MONO;
    }

    if (bits_per_sample != 16 && bits_per_sample != 32) {
        ESP_LOGE(TAG, "Unable to configure bits_per_sample %d", bits_per_sample);
        bits_per_sample = 16;
    }

    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM, I2S_ROLE_MASTER);

    ret_val |= i2s_new_channel(&chan_cfg, NULL, &rx_handle);
    i2s_std_config_t std_cfg = I2S_CONFIG_DEFAULT(sample_rate, channel_fmt, bits_per_sample);
    ret_val |= i2s_channel_init_std_mode(rx_handle, &std_cfg);
    ret_val |= i2s_channel_enable(rx_handle);
    ESP_LOGE(TAG, "I2S rx init end.");
#else
    i2s_channel_fmt_t channel_fmt = I2S_CHANNEL_FMT_RIGHT_LEFT;
    if (channel_format == 1) {
        channel_fmt = I2S_CHANNEL_FMT_ONLY_LEFT;
    } else if (channel_format == 2) {
        channel_fmt = I2S_CHANNEL_FMT_RIGHT_LEFT;
    } else {
        ESP_LOGE(TAG, "Unable to configure channel_format %d", channel_format);
        channel_format = 1;
        channel_fmt = I2S_CHANNEL_FMT_ONLY_LEFT;
    }

    if (bits_per_sample != 16 && bits_per_sample != 32) {
        ESP_LOGE(TAG, "Unable to configure bits_per_sample %d", bits_per_sample);
        bits_per_sample = 16;
    }

    if (i2s_num == I2S_NUM_1) {
        i2s_config_t i2s_config = I2S_CONFIG_DEFAULT(sample_rate, channel_fmt, bits_per_sample);

        i2s_pin_config_t pin_config = {
            .bck_io_num = GPIO_I2S_SCLK,
            .ws_io_num = GPIO_I2S_LRCK,
            .data_out_num = GPIO_I2S_DOUT,
            .data_in_num = GPIO_I2S_SDIN,
            .mck_io_num = GPIO_I2S_MCLK,
        };

        ret_val |= i2s_driver_install(i2s_num, &i2s_config, 0, NULL);
        ret_val |= i2s_set_pin(i2s_num, &pin_config);
    } else if (i2s_num == I2S_NUM_0) {
        i2s_config_t i2s_config = I2S0_CONFIG_DEFAULT(sample_rate, channel_fmt, bits_per_sample);

        i2s_pin_config_t pin_config = {
            .bck_io_num = GPIO_I2S0_SCLK,
            .ws_io_num = GPIO_I2S0_LRCK,
            .data_out_num = GPIO_I2S0_DOUT,
            .data_in_num = GPIO_I2S0_SDIN,
            .mck_io_num = GPIO_I2S0_MCLK,
        };

        ret_val |= i2s_driver_install(i2s_num, &i2s_config, 0, NULL);
        ret_val |= i2s_set_pin(i2s_num, &pin_config);
    }
#endif

    return ret_val;
}

/* 创建tx_handle，初始化并便能。*/
static esp_err_t bsp_i2s_tx_init(uint32_t sample_rate, int channel_format, int bits_per_sample)
{
    esp_err_t ret_val = ESP_OK;

#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
    i2s_slot_mode_t channel_fmt = I2S_SLOT_MODE_STEREO;
    if (channel_format == 1) {
        channel_fmt = I2S_SLOT_MODE_MONO;
    } else if (channel_format == 2) {
        channel_fmt = I2S_SLOT_MODE_STEREO;
    } else {
        ESP_LOGE(TAG, "Unable to configure channel_format %d", channel_format);
        channel_format = 1;
        channel_fmt = I2S_SLOT_MODE_MONO;
    }

    if (bits_per_sample != 16 && bits_per_sample != 32) {
        ESP_LOGE(TAG, "Unable to configure bits_per_sample %d", bits_per_sample);
        bits_per_sample = 16;
    }

    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM, I2S_ROLE_MASTER);
    chan_cfg.auto_clear = true; // Auto clear the legacy data in the DMA buffer

    ret_val |= i2s_new_channel(&chan_cfg, &tx_handle, NULL);
    i2s_std_config_t std_cfg = I2S_CONFIG_DEFAULT(sample_rate, channel_fmt, bits_per_sample);
    ret_val |= i2s_channel_init_std_mode(tx_handle, &std_cfg);
    ret_val |= i2s_channel_enable(tx_handle);
    ESP_LOGE(TAG, "I2S tx init end.");
#else
    i2s_channel_fmt_t channel_fmt = I2S_CHANNEL_FMT_RIGHT_LEFT;
    if (channel_format == 1) {
        channel_fmt = I2S_CHANNEL_FMT_ONLY_LEFT;
    } else if (channel_format == 2) {
        channel_fmt = I2S_CHANNEL_FMT_RIGHT_LEFT;
    } else {
        ESP_LOGE(TAG, "Unable to configure channel_format %d", channel_format);
        channel_format = 1;
        channel_fmt = I2S_CHANNEL_FMT_ONLY_LEFT;
    }

    if (bits_per_sample != 16 && bits_per_sample != 32) {
        ESP_LOGE(TAG, "Unable to configure bits_per_sample %d", bits_per_sample);
        bits_per_sample = 16;
    }

    if (i2s_num == I2S_NUM_1) {
        i2s_config_t i2s_config = I2S_CONFIG_DEFAULT(sample_rate, channel_fmt, bits_per_sample);

        i2s_pin_config_t pin_config = {
            .bck_io_num = GPIO_I2S_SCLK,
            .ws_io_num = GPIO_I2S_LRCK,
            .data_out_num = GPIO_I2S_DOUT,
            .data_in_num = GPIO_I2S_SDIN,
            .mck_io_num = GPIO_I2S_MCLK,
        };

        ret_val |= i2s_driver_install(i2s_num, &i2s_config, 0, NULL);
        ret_val |= i2s_set_pin(i2s_num, &pin_config);
    } else if (i2s_num == I2S_NUM_0) {
        i2s_config_t i2s_config = I2S0_CONFIG_DEFAULT(sample_rate, channel_fmt, bits_per_sample);

        i2s_pin_config_t pin_config = {
            .bck_io_num = GPIO_I2S0_SCLK,
            .ws_io_num = GPIO_I2S0_LRCK,
            .data_out_num = GPIO_I2S0_DOUT,
            .data_in_num = GPIO_I2S0_SDIN,
            .mck_io_num = GPIO_I2S0_MCLK,
        };

        ret_val |= i2s_driver_install(i2s_num, &i2s_config, 0, NULL);
        ret_val |= i2s_set_pin(i2s_num, &pin_config);
    }
#endif

    return ret_val;
}
/* 删除i2s通道，并释放相关资源。*/
static esp_err_t bsp_i2s_deinit(bool is_rx_handle)
{
    esp_err_t ret_val = ESP_OK;

#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
    if(is_rx_handle){
        if (rx_handle) {
            ret_val |= i2s_channel_disable(rx_handle);
            ret_val |= i2s_del_channel(rx_handle);
            rx_handle = NULL;
        }
    }else{
        if (tx_handle) {
                ret_val |= i2s_channel_disable(tx_handle);
                ret_val |= i2s_del_channel(tx_handle);
                tx_handle = NULL;
        }
    }
#else
    ret_val |= i2s_stop(I2S_NUM);
    ret_val |= i2s_driver_uninstall(I2S_NUM);
#endif

    return ret_val;
}

esp_err_t bsp_i2c_init(i2c_port_t i2c_num, uint32_t clk_speed)
{
    // static i2c_config_t i2c_cfg = {
    //     .mode = I2C_MODE_MASTER,
    //     .scl_io_num = GPIO_I2C_SCL,
    //     .sda_io_num = GPIO_I2C_SDA,
    //     .scl_pullup_en = GPIO_PULLUP_DISABLE,
    //     .sda_pullup_en = GPIO_PULLUP_DISABLE,
    //     .master.clk_speed = 400000,
    //     // .clk_flags = I2C_SCLK_SRC_FLAG_AWARE_DFS,
    // };
    // esp_err_t ret = i2c_param_config(i2c_num, &i2c_cfg);
    // if (ret != ESP_OK) {
    //     return ESP_FAIL;
    // }
    // return i2c_driver_install(i2c_num, i2c_cfg.mode, 0, 0, 0);
    return ESP_OK;
}

esp_err_t bsp_codec_record_dev_create(uint32_t sample_rate, int channel_format, int bits_per_sample)
{
    esp_err_t ret_val = ESP_OK;

    // bsp_i2s_rx_init(sample_rate, channel_format, bits_per_sample);

    // Do initialize of related interface: data_if, ctrl_if and gpio_if
    audio_codec_i2s_cfg_t i2s_cfg = {
        .port = I2S_NUM,
#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
        .rx_handle = rx_handle,
        .tx_handle = NULL,
#endif
    };
    record_data_if = audio_codec_new_i2s_data(&i2s_cfg);

    audio_codec_i2c_cfg_t i2c_cfg = {.addr = ES8388_CODEC_DEFAULT_ADDR};
    record_ctrl_if = audio_codec_new_i2c_ctrl(&i2c_cfg);
    // New input codec interface
    es8388_codec_cfg_t es8388_cfg = {
        .codec_mode = ESP_CODEC_DEV_WORK_MODE_ADC,
        .ctrl_if = record_ctrl_if,
        .master_mode = false,
    };
    record_codec_if = es8388_codec_new(&es8388_cfg);
    ESP_LOGE(TAG, "es8388 recor_codec_if create.");
    // New input codec device
    esp_codec_dev_cfg_t dev_cfg = {
        .codec_if = record_codec_if,
        .data_if = record_data_if,
        .dev_type = ESP_CODEC_DEV_TYPE_IN,
    };
    record_dev = esp_codec_dev_new(&dev_cfg);

    esp_codec_dev_sample_info_t fs = {
        .sample_rate = 16000,
        .channel = 2,
        .bits_per_sample = 32,
    };
    esp_codec_dev_open(record_dev, &fs);
    // esp_codec_dev_set_in_gain(record_dev, RECORD_VOLUME);
    esp_codec_dev_set_in_channel_gain(record_dev, ESP_CODEC_DEV_MAKE_CHANNEL_MASK(0), RECORD_VOLUME);
    esp_codec_dev_set_in_channel_gain(record_dev, ESP_CODEC_DEV_MAKE_CHANNEL_MASK(1), RECORD_VOLUME);

    ESP_LOGE(TAG, "recorder dev create.");
    return ret_val;
}

esp_err_t bsp_codec_play_dev_create(uint32_t sample_rate, int channel_format, int bits_per_sample)
{
    esp_err_t ret_val = ESP_OK;

    bsp_i2s_init(sample_rate, channel_format, bits_per_sample);
    // bsp_i2s_rx_init(16000, 2, 32);
    // Do initialize of related interface: data_if, ctrl_if and gpio_if
    audio_codec_i2s_cfg_t i2s_cfg = {
        .port = I2S_NUM,
#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
        .rx_handle = NULL,
        .tx_handle = tx_handle,
#endif
    };
    play_data_if = audio_codec_new_i2s_data(&i2s_cfg);

    audio_codec_i2c_cfg_t i2c_cfg = {.addr = ES8388_CODEC_DEFAULT_ADDR};
    play_ctrl_if = audio_codec_new_i2c_ctrl(&i2c_cfg);
    play_gpio_if = audio_codec_new_gpio();
    // New output codec interface
    es8388_codec_cfg_t es8388_cfg = {
        .codec_mode = ESP_CODEC_DEV_WORK_MODE_DAC,
        .ctrl_if = play_ctrl_if,
        .gpio_if = play_gpio_if,
    };
    play_codec_if = es8388_codec_new(&es8388_cfg);
    ESP_LOGE(TAG, "es8388 recor_codec_if create.");
    // New output codec device
    esp_codec_dev_cfg_t dev_cfg = {
        .codec_if = play_codec_if,
        .data_if = play_data_if,
        .dev_type = ESP_CODEC_DEV_TYPE_OUT,
    };
    play_dev = esp_codec_dev_new(&dev_cfg);
    ESP_LOGE(TAG, "es8388 play dev create.");

    esp_codec_dev_sample_info_t fs = {
        .sample_rate = sample_rate,
        .channel = channel_format,
        .bits_per_sample = bits_per_sample,
    };
    ESP_LOGE("TEST", "OPEN PLAY DEV.");

    esp_codec_dev_set_out_vol(play_dev, PLAYER_VOLUME);   
    esp_codec_dev_open(play_dev, &fs);   
    ESP_LOGE(TAG, "play dev init.");
    return ret_val;
}

esp_err_t bsp_codec_record_dev_delete(void)
{
    esp_err_t ret_val = ESP_OK;

    bsp_i2s_deinit(true);

    if (record_dev) {
        esp_codec_dev_close(record_dev);
        esp_codec_dev_delete(record_dev);
        record_dev = NULL;
    }

    // Delete codec interface
    if (record_codec_if) {
        audio_codec_delete_codec_if(record_codec_if);
        record_codec_if = NULL;
    }
    
    // Delete codec control interface
    if (record_ctrl_if) {
        audio_codec_delete_ctrl_if(record_ctrl_if);
        record_ctrl_if = NULL;
    }
    
    // Delete codec data interface
    if (record_data_if) {
        audio_codec_delete_data_if(record_data_if);
        record_data_if = NULL;
    }

    return ret_val;
}

esp_err_t bsp_codec_play_dev_delete(void)
{
    esp_err_t ret_val = ESP_OK;

    bsp_i2s_deinit(false);

    if (play_dev) {
        esp_codec_dev_close(play_dev);
        esp_codec_dev_delete(play_dev);
        play_dev = NULL;
    }

    // Delete codec interface
    if (play_codec_if) {
        audio_codec_delete_codec_if(play_codec_if);
        play_codec_if = NULL;
    }
    
    // Delete codec control interface
    if (play_ctrl_if) {
        audio_codec_delete_ctrl_if(play_ctrl_if);
        play_ctrl_if = NULL;
    }
    
    if (play_gpio_if) {
        audio_codec_delete_gpio_if(play_gpio_if);
        play_gpio_if = NULL;
    }
    
    // Delete codec data interface
    if (play_data_if) {
        audio_codec_delete_data_if(play_data_if);
        play_data_if = NULL;
    }

    return ret_val;
}

esp_err_t bsp_codec_record_dev_open(uint32_t sample_rate, int channel_format, int bits_per_sample)
{
    esp_err_t err = ESP_OK;

    if(record_dev){
        esp_codec_dev_sample_info_t fs = {
            .sample_rate = sample_rate,
            .channel = channel_format,
            .bits_per_sample = bits_per_sample,
        };
        ESP_LOGE("TEST", "OPEN record DEV.");
        err = esp_codec_dev_open(record_dev, &fs);
        // esp_codec_dev_set_in_gain(record_dev, RECORD_VOLUME);
        esp_codec_dev_set_in_channel_gain(record_dev, ESP_CODEC_DEV_MAKE_CHANNEL_MASK(0), RECORD_VOLUME);
        esp_codec_dev_set_in_channel_gain(record_dev, ESP_CODEC_DEV_MAKE_CHANNEL_MASK(1), RECORD_VOLUME);       
    }
    return err;
}

esp_err_t bsp_codec_record_dev_close(void)
{
    if(record_dev){
        return esp_codec_dev_close(record_dev);
    }
    return ESP_OK;
}

esp_err_t bsp_codec_play_dev_open(uint32_t sample_rate, int channel_format, int bits_per_sample)
{
    esp_err_t err = ESP_OK;
    if(play_dev){
        esp_codec_dev_sample_info_t fs = {
            .sample_rate = sample_rate,
            .channel = channel_format,
            .bits_per_sample = bits_per_sample,
        };
        ESP_LOGE("TEST", "OPEN PLAY DEV.");
        
        err = esp_codec_dev_open(play_dev, &fs);
        esp_codec_dev_set_out_vol(play_dev, PLAYER_VOLUME);
    }
    return err;
}

esp_err_t bsp_codec_play_dev_close(void)
{
    if(play_dev){
        return esp_codec_dev_close(play_dev);
    }
    return ESP_OK;
}

esp_err_t bsp_audio_set_play_vol(int volume)
{
    if (!play_dev) {
        ESP_LOGE(TAG, "DAC codec init fail");
        return ESP_FAIL;
    }
    esp_codec_dev_set_out_vol(play_dev, volume);
    return ESP_OK;
}

esp_err_t bsp_audio_get_play_vol(int *volume)
{
    if (!play_dev) {
        ESP_LOGE(TAG, "DAC codec init fail");
        return ESP_FAIL;
    }
    esp_codec_dev_get_out_vol(play_dev, volume);
    return ESP_OK;
}

esp_err_t bsp_audio_play(const int16_t* data, int length, TickType_t ticks_to_wait)
{
    esp_err_t ret = ESP_OK;
    if (!play_dev) {
        return ESP_FAIL;
    }
    ret = esp_codec_dev_write(play_dev, (void *)data, length);

    return ret;
}

esp_err_t bsp_get_feed_data(bool is_get_raw_channel, int16_t *buffer, int buffer_len)
{
    esp_err_t ret = ESP_OK;
    int audio_chunksize = buffer_len / (sizeof(int16_t) * ADC_I2S_CHANNEL);

    ret = esp_codec_dev_read(record_dev, (void *)buffer, buffer_len);
    if (!is_get_raw_channel) {
        for (int i = 0; i < audio_chunksize; i++) {
            int16_t ref = buffer[4 * i + 0];
            buffer[2 * i + 0] = buffer[4 * i + 1];
            buffer[2 * i + 1] = ref;
        }
    }

    return ret;
}

int bsp_get_feed_channel(void)
{
    return ADC_I2S_CHANNEL;
}



