#include "stdio.h"
#include "stdlib.h"
#include "player.h"
#include <string.h>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "wav_codec.h"
#include <sys/stat.h>
#include "bsp_audio.h"
#include "simple_file_decoder.h"
#include "simple_http_decoder.h"

#define TAG    "player"
#define READ_RINGBUF_BLOCK_SIZE    (512)
#define READ_RINGBUF_BLOCK_NUM      (8)

player_handle_t *player = NULL;

void player_play(const char *uri)
{
    if(!player){
        player = calloc(1, sizeof(player_handle_t));
        if(player){
            player->player_event = xEventGroupCreate();  
            player->decode_ringbuff = rb_create(READ_RINGBUF_BLOCK_SIZE, READ_RINGBUF_BLOCK_NUM); 
            if(!player->player_event || !player->decode_ringbuff){
                if(player->player_event){ vEventGroupDelete(player->player_event); }
                if(player->decode_ringbuff){ rb_destroy(player->decode_ringbuff); }
                free(player);
                return;
            } 
        }else{
            return;
        }
   
    }else{
        player_stop();
    }

    rb_reset(player->decode_ringbuff);
    player->file_uri = uri;
    player->player_state = PLAYER_STATE_PLAYING;

    if(strstr(uri, "http")){   // web play, include https
        xTaskCreatePinnedToCore(&simple_http_read_task, "simple_http_read_task", 4 * 1024, (void*)player, 8, &player->simple_http_read_task_handle, CORE_NUM1);
    }else{
    //    if(strstr(uri, ".wav")){
    //         player->audio_type = AUDIO_WAV_FILE_PLAY;
    //         xTaskCreatePinnedToCore(&wav_file_read_task, "wav_file_read_task", 4 * 1024, (void*)player, 8, &player->wav_file_read_task, CORE_NUM1);
    //     }else{
            xTaskCreatePinnedToCore(&simple_file_decoder_task, "simple_file_decoder_task", 4 * 1024, (void*)player, 8, &player->simple_file_decoder_task_handle, CORE_NUM1);
        // }       
    }
}

void player_pause(void)
{
    if(player && player->player_state == PLAYER_STATE_PLAYING){
        // xEventGroupSetBits(player->player_event, EV_PLAY_READ_TASK_PAUSE | EV_PLAY_WRITE_TASK_PAUSE);
        if(player->simple_http_read_task_handle && player->simple_http_decoder_task_handle){
            vTaskSuspend(player->simple_http_read_task_handle);
            vTaskSuspend(player->simple_http_decoder_task_handle);
        }
        player->player_state = PLAYER_STATE_PAUSE;
    }
}

void player_resume(void)
{
    if(player && player->player_state == PLAYER_STATE_PAUSE){
        ESP_LOGE(TAG, "resume.");
        vTaskResume(player->simple_http_read_task_handle);
        vTaskResume(player->simple_http_decoder_task_handle);
        player->player_state = PLAYER_STATE_PLAYING;
    }
}

void player_stop(void)
{
    if(player && player->player_state != PLAYER_STATE_INIT &&
       player->player_state != PLAYER_STATE_STOPPED){
        if(player->player_state == PLAYER_STATE_PAUSE){
            if(player->simple_http_read_task_handle && player->simple_http_decoder_task_handle){
                vTaskResume(player->simple_http_read_task_handle);
                vTaskResume(player->simple_http_decoder_task_handle);
            }
        }

        xEventGroupSetBits(player->player_event, EV_PLAY_STOP);
        vTaskDelay(20 / portTICK_PERIOD_MS);
    }
}

void player_deinit(void)
{
    if(player){
        if(player->player_state == PLAYER_STATE_PLAYING){

        }else if(player->player_state == PLAYER_STATE_PAUSE){
            
        }

        if(player->decode_ringbuff){ rb_destroy(player->decode_ringbuff);}
        if(player->player_queue){vQueueDelete(player->player_queue);}
        free(player);
    }
}

int player_get_state(void)
{
    return player->player_state;
}

void player_set_vol(int vol)
{
    bsp_audio_set_play_vol(vol);   
}

void player_increase_vol(void)
{
    int vol = 0;
    bsp_audio_get_play_vol(&vol);
    if (vol < 50) {
        vol += 3;
    } else if (vol < 70) {
        vol += 2;
    } else if (vol < 95) {
        vol += 1;
    } else {
        vol = 95;
    }
    bsp_audio_set_play_vol(vol);
}

void player_decrease_vol(void)
{
    int vol = 65;
    bsp_audio_get_play_vol(&vol);
    if (vol >= 95) {
        vol -= 1;
    } else if (vol >= 70) {
        vol -= 2;
    } else if (vol > 50) {
        vol -= 3;
    } else {
        vol = 50;
    }

    bsp_audio_set_play_vol(vol);
}
