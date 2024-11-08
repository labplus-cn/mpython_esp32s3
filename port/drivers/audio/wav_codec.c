/* ------------------------------------------------------------------
 * Copyright (C) 2009 Martin Storsjo
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied.
 * See the License for the specific language governing permissions
 * and limitations under the License.
 * -------------------------------------------------------------------
 */
#include "esp_err.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "vfs_lfs2.h"
#include "bsp_audio.h"
#include "audio.h"
#include "player.h"
#include "recorder.h"
#include "es8388.h"
#include "audio_hal.h"

static const char *TAG = "wav_codec";

#define I2S_NUM         (0)
#define I2S_MCK_IO     (GPIO_NUM_39)
#define I2S_BCK_IO     (GPIO_NUM_41)
#define I2S_WS_IO      (GPIO_NUM_42)
#define I2S_DO_IO      (GPIO_NUM_38)
#define I2S_DI_IO      (GPIO_NUM_40)

#define EXAMPLE_RECV_BUF_SIZE   (1024)
#define EXAMPLE_SAMPLE_RATE     (16000)
#define EXAMPLE_MCLK_MULTIPLE  (256)  // (384) // If not using 24-bit data width, 256 should be enough
#define EXAMPLE_MCLK_FREQ_HZ    (EXAMPLE_SAMPLE_RATE * EXAMPLE_MCLK_MULTIPLE)
#define EXAMPLE_VOICE_VOLUME    CONFIG_EXAMPLE_VOICE_VOLUME
#if CONFIG_EXAMPLE_MODE_ECHO
#define EXAMPLE_MIC_GAIN        CONFIG_EXAMPLE_MIC_GAIN
#endif

static i2s_chan_handle_t tx_handle = NULL;
static i2s_chan_handle_t rx_handle = NULL;

static esp_err_t i2s_driver_init(void)
{
    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM, I2S_ROLE_MASTER);
    chan_cfg.auto_clear = true; // Auto clear the legacy data in the DMA buffer
    ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, &tx_handle, &rx_handle));
    i2s_std_config_t std_cfg = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(EXAMPLE_SAMPLE_RATE),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_STEREO),
        .gpio_cfg = {
            .mclk = I2S_MCK_IO,
            .bclk = I2S_BCK_IO,
            .ws = I2S_WS_IO,
            .dout = I2S_DO_IO,
            .din = I2S_DI_IO,
            .invert_flags = {
                .mclk_inv = false,
                .bclk_inv = false,
                .ws_inv = false,
            },
        },
    };
    std_cfg.clk_cfg.mclk_multiple = EXAMPLE_MCLK_MULTIPLE;

    ESP_ERROR_CHECK(i2s_channel_init_std_mode(tx_handle, &std_cfg));
    ESP_ERROR_CHECK(i2s_channel_init_std_mode(rx_handle, &std_cfg));
    ESP_ERROR_CHECK(i2s_channel_enable(tx_handle));
    ESP_ERROR_CHECK(i2s_channel_enable(rx_handle));
    return ESP_OK;
}

