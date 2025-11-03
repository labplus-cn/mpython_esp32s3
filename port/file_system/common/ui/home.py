import lvgl as lv
from lv_gui import CANVAS
from utils import change_route, set_key_config, lv_group

container = None
INDEX_PAGE = [
    {'name': '水平仪', 'page': 'gradienter', 'icon': 'gradienter', 'x': 10, 'y': 6},
    {'name': '人脸检测', 'page': 'face', 'icon': 'face', 'x': 113, 'y': 6},
    # {'name': '时钟', 'page': 'clock', 'icon': 'clock', 'x': 113, 'y': 6},
    {'name': '语音识别', 'page': 'voice', 'icon': 'voice', 'x': 216, 'y': 6},
    {'name': '光线', 'page': 'light', 'icon': 'light', 'x': 10, 'y': 88},
    {'name': '声音', 'page': 'sound', 'icon': 'sound', 'x': 113, 'y': 88},
    {'name': '游戏', 'page': 'game', 'icon': 'game', 'x': 216, 'y': 88}
]

def item_clicked_cb(e):
    data = e.user_data.__cast__()
    change_route(data.get('page'))


def init():
    global container
    
    obj_sty = lv.style_t()
    obj_sty.init()
    obj_sty.set_pad_all(0)
    obj_sty.set_radius(0)
    obj_sty.set_border_width(0)
    
    container_sty = lv.style_t()
    container_sty.init()
    container_sty.set_size(lv.pct(100), lv.pct(100))
    container_sty.set_bg_color(lv.color_hex(0x000000))
    container_sty.set_pad_gap(0)
    
    item_sty = lv.style_t()
    item_sty.init()
    item_sty.set_size(97, 78)
    item_sty.set_bg_color(lv.color_hex(0x000000))
    item_sty.set_bg_opa(0)
    item_sty.set_border_width(2)
    item_sty.set_border_color(lv.color_hex(0xFFFFFF))
    item_sty.set_border_opa(0)
    item_sty.set_outline_width(0)
    item_sty.set_radius(12)
    item_sty.set_pad_all(0)
    item_sty.set_pad_top(0)
    item_sty.set_margin_bottom(12)
    
    item_active_sty = lv.style_t()
    item_active_sty.init()
    item_active_sty.set_border_opa(255)
    
    item_clicked_sty = lv.style_t()
    item_clicked_sty.init()
    item_clicked_sty.set_bg_opa(100)
    
    
    container = lv.obj()
    container.add_style(obj_sty, lv.PART.MAIN)
    container.add_style(container_sty, lv.PART.MAIN)
    container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    
    gui = CANVAS(container)
    gui.clear()

    for item in INDEX_PAGE:
        x = item.get('x')
        y = item.get('y')
        item_obj = lv.obj(container)
        item_obj.set_pos(x - 2, y - 2)
        item_obj.add_style(item_sty, lv.PART.MAIN)
        item_obj.add_style(item_active_sty, lv.STATE.FOCUSED)
        item_obj.add_style(item_clicked_sty, lv.STATE.PRESSED)
        item_obj.set_scroll_dir(lv.DIR.NONE)
        item_obj.add_event_cb(item_clicked_cb, lv.EVENT.CLICKED, {'page': item.get('page') })
        lv_group.add_obj(item_obj)
        
        gui.draw_img(x, y - 2, '/ui/assets/' + item.get('icon') + '.png', 93, 74)
    
    gui.update()
    
    # lv.screen_load(container)

    set_key_config({})
        

def destroy():
    global container
    container.clean()
    container = None