#ifndef __PLAYER_
#define __PLAYER_
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
typedef struct
{
    QueueHandle_t player_queue;
    int rb_size;
    int frame_size;
    char **file_list;
    char *audio_file;
    int file_num;
    int max_file_num;
    int player_state;
    int vol;
    TaskHandle_t stream_in;
    TaskHandle_t stream_out;
} player_handle_t;

typedef void* player_handle;
#define FATFS_PATH_LENGTH_MAX 256

void *player_create(const char *file, int ringbuf_size, unsigned int core_num);
void player_play(void *handle, const char *path);
void player_pause(void *handle);
void player_continue(void *handle);
void player_exit(void *handle);
int player_get_state(void *handle);
void player_increase_vol(void *handle);
void player_decrease_vol(void *handle);

#endif
