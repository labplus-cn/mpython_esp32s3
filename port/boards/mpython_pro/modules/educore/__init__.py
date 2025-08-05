print('educore init')

from ._educore import *
from ._smartcamera import EduSmartCamera
from ._ble import *


'''继承AI摄像头'''
class smartcamera(EduSmartCamera):
    def __init__(self, tx=16, rx=15):
        _tx = pins_esp32[tx]
        _rx = pins_esp32[rx]
        super().__init__(tx=_tx, rx=_rx)


# class smartcamera1956(Camera1956):
#     def __init__(self, tx=15, rx=16):
#         _tx = pins_esp32[tx]
#         _rx = pins_esp32[rx]
#         super().__init__(tx=_tx, rx=_rx)

# wifi
wifi = WiFi()

# OLED
oled = OLED()

# MQTT 
mqttclient = MqttClient()


# 网页版人工智能摄像头
webcamera = webcamera()