wav_codec_t *wav_file_open(const char *path_in, int mode)
{
	size_t len;
	uint8_t data[44] = {0};

	wav_codec_t *wav_codec = (wav_codec_t*) calloc(1, sizeof(wav_codec_t));
	if(!wav_codec){
		ESP_LOGE(TAG, "wav_codec is null.");
		return NULL;
	}

	wav_codec->lfs2_file = vfs_lfs2_file_open(path_in, mode);
	if(!wav_codec->lfs2_file){
		ESP_LOGE(TAG, "fiel open fault.");
		goto failt;
	}

	if(mode == LFS2_O_RDONLY){ //decoder
		len = lfs2_file_read(&wav_codec->lfs2_file->vfs->lfs, &wav_codec->lfs2_file->file, &data, 44); //read wav head
		if(len < 44){
			ESP_LOGE(TAG, "Bad file.");
			goto failt;;
		}

		wav_head_parser(data, &wav_codec->wav_info);
		if(wav_codec->wav_info.fileChunkID != 0X46464952 && wav_codec->wav_info.fileFormat != 0X45564157){
			ESP_LOGE(TAG, "Not wave file");
			goto failt;;
		}
		// ESP_LOGE(TAG, "wav format: %d, channels: %d sample rate: %ld, bits per sample: %d, data lenght: %ld", wav_codec->wav_info.audioFormat, wav_codec->wav_info.channels, 
		// 	wav_codec->wav_info.sampleRate, wav_codec->wav_info.bits_per_sample, wav_codec->wav_info.dataSize);
	}else if((mode & LFS2_O_WRONLY) == LFS2_O_WRONLY){ //encoder
		// write wav header to file.
		/* make wav head */
		wav_header_t *wav_header = calloc(1, sizeof(wav_header_t));
		if (!wav_header)
			mp_raise_ValueError(MP_ERROR_TEXT("Can not alloc enough memory to make wav head."));
		wav_head_init(wav_header, 16000, 16, 2, recorder->total_frames * FRAME_SIZE);
		lfs2_file_write(&wav_codec->lfs2_file->vfs->lfs, &wav_codec->lfs2_file->file, (uint8_t *)wav_header, sizeof(wav_header_t));
		// lfs2_file_sync(&wav_codec->lfs2_file->vfs->lfs, &wav_codec->lfs2_file->file);
		free(wav_header);
	}

	return wav_codec;
failt:
	free(wav_codec);
	return NULL;
}

void wav_file_close(wav_codec_t *wav_codec)
{
	vfs_lfs2_file_close(wav_codec->lfs2_file);
	if(wav_codec){
		free(wav_codec);
	}
}
		
void wav_file_read_task(void *arg)
{
	// ESP_LOGE(TAG, "wav decodec task begin, RAM left: %ld", esp_get_free_heap_size());
    player_handle_t *player = arg;
	size_t len = 0;
	EventBits_t uxBits;
	size_t ringBufFreeBytes = 0;

    unsigned char* buffer = calloc(FRAME_SIZE, sizeof(unsigned char));
	if(!buffer){
		return;
	}

	wav_codec_t *wav_codec = wav_file_open(player->file_uri, LFS2_O_RDONLY);
	if(!wav_codec){
		ESP_LOGE(TAG, "Wave file open failt.");
		return;
	}
	player->wav_codec = wav_codec;

	len = lfs2_file_read(&wav_codec->lfs2_file->vfs->lfs, &wav_codec->lfs2_file->file, buffer, FRAME_SIZE);
	fill_ringbuf(player->stream_out_ringbuff, buffer, len);

	xTaskCreatePinnedToCore(&stream_i2s_write_task, "stream_out", 5 * 1024, (void*)player, 8, &player->stream_i2s_write_task, CORE_NUM1);

    while (1) {
		ringBufFreeBytes = xRingbufferGetCurFreeSize(player->stream_out_ringbuff);
		if( ringBufFreeBytes >= FRAME_SIZE){
			len = lfs2_file_read(&wav_codec->lfs2_file->vfs->lfs, &wav_codec->lfs2_file->file, buffer, FRAME_SIZE);
			if(len > 0){
				xRingbufferSend(player->stream_out_ringbuff, (const void *)buffer, len, 100/portTICK_PERIOD_MS);
			}
			
			if(len < FRAME_SIZE){  //文件读完了
				xEventGroupSetBits(
					player->player_event,    // The event group being updated.
					EV_DEL_STREAM_OUT_TASK );// The bits being set.
				break;
			}
		}
		uxBits = xEventGroupWaitBits(    
					player->player_event,    // The event group being tested.
					EV_DEL_FILE_READ_TASK,  // The bits within the event group to wait for.
					pdTRUE,         // BIT_0 and BIT_4 should be cleared before returning.
					pdFALSE,         // not wait for both bits, either bit will do.
					10 / portTICK_PERIOD_MS ); // Wait a maximum of 100ms for either bit to be set.
		if(uxBits & EV_DEL_FILE_READ_TASK){ //Has get stop event.
			goto exit;
		}
    }
exit:
	wav_file_close(wav_codec);
	free(buffer);
	// ESP_LOGE(TAG, "wav decodec task end, RAM left: %ld", esp_get_free_heap_size());
	// player->wav_file_read_task = NULL;
	vTaskDelete(NULL);	
}

