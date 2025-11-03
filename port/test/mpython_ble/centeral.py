from mpython_ble.application import Centeral
from mpython_ble import UUID
from mpython import *
import time
import struct

def _ble_centeral_notify_callback(_1, _2):
    pass

def on_button_a_pressed(_):
    _ble_centeral.characteristic_write(_c1.value_handle, struct.pack("<i", int(light.read())))
    print(f'light: {light.read()} is send.')


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
    print(str(struct.unpack("<i", _notify_data)[0]))
    
_ble_centeral = Centeral(bytes('mpy_centeral', 'utf-8'))
print("centeral name mpy_centeral")
_ble_centeral.notify_callback(_ble_centeral_notify_callback)

_ble_profile = _ble_centeral.connect(name=bytes('mpy_ble', 'utf-8'))
while True: 
    if _ble_centeral.is_connected():
        _c1 = _ble_get_characteristic(UUID(0x181A), UUID(0x2A6E))
        print("Is connect! peripheral name:" + str(_ble_centeral.connected_info()[2].decode('UTF-8','ignore')))
        break
    time.sleep(1)
