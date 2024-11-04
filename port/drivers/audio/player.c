#include "stdio.h"
#include "stdlib.h"
#include "player.h"
#include <string.h>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "wav_decoder.h"
#include "freertos/queue.h"
#include <sys/stat.h>
#include "audio_board.h"
#include <dirent.h>
#include "msg.h"

#define TAG    "player"

player_handle_t *player = NULL;

int file_list_scan(void *handle, const char *path)
{
    player_handle_t *player = handle;
    struct dirent *ret;
    DIR *dir;
    dir = opendir(path);
    int path_len = strlen(path);
    if (dir != NULL) {
        while ((ret = readdir(dir)) != NULL && player->file_num < player->max_file_num) { // NULL if reach the end of directory

            if (ret->d_type != 1) // continue if d_type is not file
                continue;

            int len = strlen(ret->d_name);
            if (len > FATFS_PATH_LENGTH_MAX - path_len - 1) // continue if name is too long
                continue;

            char *suffix = ret->d_name + len - 4;

            if (strcmp(suffix, ".wav") == 0 || strcmp(suffix, ".WAV") == 0 ) {

                memset(player->file_list[player->file_num], 0, FATFS_PATH_LENGTH_MAX);
                memcpy(player->file_list[player->file_num], path, path_len);
                memcpy(player->file_list[player->file_num] + path_len, ret->d_name, len + 1);
                printf("%d -> %s\n", player->file_num, player->file_list[player->file_num]);
                player->file_num++;
            }
        }
        closedir(dir);
    } else {
        printf("opendir NULL \r\n");
    }
    return player->file_num;
}

void play_tast(void *arg)
{
    while(1){

    }
}

void player_play(const char *uri)
{
    if(!player){
        player = calloc(1, sizeof(player_handle_t));
        player->player_event = xEventGroupCreate(); 
        player->player_queue = xQueueCreate(10, sizeof(msg_t));      
    }else{
        if(player->player_state == 1 || player->player_state == 2){

        }
    }

    player->uri = uri;
    player->player_state = 1;
    if(strstr(uri, "http")){   // web play, include https

    }else{
        if(strstr(uri, ".mp3"))){
            player_instance->content_type = AUDIO_MPEG;
        }else if(strstr(uri, ".pcm")){
            player_instance->content_type = AUDIO_PCM;
        }else if(strstr(uri, ".wav")){
            audio_handle->audio_type = AUDIO_WAV_FILE_PLAY;
            xTaskCreatePinnedToCore(&wav_file_read_task, "wav_file_read_task", 4 * 1024, (void*)player, 8, player->wav_file_read_task, CORE_NUM1);
            // ESP_LOGE(TAG, "wav file");
        }else if(strstr(uri, ".m4a")){
            player_instance->content_type = AUDIO_MP4;
        }else if(strstr(uri, ".aac")){
            player_instance->content_type = AUDIO_AAC;
        }
        else{
            mp_warning(NULL, "Not suport format.");
            return;
        }        
    }
}

void player_pause(void)
{
    player->player_state = 2;
}

void player_resume(void)
{
    player->player_state = 3;
}

void player_stop(void)
{
    xEventGroupSetBits(
            xEventGroup,    // The event group being updated.
            EV_DEL_FILE_READ_TASK | EV_DEL_STREAM_OUT_TASK );// The bits being set.
}

int player_get_state(void)
{
    return player->player_state;
}

void player_set_vol(int vol)
{
    esp_audio_set_play_vol(vol);   
}

void player_increase_vol(void)
{
    int vol = 0;
    esp_audio_get_play_vol(&vol);
    if (vol < 50) {
        vol += 3;
    } else if (vol < 70) {
        vol += 2;
    } else if (vol < 95) {
        vol += 1;
    } else {
        vol = 95;
    }
    esp_audio_set_play_vol(vol);
}

void player_decrease_vol(void)
{
    int vol = 65;
    esp_audio_get_play_vol(&vol);
    if (vol >= 95) {
        vol -= 1;
    } else if (vol >= 70) {
        vol -= 2;
    } else if (vol > 50) {
        vol -= 3;
    } else {
        vol = 50;
    }

    esp_audio_set_play_vol(vol);
}


