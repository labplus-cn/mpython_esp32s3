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

    uint8_t *stream_out_buff = malloc(FRAME_SIZE * sizeof(uint8_t));
    if(!stream_out_buff){
        return;
    }

    esp_board_codec_dev_open(player->wav_info.sample_rate, player->wav_info.channels, player->wav_info.bits_per_sample);
    while (1) {
        len = read_ringbuf(player->stream_out_ringbuff, FRAME_SIZE, stream_out_buff);
        if(len > 0){
            if(player->audio_type == AUDIO_WAV_FILE_PLAY){
                // ESP_LOGE(TAG, "stream out data. len: %d", len);
                esp_audio_play((int16_t *)stream_out_buff, len, portMAX_DELAY);
            }else if(player->audio_type == AUDIO_WAV_FILE_RECORD){
                //write data to file
            }
        }else{
            memset(stream_out_buff, 0, FRAME_SIZE);
            esp_audio_play((int16_t *)stream_out_buff, FRAME_SIZE, portMAX_DELAY);
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
    esp_board_codec_dev_close();
    if(stream_out_buff){
        free(stream_out_buff);
    }
    ESP_LOGE(TAG, "stream out task end, RAM left: %ld", esp_get_free_heap_size());
    player->stream_out_task = NULL;
    vTaskDelete(NULL);
}



