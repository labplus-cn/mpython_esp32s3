#ifndef __RECORDER_
#define __RECORDER_
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/ringbuf.h"
#include "py/obj.h"
#include "wav_codec.h"

typedef struct
{
    wav_codec_t *wav_codec;
    int frame_size;
    const char *file_uri;
    uint8_t time;
    uint8_t total_frames;
    EventGroupHandle_t recorder_event;
    RingbufHandle_t stream_in_ringbuff;
} recorder_handle_t;

// typedef void* recorder_handle;
void recorder_record(const char *filename, int time);

void fill_ringbuf(RingbufHandle_t ring_buff, uint8_t *buffer, size_t len);
uint16_t read_ringbuf(RingbufHandle_t ring_buff, size_t supply_bytes, uint8_t *buffer);
void clear_ringbuf(RingbufHandle_t ring_buff);

extern recorder_handle_t *recorder;

#endif
