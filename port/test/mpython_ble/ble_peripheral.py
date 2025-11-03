from mpython_ble.gatts import Profile
from mpython_ble.services import Service
from mpython_ble.application import Peripheral
from mpython_ble import UUID
from mpython_ble.characteristics import Characteristic
import struct
import binascii
import time
from mpython import *

def _ble_peripheral_connection_callback(_1, _2, _3):
    pass

def _ble_peripheral_write_callback(_1, _2, _3):
    pass

def on_button_a_pressed(_):
    global _data, _attr_handle, _addr, _addr_type, _conn_handle
    _ble_peripheral.attrubute_write(_c1.value_handle, struct.pack("<i", int(light.read())), notify=True)

button_a.event_pressed = on_button_a_pressed

def on_button_b_pressed(_):
    global _data, _attr_handle, _addr, _addr_type, _conn_handle
    _ble_peripheral.disconnect()
    print('MAC地址：' + str(binascii.hexlify(_ble_peripheral.mac).decode('UTF-8','ignore')))

button_b.event_pressed = on_button_b_pressed

def _ble_peripheral_connection_callback(_conn_handle, _addr_type, _addr):
    _addr = binascii.hexlify(_addr).decode('UTF-8','ignore')
    print('已连接到：' + str('主机：' + str(_addr)))

def _ble_peripheral_write_callback(_conn_handle, _attr_handle, _data):
    _data = binascii.hexlify(_data)
    print(_data)
# 按A键改写值并通知主机，按B键断开连接。
_ble_service = Service(UUID(0x181A))
if True:
    _c1 = Characteristic(UUID(0x2A6E), properties='rwn')
    _ble_service.add_characteristics(_c1)

_ble_profile = Profile()
_ble_profile.add_services(_ble_service)

_ble_peripheral = Peripheral(name=bytes('mpy_ble', 'utf-8'), profile=_ble_profile)
_ble_peripheral.connection_callback(_ble_peripheral_connection_callback)
_ble_peripheral.write_callback(_ble_peripheral_write_callback)
_ble_peripheral.advertise(True)
_ble_peripheral.attrubute_write(_c1.value_handle, struct.pack('<L', 0), notify=False)
print('等待主机连接 ...')
print('蓝牙名称：mpy_ble')
# print('MAC：' + str(binascii.hexlify(_ble_peripheral.mac).decode('UTF-8','ignore')))

while True:
    print('值：' + str(struct.unpack("<i", _ble_peripheral.attrubute_read(_c1.value_handle))[0]))
    time.sleep(2)
