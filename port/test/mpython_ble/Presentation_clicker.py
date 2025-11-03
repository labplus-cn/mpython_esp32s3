# 蓝牙翻页笔示例
# 运行测试代码，乐动掌控模拟为一个翻页笔设备
# A B键：上下翻页
# P键：阅读  T键：退出
# N键：全屏  H键：关闭

from mpython import *
from mpython_ble.application import HID
from mpython_ble.hidcode import KeyboardCode

def _ble_hid_connect_callback(_1, _2, _3):pass

def on_button_a_pressed(_):
    global v
    _ble_hid.keyboard_send(KeyboardCode.PAGE_UP)

button_a.event_pressed = on_button_a_pressed

def on_button_b_pressed(_):
    global v
    _ble_hid.keyboard_send(KeyboardCode.PAGE_DOWN)

button_b.event_pressed = on_button_b_pressed

def on_touchpad_p_pressed(val):
    global v
    if val != 1: return
    _ble_hid.keyboard_send(KeyboardCode.CONTROL, KeyboardCode.H)

touchpad_p.set_event_cb(on_touchpad_p_pressed)

def on_touchpad_t_pressed(val):
    global v
    if val != 1: return
    _ble_hid.keyboard_send(KeyboardCode.ESCAPE)

touchpad_t.set_event_cb(on_touchpad_t_pressed)

def on_touchpad_n_pressed(val):
    global v
    if val != 1: return
    _ble_hid.keyboard_send(KeyboardCode.CONTROL, KeyboardCode.L)

touchpad_n.set_event_cb(on_touchpad_n_pressed)

def on_touchpad_h_pressed(val):
    global v
    if val != 1: return
    _ble_hid.keyboard_send(KeyboardCode.ALT, KeyboardCode.F4)

touchpad_h.set_event_cb(on_touchpad_h_pressed)

_ble_hid = HID(name=bytes('mpy_hid', 'utf-8'), battery_level=100)
_ble_hid.hid_device.connection_callback(_ble_hid_connect_callback)
_ble_hid.advertise(True)