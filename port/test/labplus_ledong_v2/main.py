# # # 1、A B按键
# # 说明：按A键，终端打印A，B键，打印B
# # from mpython import *

# # def on_button_a_pressed(_):
# #     print('A')

# # button_a.event_pressed = on_button_a_pressed

# # def on_button_b_pressed(_):
# #     print('B')

# # button_b.event_pressed = on_button_b_pressed

# # # # 2、数字光线
# # # 显示环境光线值
# # from mpython import *
# # import time

# # while True:
# #     print(light.read())
# #     time.sleep_ms(100)
    
# # # 3、6轴
# # from mpython import *

# # import time
# # while True:
# #     print(accelerometer.get_x())
# #     print(accelerometer.get_y())
# #     print(accelerometer.get_z())
# #     print('-----------------------------------')
# #     time.sleep(1)
 
# # # # 4、磁力计   
# # from mpython import *

# # import time
# # while True:
# #     print(magnetic.get_x())
# #     print(magnetic.get_y())
# #     print(magnetic.get_z())
# #     print('-----------------------------------')
# #     time.sleep(1)

# # # 5、声音触发器
# # 说明：打印声音采样值

# # from mpython import *
# # import time

# # while True:
# #     print(sound.read())
# #     time.sleep_ms(50)
    
# # # # 6、触摸板
# # # 说明：触摸板按下后，终端打印对应字母

# # from mpython import *

# # def on_touchpad_p_pressed(val):
# #     if val != 1: return
# #     print('p')

# # touchpad_p.set_event_cb(on_touchpad_p_pressed)

# # def on_touchpad_h_pressed(val):
# #     if val != 1: return
# #     print('h')

# # touchpad_h.set_event_cb(on_touchpad_h_pressed)

# # def on_touchpad_y_pressed(val):
# #     if val != 1: return
# #     print('y')

# # touchpad_y.set_event_cb(on_touchpad_y_pressed)

# # def on_touchpad_o_pressed(val):
# #     if val != 1: return
# #     print('o')

# # touchpad_o.set_event_cb(on_touchpad_o_pressed)

# # def on_touchpad_t_pressed(val):
# #     if val != 1: return
# #     print('t')

# # touchpad_t.set_event_cb(on_touchpad_t_pressed)

# # def on_touchpad_n_pressed(val):
# #     if val != 1: return
# #     print('n')

# # touchpad_n.set_event_cb(on_touchpad_n_pressed)

# # # 7、摄像头
# # 说明：显示摄像头画面

# # from mpython import *
# # import AIcamera

# # isDetect = False

# # def cb(_):
# #     global isDetect
# #     isDetect = True

# # AIcamera.init(AIcamera.CODE_SCANNER,cb)

# # # # 8、蜂鸣器
# # from mpython import *
# # import music
# # music.play(music.DADADADUM, pin=Pin.P12, wait=False, loop=False)

# # #  9、RGB
# # 显示白灯
# # from mpython import *

# # import neopixel

# # my_rgb = neopixel.NeoPixel(Pin(Pin.P7), n=3, bpp=3, timing=1)
# # my_rgb.fill( (20, 20, 20) )
# # my_rgb.write()

# # # # 10、录音
# # from mpython import *
# # import audio

# # audio.record('2.wav', 5)
# # audio.play('2.wav')

# # # 11、电机
# # 1为拓展接口电机，需要外接电机
# # 2为板载风扇
# from mpython import ledong_shield
# ledong_shield.set_motor(2, 100)
# ledong_shield.set_motor(1, 100)

# import music

# music.play(music.DADADADUM, pin=Pin.P12, wait=False, loop=True)
    

# # # 12、屏幕显示
# # 说明：屏幕显示红色、绿色、蓝色
# # import time
# # import lcd 
# # while True:
# #     lcd.draw_color(lcd.RED)
# #     time.sleep(1)
# #     lcd.draw_color(lcd.GREEN)
# #     time.sleep(1)
# #     lcd.draw_color(lcd.BLUE)
# #     time.sleep(1)

    
# # 14 接口
# # 说明：接口0-3输出高低电平，可接一个LED灯显示结果。
# # IIC接口用一个IIC模块测试，使用i2c.scan()测试，能扫到模块地址
# # from mpython import *

