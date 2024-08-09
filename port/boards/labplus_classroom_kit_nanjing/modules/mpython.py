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
import NVS

i2c = I2C(0, scl=Pin(Pin.P19), sda=Pin(Pin.P20), freq=400000)

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


pins_remap_esp32 = (33, 32, 35, 34, 39, 0, 16, 17, 26, 25, 36, 2, -1, 18, 19, 21, 5, -1, -1, 22, 23, -1, -1, 27, 14, 12,
                    13, 15, 4)


class MPythonPin():
    def __init__(self, pin, mode=PinMode.IN, pull=None):
        if mode not in [PinMode.IN, PinMode.OUT, PinMode.PWM, PinMode.ANALOG, PinMode.OUT_DRAIN]:
            raise TypeError("mode must be 'IN, OUT, PWM, ANALOG,OUT_DRAIN'")
        if pin == 4:
            raise TypeError("P4 is used for light sensor")
        if pin == 10:
            raise TypeError("P10 is used for sound sensor")
        try:
            self.id = pins_remap_esp32[pin]
        except IndexError:
            raise IndexError("Out of Pin range")
        if mode == PinMode.IN:
            # if pin in [3]:
            #     raise TypeError('IN not supported on P%d' % pin)
            self.Pin = Pin(self.id, Pin.IN, pull)
        if mode == PinMode.OUT:
            if pin in [2, 3]:
                raise TypeError('OUT not supported on P%d' % pin)
            self.Pin = Pin(self.id, Pin.OUT, pull)
        if mode == PinMode.OUT_DRAIN:
            if pin in [2, 3]:
                raise TypeError('OUT_DRAIN not supported on P%d' % pin)
            self.Pin = Pin(self.id, Pin.OPEN_DRAIN, pull)
        if mode == PinMode.PWM:
            if pin not in [0, 1, 5, 6, 7, 8, 9, 11, 13, 14, 15, 16, 19, 20, 23, 24, 25, 26, 27, 28]:
                raise TypeError('PWM not supported on P%d' % pin)
            self.pwm = PWM(Pin(self.id), duty=0)
        if mode == PinMode.ANALOG:
            if pin not in [0, 1, 2, 3, 4, 10]:
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
rgb = NeoPixel(Pin(17, Pin.OUT), 4, 3, 1, brightness=0.3)
rgb.write()

# light sensor
light = ADC(Pin(39))
light.atten(light.ATTN_11DB)

# sound sensor
sound = ADC(Pin(36))
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
    
    def status(self):
        val = self.__pin.value()
        if(val==0):
            return 1
        elif(val==1):
            return 0

    def irq(self, *args, **kws):
        self.__pin.irq(*args, **kws)


# button_a = Pin(0, Pin.IN, Pin.PULL_UP)
# button_b = Pin(2, Pin.IN, Pin.PULL_UP)
button_a = Button(34)
button_b = Button(38)

class Ledong_shield(object):
    def __init__(self):
        self.speed = 0 
        self.i2c = i2c
        self.i2c_addr = 17

    def set_motor(self, motor_num, speed):
        self.speed = speed
        if self.speed > 100:
            self.speed = 100
        if self.speed < -100:
            self.speed = -100
        self.i2c.writeto(self.i2c_addr, bytearray([motor_num, self.speed]), True)

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
