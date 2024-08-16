/*
 * This file is part of the MicroPython project, http://micropython.org/
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2023 Damien P. George
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include "py/runtime.h"

#if MICROPY_PY_TTS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_tts.h"
#include "esp_tts_voice_xiaole.h"
#include "esp_tts_voice_template.h"
// #include "esp_tts_player.h"
// #include "esp_board_init.h"
// #include "ringbuf.h"

// #include "tts_urat.h"

// #include "wav_encoder.h"
#include "esp_partition.h"
#include "esp_idf_version.h"
// #include "shared/runtime/pyexec.h"

static mp_obj_t tts_init(void) {
/*** 1. create esp tts handle ***/
    // initial voice set from separate voice data partition

    const esp_partition_t* part=esp_partition_find_first(ESP_PARTITION_TYPE_DATA, ESP_PARTITION_SUBTYPE_ANY, "voice_data");
    if (part==NULL) { 
        printf("Couldn't find voice data partition!\n"); 
        return mp_const_none;
    } else {
        printf("voice_data paration size:%d\n", (int)part->size);
    }
    void* voicedata;
#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
    esp_partition_mmap_handle_t mmap;
    esp_err_t err=esp_partition_mmap(part, 0, part->size, ESP_PARTITION_MMAP_DATA, &voicedata, &mmap);
#endif
    if (err != ESP_OK) {
        printf("Couldn't map voice data partition!\n"); 
        return mp_const_none;
    }
    esp_tts_voice_t *voice=esp_tts_voice_set_init(&esp_tts_voice_template, (int16_t*)voicedata); 
    
    esp_tts_handle_t *tts_handle=esp_tts_create(voice);

    /*** 2. play prompt text ***/
    char *prompt1="欢迎使用乐鑫语音合成";  
    printf("%s\n", prompt1);
    if (esp_tts_parse_chinese(tts_handle, prompt1)) {
            int len[1]={0};
            do {
                short *pcm_data=esp_tts_stream_play(tts_handle, len, 3);
// #ifdef SDCARD_OUTPUT_ENABLE
//                 wav_encoder_run(wav_encoder, pcm_data, len[0]*2);
// #else
//                 esp_audio_play(pcm_data, len[0]*2, portMAX_DELAY);
// #endif
                printf("data:%d \n", len[0]);
            } while(len[0]>0);
    }
    esp_tts_stream_reset(tts_handle);
// #ifdef SDCARD_OUTPUT_ENABLE
//     wav_encoder_close(wav_encoder);
// #endif

    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_0(tts_init_obj, tts_init);

static const mp_rom_map_elem_t tts_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_tts) },
    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&tts_init_obj)},
};
static MP_DEFINE_CONST_DICT(tts_module_globals, tts_module_globals_table);

const mp_obj_module_t mp_module_tts = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&tts_module_globals,
};

MP_REGISTER_EXTENSIBLE_MODULE(MP_QSTR_tts, mp_module_tts);

#endif // MICROPY_PY_TTS
