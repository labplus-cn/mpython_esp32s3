
#pragma once

#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/ringbuf.h"

#ifdef __cplusplus
extern "C" {
#endif

#define BUFFER_SIZE 1024
#define RINGBUF_SIZE   (3880)
#define RINGBUF_WATER_SIZE (1940)
#define FILE_READ_LEN  (64)

typedef enum{
    AUDIO_WAV_FILE_PLAY,
    AUDIO_WAV_FILE_RECORD,
}audio_type_t;
typedef struct
{
    audio_type_t audio_type;
    bool audio_is_init;
    RingbufHandle_t stream_out_ringbuff;
    uint8_t *stream_out_buff;
    uint8_t *stream_out_zero_buff; 
} audio_handle_t;

// typedef void* audio_handle_t;

void audio_init(void);
void audio_deinit(void);
void fill_ringbuf(RingbufHandle_t ring_buff, uint8_t *buffer, uint16_t len);
uint16_t read_ringbuf(RingbufHandle_t ring_buff, uint16_t supply_bytes, uint8_t *buffer);

extern audio_handle_t *audio_handle;

#ifdef __cplusplus
}
#endif
