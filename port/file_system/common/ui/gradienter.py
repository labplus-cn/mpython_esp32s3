import lvgl as lv
from lv_gui import CANVAS
from mpython import accelerometer
from utils import change_route, set_key_config, lv_group

container = None
timer_flag = False

def gui_back_cb(e):
    change_route('home', destroy)

def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def lv_timer_cb(timer):
    if not timer_flag:
        timer.delete()
    else:
        data = timer.user_data.__cast__()
        gui = data.get('gui')
        a_y = accelerometer.get_y()
        a_y = -1 if a_y < -1 else a_y
        a_y = 1 if a_y > 1 else a_y
        a_x = accelerometer.get_x() * -1
        a_x = -1 if a_x < -1 else a_x
        a_x = 1 if a_x > 1 else a_x
        X = int(map_range(a_y, -1, 1, 100, 222))
        Y = int(map_range(a_x, -1, 1, 24, 146))
        gui.draw_round(160, 86, 86, 0, 0x00DDFF, 0x0080FF, 1, 1)
        gui.draw_round(160, 86, 73, 0, 0x00DDFF, 0xffffff, 1, 1)
        gui.draw_round(160, 86, 76, 6, 0x00DDFF, 0xffffff, 1, 1)
        gui.draw_line(87, 86, 97, 86, size=4, color=0x00DDFF)
        gui.draw_line(223, 86, 233, 86, size=4, color=0x00DDFF)
        gui.draw_line(160, 13, 160, 23, size=4, color=0x00DDFF)
        gui.draw_line(160, 149, 160, 159, size=4, color=0x00DDFF)
        gui.draw_line(130, 86, 190, 86, size=4, color=0x00DDFF)
        gui.draw_line(160, 56, 160, 116, size=4, color=0x00DDFF)
        gui.draw_round(X, Y, 9, 0, 0xff0000, 0xff0000, 1, 1)
        gui.update()


def init():
    global container, timer_flag
    timer_flag = True
    
    obj_sty = lv.style_t()
    obj_sty.init()
    obj_sty.set_pad_all(0)
    obj_sty.set_radius(0)
    obj_sty.set_border_width(0)
    
    container_sty = lv.style_t()
    container_sty.init()
    container_sty.set_size(lv.pct(100), lv.pct(100))
    container_sty.set_bg_color(lv.color_hex(0x0080FF))
    container_sty.set_pad_gap(0)

    
    container = lv.obj()
    container.add_style(obj_sty, lv.PART.MAIN)
    container.add_style(container_sty, lv.PART.MAIN)
    container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    
    gui = CANVAS(container)
    
    back_txt = lv.label(container)
    back_txt.set_pos(10, 0)
    back_txt.set_text('A-返回')
    back_txt.set_style_text_font(lv.font_siyuan_heiti_medium_24, 0)
    back_txt.set_style_text_color(lv.color_hex(0xffffff), lv.PART.MAIN)
    
    back_btn = lv.obj(container)
    back_btn.set_size(0, 0)
    back_btn.add_style(obj_sty, lv.PART.MAIN)
    back_btn.add_event_cb(gui_back_cb, lv.EVENT.CLICKED, None)
    lv_group.add_obj(back_btn)
    
    gui.set_bg_color(0x0080FF)
    
    lv.timer_create(lv_timer_cb, 50, {'gui': gui})

    set_key_config({
        'button_a_key_cb': lambda: back_btn.send_event(lv.EVENT.CLICKED, None),
        'button_b_key_cb': lambda: None
    })
    
    
def destroy():
    global container, timer_flag
    timer_flag = False
    container.clean()
    container = None