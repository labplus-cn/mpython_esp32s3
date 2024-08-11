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

i2c = I2C(0, scl=Pin(22), sda=Pin(23), freq=400000)

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

class Font(object):
    def __init__(self, font_address=0x400000):
        self.font_address = font_address
        buffer = bytearray(18)
        esp.flash_read(self.font_address, buffer)
        self.header, \
            self.height, \
            self.width, \
            self.baseline, \
            self.x_height, \
            self.Y_height, \
            self.first_char,\
            self.last_char = ustruct.unpack('4sHHHHHHH', buffer)
        self.first_char_info_address = self.font_address + 18

    def GetCharacterData(self, c):
        uni = ord(c)
        # if uni not in range(self.first_char, self.last_char):
        #     return None
        if (uni < self.first_char or uni > self.last_char):
            return None
        char_info_address = self.first_char_info_address + \
            (uni - self.first_char) * 6
        buffer = bytearray(6)
        esp.flash_read(char_info_address, buffer)
        ptr_char_data, len = ustruct.unpack('IH', buffer)
        if (ptr_char_data) == 0 or (len == 0):
            return None
        buffer = bytearray(len)
        esp.flash_read(ptr_char_data + self.font_address, buffer)
        return buffer


class TextMode():
    normal = 1
    rev = 2
    trans = 3
    xor = 4


class OLED(SSD1106_I2C):
    """ 128x64 oled display """

    def __init__(self):
        super().__init__(128, 64, i2c)
        self.f = Font()
        if self.f is None:
            raise Exception('font load failed')

    def DispChar(self, s, x, y, mode=TextMode.normal, auto_return=False):
            row = 0
            str_width = 0
            if self.f is None:
                return
            for c in s:
                data = self.f.GetCharacterData(c)
                if data is None:
                    if auto_return is True:
                        x = x + self.f.width
                    else:
                        x = x + self.width
                    continue
                width, bytes_per_line = ustruct.unpack('HH', data[:4])
                # print('character [%d]: width = %d, bytes_per_line = %d' % (ord(c)
                # , width, bytes_per_line))
                if auto_return is True:
                    if x > self.width - width:
                        str_width += self.width - x
                        x = 0
                        row += 1
                        y += self.f.height
                        if y > (self.height - self.f.height)+0:
                            y, row = 0, 0
                for h in range(0, self.f.height):
                    w = 0
                    i = 0
                    while w < width:
                        mask = data[4 + h * bytes_per_line + i]
                        if (width - w) >= 8:
                            n = 8
                        else:
                            n = width - w
                        py = y + h
                        page = py >> 3
                        bit = 0x80 >> (py % 8)
                        for p in range(0, n):
                            px = x + w + p
                            c = 0
                            if (mask & 0x80) != 0:
                                if mode == TextMode.normal or \
                                        mode == TextMode.trans:
                                    c = 1
                                if mode == TextMode.rev:
                                    c = 0
                                if mode == TextMode.xor:
                                    c = self.buffer[page * (self.width if auto_return is True else 128) + px] & bit
                                    if c != 0:
                                        c = 0
                                    else:
                                        c = 1
                                super().pixel(px, py, c)
                            else:
                                if mode == TextMode.normal:
                                    c = 0
                                    super().pixel(px, py, c)
                                if mode == TextMode.rev:
                                    c = 1
                                    super().pixel(px, py, c)
                            mask = mask << 1
                        w = w + 8
                        i = i + 1
                x = x + width + 1
                str_width += width + 1
            return (str_width-1,(x-1, y))

    def DispChar_font(self, font, s, x, y, invert=False):
        """
        custom font display.Ref by , https://github.com/peterhinch/micropython-font-to-py
        :param font:  use font_to_py.py script convert to `py` from `ttf` or `otf`.
        """
        screen_width = self.width
        screen_height = self.height
        text_row = x
        text_col = y
        text_length = 0
        if font.hmap():
            font_map = framebuf.MONO_HMSB if font.reverse() else framebuf.MONO_HLSB
        else:
            raise ValueError('Font must be horizontally mapped.')
        for c in s:
            glyph, char_height, char_width = font.get_ch(c)
            buf = bytearray(glyph)
            if invert:
                for i, v in enumerate(buf):
                    buf[i] = 0xFF & ~ v
            fbc = framebuf.FrameBuffer(buf, char_width, char_height, font_map)
            if text_row + char_width > screen_width - 1:
                text_length += screen_width-text_row
                text_row = 0
                text_col += char_height
            if text_col + char_height > screen_height + 2:
                text_col = 0

            super().blit(fbc, text_row, text_col)
            text_row = text_row + char_width+1
            text_length += char_width+1
        return (text_length-1, (text_row-1, text_col))

