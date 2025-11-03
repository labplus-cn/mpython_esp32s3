#include "py/runtime.h"
#include "who_lcd.h"
#include "esp_camera.h"

static mp_obj_t mp_lcd_init(void)
{
    lcd_init();
    return mp_const_none; 
}
static MP_DEFINE_CONST_FUN_OBJ_0(mp_lcd_init_obj, mp_lcd_init);

static mp_obj_t mp_lcd_deinit(void)
{
    lcd_deinit();
    return mp_obj_new_int_from_uint(0);
}
static MP_DEFINE_CONST_FUN_OBJ_0(mp_lcd_deinit_obj, mp_lcd_deinit);

static mp_obj_t mp_lcd_draw_logo(void)
{
    lcd_draw_logo();
    return mp_const_none; 
}
static MP_DEFINE_CONST_FUN_OBJ_0(mp_lcd_draw_logo_obj, mp_lcd_draw_logo);

// static mp_obj_t draw_image(mp_obj_t image)
// {
//     camera_fb_t *frame = MP_OBJ_TO_PTR(image);
//     display_draw_image(frame);

//     return mp_const_none; 
// }
// static MP_DEFINE_CONST_FUN_OBJ_1(display_draw_image_obj, draw_image);

static mp_obj_t mp_lcd_draw_color(mp_obj_t color)
{
    int _color = mp_obj_get_int(color);
    lcd_set_color(_color);

    return mp_const_none; 
}
static MP_DEFINE_CONST_FUN_OBJ_1(mp_lcd_draw_color_obj, mp_lcd_draw_color);

static const mp_rom_map_elem_t lcd_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_lcd) },
    { MP_ROM_QSTR(MP_QSTR___init__), MP_ROM_PTR(&mp_lcd_init_obj) },
    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&mp_lcd_init_obj) },
    { MP_ROM_QSTR(MP_QSTR___del__), MP_ROM_PTR(&mp_lcd_deinit_obj) },
    { MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&mp_lcd_deinit_obj) },
    { MP_ROM_QSTR(MP_QSTR_draw_logo), MP_ROM_PTR(&mp_lcd_draw_logo_obj) },
    { MP_ROM_QSTR(MP_QSTR_draw_color), MP_ROM_PTR(&mp_lcd_draw_color_obj) },
    { MP_ROM_QSTR(MP_QSTR_PINK), MP_ROM_INT(GUI_Pink) },
    { MP_ROM_QSTR(MP_QSTR_DEEP_PINK), MP_ROM_INT(GUI_DeepPink) },
    { MP_ROM_QSTR(MP_QSTR_PURPLE), MP_ROM_INT(GUI_Purple) },
    { MP_ROM_QSTR(MP_QSTR_BLUE), MP_ROM_INT(GUI_Blue) },
    { MP_ROM_QSTR(MP_QSTR_LIGHT_BLUE), MP_ROM_INT(GUI_LightBLue) },
    { MP_ROM_QSTR(MP_QSTR_MEDIUM_BLUE), MP_ROM_INT(GUI_MediumBlue) },
    { MP_ROM_QSTR(MP_QSTR_DARK_BLUE), MP_ROM_INT(GUI_DarkBlue) },
    { MP_ROM_QSTR(MP_QSTR_SKY_BLUE), MP_ROM_INT(GUI_SkyBlue) },
    { MP_ROM_QSTR(MP_QSTR_LIGHT_CYAN), MP_ROM_INT(GUI_LightCyan) },
    { MP_ROM_QSTR(MP_QSTR_DARK_CYAN), MP_ROM_INT(GUI_DarkCyan) },
    { MP_ROM_QSTR(MP_QSTR_GREEN), MP_ROM_INT(GUI_Green) },
    { MP_ROM_QSTR(MP_QSTR_LIGHT_GREEN), MP_ROM_INT(GUI_LightGreen) },
    { MP_ROM_QSTR(MP_QSTR_DARK_GREEN), MP_ROM_INT(GUI_DarkGreen) },
    { MP_ROM_QSTR(MP_QSTR_GREEN_YELLOW), MP_ROM_INT(GUI_GreenYellow) },
    { MP_ROM_QSTR(MP_QSTR_LIGHT_YELLOW), MP_ROM_INT(GUI_LightYellow) },
    { MP_ROM_QSTR(MP_QSTR_YELLO), MP_ROM_INT(GUI_Yellow) },
    { MP_ROM_QSTR(MP_QSTR_ORANGE), MP_ROM_INT(GUI_Orange) },
    { MP_ROM_QSTR(MP_QSTR_RED), MP_ROM_INT(GUI_Red) },
    { MP_ROM_QSTR(MP_QSTR_DARK_RED), MP_ROM_INT(GUI_DarkRed) },
    { MP_ROM_QSTR(MP_QSTR_WHITE), MP_ROM_INT(GUI_White) },
    { MP_ROM_QSTR(MP_QSTR_GRAY), MP_ROM_INT(GUI_Gray) },
    { MP_ROM_QSTR(MP_QSTR_LIGHT_GRAY), MP_ROM_INT(GUI_LightGray) },
    { MP_ROM_QSTR(MP_QSTR_DARK_GRAY), MP_ROM_INT(GUI_DarkGray) },
    { MP_ROM_QSTR(MP_QSTR_BLACK), MP_ROM_INT(GUI_Black) },
    { MP_ROM_QSTR(MP_QSTR_LIGHT_SKY_BLUE), MP_ROM_INT(GUI_LightSkyBlue) },
    { MP_ROM_QSTR(MP_QSTR_DEEP_SKY_BLUE), MP_ROM_INT(GUI_DeepSkyBlue) },
    { MP_ROM_QSTR(MP_QSTR_CYAN), MP_ROM_INT(GUI_Cyan) },
    { MP_ROM_QSTR(MP_QSTR_SPRING_GREEN), MP_ROM_INT(GUI_SpringGreen) },
    { MP_ROM_QSTR(MP_QSTR_GOLD), MP_ROM_INT(GUI_Gold) },
    { MP_ROM_QSTR(MP_QSTR_DARK_ORANGE), MP_ROM_INT(GUI_DarkOrange) },
    { MP_ROM_QSTR(MP_QSTR_BROWN), MP_ROM_INT(GUI_Brown) },
    { MP_ROM_QSTR(MP_QSTR_LIGHT_GRAY), MP_ROM_INT(GUI_LightGray) },
};

static MP_DEFINE_CONST_DICT(lcd_module_globals, lcd_module_globals_table);

// Define module object.
const mp_obj_module_t lcd_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&lcd_module_globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_lcd, lcd_cmodule);
