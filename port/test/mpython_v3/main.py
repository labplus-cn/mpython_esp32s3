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

while True:
    print("hello")
  
# # ----------------------------------------------
# # 3、数字光线
# # 显示环境光线值
# from mpython import *
# import time

# while True:
#     print(light.read())
#     time.sleep(1)

# # ----------------------------------------------

    
# # ----------------------------------------------
# # '''
# # 6、声音触发器
# # 说明：打印声音采样值
# # '''
# from mpython import *
# import time

# while True:
#     print(sound.read())
#     time.sleep_ms(50)
    
# # ----------------------------------------------
# # 8、蜂鸣器
# from mpython import *
# import music
# music.play(music.DADADADUM, pin=Pin.P12, wait=False, loop=False)

# # ----------------------------------------------
# # 9、RGB
# # 显示白灯
# from mpython import *

# rgb.fill((int(255), int(255), int(255))) 
# rgb.write()



# # ----------------------------------------------
# # 16、音乐播放
# from mpython import *
# import audio

# my_wifi = wifi()
# my_wifi.connectWiFi("office", "wearemaker")

# audio.play('http://cdn.makeymonkey.com/test/test.mp3')
# time.sleep(10)
# audio.stop()

# # ----------------------------------------------
# # 17、录音
# from mpython import *
# import audio

# audio.record('2.wav', 5, 16, 1, 8000)
# audio.play('2.wav')

# # ----------------------------------------------
# # 18、噪声计
# # 说明：打印噪声计值，单位：dB
# # 城市5类环境噪声标准值如下：
# # 类别   昼间     夜间
# # 0类   50分贝   40分贝
# # 1类   55分贝   45分贝
# # 2类   60分贝   50分贝
# # 3类   65分贝   55分贝
# # 4类   70分贝   55分贝
# # 各类标准的适用区域：
# # 0类标准适用于疗养区、高级别墅区、高级宾馆区等特别需要安静的区域。位于城郊和乡村的这一类区域分别按严于0类标准5分贝执行。
# # 1类标准适用于以居住、文教机关为主的区域。乡村居住环境可参照执行该类标准。
# # 2类标准适用于居住、商业、工业混杂区。
# # 3类标准适用于工业区。
# # 4类标准适用于城市中的道路交通干线道路两侧区域，穿越城区的铁路主、次干线两侧区域的背景噪声（指不通过列车噪声的控制来达到目的而实测得的背景噪声）。

# # 噪声测量应用不要与录音应用同时使用，否则会导致录音数据异常。

# import time
# from mpython import *
# import audio

# while True:
#     print(audio.loudness())
#     time.sleep_ms(20)  


# # 18 屏幕显示
# # 说明：屏幕显示红色、绿色、蓝色
# import time
# import lcd 
# while True:
#     lcd.draw_color(lcd.RED)
#     time.sleep(1)
#     lcd.draw_color(lcd.GREEN)
#     time.sleep(1)
#     lcd.draw_color(lcd.BLUE)
#     time.sleep(1)
    
    
# # 接口，接拓展板测试
# # 说明：接口0-3输出高低电平，可接一个LED灯显示结果。
# # IIC接口用一个IIC模块测试，使用i2c.scan()测试，能扫到模块地址
# from mpython import *

# p0 = MPythonPin(0, PinMode.OUT)
# p1 = MPythonPin(1, PinMode.OUT)
# p2 = MPythonPin(2, PinMode.OUT)
# p3 = MPythonPin(3, PinMode.OUT)
# while True:
#     p0.write_digital(0)
#     p1.write_digital(0)
#     p2.write_digital(0)
#     p3.write_digital(0)
#     time.sleep(1)
#     p0.write_digital(1)
#     p1.write_digital(1)
#     p2.write_digital(1)
#     p3.write_digital(1)
#     time.sleep(1)

    