#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "freertos/semphr.h"
#include "esp_tts.h"
#include "esp_tts_voice_xiaole.h"
#include "esp_tts_voice_template.h"
#include "esp_tts_player.h"
#include "ringbuf.h"

#include "esp_partition.h"
#include "esp_idf_version.h"
#include "bsp_audio.h"
#include "sc.h"

static esp_tts_handle_t *g_tts_handle = NULL;
SemaphoreHandle_t tts_semaphore;

volatile int tts_flag = 0;
volatile int tts_init_flag = 0;

extern BaseType_t xTaskCreatePinnedToCore( TaskFunction_t pxTaskCode,
                                             const char * const pcName,
                                             const uint32_t usStackDepth,
                                             void * const pvParameters,
                                             UBaseType_t uxPriority,
                                             TaskHandle_t * const pxCreatedTask,
                                             const BaseType_t xCoreID );

void model_init(void)
{
    if(tts_init_flag){
        return;
    }
    const esp_partition_t *part = esp_partition_find_first(ESP_PARTITION_TYPE_DATA, ESP_PARTITION_SUBTYPE_ANY, "voice_data");
    if (part == NULL) {
        printf("Couldn't find voice data partition!\n");
        return;
    }

    const void *voicedata;
    esp_partition_mmap_handle_t mmap;
    esp_err_t err = esp_partition_mmap(part, 0, part->size, ESP_PARTITION_MMAP_DATA, (const void **)&voicedata, &mmap);
    if (err != ESP_OK) {
        printf("Couldn't map voice data partition!\n");
        return;
    }

    // 初始化语音模型，使用模板初始化
    esp_tts_voice_t *voice = esp_tts_voice_set_init(&esp_tts_voice_template, (int16_t *)voicedata);
    if (voice == NULL) {
        printf("TTS voice init failed!\n");
        return;
    }
    g_tts_handle = esp_tts_create(voice);
    tts_init_flag=1;
}

static void text_to_speech_task(void *arg)
{
    const char *text = (const char *)arg;
    if (g_tts_handle == NULL) {
        printf("TTS model not initialized!\n");
        xSemaphoreGive(tts_semaphore);
        vTaskDelete(NULL);
        return;
    }

    if (esp_tts_parse_chinese(g_tts_handle, text)) {
        tts_flag = 1;
        int len[1] = {0};

        bsp_codec_dev_delete();
        bsp_codec_dev_create();
//        bsp_audio_set_play_vol(50);
        bsp_codec_dev_open(10000, 2, 16);

        do {
//            short *pcm = (short *)heap_caps_malloc(4*1024 * sizeof(short), MALLOC_CAP_SPIRAM);
            short *pcm = esp_tts_stream_play(g_tts_handle, len, 0);
            bsp_audio_play2(pcm, len[0] * 2, portMAX_DELAY);
        } while (len[0] > 0);

        bsp_codec_dev_close();
        bsp_codec_dev_open(16000, 1, 16);
        tts_flag = 0;
    }

    esp_tts_stream_reset(g_tts_handle);
    xSemaphoreGive(tts_semaphore);
    vTaskDelete(NULL);
}

void text_to_speech(const char *text)
{
    sc_stop_flag = 1;
    tts_semaphore = xSemaphoreCreateBinary();
    xTaskCreatePinnedToCore(text_to_speech_task, "tts_task", 4*1024, (void *)text, 5, NULL, 0);
    xSemaphoreTake(tts_semaphore, portMAX_DELAY);
    sc_stop_flag = 0;
    vSemaphoreDelete(tts_semaphore);
}

int get_tts_flag(void) {
    return tts_flag;
}

int get_tts_init_flag(void) {
    return tts_init_flag;
}