# # # p0 = MPythonPin(0, PinMode.OUT)
# # # p1 = MPythonPin(1, PinMode.OUT)
# # # p2 = MPythonPin(2, PinMode.OUT)
# # # p3 = MPythonPin(3, PinMode.OUT)
# # # p4 = MPythonPin(4, PinMode.OUT)
# # # p6 = MPythonPin(6, PinMode.OUT)
# # # p8 = MPythonPin(8, PinMode.OUT)
# # p9 = MPythonPin(9, PinMode.OUT)
# # while True:
# #     # p0.write_digital(0)
# #     # p1.write_digital(0)
# #     # p2.write_digital(0)
# #     # p3.write_digital(0)
# #     # p4.write_digital(0)
# #     # p6.write_digital(0)
# #     # p8.write_digital(0)
# #     p9.write_digital(0)
# #     time.sleep(1)
# #     # p0.write_digital(1)
# #     # p1.write_digital(1)
# #     # p2.write_digital(1)
# #     # p3.write_digital(1)
# #     # p4.write_digital(1)
# #     # p6.write_digital(1)
# #     # p8.write_digital(1)
# #     p9.write_digital(1)
# #     time.sleep(1)

# # # 15 超声波测试IIC接口
# # from mpython import *
# # from bluebit import *

# # import time

# # ultrasonic = Ultrasonic()
# # while True:
# #     print(ultrasonic.distance())
# #     time.sleep(1)
    
# # # 16 最大功耗测试
# # 说明：测试最大功耗，开wifi，开蜂鸣器，开电机，接4.0AI摄像头
# # 测试结果：15：26-16：46，1小时20分钟，功耗1.2W

# # from mpython import *
# # import network

# # my_wifi = wifi()
# # my_wifi.connectWiFi("office", "wearemaker")

# # from mpython import ledong_shield
# # ledong_shield.set_motor(2, 100)
# # ledong_shield.set_motor(1, 100)

# # import music
# # music.play(music.DADADADUM, pin=Pin.P12, wait=False, loop=True)
    
    
    
    
# # 新力传感器测试代码
# # from bluebit import Forece

# # forece = Forece()  # 初始化力传感器，接口I2C


# # while True:
# #     sensor_values = forece.read() # 读取传感器数据
# #     print("力:", sensor_values[0])
# #     print("克:", sensor_values[1])
# #     print('-'*10)
# #     time.sleep(1)

# # 摄像头数据抓取
# # 摄像头模块增加get_jpg() api用于抓取摄像头图像，返回jpg格式数据，
# # 数据可保存到文件系统或上传到网络。
# from mpython import *
# import sensor

# need_save = False
# n = 0

# def on_button_a_pressed(_):
#     global need_save, n
#     need_save = True
#     n += 1
#     if(n > 10):
#         n = 10

# button_a.event_pressed = on_button_a_pressed

# sensor.reset()
# # 按A键抓取摄像头数据保存为jpg文件
# while True:
#     sensor.snapshot()
#     if need_save:
#         f = open(f'{n}.jpg', 'wb')
#         f.write(sensor.get_jpg())
#         f.close()
#         need_save = False
#     sensor.free_fb() # 此行代码不能省，要释放缓存
#     time.sleep_ms(40)


# from mpython import *
# from mpython_ble.application import BLEUART
# import ubinascii
# import machine
# import time

# _ble_uart = BLEUART(name=bytes('mpy_uart', 'utf-8'), role=BLEUART.MASTER)

# def on_button_a_pressed(_):
#     global _ble_uart
#     if _ble_uart and _ble_uart.is_connected():
#         _ble_uart.write(bytes('abc', 'utf-8'))

# button_a.event_pressed = on_button_a_pressed

# def _ble_uart_irq():
#     global _ble_uart
#     _received_data = bytes(_ble_uart.read())
#     print('recieve data')
#     print((_received_data).decode('UTF-8','ignore'))
    
# _ble_uart.irq(_ble_uart_irq)

# while True:
#     if _ble_uart and _ble_uart.is_connected():
#         print('is connect')
#     else:
#         machine.reset()
#     time.sleep(1)

# import ubluetooth
# from micropython import const
# import time

# # BLE常量定义
# _IRQ_CENTRAL_CONNECT = const(1)
# _IRQ_CENTRAL_DISCONNECT = const(2)
# _IRQ_GATTC_SERVICE_RESULT = const(3)
# _IRQ_GATTC_SERVICE_DONE = const(4)
# _IRQ_GATTC_CHARACTERISTIC_RESULT = const(5)
# _IRQ_GATTC_CHARACTERISTIC_DONE = const(6)
# _IRQ_GATTC_READ_RESULT = const(7)
# _IRQ_GATTC_READ_DONE = const(8)
# _IRQ_GATTC_WRITE_DONE = const(9)
# _IRQ_GATTC_NOTIFY = const(10)

