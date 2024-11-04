#include "stdio.h"
#include "stdlib.h"
#include <string.h>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "freertos/event_groups.h"
#include "freertos/ringbuf.h"
#include "audio_board.h"
#include "audio.h"
#include "player.h"

#define TAG    "stream_out"

void stream_out_task(void *arg)
{
    ESP_LOGE(TAG, "start stream out.");
    player_handle_t *player = arg;
    uint16_t len;
    EventBits_t uxBits;

    esp_board_codec_dev_open(player->wav_info.sample_rate, player->wav_info.channels, player->wav_info.bits_per_sample);

    while (1) {
        len = read_ringbuf(audio_handle->stream_out_ringbuff, BUFFER_SIZE, audio_handle->stream_out_buff);
        if(len > 0){
            if(audio_handle->audio_type == AUDIO_WAV_FILE_PLAY){
                esp_audio_play((int16_t *)audio_handle->stream_out_buff, BUFFER_SIZE, portMAX_DELAY);
            }else if(audio_handle->audio_type == AUDIO_WAV_FILE_RECORD){
                //write data to file
            }
            vTaskDelay(1 / portTICK_PERIOD_MS);
        }else{
            vTaskDelay(16 / portTICK_PERIOD_MS);
        }

        uxBits = xEventGroupWaitBits(
                    player->player_event,    // The event group being tested.
                    EV_DEL_STREAM_OUT_TASK,  // The bits within the event group to wait for.
                    pdTRUE,         // BIT_0 and BIT_4 should be cleared before returning.
                    pdFALSE,         // not wait for both bits, either bit will do.
                    5 / portTICK_PERIOD_MS ); // Wait a maximum of 100ms for either bit to be set.
		if(uxBits & EV_DEL_FILE_READ_TASK){
			goto exit;
        }
    }

exit:
    esp_board_codec_dev_close();
    vTaskDelete(NULL);
}



