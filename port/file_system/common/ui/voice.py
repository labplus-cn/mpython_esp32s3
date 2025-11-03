import time
import lvgl as lv
from lv_gui import CANVAS
from mpython import rgb
import audio
import sc
from utils import change_route, set_key_config, lv_group

container = None
timer_flag = False
img_index = 0
anim_imgs = [
    'ui/assets/light-pic1.png',
    'ui/assets/light-pic2.png',
    'ui/assets/light-pic3.png',
    'ui/assets/light-pic2.png',
]
play_time = time.time() - 16

# 初始化
sc.init(wakeup_word="我在")
sc.add(1,"kai deng")
sc.add(2,"guan deng")
sc.add(3,"da kai yin yue")
sc.add(4,"guan bi yin yue")
sc.update()

def gui_back_cb(e):
    change_route('home', destroy)

def lv_timer_cb(timer):
    global img_index, play_time
    if not timer_flag:
        timer.delete()
    else:
        data = timer.user_data.__cast__()
        gui = data.get('gui')
        gui.clear()
        gui.draw_img(38, 106, anim_imgs[img_index], 244, 46)
        gui.update()
        img_index = 0 if img_index >= 3 else img_index + 1
        res=sc.get_latest_id()
        if res:
            print(res)
            if res == 1:
                rgb.fill((int(255), int(0), int(0)))
                rgb.write()
                time.sleep_ms(1)
            elif res == 2:
                rgb.fill( (0, 0, 0) )
                rgb.write()
                time.sleep_ms(1)
            # elif res == 3:
            #     audio.set_volume(80)
            #     if time.time() >= (play_time + 15):
            #         play_time = time.time()
            #         audio.play('ui/assets/voice-music.mp3')
            # elif res == 4:
            #     audio.set_volume(0)

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
    gui.set_bg_color(0x000000)
    
    back_txt = lv.label(container)
    back_txt.set_pos(10, 0)
    back_txt.set_text('A-返回')
    back_txt.set_style_text_font(lv.font_siyuan_heiti_medium_24, 0)
    back_txt.set_style_text_color(lv.color_hex(0xFFFFFF), lv.PART.MAIN)
    
    con_txt1 = lv.label(container)
    con_txt1.set_text('唤醒词：你好小智')
    con_txt1.set_style_text_font(lv.font_siyuan_heiti_medium_24, 0)
    con_txt1.set_style_text_color(lv.color_hex(0xFFFFFF), lv.PART.MAIN)
    con_txt1.set_style_text_align(lv.TEXT_ALIGN.CENTER, lv.PART.MAIN)
    con_txt1.align(lv.ALIGN.CENTER, 0, -20)
    
    con_txt2 = lv.label(container)
    con_txt2.set_text('命令词：开灯/关灯')
    con_txt2.set_style_text_font(lv.font_siyuan_heiti_medium_24, 0)
    con_txt2.set_style_text_color(lv.color_hex(0xFFFFFF), lv.PART.MAIN)
    con_txt2.set_style_text_align(lv.TEXT_ALIGN.CENTER, lv.PART.MAIN)
    con_txt2.align(lv.ALIGN.CENTER, 0, 10)
    
    back_btn = lv.obj(container)
    back_btn.set_size(0, 0)
    back_btn.add_style(obj_sty, lv.PART.MAIN)
    back_btn.add_event_cb(gui_back_cb, lv.EVENT.CLICKED, None)
    lv_group.add_obj(back_btn)
    
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