# _UART_UUID = ubluetooth.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
# _UART_TX = (ubluetooth.UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E'), ubluetooth.FLAG_READ | ubluetooth.FLAG_NOTIFY,)
# _UART_RX = (ubluetooth.UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E'), ubluetooth.FLAG_WRITE,)
# _UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX,),)

# _ADV_NAME = 'mpy_uart'  # 要连接的外设名称

# class BLECentral:
#     def __init__(self, ble):
#         self.ble = ble
#         self.ble.active(True)
#         self.ble.irq(self._irq)
        
#         self.conn_handle = None
#         self.rx_handle = None
#         self.tx_handle = None
        
#         self.scanning = False
#         self.services_discovered = False

#     def _irq(self, event, data):
#         # 跟踪连接
#         if event == _IRQ_CENTRAL_CONNECT:
#             conn_handle, _, _ = data
#             self.conn_handle = conn_handle
#             print('已连接')

#         # 跟踪断开连接
#         elif event == _IRQ_CENTRAL_DISCONNECT:
#             conn_handle, _, _ = data
#             self.conn_handle = None
#             self.rx_handle = None
#             self.tx_handle = None
#             self.services_discovered = False
#             print('已断开连接')
#             # 尝试重新连接
#             self.start_scan()

#         # 发现服务
#         elif event == _IRQ_GATTC_SERVICE_RESULT:
#             conn_handle, start_handle, end_handle, uuid = data
#             if conn_handle == self.conn_handle and uuid == _UART_UUID:
#                 self.ble.gattc_discover_characteristics(conn_handle, start_handle, end_handle)

#         # 服务发现完成
#         elif event == _IRQ_GATTC_SERVICE_DONE:
#             conn_handle, status = data
#             if status != 0:
#                 print('服务发现失败')

#         # 发现特征
#         elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
#             conn_handle, def_handle, value_handle, properties, uuid = data
#             if conn_handle == self.conn_handle and uuid == _UART_TX[0]:
#                 self.tx_handle = value_handle
#             elif conn_handle == self.conn_handle and uuid == _UART_RX[0]:
#                 self.rx_handle = value_handle

#         # 特征发现完成
#         elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
#             conn_handle, status = data
#             if status == 0:
#                 self.services_discovered = True
#                 print('服务和特征发现完成')
#             else:
#                 print('特征发现失败')

#         # 读取结果
#         elif event == _IRQ_GATTC_READ_RESULT:
#             conn_handle, value_handle, char_data = data
#             print('读取到数据:', bytes(char_data))

#         # 读取完成
#         elif event == _IRQ_GATTC_READ_DONE:
#             conn_handle, value_handle, status = data
#             if status != 0:
#                 print('读取失败')

#         # 写入完成
#         elif event == _IRQ_GATTC_WRITE_DONE:
#             conn_handle, value_handle, status = data
#             if status == 0:
#                 print('数据写入成功')
#             else:
#                 print('数据写入失败')

#         # 收到通知
#         elif event == _IRQ_GATTC_NOTIFY:
#             conn_handle, value_handle, notify_data = data
#             print('收到通知:', bytes(notify_data))

#     # 开始扫描设备
#     def start_scan(self):
#         self.scanning = True
#         self.ble.gap_scan(2000, 30000, 30000)  # 扫描2秒
#         print('开始扫描设备...')

#     # 停止扫描
#     def stop_scan(self):
#         self.ble.gap_scan(None)
#         self.scanning = False

#     # 连接到指定地址的设备
#     def connect(self, addr_type, addr):
#         if self.conn_handle is None:
#             self.ble.gap_connect(addr_type, addr)
#             print('尝试连接到设备')

#     # 断开连接
#     def disconnect(self):
#         if self.conn_handle is not None:
#             self.ble.gap_disconnect(self.conn_handle)
#             self.conn_handle = None
#             print('断开连接')

#     # 发现服务
#     def discover_services(self):
#         if self.conn_handle is not None:
#             self.ble.gattc_discover_services(self.conn_handle)
#             print('开始发现服务')

#     # 读取特征值
#     def read(self):
#         if self.conn_handle is not None and self.tx_handle is not None:
#             self.ble.gattc_read(self.conn_handle, self.tx_handle)
#             print('读取数据中...')

#     # 写入数据
#     def write(self, data):
#         if self.conn_handle is not None and self.rx_handle is not None:
#             self.ble.gattc_write(self.conn_handle, self.rx_handle, data)
#             print('发送数据:', data)

# # 主程序
# def main():
#     ble = ubluetooth.BLE()
#     central = BLECentral(ble)
    
#     central.start_scan()
    
