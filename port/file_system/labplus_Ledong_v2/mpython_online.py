# -*- coding:utf-8 -*-
# @Description : A transfer protocol between 'Ledong 2.0' board and Python on PC

from machine import I2C, PWM, Pin, ADC, Timer
from mpython import *
from servo import Servo
import time
import music


'''
按钮(A B按键）   IO0/P5 IO46/P11
阻性器件    IO4/P3
光照传感器   IIC
6轴  IIC
磁力计 IIC
声音  IO6/P10
触摸按键    P Y T H O N
'''

def get_touchpad():
    val=0x00
    if touchpad_p.is_pressed():
        val=val|0x80
    else:
        val=val&0x7F
    if touchpad_y.is_pressed():
        val=val|0x40
    else:
        val=val&0xBF
    if touchpad_t.is_pressed():
        val=val|0x20
    else:
        val=val&0xDF
    if touchpad_h.is_pressed():
        val=val|0x10
    else:
        val=val&0xEF
    if touchpad_o.is_pressed():
        val=val|0x08
    else:
        val=val&0xF7
    if touchpad_n.is_pressed():
        val=val|0x04
    else:
        val=val&0xFB
    if button_a.is_pressed():
        val=val|0x02
    else:
        val=val&0xFD
    if button_b.is_pressed():
        val=val|0x01
    else:
        val=val&0xFE
    return val

import dht
dht11 = None
res_dict = {}
dht_ready = 0

def timer15_tick(_):
    global dht_ready, dht11
    try: 
        dht11.measure()
        dht_ready = 1
    except: pass

def DHT(pin):
    global dht11
    dht11 = dht.DHT11(Pin(pin))
    tim15 = Timer(15)
    tim15.init(period=1000, mode=Timer.PERIODIC, callback=timer15_tick)

def run_code(_code):
    if "DHT(" in _code:
        DHT(eval("Pin.P"+_code[4:-1]))
    else:
        try:
            eval("exec(\"" + _code + "\",globals())")
        except:
            print(_code)


_is_shaked = _is_thrown = False
_last_x = _last_y = _last_z = _count_shaked = _count_thrown = 0
_pind = {}
_pina = {}

def timer1_tick(_):
    global _is_shaked, _is_thrown, _last_x, _last_y, _last_z, _count_shaked, _count_thrown
    if _is_shaked:
        _count_shaked += 1
        if _count_shaked == 5: _count_shaked = 0
    if _is_thrown:
        _count_thrown += 1
        if _count_thrown == 10: _count_thrown = 0
    x=accelerometer.get_x(); y=accelerometer.get_y(); z=accelerometer.get_z()
    if _count_thrown == 0: _is_thrown = (x * x + y * y + z * z < 0.25)
    if _last_x == 0 and _last_y == 0 and _last_z == 0:
        _last_x = x; _last_y = y; _last_z = z; return
    diff_x = x - _last_x; diff_y = y - _last_y; diff_z = z - _last_z
    _last_x = x; _last_y = y; _last_z = z
    if _count_shaked > 0: return
    _is_shaked = (diff_x * diff_x + diff_y * diff_y + diff_z * diff_z > 1)
    
def timer2_tick(_):
    global _pind, _pina, res_dict, dht_ready
    res_dict["l"] = light.read()
    res_dict["s"] = sound.read()
    res_dict["x"] = float("%.4f" % accelerometer.get_x())
    res_dict["y"] = float("%.4f" % accelerometer.get_y())
    res_dict["z"] = float("%.4f" % accelerometer.get_z())
    res_dict["gx"] = float("%.4f" % gyroscope.get_x())
    res_dict["gy"] = float("%.4f" % gyroscope.get_y())
    res_dict["gz"] = float("%.4f" % gyroscope.get_z())
    res_dict["mx"] = float("%.4f" % magnetic.get_x())
    res_dict["my"] = float("%.4f" % magnetic.get_y())
    res_dict["mz"] = float("%.4f" % magnetic.get_z())
    res_dict["mf"] = float("%.4f" % magnetic.get_field_strength())
    res_dict["mh"] = float("%.4f" % magnetic.get_heading())
    res_dict["d"] = get_touchpad()
    res_dict["t"] = 2 if _is_thrown else 1 if _is_shaked else 0
    for i in _pind.keys():
        res_dict["d" + str(i)] = MPythonPin(i, PinMode.IN).read_digital()
        time.sleep_ms(20)
    for i in _pina.keys():
        res_dict["a" + str(i)] = MPythonPin(i, PinMode.ANALOG).read_analog()
        time.sleep_ms(20)
    if dht_ready == 1:
        res_dict["dhth"] = float("%.4f" % dht11.temperature())
        res_dict["dhtc"] = float("%.4f" % dht11.humidity())
        dht_ready = 0

    print(res_dict)

tim1 = Timer(1)
tim2 = Timer(2)

tim1.init(period=100, mode=Timer.PERIODIC, callback=timer1_tick)
tim2.init(period=200, mode=Timer.PERIODIC, callback=timer2_tick)

while True:
    run_code(input())
