#ifndef __RECORDER_
#define __RECORDER_
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "ringbuf.h"
#include "py/obj.h"
#include "wav_codec.h"

#define READ_RINGBUF_BLOCK_SIZE    (1000)
#define READ_RINGBUF_BLOCK_NUM      (4)

#define EV_RECORD_END       1

typedef struct
{
    wav_codec_t *wav_codec;
    int frame_size;
    const char *file_uri;
    uint8_t time;
    uint16_t total_frames;
    wav_fmt_t wav_fmt;
    EventGroupHandle_t recorder_event;
    ringbuf_handle_t record_ringbuff;
} recorder_handle_t;

// typedef void* recorder_handle;
void recorder_record(const char *filename, wav_fmt_t fmt, int time);

extern recorder_handle_t *recorder;

#endif