# display
if 60 in i2c.scan():
    oled = OLED()
    display = oled
else:
    pass


class Magnetic(object):
    """ MMC5983MA driver """
    """ MMC5603NJ driver 20211028替换"""
    def __init__(self):
        self.addr = 48
        self.i2c = i2c
        self._judge_id()
        time.sleep_ms(5)
        if (self.product_ID==48):
            pass  # MMC5983MA
        elif (self.product_ID==16):
            pass  # MMC5603NJ
        else:
            raise OSError("Magnetic init error")
        """ MMC5983MA driver """
        # 传量器裸数据，乘0.25后转化为mGS
        self.raw_x = 0.0
        self.raw_y = 0.0
        self.raw_z = 0.0
        # 校准后的偏移量, 基于裸数据
        self.cali_offset_x = 0.0 
        self.cali_offset_y = 0.0
        self.cali_offset_z = 0.0
        # 去皮偏移量，类似电子秤去皮功能，基于裸数据。
        self.peeling_x = 0.0
        self.peeling_y = 0.0
        self.peeling_z = 0.0
        self.is_peeling = 0
        if (self.chip==1):
            self.i2c.writeto(self.addr, b'\x09\x20\xbd\x00', True)
        """ MMC5603NJ driver """
        if (self.chip==2):
            self._writeReg(0x1C, 0x80)#软件复位
            time.sleep_ms(100)
            self._writeReg(0x1A, 255)
            self._writeReg(0x1B, 0b10100001)
            # self._writeReg(0x1C, 0b00000011)
            self._writeReg(0x1C, 0b00000000)
            self._writeReg(0x1D, 0b10010000)
            time.sleep_ms(100)

    def _readReg(self, reg, nbytes=1):
        return i2c.readfrom_mem(self.addr, reg, nbytes)

    def _writeReg(self, reg, value):
        i2c.writeto_mem(self.addr, reg, value.to_bytes(1, 'little')) 

    def _set_offset(self):
        if(self.chip == 1):
            self.i2c.writeto(self.addr, b'\x09\x08', True)  #set
            self.i2c.writeto(self.addr, b'\x09\x01', True)
            while True:
                self.i2c.writeto(self.addr, b'\x08', False)
                buf = self.i2c.readfrom(self.addr, 1)
                status = ustruct.unpack('B', buf)[0]
                if(status & 0x01):
                    break
            self.i2c.writeto(self.addr, b'\x00', False)
            buf = self.i2c.readfrom(self.addr, 6)
            data = ustruct.unpack('>3H', buf)

            self.i2c.writeto(self.addr, b'\x09\x10', True)  #reset

            self.i2c.writeto(self.addr, b'\x09\x01', True)
            while True:
                self.i2c.writeto(self.addr, b'\x08', False)
                buf = self.i2c.readfrom(self.addr, 1)
                status = ustruct.unpack('B', buf)[0]
                if(status & 0x01):
                    break
            self.i2c.writeto(self.addr, b'\x00', False)
            buf = self.i2c.readfrom(self.addr, 6)
            data1 = ustruct.unpack('>3H', buf)

            self.x_offset = (data[0] + data1[0])/2
            self.y_offset = (data[1] + data1[1])/2
            self.z_offset = (data[2] + data1[2])/2
        elif(self.chip == 2):
            pass
    
    def _get_raw(self):
        if (self.chip == 1):
            retry = 0
            if (retry < 5):
                try:
                    self.i2c.writeto(self.addr, b'\x09\x08', True)  #set

                    self.i2c.writeto(self.addr, b'\x09\x01', True)
                    while True:
                        self.i2c.writeto(self.addr, b'\x08', False)
                        buf = self.i2c.readfrom(self.addr, 1)
                        status = ustruct.unpack('B', buf)[0]
                        if(status & 0x01):
                            break
                    self.i2c.writeto(self.addr, b'\x00', False)
                    buf = self.i2c.readfrom(self.addr, 6)
                    data = ustruct.unpack('>3H', buf)

                    self.i2c.writeto(self.addr, b'\x09\x10', True)  #reset

                    self.i2c.writeto(self.addr, b'\x09\x01', True)
                    while True:
                        self.i2c.writeto(self.addr, b'\x08', False)
                        buf = self.i2c.readfrom(self.addr, 1)
                        status = ustruct.unpack('B', buf)[0]
                        if(status & 0x01):
                            break
                    self.i2c.writeto(self.addr, b'\x00', False)
                    buf = self.i2c.readfrom(self.addr, 6)
                    data1 = ustruct.unpack('>3H', buf)

                    self.raw_x = -((data[0] - data1[0])/2)
                    self.raw_y = -((data[1] - data1[1])/2)
                    self.raw_z = -((data[2] - data1[2])/2)
                    # print(str(self.raw_x) + "   " + str(self.raw_y) + "  " + str(self.raw_z))
                except:
                    retry = retry + 1
            else:
                raise Exception("i2c read/write error!")     
        elif(self.chip == 2):
            retry = 0
            if (retry < 5):
                try:
                    _raw_x = 0.0
                    _raw_y = 0.0
                    _raw_z = 0.0

                    self.i2c.writeto(self.addr, b'\x1B\x08', True)  #set
                    self.i2c.writeto(self.addr, b'\x1B\x01', True)
                    
                    while True:
                        sleep_ms(25)
                        buf = self._readReg(0x18, 1)
                        status = buf[0]
                        if(status & 0x40):
                            break

                    buf = self._readReg(0x00, 9)

                    _raw_x = (buf[0] << 12) | (buf[1] << 4) | (buf[6] >> 4)
                    _raw_y = (buf[2] << 12) | (buf[3] << 4) | (buf[7] >> 4)
                    _raw_z = (buf[4] << 12) | (buf[5] << 4) | (buf[8] >> 4)

                    self.raw_x = _raw_x
                    self.raw_y = _raw_y
                    self.raw_z = _raw_z
                except:
                    retry = retry + 1
            else:
                raise Exception("i2c read/write error!")

    def peeling(self):
        '''
        去除磁场环境
        '''
        self._get_raw()
        self.peeling_x = self.raw_x
        self.peeling_y = self.raw_y
        self.peeling_z = self.raw_z
        self.is_peeling = 1

    def clear_peeling(self):
        self.peeling_x = 0.0
        self.peeling_y = 0.0
        self.peeling_z = 0.0
        self.is_peeling = 0

    def get_x(self):
        if (self.chip == 1):
            self._get_raw()
            return self.raw_x * 0.25
        if (self.chip == 2):
            self._get_raw()
            if(self.cali_offset_x):
                return -0.0625 * (self.raw_x - self.cali_offset_x)
            else:
                return -0.0625 * (self.raw_x - 524288)
            # return -(self.raw_x - 524288)/16384

    def get_y(self):
        if (self.chip == 1):
            self._get_raw()
            return self.raw_y * 0.25
        if (self.chip == 2):
            self._get_raw()
            if(self.cali_offset_y):
                return -0.0625 * (self.raw_y - self.cali_offset_y)
            else:
                return -0.0625 * (self.raw_y - 524288)
            # return -(self.raw_y - 524288)/16384

    def get_z(self):
        if (self.chip == 1):
            self._get_raw()
            return self.raw_z * 0.25 
        if (self.chip == 2):
            self._get_raw()
            if(self.cali_offset_z):
                return 0.0625 * (self.raw_z - self.cali_offset_z)
            else:
                return 0.0625 * (self.raw_z - 524288)
            # return (self.raw_z - 524288)/16384

    def get_field_strength(self):
        if(self.chip==1):
            self._get_raw()
            if self.is_peeling == 1:
                return (math.sqrt((self.raw_x - self.peeling_x)*(self.raw_x - self.peeling_x) + (self.raw_y - self.peeling_y)*(self.raw_y - self.peeling_y) + (self.raw_z - self.peeling_z)*(self.raw_z - self.peeling_z)))*0.25
            return (math.sqrt(self.raw_x * self.raw_x + self.raw_y * self.raw_y + self.raw_z * self.raw_z))*0.25
        elif(self.chip==2):
            self._get_raw()
            if self.is_peeling == 1:
                return (math.sqrt(math.pow(self.raw_x - self.peeling_x, 2) + pow(self.raw_y - self.peeling_y, 2) + pow(self.raw_z - self.peeling_z , 2)))*0.0625
            return (math.sqrt(math.pow(self.get_x(), 2) + pow(self.get_y(), 2) + pow(self.get_z(), 2)))

    def calibrate(self):
        oled.fill(0)
        oled.DispChar("步骤1:", 0,0,1)
        oled.DispChar("如图",0,26,1)
        oled.DispChar("转几周",0,43,1)
        oled.bitmap(64,0,calibrate_img.rotate,64,64,1)
        oled.show()
        self._get_raw()
        min_x = max_x = self.raw_x
        min_y = max_y = self.raw_y
        min_z = max_z = self.raw_z
        ticks_start = time.ticks_ms()
        while (time.ticks_diff(time.ticks_ms(), ticks_start) < 15000) :
            self._get_raw()
            min_x = min(self.raw_x, min_x)
            min_y = min(self.raw_y, min_y)
            max_x = max(self.raw_x, max_x)
            max_y = max(self.raw_y, max_y)
            time.sleep_ms(100)
        self.cali_offset_x = (max_x + min_x) / 2
        self.cali_offset_y = (max_y + min_y) / 2
        print('cali_offset_x: ' + str(self.cali_offset_x) + '  cali_offset_y: ' + str(self.cali_offset_y))
        oled.fill(0)
        oled.DispChar("步骤2:", 85,0,1)
        oled.DispChar("如图",85,26,1)
        oled.DispChar("转几周",85,43,1)
        oled.bitmap(0,0,calibrate_img.rotate1,64,64,1)
        oled.show()
        ticks_start = time.ticks_ms()
        while (time.ticks_diff(time.ticks_ms(), ticks_start) < 15000) :
            self._get_raw()
            min_z = min(self.raw_z, min_z)
            max_z = max(self.raw_z, max_z)
            time.sleep_ms(100)
        self.cali_offset_z = (max_z + min_z) / 2
  
        print('cali_offset_z: ' + str(self.cali_offset_z))

        oled.fill(0)
        oled.DispChar("校准完成", 40,24,1)
        oled.show()
        oled.fill(0)

    def get_heading(self):
        if(self.chip==1):
            self._get_raw()
            temp_x = self.raw_x - self.cali_offset_x
            temp_y = self.raw_y - self.cali_offset_y
            # temp_z = self.raw_z - self.cali_offset_z
            heading = math.atan2(temp_y, -temp_x) * (180 / 3.14159265) + 180 + 3
            return heading
        else:
            if(self.cali_offset_x):
                self._get_raw()
                temp_x = -(self.raw_x - self.cali_offset_x)
                temp_y = -(self.raw_y - self.cali_offset_y)
                heading = math.atan2(temp_y, -temp_x) * (180 / 3.14159265) + 180 + 3
            else:
                heading = math.atan2(self.get_y(), -self.get_x()) * (180 / 3.14159265) + 180 + 3
            return heading
        
    def _get_temperature(self):
        if(self.chip==1):
            retry = 0
            if (retry < 5):
                try:
                    self.i2c.writeto(self.addr, b'\x09\x02', True)
                    while True:
                        self.i2c.writeto(self.addr, b'\x08', False)
                        buf = self.i2c.readfrom(self.addr, 1)
                        status = ustruct.unpack('B', buf)[0]
                        if(status & 0x02):
                            break
                    self.i2c.writeto(self.addr, b'\x07', False)
                    buf = self.i2c.readfrom(self.addr, 1)
                    temp = (ustruct.unpack('B', buf)[0])*0.8 -75
                    # print(data)
                    return temp
                except:
                    retry = retry + 1
            else:
                raise Exception("i2c read/write error!")   
        elif(self.chip == 2):
            pass

    def _get_id(self):
        if (self.chip==1):
            retry = 0
            if (retry < 5):
                try:
                    self.i2c.writeto(self.addr, bytearray([0x2f]), False)
                    buf = self.i2c.readfrom(self.addr, 1, True)
                    print(buf)
                    id = ustruct.unpack('B', buf)[0]
                    return id
                except:
                    retry = retry + 1
            else:
                raise Exception("i2c read/write error!")
        elif (self.chip==2):
            retry = 0
            if (retry < 5):
                try:
                    self.i2c.writeto(self.addr, bytearray([0x39]), False)
                    buf = self.i2c.readfrom(self.addr, 1, True)
                    id = ustruct.unpack('B', buf)[0]
                    return id
                except:
                    retry = retry + 1
            else:
                raise Exception("i2c read/write error!")

    def _judge_id(self):
        """
        判断product_ID
        """
        retry = 0
        if (retry < 5):
            try:
                self.i2c.writeto(self.addr, bytearray([0x39]), False)
                buf = self.i2c.readfrom(self.addr, 1, True)
                id = ustruct.unpack('B', buf)[0]
                if(id == 16):
                    self.chip = 2
                    self.product_ID = 16
                else:
                    self.chip = 1
                    self.product_ID = 48
            except:
                retry = retry + 1
        else:
            raise Exception("i2c read/write error!")  

# Magnetic
if 48 in i2c.scan():
    magnetic = Magnetic()



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
# rgb = NeoPixel(Pin(17, Pin.OUT), 3, 3, 1, brightness=0.3)
# rgb.write()

# light sensor
light = ADC(Pin(39))
light.atten(light.ATTN_11DB)

# sound sensor
sound = ADC(Pin(36))
sound.atten(sound.ATTN_11DB)


def numberMap(inputNum, bMin, bMax, cMin, cMax):
    outputNum = 0
    outputNum = ((cMax - cMin) / (bMax - bMin)) * (inputNum - bMin) + cMin
    return outputNum
