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
#include "audio.h"
#include <dirent.h>

#define CODEC_CHANNEL 2
#define CODEC_SAMPLE_RATE 16000
#define TAG    "player"

player_handle_t *player = NULL;

void stream_in_task(void *arg)
{
    player_handle_t *player = arg;
    unsigned char* buffer = calloc(player->frame_size, sizeof(unsigned char));
    wav_decoder_t* wav_decoder = NULL;
    static bool playdev_is_open = false;

    // int channels = CODEC_CHANNEL;
    // int sample_rate = CODEC_SAMPLE_RATE;
    wav_decoder = wav_decoder_init();
    if (wav_decoder == NULL) {
        return;
    } else {
        player->wav_codec = wav_decoder;
    }

    while (1) {
        switch (player->player_state) {
        case 1: // play
            if(!playdev_is_open){
                // esp_board_play_dev_create(16000, 2, 32);
                wav_file_open(wav_decoder, player->file_uri);
                esp_board_codec_dev_open(wav_decoder->sample_rate, wav_decoder->channels, wav_decoder->bits_per_sample);
                playdev_is_open = true;
                // ESP_LOGE(TAG, "begin play.");
            }
            int size = lfs2_file_read(&wav_decoder->lfs2_file->vfs->lfs, &wav_decoder->lfs2_file->file, buffer, player->frame_size);
            
            if (size < player->frame_size) { //要结束了
                memset(buffer + size, 0, player->frame_size - size); //清掉buffer无效数据区,避免杂音
                // wav_decoder_deinit(wav_decoder);
                // wav_decoder = NULL; //?释放
                // ESP_LOGE(TAG, "IDLE");
                while(1){
                    vTaskDelay(16 / portTICK_PERIOD_MS);
                }
                // player->player_state = 4;
            }
            xQueueSend(player->player_queue, buffer, portMAX_DELAY);
            vTaskDelay(1 / portTICK_PERIOD_MS);
            break;
        case 2: // pause or stop
            vTaskDelay(16 / portTICK_PERIOD_MS);
            break;

        case 3: // continue
            player->player_state = 1;
            break;

        case 4: // exit
            vTaskDelay(2000 / portTICK_PERIOD_MS);
            esp_board_codec_dev_close();
            free(buffer);
            if (wav_decoder != NULL){
                wav_decoder_deinit(wav_decoder);
                wav_decoder = NULL; 
            }
            free(player);
            player = NULL;
            // return;
            vTaskDelete(NULL);
            break;
        case 5: //stop
            vTaskDelay(16 / portTICK_PERIOD_MS);
            break;

        default: // exit
            vTaskDelay(100 / portTICK_PERIOD_MS);
        }
    }
}

void stream_out_task(void *arg)
{
    player_handle_t *player = arg;
    int16_t* buffer = calloc(player->frame_size, sizeof(unsigned char));
    int16_t* zero_buffer = calloc(player->frame_size, sizeof(unsigned char));
    ESP_LOGE(TAG, "stream_out is running.\n");
    int count = 0;
    while (1) {
        count++;
        switch (player->player_state) {
        case 1: // play
            xQueueReceive(player->player_queue, buffer, portMAX_DELAY);
            esp_audio_play(buffer, player->frame_size, portMAX_DELAY);
            // ESP_LOGE("WAV", "file_pos: %ld, data_len: %ld\n", fs_tell(player->wav_codec->file), player->wav_codec->data_length);
            // vTaskDelay(16 / portTICK_PERIOD_MS);
            break;

        case 2: // pause
            esp_audio_play(zero_buffer, player->frame_size, portMAX_DELAY);
            break;

        case 3: // resume
            player->player_state = 1;
            // vTaskDelay(16 / portTICK_PERIOD_MS);
            break;

        case 4: // exit
            printf("play end.\n");
            vTaskDelay(2000 / portTICK_PERIOD_MS);
            free(buffer);
            while(1){
                 vTaskDelay(200 / portTICK_PERIOD_MS);
            }
        case 5: //stop
            vTaskDelay(16 / portTICK_PERIOD_MS);
            break;

        default: // exit
            // i2s_zero_dma_buffer(0);
            vTaskDelay(100 / portTICK_PERIOD_MS);

        }
    }
}

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

void player_create(int ringbuf_size, unsigned int core_num)
{
    if (ringbuf_size < 1024)
        ringbuf_size = 1024;
    else
        ringbuf_size = (ringbuf_size / 1024 + 1) * 1024;

    if (core_num > 1)
        core_num = 1;

    player = calloc(1, sizeof(player_handle_t));

    player->frame_size = 1024;
    player->rb_size = ringbuf_size;
    player->player_queue = xQueueCreate(ringbuf_size / player->frame_size, player->frame_size);
    player->player_state = 0;
    player->file_num = 0;
    player->max_file_num = 10;

    xTaskCreatePinnedToCore(&stream_in_task, "stream_in", 4 * 1024, (void*)player, 8, NULL, core_num);
    xTaskCreatePinnedToCore(&stream_out_task, "stream_out", 2 * 1024, (void*)player, 8, NULL, core_num);
}

void player_play(void *handle, const char *file_uri)
{
    player_handle_t *player = handle;
    if(player->player_state == 1 || player->player_state == 2){
        if(player->file_uri){
            wav_file_close(player->wav_codec);
            // esp_board_play_dev_close();
        }
    }

    player->file_uri = file_uri;
    player->player_state = 1;
}

void player_pause(void *handle)
{
    player_handle_t *player = handle;
    player->player_state = 2;
    // printf("pause\n");
}

void player_continue(void *handle)
{
    player_handle_t *player = handle;
    player->player_state = 3;
    // printf("play\n");
}

void player_exit(void *handle)
{
    player_handle_t *player = handle;
    player->player_state = 4;
}

int player_get_state(void *handle)
{
    player_handle_t *player = handle;
    return player->player_state;
}

void player_set_vol(void *handle, int vol)
{
    esp_audio_set_play_vol(vol);
    
}

void player_increase_vol(void *handle)
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

void player_decrease_vol(void *handle)
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


