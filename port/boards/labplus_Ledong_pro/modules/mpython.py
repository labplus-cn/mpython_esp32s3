# labplus mPython library
# MIT license; Copyright (c) 2018 labplus
# V1.0 Zhang KaiHua(apple_eat@126.com)

# mpython buildin periphers drivers

# history:
# V1.1 add oled draw function,add buzz.freq().  by tangliufeng
# V1.2 add servo/ui class,by tangliufeng

from machine import I2C, PWM, Pin, ADC, TouchPad
from ssd1106 import SSD1106_I2C
import esp, math, time, network
import ustruct, array
from neopixel import NeoPixel
# from esp import dht_readinto
from time import sleep_ms, sleep_us, sleep
import framebuf 
import calibrate_img
from micropython import schedule,const
from esp32 import NVS

i2c = I2C(0, scl=Pin(34), sda=Pin(35), freq=400000)

if '_print' not in dir(): _print = print

def print(_t, *args, sep=' ', end='\n'):
    _s = str(_t)[0:1]
    if u'\u4e00' <= _s <= u'\u9fff':
        _print(' ' + str(_t), *args, sep=sep, end=end)
    else:
        _print(_t, *args, sep=sep, end=end)

# my_wifi = wifi()
#多次尝试连接wifi
def try_connect_wifi(_wifi, _ssid, _pass, _times):
    if _times < 1: return False
    try:
        print("Try Connect WiFi ... {} Times".format(_times) )
        _wifi.connectWiFi(_ssid, _pass)
        if _wifi.sta.isconnected(): return True
        else:
            time.sleep(5)
            return try_connect_wifi(_wifi, _ssid, _pass, _times-1)
    except:
        time.sleep(5)
        return try_connect_wifi(_wifi, _ssid, _pass, _times-1)

class PinMode(object):
    IN = 1
    OUT = 2
    PWM = 3
    ANALOG = 4
    OUT_DRAIN = 5
# P4: light P5: A P10: sound P11: B P12: buzzer P21: RGB LED
#                   P0 P1 P2 P3 P4 P5 P6 P7 P8  P9 P10 P11 P12 P13 P14 P15 P16        P19  P20 P21    P23 P24 P25 P26 P27 P28
#                               *  *                *  *   *                          scl  sda *       P  Y   T   H   O   N
pins_remap_esp32 = (1, 2, 3, 4, 5, 0, 7, 8, 15, 16, 6, 46, 21, 17, 18, 48, 47, -1, -1, 34, 35, 33, -1, 9, 10, 11, 12, 13, 14)