void stream_i2s_write_task(void *arg)
{
    // ESP_LOGE(TAG, "stream out task begin, RAM left: %ld", esp_get_free_heap_size());
    player_handle_t *player = arg;
    uint16_t len;
    EventBits_t uxBits;
	size_t bytes_write = 0;

    uint8_t *stream_buff = calloc(FRAME_SIZE, sizeof(uint8_t));
    if(!stream_buff){
        return;
    }

    // bsp_codec_dev_open(player->wav_codec->wav_info.sampleRate, player->wav_codec->wav_info.channels, player->wav_codec->wav_info.bits_per_sample);
	//  bsp_codec_dev_open(16000, 2, 16);
es8388_set_voice_mute(false);
    while (1) {
        len = read_ringbuf(player->stream_out_ringbuff, FRAME_SIZE, stream_buff);
        // ESP_LOGE(TAG, "ring buffer read len: %d", len);
        if(len > 0){
            if(player->audio_type == AUDIO_WAV_FILE_PLAY){
                // bsp_audio_play((int16_t *)stream_buff, len, portMAX_DELAY);
				i2s_channel_write(tx_handle, stream_buff, len, &bytes_write, 1000);
            }else if(player->audio_type == AUDIO_WAV_FILE_RECORD){
                //write data to file
            }
        }else{
            memset(stream_buff, 0, FRAME_SIZE);
            // bsp_audio_play((int16_t *)stream_buff, FRAME_SIZE / 2, portMAX_DELAY);
			i2s_channel_write(tx_handle, stream_buff, len, &bytes_write, 1000);
            vTaskDelay(200 / portTICK_PERIOD_MS);
            goto exit;
        }
        uxBits = xEventGroupWaitBits(
                    player->player_event,    // The event group being tested.
                    EV_DEL_STREAM_OUT_TASK,  // The bits within the event group to wait for.
                    pdTRUE,         // BIT_0 and BIT_4 should be cleared before returning.
                    pdFALSE,         // not wait for both bits, either bit will do.
                    5 / portTICK_PERIOD_MS ); // Wait a maximum of 100ms for either bit to be set.
		if(uxBits & EV_DEL_STREAM_OUT_TASK){
            vTaskDelay(200 / portTICK_PERIOD_MS);
			goto exit;
        }
    }

exit:
    bsp_codec_dev_close();
    if(stream_buff){
        free(stream_buff);
    }
    // ESP_LOGE(TAG, "stream out task end, RAM left: %ld", esp_get_free_heap_size());
    player->stream_i2s_write_task = NULL;
    vTaskDelete(NULL);
}

void wav_file_write_task(void *arg)
{
	ESP_LOGE(TAG, "wav file write task begin, RAM left: %ld", esp_get_free_heap_size());
    recorder_handle_t *recorder = arg;
	EventBits_t uxBits;
	size_t len = 0;

    unsigned char* buffer = calloc(FRAME_SIZE, sizeof(unsigned char));
	if(!buffer){
		return;
	}

	wav_codec_t *wav_codec = wav_file_open(recorder->file_uri, LFS2_O_WRONLY | LFS2_O_CREAT);
	if(!wav_codec){
			ESP_LOGE(TAG, "Wave file open failt.");
		return;
	}
	recorder->wav_codec = wav_codec;

    while (1) {
		len = read_ringbuf(recorder->stream_in_ringbuff, FRAME_SIZE, buffer);
		if(len > 0){
			lfs2_file_write(&wav_codec->lfs2_file->vfs->lfs, &wav_codec->lfs2_file->file, buffer, len);
			// lfs2_file_sync(&wav_codec->lfs2_file->vfs->lfs, &wav_codec->lfs2_file->file);
		}
		uxBits = xEventGroupWaitBits(    
					recorder->recorder_event,    // The event group being tested.
					EV_DEL_FILE_WRITE_TASK,  // The bits within the event group to wait for.
					pdTRUE,         // BIT_0 and BIT_4 should be cleared before returning.
					pdFALSE,         // not wait for both bits, either bit will do.
					2 / portTICK_PERIOD_MS ); // Wait a maximum of 100ms for either bit to be set.
		if(uxBits & EV_DEL_FILE_WRITE_TASK){ //Has get stop event.
			goto exit;
		}
    }

exit:
	wav_file_close(wav_codec);
	free(buffer);
	ESP_LOGE(TAG, "wav file write task end, RAM left: %ld", esp_get_free_heap_size());
	vTaskDelete(NULL);	
}

