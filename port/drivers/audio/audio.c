#include "stdio.h"
#include "stdlib.h"
#include <string.h>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "audio.h"
#include "bsp_audio.h"

audio_handle_t *audio_handle = NULL;

void audio_init(void)
{
    if(!audio_handle){
        bsp_codec_dev_create();
    }
}

void audio_deinit(void)
{
    if(audio_handle){
        bsp_codec_dev_delete();
    }
}
