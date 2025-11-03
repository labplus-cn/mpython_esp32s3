import time, gc
import lvgl as lv
import lcd
import lv_displayer
from mpython import button_a, button_b

from lv_utils import event_loop

ASSETS_LIST = [
    'gradienter', 'clock', 'voice', 'light', 'sound', 'game'
]
assets_src = {}


lv_group = None
key_timer = None
key_is_end = None
key_pressed = None
button_a_key_cb = None
button_b_key_cb = None

def ui_detect_key():
    global key_pressed, key_is_end
    if key_is_end is None:
        if button_a.is_pressed():   #按键被按下
            time.sleep_ms(50) #消除抖动
            if button_a.is_pressed(): #确认按键被按下
                key_is_end = 'btn_a'
                if button_a_key_cb:
                    button_a_key_cb()
                else:
                    key_pressed = lv.KEY.ENTER

        elif button_b.is_pressed():   #按键被按下
            time.sleep_ms(50) #消除抖动
            if button_b.is_pressed(): #确认按键被按下
                key_is_end = 'btn_b'
                if button_b_key_cb:
                    button_b_key_cb()
                else:
                    key_pressed = lv.KEY.NEXT
                
    elif key_is_end and (not button_a.is_pressed()) and (not button_b.is_pressed()):
        key_is_end = None


# 输入设备按下响应回调
def my_input_read(indev_drv, data):
    global key_pressed
    ui_detect_key()
    if key_pressed is not None:
        data.key = key_pressed
        data.state = lv.INDEV_STATE.PRESSED
        key_pressed = None  # 清除按键状态
    else:
        data.state = lv.INDEV_STATE.RELEASED
    return False  # 表示没有更多数据

# 创建输入设备组并绑定
def create_group():
    global lv_group, key_timer
    lv_group = lv.group_create()
    # 创建输入设备
    indev = lv.indev_create()
    indev.set_type(lv.INDEV_TYPE.KEYPAD)  # 设为键盘输入
    indev.set_read_cb(my_input_read)      # 绑定回调

    # 绑定到 lv_group
    indev.set_group(lv_group)

def set_key_config(fns = {}):
    global button_a_key_cb, button_b_key_cb
    button_a_key_cb = fns.get('button_a_key_cb')
    button_b_key_cb = fns.get('button_b_key_cb')
    group_wrap = fns.get('group_wrap')
    lv_group.set_wrap(group_wrap if group_wrap is not None else True)

def import_module(name):
    try:
        module = __import__(name)
        return module
    except ImportError as e:
        print(f"Module {name} not found: {e}")
        return None

def load_assets():
    global assets_src
    for item in ASSETS_LIST:
        data = None
        with open('/ui/assets/' + item + '.png','rb') as f:
            data = f.read()
        img_src = lv.image_dsc_t({
            'data_size': len(data),
            'data': data
        })
        assets_src[item.replace("-", "_")] = img_src

def get_img_src(name):
    return assets_src[name.replace("-", "_")]

def change_route(url, destroy=None):
    try:
        if destroy is not None: 
            lv_group.remove_all_objs()
            destroy()  # 删除当前页面
            gc.collect()
        page_obj = import_module(url)
        page_obj.init()
        if hasattr(page_obj, 'container'):
            lv.screen_load(page_obj.container)
    except Exception as e:
        print(f"path {url} not found: {e}")