void stream_i2s_read_task(void *arg)
{
    ESP_LOGE(TAG, "stream in task begin, RAM left: %ld", esp_get_free_heap_size());
    recorder_handle_t *recorder = arg;
	uint16_t frame_cnt = 0;

    // uint8_t *stream_buff = calloc(FRAME_SIZE, sizeof(uint8_t));
    // if(!stream_buff){
    //     return;
    // }

    // bsp_codec_dev_open(16000, 2, 16);
	// xTaskCreatePinnedToCore(&wav_file_write_task, "wav_file_write_task", 4 * 1024, (void*)recorder, 8, NULL, CORE_NUM1);
	wav_codec_t *wav_codec = wav_file_open(recorder->file_uri, LFS2_O_WRONLY | LFS2_O_CREAT);
	if(!wav_codec){
			ESP_LOGE(TAG, "Wave file open failt.");
		return;
	}
	recorder->wav_codec = wav_codec;

    int *mic_data = malloc(EXAMPLE_RECV_BUF_SIZE);
    if (!mic_data) {
        ESP_LOGE(TAG, "[echo] No memory for read data buffer");
        abort();
    }
    esp_err_t ret = ESP_OK;
    size_t bytes_read = 0;
    size_t bytes_write = 0;

	i2s_driver_init();
	audio_hal_codec_config_t audio_codec_cfg = AUDIO_CODEC_DEFAULT_CONFIG();
	es8388_init(&audio_codec_cfg);
    if (es8388_config_i2s(audio_codec_cfg.codec_mode, &(audio_codec_cfg.i2s_iface)) != ESP_OK) {
        ESP_LOGE(TAG, "es8311 codec config i2s failed");
        abort();
    } else {
        es8388_set_voice_volume(0);
        es8388_ctrl_state(AUDIO_HAL_CODEC_MODE_BOTH, AUDIO_HAL_CTRL_START);
        ESP_LOGI(TAG, "es8311 config i2s init success");
    }
	es8388_set_voice_mute(true);
	// es8388_read_all();

    while (1) {
        // if(xRingbufferGetCurFreeSize(recorder->stream_in_ringbuff) >= FRAME_SIZE){
			// bsp_get_feed_data(true, stream_buff, FRAME_SIZE);
			// bsp_audio_play(stream_buff, FRAME_SIZE, portMAX_DELAY);
			// // fill_ringbuf(recorder->stream_in_ringbuff, stream_buff, FRAME_SIZE);	
			// frame_cnt++;
			// ESP_LOGE(TAG, "frame cnt: %d", frame_cnt);

			memset(mic_data, 0, EXAMPLE_RECV_BUF_SIZE);
			ret = i2s_channel_read(rx_handle, mic_data, EXAMPLE_RECV_BUF_SIZE, &bytes_read, 1000);
			// ret = i2s_channel_write(tx_handle, mic_data, EXAMPLE_RECV_BUF_SIZE, &bytes_write, 1000);
			lfs2_file_write(&wav_codec->lfs2_file->vfs->lfs, &wav_codec->lfs2_file->file, mic_data, EXAMPLE_RECV_BUF_SIZE);
			frame_cnt++;
			// ESP_LOGE(TAG, "freme cnt: %d", frame_cnt);
			if(frame_cnt > recorder->total_frames){
				xEventGroupSetBits(
					recorder->recorder_event,    // The event group being updated.
					EV_DEL_FILE_WRITE_TASK );// The bits being set.
				break;
			}
			// vTaskDelay(1 / portTICK_PERIOD_MS);
			// ESP_LOGE(TAG, "ring buffer read len: %d", len);		
			// }else{
            // vTaskDelay(2 / portTICK_PERIOD_MS);
			// }
    }

    // bsp_codec_dev_close();
    // if(stream_buff){
    //     free(stream_buff);
    // }
	wav_file_close(wav_codec);
	free(mic_data);
    ESP_LOGE(TAG, "stream in task end, RAM left: %ld", esp_get_free_heap_size());
    vTaskDelete(NULL);
}