class MPythonPin():
    def __init__(self, pin, mode=PinMode.IN, pull=None):
        if mode not in [PinMode.IN, PinMode.OUT, PinMode.PWM, PinMode.ANALOG, PinMode.OUT_DRAIN]:
            raise TypeError("mode must be 'IN, OUT, PWM, ANALOG,OUT_DRAIN'")
        if pin == 4:
            raise TypeError("P4 is used for internal light sensor")
        if pin == 10:
            raise TypeError("P10 is used for internalsound sensor")
        if pin == 5 or pin == 11:
            raise TypeError("P5 or P11 is used for internal A B key.")
        if pin == 21:
            raise TypeError("P21 is used for internal RGB LED.")
        if pin == 12:
            raise TypeError("P12 is used for internal buzzer.")
        try:
            self.id = pins_remap_esp32[pin]
        except IndexError:
            raise IndexError("Out of Pin range")
        if mode == PinMode.IN:
            if pin not in [0, 1, 2, 3, 6, 7, 8, 9, 13, 14, 15, 16]:
                raise TypeError('IN not supported on P%d' % pin)
            self.Pin = Pin(self.id, Pin.IN, pull)
        if mode == PinMode.OUT:
            if pin not in [0, 1, 2, 3, 6, 7, 8, 9, 13, 14, 15, 16]:
                raise TypeError('OUT not supported on P%d' % pin)
            self.Pin = Pin(self.id, Pin.OUT, pull)
        if mode == PinMode.OUT_DRAIN:
            if pin not in [0, 1, 2, 3, 6, 7, 8, 9, 13, 14, 15, 16]:
                raise TypeError('OUT_DRAIN not supported on P%d' % pin)
            self.Pin = Pin(self.id, Pin.OPEN_DRAIN, pull)
        if mode == PinMode.PWM:
            if pin not in [0, 1, 2, 3, 6, 7, 8, 9, 13, 14, 15, 16]:
                raise TypeError('PWM not supported on P%d' % pin)
            self.pwm = PWM(Pin(self.id), duty=0)
        if mode == PinMode.ANALOG:
            if pin not in [0, 1, 2, 3, 6, 7]:
                raise TypeError('ANALOG not supported on P%d' % pin)
            self.adc = ADC(Pin(self.id))
            self.adc.atten(ADC.ATTN_11DB)
        self.mode = mode

    def irq(self, handler=None, trigger=Pin.IRQ_RISING):
        if not self.mode == PinMode.IN:
            raise TypeError('the pin is not in IN mode')
        return self.Pin.irq(handler, trigger)

    def read_digital(self):
        if not self.mode == PinMode.IN:
            raise TypeError('the pin is not in IN mode')
        return self.Pin.value()

    def write_digital(self, value):
        if self.mode not in [PinMode.OUT, PinMode.OUT_DRAIN]:
            raise TypeError('the pin is not in OUT or OUT_DRAIN mode')
        self.Pin.value(value)

    def read_analog(self):
        if not self.mode == PinMode.ANALOG:
            raise TypeError('the pin is not in ANALOG mode')
        return self.adc.read()
        

    def write_analog(self, duty, freq=1000):
        if not self.mode == PinMode.PWM:
            raise TypeError('the pin is not in PWM mode')
        self.pwm.freq(freq)
        self.pwm.duty(duty)

'''
# to be test
class LightSensor(ADC):
    
    def __init__(self):
        super().__init__(Pin(pins_remap_esp32[4]))
        # super().atten(ADC.ATTN_11DB)
    
    def value(self):
        # lux * k * Rc = N * 3.9/ 4096
        # k = 0.0011mA/Lux
        # lux = N * 3.9/ 4096 / Rc / k
        return super().read() * 1.1 / 4095 / 6.81 / 0.011
    
'''

class wifi:
    def __init__(self):
        self.sta = network.WLAN(network.STA_IF)
        self.ap = network.WLAN(network.AP_IF)

    def connectWiFi(self, ssid, passwd, timeout=10):
        if self.sta.isconnected():
            self.sta.disconnect()
        self.sta.active(True)
        list = self.sta.scan()
        for i, wifi_info in enumerate(list):
            try:
                if wifi_info[0].decode() == ssid:
                    self.sta.connect(ssid, passwd)
                    wifi_dbm = wifi_info[3]
                    break
            except UnicodeError:
                self.sta.connect(ssid, passwd)
                wifi_dbm = '?'
                break
            if i == len(list) - 1:
                raise OSError("SSID invalid / failed to scan this wifi")
        start = time.time()
        print("Connection WiFi", end="")
        while (self.sta.ifconfig()[0] == '0.0.0.0'):
            if time.ticks_diff(time.time(), start) > timeout:
                print("")
                raise OSError("Timeout!,check your wifi password and keep your network unblocked")
            print(".", end="")
            time.sleep_ms(500)
        print("")
        print('WiFi(%s,%sdBm) Connection Successful, Config:%s' % (ssid, str(wifi_dbm), str(self.sta.ifconfig())))

    def disconnectWiFi(self):
        if self.sta.isconnected():
            self.sta.disconnect()
        self.sta.active(False)
        print('disconnect WiFi...')

    def enable_APWiFi(self, essid, password=b'',channel=10):
        self.ap.active(True)
        if password:
            authmode=4
        else:
            authmode=0
        self.ap.config(essid=essid,password=password,authmode=authmode, channel=channel)

    def disable_APWiFi(self):
        self.ap.active(False)
        print('disable AP WiFi...')

# 3 rgb leds
rgb = NeoPixel(Pin(33, Pin.OUT), 3, 3, 1, brightness=0.3)
rgb.write()

