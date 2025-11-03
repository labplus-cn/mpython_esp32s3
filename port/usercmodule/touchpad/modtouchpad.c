/*
 * This file is part of the MicroPython project, http://micropython.org/
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2017 Nick Moore
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
#include "py/mphal.h"
#include "driver/gpio.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "focaltech_core.h"
#include "py/obj.h"
#include "esp_log.h"

#define TOUCHPAD_NUM     6
typedef enum{
    PAD_P,
    PAD_Y,
    PAD_T,
    PAD_H,
    PAD_O,
    PAD_N,
}tp_id_t;

static keys_state_t key_state_array[MAX_POINTS_TOUCH_TRACE];

static QueueHandle_t touchpad_gpio_evt_queue = NULL;;
extern int fts_fwupg_auto_upgrade(void);

typedef struct _mtp_obj_t {
    mp_obj_base_t base;
    tp_id_t tp_num;
    bool was_pressed;  
    bool is_released;
    bool is_pressed;
    uint8_t pressed_cnt;
} mtp_obj_t;

extern const mp_obj_type_t machine_touchpad_type;
mtp_obj_t touchpad_obj[6] = {
    {{&machine_touchpad_type}, PAD_P, false, false, 0}, 
    {{&machine_touchpad_type}, PAD_Y, false, false, 0},
    {{&machine_touchpad_type}, PAD_T, false, false, 0},
    {{&machine_touchpad_type}, PAD_H, false, false, 0},
    {{&machine_touchpad_type}, PAD_O, false, false, 0},
    {{&machine_touchpad_type}, PAD_N, false, false, 0},
};

static void int_pin_isr_handler(void *arg)
{
    uint32_t gpio_num = (uint32_t) arg;
    if(gpio_num == 45){
        xQueueSendFromISR(touchpad_gpio_evt_queue, &gpio_num, NULL);
    }   
}

static void touchpad_task(void* arg)
{
    uint32_t io_num;
    int type;
    int keyid;
    mp_obj_t event_cb = NULL;
    for (;;) {
        if (xQueueReceive(touchpad_gpio_evt_queue, &io_num, portMAX_DELAY)) {
            if(io_num == 45){
                fts_touch_process(key_state_array);

                if(key_state_array[0].type == 1){
                    // ESP_LOGI("touchpad:", "key press. key_id %d\r\n", key_state_array[0].key_id);
                    touchpad_obj[key_state_array[0].key_id].was_pressed = true;
                    touchpad_obj[key_state_array[0].key_id].is_pressed = true;
                    touchpad_obj[key_state_array[0].key_id].pressed_cnt++;
                    event_cb = MP_STATE_PORT(mtp_etent_cb_array)[key_state_array[0].key_id];
                    if(event_cb){
                        mp_sched_schedule(event_cb, mp_obj_new_int(1));
                    }

                }else if(key_state_array[0].type == 2){
                    // ESP_LOGI("touchpad:", "key releasekey_id %d\r\n", key_state_array[0].key_id);
                    touchpad_obj[key_state_array[0].key_id].is_pressed = false;
                    touchpad_obj[key_state_array[0].key_id].is_released = true;
                    event_cb = MP_STATE_PORT(mtp_etent_cb_array)[key_state_array[0].key_id];
                    if(event_cb){
                        mp_sched_schedule(event_cb, mp_obj_new_int(0));
                    }
                }
            }
            // xQueueReset(touchpad_gpio_evt_queue);
        }
        vTaskDelay(100 / portTICK_PERIOD_MS);
    }
}

static mp_obj_t set_event_cb(mp_obj_t self_in, mp_obj_t event_cb)
{
    mtp_obj_t *self = self_in;
    MP_STATE_PORT(mtp_etent_cb_array)[self->tp_num] = event_cb;
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_2(set_event_cb_obj, set_event_cb);

static mp_obj_t is_pressed(mp_obj_t self_in)
{
    mtp_obj_t *self = self_in;
    // return mp_obj_new_bool(self->is_pressed);

    mp_obj_t _was_pressed = mp_obj_new_bool(self->was_pressed); //当前，经常有检测不到按键弹起，所以用was_pressed暂时替代。
    self->was_pressed = false;

    return _was_pressed;

}
static MP_DEFINE_CONST_FUN_OBJ_1(is_pressed_obj, is_pressed);

static mp_obj_t was_pressed(mp_obj_t self_in)
{
    mtp_obj_t *self = self_in;
    mp_obj_t _was_pressed = mp_obj_new_bool(self->was_pressed);
    self->was_pressed = false;

    return _was_pressed;

}
static MP_DEFINE_CONST_FUN_OBJ_1(was_pressed_obj, was_pressed);

static mp_obj_t get_presses(mp_obj_t self_in)
{
    mtp_obj_t *self = self_in;
    mp_obj_t _pressed_cnt = MP_OBJ_NEW_SMALL_INT(self->pressed_cnt);
    self->pressed_cnt = 0;

    return _pressed_cnt;

}
static MP_DEFINE_CONST_FUN_OBJ_1(get_presses_obj, get_presses);

static mp_obj_t mtp_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw,
    const mp_obj_t *args) {
    mp_arg_check_num(n_args, n_kw, 1, 1, true);
    int touchpad_id = mp_obj_get_int(args[0]);

    const mtp_obj_t *self = NULL;
    for (int i = 0; i < MP_ARRAY_SIZE(touchpad_obj); i++) {
        if (touchpad_id == touchpad_obj[i].tp_num) {
            self = &touchpad_obj[i];
            break;
        }
    }
    if (!self) {
        mp_raise_ValueError(MP_ERROR_TEXT("invalid pin for touchpad"));
    }

    static int initialized = 0;
    if (!initialized) {
        int ret;
        // int ret = fts_fwupg_auto_upgrade();
        // if(ret < 0) {
        //     mp_raise_ValueError(MP_ERROR_TEXT("firmware upgrade fails."));
        // }
        ret = fts_check_id1();
        if (ret < 0){
            mp_raise_ValueError(MP_ERROR_TEXT("get chip id fails."));
        }

        gpio_config_t io_conf = {};
        io_conf.intr_type = GPIO_INTR_NEGEDGE; //interrupt of rising edge
        io_conf.pin_bit_mask = 1ULL<<45;
        io_conf.mode = GPIO_MODE_INPUT;
        io_conf.pull_up_en = 1; //enable pull-up mode
        gpio_config(&io_conf);
        gpio_install_isr_service(0);
        gpio_isr_handler_add(45, int_pin_isr_handler, (void*) 45);  
    
        touchpad_gpio_evt_queue = xQueueCreate(10, sizeof(uint32_t));
        xTaskCreatePinnedToCore(touchpad_task, "touchpad_task", 4 * 1024, NULL, 2, NULL, 1);

        initialized = 1;
    }

    return MP_OBJ_FROM_PTR(self);
}

static mp_obj_t update_fw(mp_obj_t self_in)
{
    mtp_obj_t *self = self_in;
    int ret = fts_fwupg_auto_upgrade();
    if(ret < 0) {
        mp_raise_ValueError(MP_ERROR_TEXT("firmware upgrade fails."));
    }
    return mp_obj_new_int(ret);
}
static MP_DEFINE_CONST_FUN_OBJ_0(update_fw_obj, update_fw);

static const mp_rom_map_elem_t mtp_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_TouchPad) },
    { MP_ROM_QSTR(MP_QSTR_set_event_cb), MP_ROM_PTR(&set_event_cb_obj) },
    { MP_ROM_QSTR(MP_QSTR_is_pressed), MP_ROM_PTR(&is_pressed_obj) },
    { MP_ROM_QSTR(MP_QSTR_was_pressed), MP_ROM_PTR(&was_pressed_obj) },
    { MP_ROM_QSTR(MP_QSTR_get_presses), MP_ROM_PTR(&get_presses_obj) },
};

static MP_DEFINE_CONST_DICT(mtp_locals_dict, mtp_locals_dict_table);

MP_DEFINE_CONST_OBJ_TYPE(
    machine_touchpad_type,
    MP_QSTR_TouchPad,
    MP_TYPE_FLAG_NONE,
    make_new, mtp_make_new,
    locals_dict, &mtp_locals_dict
    );


static const mp_rom_map_elem_t toupad_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_touchpad) },
    { MP_ROM_QSTR(MP_QSTR_TouchPad), MP_ROM_PTR(&machine_touchpad_type) },
    { MP_ROM_QSTR(MP_QSTR_update_fw), MP_ROM_PTR(&update_fw_obj) },
};
static MP_DEFINE_CONST_DICT(toupad_locals_dict, toupad_locals_dict_table);

const mp_obj_module_t touchpad_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t * ) & toupad_locals_dict,
};

MP_REGISTER_MODULE(MP_QSTR_touchpad, touchpad_module);
MP_REGISTER_ROOT_POINTER(mp_obj_t *mtp_etent_cb_array[TOUCHPAD_NUM]);
