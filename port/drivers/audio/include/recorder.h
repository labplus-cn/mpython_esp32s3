#ifndef __RECORDER_
#define __RECORDER_
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/ringbuf.h"
#include "py/obj.h"
#include "wav_codec.h"

#define RECORD_FRAME_SIZE   (1000)
#define RECORD_RINGBUF_SIZE (4000)
typedef struct
{
    wav_codec_t *wav_codec;
    int frame_size;
    const char *file_uri;
    uint8_t time;
    uint16_t total_frames;
    wav_fmt_t wav_fmt;
    EventGroupHandle_t recorder_event;
    RingbufHandle_t stream_in_ringbuff;
} recorder_handle_t;

// typedef void* recorder_handle;
void recorder_record(const char *filename, int time);

extern recorder_handle_t *recorder;

#endif
