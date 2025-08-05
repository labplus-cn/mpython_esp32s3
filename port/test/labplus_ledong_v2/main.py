# # 1、A B按键
# 说明：按A键，终端打印A，B键，打印B
# from mpython import *

# def on_button_a_pressed(_):
#     print('A')

# button_a.event_pressed = on_button_a_pressed

# def on_button_b_pressed(_):
#     print('B')

# button_b.event_pressed = on_button_b_pressed

# # # 2、数字光线
# # 显示环境光线值
# from mpython import *
# import time

# while True:
#     print(light.read())
#     time.sleep_ms(100)
    
# # 3、6轴
# from mpython import *

# import time
# while True:
#     print(accelerometer.get_x())
#     print(accelerometer.get_y())
#     print(accelerometer.get_z())
#     print('-----------------------------------')
#     time.sleep(1)
 
# # # 4、磁力计   
# from mpython import *

# import time
# while True:
#     print(magnetic.get_x())
#     print(magnetic.get_y())
#     print(magnetic.get_z())
#     print('-----------------------------------')
#     time.sleep(1)

# # 5、声音触发器
# 说明：打印声音采样值

# from mpython import *
# import time

# while True:
#     print(sound.read())
#     time.sleep_ms(50)
    
# # # 6、触摸板
# # 说明：触摸板按下后，终端打印对应字母

# from mpython import *

# def on_touchpad_p_pressed(val):
#     if val != 1: return
#     print('p')

# touchpad_p.set_event_cb(on_touchpad_p_pressed)

# def on_touchpad_h_pressed(val):
#     if val != 1: return
#     print('h')

# touchpad_h.set_event_cb(on_touchpad_h_pressed)

# def on_touchpad_y_pressed(val):
#     if val != 1: return
#     print('y')

# touchpad_y.set_event_cb(on_touchpad_y_pressed)

# def on_touchpad_o_pressed(val):
#     if val != 1: return
#     print('o')

# touchpad_o.set_event_cb(on_touchpad_o_pressed)

# def on_touchpad_t_pressed(val):
#     if val != 1: return
#     print('t')

# touchpad_t.set_event_cb(on_touchpad_t_pressed)

# def on_touchpad_n_pressed(val):
#     if val != 1: return
#     print('n')

# touchpad_n.set_event_cb(on_touchpad_n_pressed)

# # 7、摄像头
# 说明：显示摄像头画面

# from mpython import *
# import AIcamera

# isDetect = False

# def cb(_):
#     global isDetect
#     isDetect = True

# AIcamera.init(AIcamera.CODE_SCANNER,cb)

# # # 8、蜂鸣器
# from mpython import *
# import music
# music.play(music.DADADADUM, pin=Pin.P12, wait=False, loop=False)

# #  9、RGB
# 显示白灯
# from mpython import *

# import neopixel

# my_rgb = neopixel.NeoPixel(Pin(Pin.P7), n=3, bpp=3, timing=1)
# my_rgb.fill( (20, 20, 20) )
# my_rgb.write()

# # # 10、录音
# from mpython import *
# import audio

# audio.record('2.wav', 5)
# audio.play('2.wav')

# # 11、电机
# 1为拓展接口电机，需要外接电机
# 2为板载风扇
from mpython import ledong_shield
ledong_shield.set_motor(2, 100)
ledong_shield.set_motor(1, 100)

import music

music.play(music.DADADADUM, pin=Pin.P12, wait=False, loop=True)
    

# # 12、屏幕显示
# 说明：屏幕显示红色、绿色、蓝色
# import time
# import lcd 
# while True:
#     lcd.draw_color(lcd.RED)
#     time.sleep(1)
#     lcd.draw_color(lcd.GREEN)
#     time.sleep(1)
#     lcd.draw_color(lcd.BLUE)
#     time.sleep(1)

    
# 14 接口
# 说明：接口0-3输出高低电平，可接一个LED灯显示结果。
# IIC接口用一个IIC模块测试，使用i2c.scan()测试，能扫到模块地址
# from mpython import *

# # p0 = MPythonPin(0, PinMode.OUT)
# # p1 = MPythonPin(1, PinMode.OUT)
# # p2 = MPythonPin(2, PinMode.OUT)
# # p3 = MPythonPin(3, PinMode.OUT)
# # p4 = MPythonPin(4, PinMode.OUT)
# # p6 = MPythonPin(6, PinMode.OUT)
# # p8 = MPythonPin(8, PinMode.OUT)
# p9 = MPythonPin(9, PinMode.OUT)
# while True:
#     # p0.write_digital(0)
#     # p1.write_digital(0)
#     # p2.write_digital(0)
#     # p3.write_digital(0)
#     # p4.write_digital(0)
#     # p6.write_digital(0)
#     # p8.write_digital(0)
#     p9.write_digital(0)
#     time.sleep(1)
#     # p0.write_digital(1)
#     # p1.write_digital(1)
#     # p2.write_digital(1)
#     # p3.write_digital(1)
#     # p4.write_digital(1)
#     # p6.write_digital(1)
#     # p8.write_digital(1)
#     p9.write_digital(1)
#     time.sleep(1)

# # 15 超声波测试IIC接口
# from mpython import *
# from bluebit import *

# import time

# ultrasonic = Ultrasonic()
# while True:
#     print(ultrasonic.distance())
#     time.sleep(1)
    
# # 16 最大功耗测试
# 说明：测试最大功耗，开wifi，开蜂鸣器，开电机，接4.0AI摄像头
# 测试结果：15：26-16：46，1小时20分钟，功耗1.2W

# from mpython import *
# import network

# my_wifi = wifi()
# my_wifi.connectWiFi("office", "wearemaker")

# from mpython import ledong_shield
# ledong_shield.set_motor(2, 100)
# ledong_shield.set_motor(1, 100)

# import music
# music.play(music.DADADADUM, pin=Pin.P12, wait=False, loop=True)
    