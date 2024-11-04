#ifndef __PLAYER_
#define __PLAYER_
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/queue.h"
#include "py/obj.h"
#include "wav_decoder.h"

#define EV_DEL_FILE_READ_TASK        1
#define EV_DEL_STREAM_OUT_TASK       2

#define CORE_NUM0 0
#define CORE_NUM1 1

typedef struct
{
    struct wav_decoder *wav_codec;
    int frame_size;
    char **file_list;
    const char *file_uri;
    int file_num;
    int max_file_num;
    int player_state;
    int vol;
    QueueHandle_t player_queue;
    EventGroupHandle_t player_event;
    TaskHandle_t wav_file_read_task;
    TaskHandle_t stream_out_task;
    wav_info_t wav_info;
} player_handle_t;

typedef void* player_handle;
#define FATFS_PATH_LENGTH_MAX 256

void player_create(int ringbuf_size, unsigned int core_num);
void player_play(const char *file_uri);
void player_pause(void);
void player_continue(void);
void player_exit(void);
int player_get_state(void);
void player_set_vol(int vol);
void player_increase_vol(void);
void player_decrease_vol(void);

extern player_handle_t *player;

#endif
