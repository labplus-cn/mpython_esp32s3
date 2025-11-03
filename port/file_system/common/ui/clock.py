import math
import utime
import lvgl as lv
from utils import change_route, set_key_config, lv_group

container = None
timer_flag = False
RADIUS = 76

def draw_clock(canvas=None, layer=None):
    x=RADIUS
    y=RADIUS
    r=RADIUS
    color = 0xFF6000
    bg_c=0xFFFFFF
    bd_c=0xFFCB5A
    
    # 绘制表盘
    dsc = lv.draw_rect_dsc_t()
    dsc.init()
    dsc.bg_color = lv.color_hex(bg_c)
    dsc.bg_opa = lv.OPA.COVER
    dsc.border_color = lv.color_hex(bd_c)
    dsc.border_width = 6
    dsc.radius = r
    coords = lv.area_t()
    coords.x1 = x - r
    coords.y1 = y - r
    coords.x2 = x + r
    coords.y2 = y + r
    lv.draw_rect(layer, dsc, coords)

    # 绘制表盘刻度
    for i in range(60):
        angle = i * 6  # 每刻度 6°
        rad = math.radians(angle - 90)
        # 刻度起点 & 终点
        x1 = int(x + (r - 10) * math.cos(rad))  # 靠近边缘
        y1 = int(y + (r - 10) * math.sin(rad))
        if i % 5 == 0:  # **整点（小时刻度）**
            x2 = int(x + (r - 20) * math.cos(rad))
            y2 = int(y + (r - 20) * math.sin(rad))
            width = 3  # 加粗
        else:  # **分钟刻度**
            x2 = int(x + (r - 18) * math.cos(rad))
            y2 = int(y + (r - 18) * math.sin(rad))
            width = 1  # 细线
        dsc = lv.draw_line_dsc_t()
        dsc.init()
        dsc.color = lv.color_hex(color)
        dsc.width = width
        dsc.opa = lv.OPA.COVER
        dsc.p1.x = x1
        dsc.p1.y = y1
        dsc.p2.x = x2
        dsc.p2.y = y2
        lv.draw_line(layer, dsc)
    
    # 绘制表盘数字
    for i in range(1, 13):
        angle = (i % 12) * 30  # 每小时 30°
        rad = math.radians(angle - 90)
        new_x = int(x + (r - 30) * math.cos(rad))
        new_y = int(y + (r - 30) * math.sin(rad))
        dsc = lv.draw_label_dsc_t()
        dsc.init()
        dsc.color = lv.color_hex(color)
        dsc.font = lv.font_montserrat_16
        dsc.opa = lv.OPA.COVER
        dsc.flag = lv.TEXT_FLAG.FIT
        dsc.align = lv.TEXT_ALIGN.CENTER
        dsc.text = str(i)
        coords = lv.area_t()
        coords.x1 = new_x - 10
        coords.y1 = new_y - 8
        coords.x2 = new_x + 10
        coords.y2 = new_y + 2
        lv.draw_label(layer, dsc, coords)
    
    # 绘制指针
    now = utime.localtime()
    hour, minute, second = now[3], now[4], now[5]
    hour_angle = (hour % 12) * 30 + (minute / 2)
    minute_angle = minute * 6 + (second / 10)
    second_angle = second * 6
    clock_draw_needle(x, y, hour_angle, int(r * 0.5), 4, 0xFFE300, layer)
    clock_draw_needle(x, y, minute_angle, int(r * 0.65), 4, 0xFFE300, layer)
    clock_draw_needle(x, y, second_angle, int(r * 0.85), 3, 0xFF0000, layer)

    # 绘制指针原点
    dsc = lv.draw_rect_dsc_t()
    dsc.init()
    dsc.bg_color = lv.color_hex(0xFF0000)
    dsc.bg_opa = lv.OPA.COVER
    dsc.border_width = 0
    dsc.radius = 10
    coords = lv.area_t()
    coords.x1 = x - 6
    coords.y1 = y - 6
    coords.x2 = x + 6
    coords.y2 = y + 6
    lv.draw_rect(layer, dsc, coords)
    
    canvas.finish_layer(layer)

def clock_draw_needle(x, y, angle, length, width, color, layer):
    rad = math.radians(angle - 90)
    x2 = int(x + length * math.cos(rad))
    y2 = int(y + length * math.sin(rad))
    dsc = lv.draw_line_dsc_t()
    dsc.init()
    dsc.color = lv.color_hex(color)
    dsc.width = width
    dsc.opa = lv.OPA.COVER
    dsc.p1.x = x 
    dsc.p1.y = y
    dsc.p2.x = x2
    dsc.p2.y = y2
    lv.draw_line(layer, dsc)

def gui_back_cb(e):
    change_route('home', destroy)

def lv_timer_cb(timer):
    if not timer_flag:
        timer.delete()
    else:
        data = timer.user_data.__cast__()
        canvas = data.get('canvas')
        layer = data.get('layer')
        draw_clock(canvas=canvas, layer=layer)


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
    container_sty.set_bg_color(lv.color_hex(0xFF811A))
    container_sty.set_pad_gap(0)


    container = lv.obj()
    container.add_style(obj_sty, lv.PART.MAIN)
    container.add_style(container_sty, lv.PART.MAIN)
    container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    
    back_txt = lv.label(container)
    back_txt.set_pos(10, 0)
    back_txt.set_text('A-返回')
    back_txt.set_style_text_font(lv.font_siyuan_heiti_medium_24, 0)
    back_txt.set_style_text_color(lv.color_hex(0xffffff), lv.PART.MAIN)
    
    draw_buf = bytearray(RADIUS * 2 * RADIUS * 2 * 4)
    canvas = lv.canvas(container)
    canvas.set_size(RADIUS * 2, RADIUS * 2)
    canvas.set_buffer(draw_buf, RADIUS * 2, RADIUS * 2, lv.COLOR_FORMAT.ARGB8888)
    canvas.center()
    canvas.fill_bg(lv.color_hex(0xFF811A), lv.OPA.COVER)
    layer = lv.layer_t()
    canvas.init_layer(layer)
    
    back_btn = lv.obj(container)
    back_btn.set_size(0, 0)
    back_btn.add_style(obj_sty, lv.PART.MAIN)
    back_btn.add_event_cb(gui_back_cb, lv.EVENT.CLICKED, None)
    lv_group.add_obj(back_btn)
    
    lv.timer_create(lv_timer_cb, 200, {'canvas': canvas, 'layer': layer})

    set_key_config({
        'button_a_key_cb': lambda: back_btn.send_event(lv.EVENT.CLICKED, None),
        'button_b_key_cb': lambda: None
    })
    
    
def destroy():
    global container, timer_flag
    timer_flag = False
    container.clean()
    container = None