#ifndef __PLAYER_
#define __PLAYER_
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/queue.h"
#include "py/obj.h"
#include "wav_codec.h"
#include "ringbuf.h"

#define EV_DEL_STREAM_IN_TASK        0x02
#define EV_PLAY_STOP                 0x04
#define EV_READ_END                  0x08
#define EV_PLAY_READ_TASK_PAUSE      0x10
#define EV_PLAY_WRITE_TASK_PAUSE     0x20
typedef enum{
    AUDIO_WAV_FILE_PLAY,
    AUDIO_WAV_FILE_RECORD,
}audio_type_t;

typedef enum{
    PLAYER_STATE_INIT,
    PLAYER_STATE_PLAYING,
    PLAYER_STATE_PAUSE,
    PLAYER_STATE_STOPPED,
}player_state_t;

typedef struct
{
    wav_codec_t *wav_codec;
    // int frame_size;
    const char *file_uri;
    int player_state;
    int vol;
    QueueHandle_t player_queue;
    EventGroupHandle_t player_event;
    TaskHandle_t simple_file_decoder_task_handle;
    TaskHandle_t stream_i2s_write_task_handle;
    TaskHandle_t simple_http_read_task_handle;
    TaskHandle_t simple_http_decoder_task_handle;
    audio_type_t audio_type;
    ringbuf_handle_t decode_ringbuff;
} player_handle_t;

typedef void* player_handle;
#define FATFS_PATH_LENGTH_MAX 256

void player_create(int ringbuf_size, unsigned int core_num);
void player_play(const char *file_uri);
void player_pause(void);
void player_resume(void);
void player_stop(void);
void player_deinit(void);
int player_get_state(void);
void player_set_vol(int vol);
void player_increase_vol(void);
void player_decrease_vol(void);

extern player_handle_t *player;

#endif
