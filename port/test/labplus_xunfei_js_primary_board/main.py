# from mpython import *

# '''
# 1、按键功能测试
# 说明：按A键，终端打印A，B键，打印B
# '''

# button A
from mpython import *

def on_button_a_pressed(_):
    print('A')

button_a.event_pressed = on_button_a_pressed

# button B
def on_button_b_pressed(_):
    print('B')

button_b.event_pressed = on_button_b_pressed

# ----------------------------------------------
# 2、温湿度
# 显示温度值
from mpython import *
import time

while True:
    print(sht20.humidity())
    print(sht20.temperature())
    time.sleep(1)
    
# ----------------------------------------------
# 3、数字光线
# 显示环境光线值
from mpython import *
import time

while True:
    print(light.read())
    time.sleep(1)
    
# ----------------------------------------------
# 4、旋钮电位器
from mpython import *

while True:
    print(pot.read())
    time.sleep_ms(300)

# ----------------------------------------------

# 5、红外探测
# 探测距离约5cm,返回ADC采样值
from mpython import *

while True:
    print(ir1.read())
    print(ir2.read())
    time.sleep(1)
    
# ----------------------------------------------
# '''
# 6、声音触发器
# 说明：打印声音采样值
# '''
from mpython import *
import time

while True:
    print(sound.read())
    time.sleep_ms(50)
   
# ----------------------------------------------
# 7、RFID  
# 打印读到的卡号
from mpython import *
import time
from mfrc import *

rfid = Rfid(i2c = i2c, i2c_addr = 47)

while True:
    print(rfid.get_serial_num())
    time.sleep(1)
    
# ----------------------------------------------
# 8、蜂鸣器
from mpython import *
import music
music.play(music.DADADADUM, pin=Pin.P12, wait=False, loop=False)

# ----------------------------------------------
# 9、RGB
# 显示白灯
from mpython import *

rgb.fill((int(255), int(255), int(255))) 
rgb.write()


# ----------------------------------------------
# 10、编码电机
# 说明：编码电机正转、反转
from mpython import *
import time

while True:
    encoder_motor.move(-60,-60)
    time.sleep(2)
    encoder_motor.move(60,60)
    time.sleep(2)

# ----------------------------------------------
# 11、超声波
# 说明：打印超声波距离,要求测量数据稳定、准确，测量范围为0-200mm， 精度：正负5mm
from mpython import *

import time
while True:
    print(get_distance())
    time.sleep(1)
    
# ----------------------------------------------
# 12、电池电量
# 说明：打印电池电量
from mpython import *

while True:
    print(get_bat_level())
    time.sleep(1)
    
# ----------------------------------------------
# 13、循迹
# 说明：打印循迹传感器值,要求每个探头测量数据稳定、准确识别黑白色块
# get_raw_val()返回的是模拟采样值
from mpython  import *

l = Line_follow()

import time
while True:
    print(l.get_val())
    # print(l.get_raw_val())
    time.sleep(1)
    
# ----------------------------------------------
# 14、风扇、水泵
from mpython import *       
set_speed(1, 60)
set_speed(2, 60)   

# ----------------------------------------------
# 15、摄像头
'''
人脸、猫脸检测
'''
'''
可选参数：
    AIcamera.FACE_DETECTION      # 人脸检测
    AIcamera.FACE_RECOGNITION    # 人脸识别
    AIcamera.CAT_FACE_DETECTION  # 猫脸检测
    AIcamera.COLOR_DETECTION     # 颜色识别
    AIcamera.MOTION_DEECTION     # 运动检测
    AIcamera.CODE_SCANNER        # 二维码识别
'''
from mpython import *
import AIcamera

isDetect = False

def cb(_):
    global isDetect
    isDetect = True

AIcamera.init(AIcamera.CODE_SCANNER,cb)

while True:
    if isDetect:
        try:
            print(AIcamera.get_result()) 
        except Exception as e:
            print(e)
        isDetect = False  
    time.sleep_ms(100)
    
# AIcamera.init(AIcamera.FACE_DETECTION,cb)
 
#获取识别结果，检测到的人脸框选位置及关键点坐标（口左角，口右角，鼻，左眼，右眼）,数据结构：（{'box': (x1, y1, x2, y2）, 'keypoint': (a0, ... , a9)}, {'box': (x1, y1, x2, y2）, 'keypoint': (a0, ... , a9)}, ...)
# 用户可以利用识别结果做点别的。
# 清除识别标记


# ----------------------------------------------
# 16、音乐播放
from mpython import *
import audio

my_wifi = wifi()
my_wifi.connectWiFi("office", "wearemaker")

audio.play('http://cdn.makeymonkey.com/test/test.mp3')
time.sleep(10)
audio.stop()

# ----------------------------------------------
# 17、录音
from mpython import *
import audio

audio.record('2.wav', 5)
audio.play('2.wav')

# ----------------------------------------------
# 18、噪声计
# 说明：打印噪声计值，单位：dB
# 城市5类环境噪声标准值如下：
# 类别   昼间     夜间
# 0类   50分贝   40分贝
# 1类   55分贝   45分贝
# 2类   60分贝   50分贝
# 3类   65分贝   55分贝
# 4类   70分贝   55分贝
# 各类标准的适用区域：
# 0类标准适用于疗养区、高级别墅区、高级宾馆区等特别需要安静的区域。位于城郊和乡村的这一类区域分别按严于0类标准5分贝执行。
# 1类标准适用于以居住、文教机关为主的区域。乡村居住环境可参照执行该类标准。
# 2类标准适用于居住、商业、工业混杂区。
# 3类标准适用于工业区。
# 4类标准适用于城市中的道路交通干线道路两侧区域，穿越城区的铁路主、次干线两侧区域的背景噪声（指不通过列车噪声的控制来达到目的而实测得的背景噪声）。

# 噪声测量应用不要与录音应用同时使用，否则会导致录音数据异常。

import time
from mpython import *
import audio

while True:
    print(audio.loudness())
    time.sleep_ms(20)  


# 18 屏幕显示
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
    
# 19 舵机
# 说明：舵机0-120度切换
from mpython import *
from servo import Servo
import time
servo_22 = Servo(22, min_us=500, max_us=2500, actuation_range=180)
while True:
    servo_22.write_angle(0)
    time.sleep(2)
    servo_22.write_angle(120)
    time.sleep(2)
    
# 20 接口
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

# 21 超声波测试IIC接口
from mpython import *
from bluebit import *

import time

ultrasonic = Ultrasonic()
while True:
    print(ultrasonic.distance())
    time.sleep(1)