# light sensor
light = ADC(Pin(5))
light.atten(light.ATTN_11DB)

# sound sensor
sound = ADC(Pin(6))
sound.atten(sound.ATTN_11DB)

# buttons
class Button:
    def __init__(self, pin_num, reverse=False):
        self.__reverse = reverse
        (self.__press_level, self.__release_level) = (0, 1) if not self.__reverse else (1, 0)
        self.__pin = Pin(pin_num, Pin.IN, pull=Pin.PULL_UP)
        self.__pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.__irq_handler)
        # self.__user_irq = None
        self.event_pressed = None
        self.event_released = None
        self.__pressed_count = 0
        self.__was_pressed = False
        # print("level: pressed is {}, released is {}." .format(self.__press_level, self.__release_level))
    

    def __irq_handler(self, pin):
        irq_falling = True if pin.value() == self.__press_level else False
        # debounce
        time.sleep_ms(10)
        if self.__pin.value() == (self.__press_level if irq_falling else self.__release_level):
            # new event handler
            # pressed event
            if irq_falling:
                if self.event_pressed is not None:
                    schedule(self.event_pressed, self.__pin)
                # key status
                self.__was_pressed = True
                if (self.__pressed_count < 100):
                    self.__pressed_count = self.__pressed_count + 1
            # release event
            else:
                if self.event_released is not None:
                    schedule(self.event_released, self.__pin)

                
    def is_pressed(self):
        if self.__pin.value() == self.__press_level:
            return True
        else:
            return False

    def was_pressed(self):
        r = self.__was_pressed
        self.__was_pressed = False
        return r

    def get_presses(self):
        r = self.__pressed_count
        self.__pressed_count = 0
        return r

    def value(self):
        return self.__pin.value()

    def irq(self, *args, **kws):
        self.__pin.irq(*args, **kws)

    def status(self):
        val = self.__pin.value()
        if(val==0):
            return 1
        elif(val==1):
            return 0

button_a = Button(0)
button_b = Button(46)

class Touch:

    def __init__(self, pin):
        self.__touch_pad = TouchPad(pin)
        self.__touch_pad.irq(self.__irq_handler)
        self.event_pressed = None
        self.event_released = None
        self.__pressed_count = 0
        self.__was_pressed = False
        self.__value = 0

    def __irq_handler(self, value):
        # when pressed
        if value == 1:
            if self.event_pressed is not None:
                self.event_pressed(value)
            self.__was_pressed = True
            self.__value = 1
            if (self.__pressed_count < 100):
                self.__pressed_count = self.__pressed_count + 1
        # when released
        else:
            self.__value = 0
            if self.event_released is not None:
                self.event_released(value)
            
    def config(self, threshold):
        self.__touch_pad.config(threshold)

    def is_pressed(self):
        if self.__value:
            return True
        else:
            return False

    def was_pressed(self):
        r = self.__was_pressed
        self.__was_pressed = False
        return r

    def get_presses(self):
        r = self.__pressed_count
        self.__pressed_count = 0
        return r

    def read(self):
        return self.__touch_pad.read()
# touchpad
touchpad_p = touchPad_P = Touch(Pin(9))
touchpad_y = touchPad_Y = Touch(Pin(10))
touchpad_t = touchPad_T = Touch(Pin(11))
touchpad_h = touchPad_H = Touch(Pin(12))
touchpad_o = touchPad_O = Touch(Pin(13))
touchpad_n = touchPad_N = Touch(Pin(14))

# shield 
class Ledong_shield(object):
    def __init__(self):
        self.speed = 0 
        self.i2c = i2c
        self.i2c_addr = 17

    def power_off(self):
        self.i2c.writeto(self.i2c_addr, b'\x06\x01', True)

    def get_battery_level(self):
        self.i2c.writeto(self.i2c_addr, b'\x05', True)
        return self.i2c.readfrom(self.i2c_addr, 1)[0]

ledong_shield = Ledong_shield()

from gui import *

def numberMap(inputNum, bMin, bMax, cMin, cMax):
    outputNum = 0
    outputNum = ((cMax - cMin) / (bMax - bMin)) * (inputNum - bMin) + cMin
    return outputNum
