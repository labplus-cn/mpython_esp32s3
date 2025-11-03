#include <string.h>
#include "py/obj.h"
#include "py/runtime.h"
#include "esp_tts.h"
#include "tts.h"


static mp_obj_t mp_model_init(void) {
    model_init();
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_0(mp_model_init_obj, mp_model_init);

static mp_obj_t mp_tts_generate(mp_obj_t text_obj) {
    // 获取文本参数
    const char* text = mp_obj_str_get_str(text_obj);
    size_t text_len = strlen(text);

    // 每次处理 50 个字符
    const size_t chunk_size = 200;
    char buffer[chunk_size + 1];  // 额外 1 字节用于存储 '\0'

    for (size_t i = 0; i < text_len; i += chunk_size) {
        size_t copy_len = (i + chunk_size < text_len) ? chunk_size : (text_len - i);
        memcpy(buffer, text + i, copy_len);
        buffer[copy_len] = '\0';  // 确保字符串结尾

        // 逐段播放
        text_to_speech(buffer);
    }

    return mp_const_none;  // 播放完成后返回 None
}

static MP_DEFINE_CONST_FUN_OBJ_1(mp_tts_generate_obj, mp_tts_generate);


// 模块定义
static const mp_rom_map_elem_t tts_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_tts) },
    { MP_ROM_QSTR(MP_QSTR_generate), MP_ROM_PTR(&mp_tts_generate_obj) },
    { MP_ROM_QSTR(MP_QSTR_model_init), MP_ROM_PTR(&mp_model_init_obj) },
};
static MP_DEFINE_CONST_DICT(tts_module_globals, tts_module_globals_table);

// 模块结构体
const mp_obj_module_t tts_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&tts_module_globals,
};

// 注册模块
MP_REGISTER_MODULE(MP_QSTR_tts, tts_module);