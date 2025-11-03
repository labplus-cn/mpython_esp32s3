# # 1、超声波
# 11、超声波
# 说明：打印超声波距离,要求测量数据稳定、准确，测量范围为0-200mm， 精度：正负5mm

from hcsr04 import HCSR04
from mpython import *
import time

hcsr04 = HCSR04(trigger_pin=Pin.P25, echo_pin=Pin.P24)
while True:
    print(hcsr04.distance_mm())
    time.sleep(1)
    
# # 2、A B按键
# 说明：按A键，终端打印A，B键，打印B
from mpython import *

def on_button_a_pressed(_):
    print('A')

button_a.event_pressed = on_button_a_pressed

def on_button_b_pressed(_):
    print('B')

button_b.event_pressed = on_button_b_pressed

# # 3、温湿度
# 显示温度值
from mpython import *

from bluebit import SHT20

import time

sht20 = SHT20()
while True:
    print(sht20.temperature())
    print(sht20.humidity())
    time.sleep_ms(1000)

# # 4、数字光线
# 显示环境光线值
from mpython import *
import time

while True:
    print(light.read())
    time.sleep_ms(100)
 
# # 5、声音触发   
# 说明：打印声音采样值
from mpython import *
import time

while True:
    print(sound.read())
    time.sleep_ms(100)

# #6、RFID2 
# 打印读到的卡号
from mpython import *
import time
from mfrc import *

rfid2 = Rfid(i2c = i2c, i2c_addr = 47)

while True:
    print(rfid2.get_serial_num())
    time.sleep(1)
    
# #6、RFID1 
# 打印读到的卡号
from mpython import *
import time
from mfrc import *

rfid1 = Rfid(i2c = i2c, i2c_addr = 43)

while True:
    print(rfid1.get_serial_num())
    time.sleep(1)

# #8、蜂鸣器
from mpython import *
import music
music.play(music.DADADADUM, pin=Pin.P12, wait=False, loop=False)

# # 9、RGB
# 显示白灯
from mpython import *

import neopixel

my_rgb = neopixel.NeoPixel(Pin(Pin.P7), n=1, bpp=3, timing=1)
my_rgb.fill( (100, 100, 100) )
my_rgb.write()

# #10、舵机
from mpython import *
from servo import Servo

servo_0 = Servo(23, min_us=500, max_us=2500, actuation_range=180)
while True:
    servo_0.write_angle(180)
    time.sleep(1)
    servo_0.write_angle(0)
    time.sleep(1)

# # 11、红外探测
# 两个红外探测的实例分别为ir1 ir2

from mpython import *
while True:
    print(ir1.read())
    print(ir2.read())
    time.sleep_ms(1000)
    
# # 12、电机
# 1为拓展接口电机，需要外接电机
# 2为板载风扇
from mpython import ledong_shield
ledong_shield.set_motor(2, 60)
ledong_shield.set_motor(1, 60)

# # 13、录音
from mpython import *
import audio

audio.record('2.wav', 5, 16, 2, 16000)
time.sleep(6)
audio.play('2.wav')



# 13 msa311 三軸
from mpython import *
offset_x = 0 
offset_y = 0
offset_z = 0

accelerometer.auto_calibrate() #自動校準
accelerometer.set_nvs_offset(offset_x,offset_y,offset_z) #手動校準
accelerometer.set_g_range(g_range=G_RANGE_2G) #G_RANGE_2G G_RANGE_4G G_RANGE_8G G_RANGE_16G


def cb1():
    print('敲擊')

def cb2():
    print('方向检测')
    
def cb3():
    print('活動')

accelerometer.configure_tap_detection(callback=cb1)
accelerometer.configure_orientation_detection(callback=cb2)
accelerometer.configure_active_detection(callback=cb3)

while True:
    print(accelerometer.read_accel())
    print(accelerometer.get_x())
    print(accelerometer.get_y())
    print(accelerometer.get_z())
    time.sleep(1)
    
# 14 接口
# 说明：接口0-3输出高低电平，可接一个LED灯显示结果。
# IIC接口用一个IIC模块测试，使用i2c.scan()测试，能扫到模块地址
from mpython import *

p0 = MPythonPin(0, PinMode.OUT)
p1 = MPythonPin(1, PinMode.OUT)
p2 = MPythonPin(2, PinMode.OUT)
p3 = MPythonPin(3, PinMode.OUT)
while True:
    p0.write_digital(0)
    p1.write_digital(0)
    p2.write_digital(0)
    p3.write_digital(0)
    time.sleep(1)
    p0.write_digital(1)
    p1.write_digital(1)
    p2.write_digital(1)
    p3.write_digital(1)
    time.sleep(1)
    
# 15 屏幕显示
# 说明：屏幕显示红色、绿色、蓝色
import time
import lcd 
while True:
    lcd.draw_color(lcd.RED)
    time.sleep(1)
    lcd.draw_color(lcd.GREEN)
    time.sleep(1)
    lcd.draw_color(lcd.BLUE)
    time.sleep(1)
    