#ifndef __RECORDER_
#define __RECORDER_
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
typedef struct
{
    QueueHandle_t recorder_queue;
    TimerHandle_t rec_Timer;
    int rb_size;
    int frame_size;
    char *audio_file;
    int recorder_state;
    int vol;
    int sample_rate;
    int bits_per_sample;
    int channels;
    TaskHandle_t stream_in;
    TaskHandle_t stream_out;
} recorder_handle_t;

typedef void* recorder_handle;
#define FATFS_PATH_LENGTH_MAX 256

void *recorder_create(const char *file, int ringbuf_size, unsigned int core_num);
void recorder_recorde(void *handle, const char *path);

#endif //__RECORDER_
