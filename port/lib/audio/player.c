#include "stdio.h"
#include "stdlib.h"
#include "audio/include/player.h"
#include <string.h>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "audio/include/wav_decoder.h"
#include "freertos/queue.h"
#include <sys/stat.h>
#include "audio/include/esp_board_init.h"
#include <dirent.h>

#define CODEC_CHANNEL 2
#define CODEC_SAMPLE_RATE 16000
#define TAG    "player"

void stream_in_task(void *arg)
{
    player_handle_t *player = arg;
    unsigned char* buffer = malloc(player->frame_size * sizeof(unsigned char));
    void * wav_decoder = NULL;
    ESP_LOGE(TAG, "create stream in running.");

    int channels = CODEC_CHANNEL;
    int sample_rate = CODEC_SAMPLE_RATE;
    wav_decoder = wav_decoder_open(player->audio_file);
    if (wav_decoder == NULL) {
        return;
    } else {
        channels = wav_decoder_get_channel(wav_decoder);
        sample_rate = wav_decoder_get_sample_rate(wav_decoder);
        ESP_LOGE(TAG, "start to play %s, channels:%d, sample rate:%d", player->audio_file,
                channels, sample_rate );
    }

    while (1) {
        switch (player->player_state) {
        case 1: // play
            int size = wav_decoder_run(wav_decoder, buffer, player->frame_size);

            if (size < player->frame_size) { //要结束了
                memset(buffer + size, 0, player->frame_size - size); //清掉buffer无效数据区
                wav_decoder_close(wav_decoder);
                wav_decoder = NULL;
                while(1){
                    vTaskDelay(16 / portTICK_PERIOD_MS);
                }
                // player->player_state = 4;
            }
            xQueueSend(player->player_queue, buffer, portMAX_DELAY);
            vTaskDelay(5 / portTICK_PERIOD_MS);
            // ESP_LOGD(TAG, "stream in.");
            break;
        case 2: // pause or stop
            vTaskDelay(16 / portTICK_PERIOD_MS);
            break;

        case 3: // continue
            player->player_state = 1;
            break;

        case 4: // exit
            vTaskDelay(2000 / portTICK_PERIOD_MS);
            printf("audio file read end.\n");
            free(buffer);
            if (wav_decoder != NULL)
                wav_decoder_close(wav_decoder);
            // return;
            vTaskDelete(NULL);

        default: // exit
            vTaskDelay(16 / portTICK_PERIOD_MS);
        }
    }
}

void stream_out_task(void *arg)
{
    player_handle_t *player = arg;
    int16_t* buffer = malloc(player->frame_size * sizeof(unsigned char));
    int16_t* zero_buffer = calloc(player->frame_size, sizeof(unsigned char));
    printf("stream_out is running.\n");
    int count = 0;
    while (1) {
        count++;
        switch (player->player_state) {
        case 1: // play
            xQueueReceive(player->player_queue, buffer, portMAX_DELAY);
            esp_audio_play(buffer, player->frame_size, portMAX_DELAY);
            // ESP_LOGE(TAG, "stream out.");
            break;

        case 2: // pause or stop
            esp_audio_play(zero_buffer, player->frame_size, portMAX_DELAY);
            break;

        case 3: // continue
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

        default: // exit
            // i2s_zero_dma_buffer(0);
            vTaskDelay(16 / portTICK_PERIOD_MS);

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

void *player_create(const char *file, int ringbuf_size, unsigned int core_num)
{
    if (ringbuf_size < 1024)
        ringbuf_size = 1024;
    else
        ringbuf_size = (ringbuf_size / 1024 + 1) * 1024;

    if (core_num > 1)
        core_num = 1;

    player_handle_t *player = malloc(sizeof(player_handle_t));

    player->frame_size = 1024;
    player->rb_size = ringbuf_size;
    player->player_queue = xQueueCreate(ringbuf_size / player->frame_size, player->frame_size);
    player->player_state = 0;
    player->file_num = 0;
    player->max_file_num = 10;
    // player->file_list = malloc(sizeof(char *)*player->max_file_num);
    // for (int i = 0; i < player->max_file_num; i++)
    //     player->file_list[i] = calloc(FATFS_PATH_LENGTH_MAX, sizeof(char));
    player->audio_file = file;

    xTaskCreatePinnedToCore(&stream_in_task, "stream_in", 2 * 1024, (void*)player, 8, NULL, core_num);
    xTaskCreatePinnedToCore(&stream_out_task, "stream_out", 2 * 1024, (void*)player, 8, NULL, core_num);

    return player;
}

void player_play(void *handle, const char *path)
{
    player_handle_t *player = handle;
    //create file list

    // file_list_scan(player, path);
    // for (int i=0; i<player->file_num; i++)
    //  printf("%s\n", player->file_list[i]);

    //set player state
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


