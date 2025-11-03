import lvgl as lv
from mpython import sound
from utils import change_route, set_key_config, lv_group

container = None
timer_flag = False

def gui_back_cb(e):
    change_route('home', destroy)

def lv_timer_cb(timer):
    if not timer_flag:
        timer.delete()
    else:
        data = timer.user_data.__cast__()
        chart = data.get('chart')
        serie = data.get('serie')
        val = sound.read()
        val = 900 if val > 900 else val
        chart.set_next_value(serie, int(val))
        chart.set_next_value(serie, int(val) * -1)


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
    container_sty.set_bg_color(lv.color_hex(0xE8E8E8))
    container_sty.set_pad_gap(0)

    
    container = lv.obj()
    container.add_style(obj_sty, lv.PART.MAIN)
    container.add_style(container_sty, lv.PART.MAIN)
    container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    
    back_txt = lv.label(container)
    back_txt.set_pos(13, 0)
    back_txt.set_text('A-返回')
    back_txt.set_style_text_font(lv.font_siyuan_heiti_medium_24, 0)
    back_txt.set_style_text_color(lv.color_hex(0xFFFFFF), lv.PART.MAIN)
    
    back_btn = lv.obj(container)
    back_btn.set_size(0, 0)
    back_btn.add_style(obj_sty, lv.PART.MAIN)
    back_btn.add_event_cb(gui_back_cb, lv.EVENT.CLICKED, None)
    lv_group.add_obj(back_btn)
    
    name_txt = lv.label(container)
    name_txt.set_text('声波图')
    name_txt.set_style_text_font(lv.font_siyuan_heiti_medium_24, 0)
    name_txt.set_style_text_color(lv.color_hex(0xFFFFFF), lv.PART.MAIN)
    name_txt.set_pos(238, 0)
    
    chart = lv.chart(container)
    chart.set_size(300, 120)
    chart.set_pos(10, 40)
    chart.add_style(obj_sty, lv.PART.MAIN)
    chart.set_style_radius(10, lv.PART.MAIN)
    chart.set_div_line_count(0, 0)
    chart.set_point_count(100)
    chart.set_range(lv.chart.AXIS.PRIMARY_Y, -1000, 1000)
    # chart.set_update_mode(lv.chart.UPDATE_MODE.CIRCULAR)
    chart.set_style_line_rounded(False, lv.PART.MAIN)
    chart.set_style_line_dash_gap(0, lv.PART.ITEMS)
    chart.set_style_pad_right(10, lv.PART.MAIN)
    # chart.set_style_transform_pivot_x(150, 0)
    # chart.set_style_transform_pivot_y(60, 0)
    # chart.set_style_transform_rotation(1800, 0)
    
    style = lv.style_t()
    style.init()
    style.set_radius(0) # 设置圆角为 0（方形点）
    style.set_size(0, 0) # 设置点的大小为 0（完全隐藏）
    chart.add_style(style, lv.PART.INDICATOR) # 应用到数据点
    
    serie = chart.add_series(lv.color_hex(0x01B90E), lv.chart.AXIS.PRIMARY_Y)
    
    lv.timer_create(lv_timer_cb, 10, {'chart': chart, 'serie': serie})

    set_key_config({
        'button_a_key_cb': lambda: back_btn.send_event(lv.EVENT.CLICKED, None),
        'button_b_key_cb': lambda: None
    })
    
    
def destroy():
    global container, timer_flag
    timer_flag = False
    container.clean()
    container = None