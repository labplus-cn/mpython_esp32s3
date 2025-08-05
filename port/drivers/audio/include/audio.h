
#pragma once

#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

#ifdef __cplusplus
extern "C" {
#endif

#define FILE_READ_LEN  (64)

typedef struct
{
    bool audio_is_init;
} audio_handle_t;

// typedef void* audio_handle_t;

void audio_init(void);
void audio_deinit(void);

extern audio_handle_t *audio_handle;

#ifdef __cplusplus
}
#endif
