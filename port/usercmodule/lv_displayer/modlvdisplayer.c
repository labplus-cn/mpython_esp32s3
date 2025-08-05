#include "esp_log.h"
#include "esp_timer.h"
#include "py/runtime.h"
#include "who_lcd.h"
#include "lvgl.h"
#include "py/obj.h"
#include "esp_lcd_panel_ops.h"

typedef struct _lv_displayet_t
{
    mp_obj_base_t base;
    lcd_t *lcd;

    size_t buf_size;
    uint16_t *buf1;
    uint16_t *buf2;

    lv_display_t *lv_display;
} lv_displayet_t;

lv_displayet_t *lv_displayer;
static void flush_cb(lv_display_t *display, const lv_area_t *area, uint8_t *data)
{
    lv_displayet_t *disp = (lv_displayet_t *) lv_display_get_user_data(display);

    lv_draw_sw_rgb565_swap(data, disp->buf_size);
    esp_lcd_panel_draw_bitmap(disp->lcd->panel, area->x1, area->y1, area->x2 + 1, area->y2 + 1, (uint16_t *)data);
}

static void transfer_done_cb(void *user_data)
{
    lv_displayet_t *disp = (lv_displayet_t *) user_data;
    lv_disp_flush_ready(disp->lv_display);
}

static uint32_t tick_get_cb()
{
    return esp_timer_get_time() / 1000;
}

static mp_obj_t lv_displayer_init(void)
{
    if(!lv_displayer){
        lv_displayer = calloc(1, sizeof(lv_displayet_t));

        lv_displayer->lcd = get_lcd_handle();
        if(!lv_displayer->lcd){
            lcd_init();
        }

        if (!lv_is_initialized()){
            lv_init();
        }
    
        lv_displayer->lv_display = lv_display_create(BOARD_LCD_H_RES, BOARD_LCD_V_RES);
    
        lv_displayer->buf_size = BOARD_LCD_H_RES * 20;
        lv_displayer->buf1 = heap_caps_malloc(lv_displayer->buf_size * sizeof(lv_color_t), MALLOC_CAP_DMA);
        assert(lv_displayer->buf1);
        lv_displayer->buf2 = heap_caps_malloc(lv_displayer->buf_size * sizeof(lv_color_t), MALLOC_CAP_DMA);
        assert(lv_displayer->buf2);
    
        lv_display_set_buffers(lv_displayer->lv_display, lv_displayer->buf1, lv_displayer->buf2, lv_displayer->buf_size, LV_DISPLAY_RENDER_MODE_PARTIAL);
    
        lv_displayer->lcd->transfer_done_cb = transfer_done_cb;
        lv_displayer->lcd->transfer_done_user_data = (void *) lv_displayer;
        lv_display_set_flush_cb(lv_displayer->lv_display, flush_cb);
        lv_display_set_user_data(lv_displayer->lv_display, lv_displayer);
        lv_tick_set_cb(tick_get_cb);
    }

    return mp_obj_new_int_from_uint(0);
}
static MP_DEFINE_CONST_FUN_OBJ_0(lv_displayer_init_obj, lv_displayer_init);

static mp_obj_t lv_displayer_deinit(void)
{
    if(lv_displayer){
        lv_tick_set_cb(NULL);
        lv_displayer->lcd->transfer_done_cb = NULL;
        lv_displayer->lcd->transfer_done_user_data = NULL;
    
        if (lv_displayer->lv_display != NULL){
            lv_display_delete(lv_displayer->lv_display);
            lv_displayer->lv_display = NULL;
        }
    
        lv_displayer->buf_size = 0;
        if (lv_displayer->buf1 != NULL){
            heap_caps_free(lv_displayer->buf1);
            lv_displayer->buf1 = NULL;
        }
        if (lv_displayer->buf2 != NULL){
            heap_caps_free(lv_displayer->buf2);
            lv_displayer->buf2 = NULL;
        }
    
        if (lv_is_initialized()){
            lv_deinit();
        }

        free(lv_displayer);
    }

    return mp_obj_new_int_from_uint(0);
}
static MP_DEFINE_CONST_FUN_OBJ_0(lv_displayer_deinit_obj, lv_displayer_deinit);

static const mp_rom_map_elem_t lv_displayer_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_lv_displayer) },
    { MP_ROM_QSTR(MP_QSTR___init__), MP_ROM_PTR(&lv_displayer_init_obj) },
    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&lv_displayer_init_obj) },
    { MP_ROM_QSTR(MP_QSTR___del__), MP_ROM_PTR(&lv_displayer_deinit_obj) },
    { MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&lv_displayer_deinit_obj) },
};
static MP_DEFINE_CONST_DICT(lv_display_module_globals, lv_displayer_module_globals_table);

const mp_obj_module_t lv_display_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&lv_display_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_lv_displayer, lv_display_cmodule);

