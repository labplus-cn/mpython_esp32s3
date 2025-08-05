#include "py/runtime.h"
#include "who_camera.h"
#include "esp_camera.h"
#include "esp_log.h"
#include "driver/gpio.h"
#include "who_lcd.h"

camera_fb_t *frame = NULL;

static mp_obj_t reset(void)
{
    camera_init(PIXFORMAT_RGB565, FRAMESIZE_QVGA, 2);

    return mp_const_none; 
}
static MP_DEFINE_CONST_FUN_OBJ_0(sensor_reset_obj, reset);

static mp_obj_t get_frame_width(void)
{
    return MP_OBJ_NEW_SMALL_INT(frame->width);
}
static MP_DEFINE_CONST_FUN_OBJ_0(get_frame_width_obj, get_frame_width);

static mp_obj_t get_frame_height(void)
{
    return MP_OBJ_NEW_SMALL_INT(frame->height);
}
static MP_DEFINE_CONST_FUN_OBJ_0(get_frame_height_obj, get_frame_height);

static mp_obj_t snapshot(void)
{
    frame = esp_camera_fb_get();
    lcd_draw_image(0, 0, frame->width, frame->height, (void *)(frame->buf));
    // ESP_LOGI("tag", "frame addr: %p", &(frame));

    // mp_obj_t items[] = {MP_OBJ_NEW_SMALL_INT(frame->width), 
    //                     MP_OBJ_NEW_SMALL_INT(frame->height),
    //                     mp_obj_new_bytes(frame->buf, frame->len) };
    // return mp_obj_new_tuple(3, items);

    // return mp_obj_new_bytes(frame->buf, frame->len);
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_0(sensor_snapshot_obj, snapshot);

static mp_obj_t free_fb(void)
{
    esp_camera_fb_return(frame);

    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_0(sensor_free_fb_obj, free_fb);

mp_obj_t sensor_init(void)
{
    if(!frame){
        frame = calloc(1, sizeof(camera_fb_t));
    }
    return mp_obj_new_int_from_uint(0);
}
static MP_DEFINE_CONST_FUN_OBJ_0(sensor_init_obj, sensor_init);

mp_obj_t sensor_deinit(void)
{
    if(frame){
        free(frame);
    }
    return mp_obj_new_int_from_uint(0);
}
static MP_DEFINE_CONST_FUN_OBJ_0(sensor_deinit_obj, sensor_deinit);

static const mp_rom_map_elem_t sensor_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_sensor) },
    { MP_ROM_QSTR(MP_QSTR___init__), MP_ROM_PTR(&sensor_init_obj) },
    { MP_ROM_QSTR(MP_QSTR___del__), MP_ROM_PTR(&sensor_deinit_obj) },
    { MP_ROM_QSTR(MP_QSTR_get_frame_width), MP_ROM_PTR(&get_frame_width_obj) },
    { MP_ROM_QSTR(MP_QSTR_get_frame_height), MP_ROM_PTR(&get_frame_height_obj) },
    { MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&sensor_deinit_obj) },
    { MP_ROM_QSTR(MP_QSTR_reset), MP_ROM_PTR(&sensor_reset_obj) },
    { MP_ROM_QSTR(MP_QSTR_snapshot), MP_ROM_PTR(&sensor_snapshot_obj) },
    { MP_ROM_QSTR(MP_QSTR_free_fb), MP_ROM_PTR(&sensor_free_fb_obj) },
};
static MP_DEFINE_CONST_DICT(sensor_module_globals, sensor_module_globals_table);

// Define module object.
const mp_obj_module_t sensor_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&sensor_module_globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_sensor, sensor_cmodule);
