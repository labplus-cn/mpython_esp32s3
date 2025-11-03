import random
import lvgl as lv
from lv_gui import CANVAS
from mpython import light
from utils import change_route, set_key_config, lv_group

container = None
timer_flag = False

playing = False
fireworks = []
firework_index = 1
COLOR = [0xffffff, 0xff0000, 0xffff00, 0xff00ff, 0x00ff00, 0x0000ff, 0X00fdff]

def creat_firework():
    global fireworks
    cx = random.randint(40, 280)
    cy = random.randint(65, 107)
    cr = random.randint(25, 45)
    color = COLOR[random.randint(0, len(COLOR) - 1)]
    for y in range(170, cy, -6):
        fireworks.append({ 'type': 'line', 'x1': cx, 'y1': (y + 6), 'x2': cx, 'y2': y, 'color': color })
        fireworks.append({ 'type': 'line', 'x1': cx, 'y1': (y + 12), 'x2': cx, 'y2': y + 6, 'color': 0x000000 })
    fireworks.append({ 'type': 'line', 'x1': cx, 'y1': cy, 'x2': cx, 'y2': cy + 12, 'color': 0x000000 })
    for r in range(0, cr, 2):
        fireworks.append({ 'type': 'round', 'x': cx, 'y': cy, 'r': r, 'bd_w': 2, 'color': color })
    for r in range(0, cr + 2, 2):
        fireworks.append({ 'type': 'round', 'x': cx, 'y': cy, 'r': r, 'bd_w': 4, 'color': 0x000000 })

def gui_back_cb(e):
    change_route('home', destroy)

def lv_timer_cb(timer):
    global fireworks, firework_index, playing
    if not timer_flag:
        timer.delete()
    else:
        data = timer.user_data.__cast__()
        gui = data.get('gui')
        back_txt = data.get('back_txt')
        tips_txt = data.get('tips_txt')
        val = light.read()
        if val < 100:
            if not playing:
                gui.draw_rect(0, 0, 320, 172, 0, 0xff0000, 0x000000, 0, 1, 1)
                playing = True
                back_txt.add_flag(lv.obj.FLAG.HIDDEN)
                tips_txt.add_flag(lv.obj.FLAG.HIDDEN)
            if firework_index > (len(fireworks) - 1):
                fireworks = []
                creat_firework()
                firework_index = 0
            item = fireworks[firework_index]
            if item.get('type') == 'line':
                gui.draw_line(item.get('x1'), item.get('y1'), item.get('x2'), item.get('y2'), size=2, color=item.get('color'), draw=1)
                item2 = fireworks[firework_index + 1]
                if item2.get('type') == 'line':
                    gui.draw_line(item2.get('x1'), item2.get('y1'), item2.get('x2'), item2.get('y2'), size=2, color=item2.get('color'), draw=1)
                    firework_index += 2
                else:
                    firework_index += 1
            else:
                gui.draw_round(item.get('x'), item.get('y'), item.get('r'), item.get('bd_w'), item.get('color'), 0xffffff, 0, 1)
                firework_index += 1
            gui.update()
        else:
            playing = False
            fireworks = []
            firework_index = 1
            gui.draw_rect(0, 0, 320, 172, 0, 0xff0000, 0xffffff, 0, 1, 1)
            gui.draw_rect(0, 0, 320, 42, 0, 0xff0000, 0xEBEBEB, 0, 1, 1)
            gui.update()
            back_txt.remove_flag(lv.obj.FLAG.HIDDEN)
            tips_txt.remove_flag(lv.obj.FLAG.HIDDEN)
            


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

    gui = CANVAS(container)
    gui.draw_rect(0, 0, 320, 172, 0, 0xff0000, 0xffffff, 0, 1, 1)
    gui.draw_rect(0, 0, 320, 42, 0, 0xff0000, 0xEBEBEB, 0, 1, 1)
    gui.update()
    
    back_txt = lv.label(container)
    back_txt.set_pos(10, 0)
    back_txt.set_text('A-返回')
    back_txt.set_style_text_font(lv.font_siyuan_heiti_medium_24, 0)
    back_txt.set_style_text_color(lv.color_hex(0x333333), lv.PART.MAIN)
    
    back_btn = lv.obj(container)
    back_btn.set_size(0, 0)
    back_btn.add_style(obj_sty, lv.PART.MAIN)
    back_btn.add_event_cb(gui_back_cb, lv.EVENT.CLICKED, None)
    lv_group.add_obj(back_btn)

    tips_txt = lv.label(container)
    tips_txt.set_text('等天黑了就可以看烟花啦！\n（提示：遮住光线传感器）')
    tips_txt.set_style_text_font(lv.font_siyuan_heiti_medium_24, 0)
    tips_txt.set_style_text_color(lv.color_hex(0x333333), lv.PART.MAIN)
    tips_txt.align(lv.ALIGN.CENTER, 0, 10)
    
    lv.timer_create(lv_timer_cb, 10, { 'gui': gui, 'back_txt': back_txt, 'tips_txt': tips_txt })

    set_key_config({
        'button_a_key_cb': lambda: back_btn.send_event(lv.EVENT.CLICKED, None),
        'button_b_key_cb': lambda: None
    })
    
    
def destroy():
    global container, timer_flag
    timer_flag = False
    container.clean()
    container = None