#     while True:
#         if central.scanning:
#             # 检查扫描结果
#             adv_report = ble.gap_scan_result()
#             if adv_report:
#                 addr_type, addr, adv_type, rssi, adv_data = adv_report
                
#                 # 解析广播数据中的名称
#                 name = None
#                 i = 0
#                 while i + 1 < len(adv_data):
#                     if adv_data[i+1] == 0x09:  # 设备名称
#                         name = bytes(adv_data[i+2:i+2+adv_data[i]]).decode()
#                         break
#                     i += 1 + adv_data[i]
                
#                 # 如果找到目标设备，停止扫描并连接
#                 if name == _ADV_NAME:
#                     central.stop_scan()
#                     print(f'找到设备: {name}, 地址: {addr}')
#                     central.connect(addr_type, addr)
#         elif central.conn_handle is not None and not central.services_discovered:
#             # 发现服务
#             central.discover_services()
#         elif central.services_discovered:
#             # 发送数据并读取响应
#             central.write(b'Hello from Central!')
#             time.sleep(2)
#             central.read()
#             time.sleep(3)
        
#         time.sleep(0.1)

# if __name__ == '__main__':
#     main()



###################################################################################
# from mpython_ble.gatts import Profile

# from mpython_ble.services import Service

# from mpython_ble.application import Peripheral

# def _ble_peripheral_connection_callback(_1, _2, _3):pass
# def _ble_peripheral_write_callback(_1, _2, _3):pass

# from mpython_ble import UUID

# from mpython_ble.characteristics import Characteristic

# import struct

# import binascii

# import time

# from mpython import *

# def on_button_a_pressed(_):
#     _ble_peripheral.attrubute_write(_c1.value_handle, struct.pack("<i", int(light.read())), notify=True)

# button_a.event_pressed = on_button_a_pressed

# def on_button_b_pressed(_):
#     _ble_peripheral.disconnect()

# button_b.event_pressed = on_button_b_pressed

# def _ble_peripheral_write_callback(_conn_handle, _attr_handle, _data):
#     _data = binascii.hexlify(_data)
#     print(_data)

# def _ble_peripheral_connection_callback(_conn_handle, _addr_type, _addr):
#     _addr = binascii.hexlify(_addr).decode('UTF-8','ignore')
#     print(_addr)
# # 按A键改写值并通知主机，按B键断开连接。
# _ble_service = Service(UUID(0x181A))
# if True:
#     _c1 = Characteristic(UUID(0x2A6E), properties='rwn')
#     _ble_service.add_characteristics(_c1)

# _ble_profile = Profile()
# _ble_profile.add_services(_ble_service)

# _ble_peripheral = Peripheral(name=bytes('mpy_ble', 'utf-8'), profile=_ble_profile)
# _ble_peripheral.connection_callback(_ble_peripheral_connection_callback)
# _ble_peripheral.write_callback(_ble_peripheral_write_callback)
# _ble_peripheral.advertise(True)
# _ble_peripheral.attrubute_write(_c1.value_handle, struct.pack('<L', 0), notify=False)
# # print(binascii.hexlify(_ble_peripheral.mac).decode('UTF-8','ignore'))
# while True:
#     print(struct.unpack("<i", _ble_peripheral.attrubute_read(_c1.value_handle))[0])
#     time.sleep(2)




from mpython_ble.application import Centeral

def _ble_centeral_notify_callback(_1, _2):pass

import time

from mpython_ble import UUID

from mpython import *

import struct

def on_button_a_pressed(_):
    global v
    v = light.read()
    _ble_centeral.characteristic_write(_c1.value_handle, struct.pack("<i", int(v)))
    print(v)

button_a.event_pressed = on_button_a_pressed

def _ble_get_characteristic(_sid, _cid):
    if _ble_profile is None: return None
    for service in _ble_profile:
        if service.uuid == _sid:
            for characteristics in service:
                if characteristics.uuid == _cid:
                    return characteristics
    return None

def _ble_centeral_notify_callback(_value_handle, _notify_data):
    global v
    print(struct.unpack("<i", _notify_data)[0])
    
_ble_centeral = Centeral(bytes('mpy_centeral', 'utf-8'))
print('name: mpy_centeral')
while True:
    _ble_profile = _ble_centeral.connect(name=bytes('mpy_ble', 'utf-8'))
    if _ble_centeral:
        _ble_centeral.notify_callback(_ble_centeral_notify_callback)
        break
    time.sleep(2)
if _ble_centeral.is_connected():
    _c1 = _ble_get_characteristic(UUID(0x181A), UUID(0x2A6E))
    print(_ble_centeral.connected_info()[2].decode('UTF-8','ignore'))


