# The MIT License (MIT)

# Copyright (c) 2018, Tangliufeng. LabPlus

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
| blue:bit modules library for mPython. 
| more about with bluebit info browse http://wiki.labplus.cn/index.php?title=Bluebit
"""
from mpython import i2c, sleep_ms, MPythonPin, PinMode,numberMap
from micropython import const
from machine import UART, ADC, Pin
import framebuf
import ubinascii
import ustruct
import math
from max30102 import MAX30102

class Thermistor:
    """
    NTC 模块。也适用于其他的热敏电阻。

    :param pin: 掌控板引脚号,如使用P0,pin=0.
    :param series_resistor: 与热敏电阻连接的串联电阻器的值。默认是10K电阻。
    :param nominal_resistance: 在标称温度下热敏电阻的阻值。
    :param nominal_temperature: 在标称电阻值下热敏电阻的温度值(以摄氏度为单位)。默认使用25.0摄氏度。
    :param b_coefficient: 热敏电阻的温度系数。
    :param high_side: 表示热敏电阻是连接在电阻分压器的高侧还是低侧。默认high_side为True。
    """

    def __init__(
        self,
        pin,
        series_resistor=10000.0,
        nominal_resistance=10000.0,
        nominal_temperature=25.0,
        b_coefficient=3935.0,
        high_side=True
    ):
        self.adc = ADC(Pin(eval("Pin.P{}".format(pin))))
        self.adc.atten(ADC.ATTN_11DB)
        self.series_resistor = series_resistor
        self.nominal_resistance = nominal_resistance
        self.nominal_temperature = nominal_temperature
        self.b_coefficient = b_coefficient
        self.high_side = high_side
    
    def getTemper(self):
        """
        获取温度,读取异常则返回None

        :return: 温度,单位摄氏度
        """
        try:
            if self.high_side:
                # Thermistor connected from analog input to high logic level.
                reading = self.adc.read_u16() / 64
                reading = (1023 * self.series_resistor) / reading
                reading -= self.series_resistor
            else:
                # Thermistor connected from analog input to ground.
                reading = self.series_resistor / (65535.0 / self.adc.read_u16() - 1.0)
            steinhart = reading / self.nominal_resistance  # (R/Ro)
            steinhart = math.log(steinhart)  # ln(R/Ro)
            steinhart /= self.b_coefficient  # 1/B * ln(R/Ro)
            steinhart += 1.0 / (self.nominal_temperature + 273.15)  # + (1/To)
            steinhart = 1.0 / steinhart  # Invert
            steinhart -= 273.15  # convert to C

            return steinhart
        except:
            return None

# 兼容以前旧接口
NTC = Thermistor

class SHT20(object):
    """
    温湿度模块SHT20控制类

    :param i2c: I2C实例对象,默认i2c=i2c.
    """

    def __init__(self, i2c=i2c):
        self.i2c = i2c

    def temperature(self):
        """
        获取温度

        :return: 温度,单位摄氏度
        """
        self.i2c.writeto(0x40, b'\xf3')
        sleep_ms(70)
        t = i2c.readfrom(0x40, 2)
        return -46.86 + 175.72 * (t[0] * 256 + t[1]) / 65535

    def humidity(self):
        """
        获取湿度

        :return: 湿度,单位%
        """
        self.i2c.writeto(0x40, b'\xf5')
        sleep_ms(25)
        t = i2c.readfrom(0x40, 2)
        return -6 + 125 * (t[0] * 256 + t[1]) / 65535


class Color(object):
    """
    颜色模块控制类

    :param i2c: I2C实例对象,默认i2c=i2c.
    """

    def __init__(self, i2c=i2c):
        self.i2c = i2c

    def getRGB(self):
        """
        获取RGB值

        :return: 返回RGB三元组,(r,g,b)
        """
        color = [0, 0, 0]
        self.i2c.writeto(0x0a, bytearray([1]))
        sleep_ms(100)
        self.i2c.writeto(0x0a, bytearray([2]))
        state = self.i2c.readfrom(0x0a, 1)
        if state[0] == 3:
            self.i2c.writeto(0x0a, bytearray([3]))
            c = self.i2c.readfrom(0x0a, 6)
            color[0] = c[5] * 256 + c[4]  # color R
            color[1] = c[1] * 256 + c[0]  # color G
            color[2] = c[3] * 256 + c[2]  # color B
            maxColor = max(color[0], color[1], color[2])
            if maxColor > 255:
                scale = 255 / maxColor
                color[0] = int(color[0] * scale)
                color[1] = int(color[1] * scale)
                color[2] = int(color[2] * scale)
        return color

    def getHSV(self):
        """
        获取HSV值

        :return: 返回HSV三元组,(h,s,v)
        """
        rgb = self.getRGB()
        r, g, b = rgb[0], rgb[1], rgb[2]
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx - mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g - b) / df) + 360) % 360
        elif mx == g:
            h = (60 * ((b - r) / df) + 120) % 360
        elif mx == b:
            h = (60 * ((r - g) / df) + 240) % 360
        if mx == 0:
            s = 0
        else:
            s = df / mx
        v = mx
        return round(h, 1), round(s, 1), round(v, 1)


class AmbientLight(object):
    """
    数字光线模块控制类

    :param i2c: I2C实例对象,默认i2c=i2c.
    """

    def __init__(self, i2c=i2c):
        self.i2c = i2c

    def getLight(self):
        """
        获取光线值

        :return: 返回光线值,单位lux
        """
        self.i2c.writeto(0x23, bytearray([0x10]))
        sleep_ms(120)
        t = self.i2c.readfrom(0x23, 2)
        sleep_ms(10)
        return int((t[0] * 256 + t[1]) / 1.2)


class Ultrasonic(object):
    """
    超声波模块控制类

    :param i2c: I2C实例对象,默认i2c=i2c.
    """

    def __init__(self, i2c=i2c):
        self.i2c = i2c

    def distance(self):
        """
        获取超声波测距

        :return: 返回测距,单位cm
        """
        self.i2c.writeto(0x0b, bytearray([1]))
        sleep_ms(2)
        temp = self.i2c.readfrom(0x0b, 2)
        distanceCM = (temp[0] + temp[1] * 256) / 10
        if(distanceCM>200):
            distanceCM=200
        return distanceCM

class SEGdisplay(object):
    """
    4段数码管模块tm1650控制类

    :param i2c: I2C实例对象,默认i2c=i2c.
    """

    def __init__(self, i2c=i2c):
        self.i2c = i2c
        addr = self.i2c.scan()
        if 36 in addr:
            self.chip = 1  # TM1650
        elif 112 in addr:
            self.chip = 2  # HT16K33
        else:
            raise OSError("Can not find 7-seg-display module.")
        if self.chip == 1:
            self.i2c.writeto(0x24, bytearray([0x01]))
            self._TubeTab = [
                0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F, 0x77,
                0x7C, 0x39, 0x5E, 0x79, 0x71, 0x00, 0x40
            ]
        elif self.chip == 2:
            self.ht16k33 = HT16K33_SEG()

    def _uint(self, x):
        """ display unsigned int number """
        charTemp = [0, 0, 0, 0]
        x = (x if x < 10000 else 9999)
        charTemp[3] = x % 10
        charTemp[2] = (x // 10) % 10
        charTemp[1] = (x // 100) % 10
        charTemp[0] = (x // 1000) % 10
        if x < 1000:
            charTemp[0] = 0x10
            if x < 100:
                charTemp[1] = 0x10
            if x < 10:
                charTemp[2] = 0x10
        if self.chip == 1:
            for i in range(0, 4):
                self.i2c.writeto(0x34 + i, bytearray([self._TubeTab[charTemp[i]]]))
        elif self.chip == 2:
            for i in range(0, 4):
                self.ht16k33.buffer[i*2] = self.ht16k33._TubeTab[charTemp[i]]
            self.ht16k33.show()

    def numbers(self, x):
        """
        数字显示-999~9999

        :param int x: 数字,范围-999~9999
        """
        x = round(x)
        if x >= 0:
            self._uint(x)
        else:
            temp = (x if x > -999 else -999)
            temp = abs(temp)
            self._uint(temp)
            if temp < 10:
                if self.chip == 1:
                    self.i2c.writeto(0x36, bytearray([self._TubeTab[0x11]]))
                elif self.chip == 2:
                    self.ht16k33.buffer[4] = self.ht16k33._TubeTab[17]
                    self.ht16k33.show()
            elif temp < 100:
                if self.chip == 1:
                    self.i2c.writeto(0x35, bytearray([self._TubeTab[0x11]]))
                elif self.chip == 2:
                    self.ht16k33.buffer[2] = self.ht16k33._TubeTab[17]
                    self.ht16k33.show()
            elif temp < 1000:
                if self.chip == 1:
                    self.i2c.writeto(0x34, bytearray([self._TubeTab[0x11]]))
                elif self.chip == 2:
                    self.ht16k33.buffer[0] = self.ht16k33._TubeTab[17]
                    self.ht16k33.show()

    def Clear(self):
        """
        数码管清屏
        """
        if self.chip == 1:
            for i in range(0, 4):
                self.i2c.writeto(0x34 + i, bytearray([self._TubeTab[0x10]]))
        elif self.chip == 2:
            self.ht16k33.fill(0)
            self.ht16k33.show()


_HT16K33_BLINK_CMD = const(0x80)
_HT16K33_BLINK_DISPLAYON = const(0x01)
_HT16K33_CMD_BRIGHTNESS = const(0xE0)
_HT16K33_OSCILATOR_ON = const(0x21)
_HT16K33_ADDR = const(0x70)


class HT16K33:
    def __init__(self, i2c=i2c):
        self.i2c = i2c
        self.address = _HT16K33_ADDR
        self._temp = bytearray(1)

        self.buffer = bytearray(16)
        self._write_cmd(_HT16K33_OSCILATOR_ON)
        self.blink_rate(0)
        self.brightness(15)

    def _write_cmd(self, byte):
        self._temp[0] = byte
        self.i2c.writeto(self.address, self._temp)

    def blink_rate(self, rate=None):
        """
        设置像素点闪烁率

        :param rate: 闪烁间隔时间,单位秒.默认None,常亮.
        """

        if rate is None:
            return self._blink_rate
        rate = rate & 0x03
        self._blink_rate = rate
        self._write_cmd(_HT16K33_BLINK_CMD | _HT16K33_BLINK_DISPLAYON
                        | rate << 1)

    def brightness(self, brightness):
        """
        设置像素点亮度

        :param brightness: 亮度级别,范围0~15.
        """
        if brightness < 0 or brightness > 15:
            raise ValueError("out of range,the brightness in 0~15")
        brightness = brightness & 0x0F
        self._brightness = brightness
        self._write_cmd(_HT16K33_CMD_BRIGHTNESS | brightness)

    def show(self):
        """
        显示生效
        """
        self.i2c.writeto_mem(self.address, 0x00, self.buffer)

    def fill(self, color):
        """
        填充所有

        :param color: 1亮;0灭
        """
        fill = 0xff if color else 0x00
        for i in range(16):
            self.buffer[i] = fill


class HT16K33Matrix(HT16K33):
    def __init__(self, i2c=i2c):
        super().__init__(i2c)

        self._fb_buffer = bytearray(self.WIDTH * self.HEIGHT * self.FB_BPP //
                                    8)
        self.framebuffer = framebuf.FrameBuffer(self._fb_buffer, self.WIDTH,
                                                self.HEIGHT, self.FORMAT)

        self.framebuffer.fill(0)
        self.pixel = self.framebuffer.pixel
        self.fill = self.framebuffer.fill
        self.text = self.framebuffer.text
        self.fill(0)
        self.show()

    def show(self):
        self._copy_buf()
        super().show()

    def bitmap(self, bitmap):
        for j in range(self.HEIGHT):
            for i in range(self.WIDTH):
                if bitmap[j] >> (7 - i) & 0x01:
                    self.pixel(i, j, 1)


class Matrix(HT16K33Matrix):
    """
    8x8点阵模块控制类

    :param i2c: I2C实例对象,默认i2c=i2c.
    """
    WIDTH = 8
    HEIGHT = 8
    FORMAT = framebuf.MONO_HLSB
    FB_BPP = 1

    def _copy_buf(self):
        for y in range(8):
            b = 0x00
            for i in range(8):

                b = ((self._fb_buffer[y] >> i) & 0x01) | b
                if i < 7:
                    b = b << 1

            self.buffer[y * 2] = b

    # commands
    _LCD_CLEARDISPLAY = const(0x01)
    _LCD_RETURNHOME = const(0x02)
    _LCD_ENTRYMODESET = const(0x04)
    _LCD_DISPLAYCONTROL = const(0x08)
    _LCD_CURSORSHIFT = const(0x10)
    _LCD_FUNCTIONSET = const(0x20)
    _LCD_SETCGRAMADDR = const(0x40)
    _LCD_SETDDRAMADDR = const(0x80)
    # flags for display entry mode
    _LCD_ENTRYRIGHT = const(0x00)
    _LCD_ENTRYLEFT = const(0x02)
    _LCD_ENTRYSHIFTINCREMENT = const(0x01)
    _LCD_ENTRYSHIFTDECREMENT = const(0x00)
    #flags for display on/off control
    _LCD_DISPLAYON = const(0x04)
    _LCD_DISPLAYOFF = const(0x00)
    _LCD_CURSORON = const(0x02)
    _LCD_CURSOROFF = const(0x00)
    _LCD_BLINKON = const(0x01)
    _LCD_BLINKOFF = const(0x00)
    #flags for display/cursor shift
    _LCD_DISPLAYMOVE = const(0x08)
    _LCD_CURSORMOVE = const(0x00)
    _LCD_MOVERIGHT = const(0x04)
    _LCD_MOVELEFT = const(0x00)
    #flags for function set
    _LCD_8BITMODE = const(0x10)
    _LCD_4BITMODE = const(0x00)
    _LCD_2LINE = const(0x08)
    _LCD_1LINE = const(0x00)
    _LCD_5x10DOTS = const(0x04)
    _LCD_5x8DOTS = const(0x00)


class HT16K33_SEG(HT16K33):
    def __init__(self, i2c=i2c):
        super().__init__(i2c)
        # 0 1 2 3 4 5 6 7 8 9 a b c d e f ' ' -
        self._TubeTab = [
            0xFC, 0x60, 0xDA, 0xF2, 0x66, 0xB6, 0xBE, 0xE0, 0xFE, 0xF6, 0xEE,
            0x3E, 0x1A, 0x7A, 0xDE, 0x8E, 0x00, 0x02]   

class MP3(object):
    """
    MP3模块控制类

    :param i2c: I2C实例对象,默认i2c=i2c.
    """

    def __init__(self, tx=-1, rx=-1, uart_num=1):
        self.uart = UART(uart_num, 9600, tx=tx, rx=rx)
        self.volume = 25

    def _cmdWrite(self, cmd):
        sum = 0
        for i in range(0, 6):
            sum += cmd[i]
        sum1 = ((0xFFFF - sum) + 1)
        sum_l = sum1 & 0xff
        sum_h = sum1 >> 8

        self.uart.write(bytearray([0x7E]))
        self.uart.write(cmd)
        self.uart.write(bytearray([sum_h]))
        self.uart.write(bytearray([sum_l]))
        self.uart.write(bytearray([0xEF]))
        sleep_ms(20)

    def play_song(self, num):
        """
        播放歌曲

        :param int num: 歌曲编号,类型为数字
        """
        var = bytearray([0xFF, 0x06, 0x03, 0x01, 0x00, num])
        self._cmdWrite(var)

    def play(self):
        """
        播放,用于暂停后的重新播放
        """
        var = bytearray([0xFF, 0x06, 0x0D, 0x01, 0x00, 0x00])
        self._cmdWrite(var)

    def playDir(self, dir, songNo):
        """
        播放指定文件夹指定歌曲

        :param int dir: 文件夹编号,类型数字
        :param int songNo: 歌曲编号,类型为数字
        """
        var = bytearray([0xFF, 0x06, 0x0F, 0x00, dir, songNo])
        self._cmdWrite(var)

    def playNext(self):
        """播下一首"""
        var = bytearray([0xFF, 0x06, 0x01, 0x00, 0x00, 0x00])
        self._cmdWrite(var)

    def playPrev(self):
        """播上一首"""
        var = bytearray([0xFF, 0x06, 0x02, 0x00, 0x00, 0x00])
        self._cmdWrite(var)

    def pause(self):
        """暂停播放"""
        var = bytearray([0xFF, 0x06, 0x0E, 0x01, 0x00, 0x00])
        self._cmdWrite(var)

    def stop(self):
        """停止播放"""
        var = bytearray([0xff, 0x06, 0x16, 0x00, 0x00, 0x00])
        self._cmdWrite(var)

    def volumeInc(self):
        """
        增加音量
        """
        self._vol += 1
        var = bytearray([0xFF, 0x06, 0x04, 0x00, 0x00, 0x00])
        self._cmdWrite(var)
        # 减小音量
    def volumeDec(self):
        """
        减小音量
        """
        self._vol -= 1
        var = bytearray([0xFF, 0x06, 0x05, 0x00, 0x00, 0x01])
        self._cmdWrite(var)

    def loop(self, songNo):
        """
        目录内指定序号歌曲循环播放

        :param int songNo: 歌曲编号,类型为数字
        """
        var = bytearray([0xFF, 0x06, 0x08, 0x00, 0x00, songNo])
        self._cmdWrite(var)

    def loopDir(self, dir):
        """
        指定目录内循环播放

        :param int dir: 文件夹编号,类型数字
        """
        # 指定目录内循环播放
        var = bytearray([0xFF, 0x06, 0x17, 0x00, dir, 0x01])
        self._cmdWrite(var)

    def singleLoop(self, onOff):
        """
        单曲循环开关

        :param int onOff: 0:不循环  1：循环
        """
        if onOff:
            var = bytearray([0xFF, 0x06, 0x19, 0x00, 0x00, 0x00])
        else:
            var = bytearray([0xFF, 0x06, 0x19, 0x00, 0x00, 0x01])
        self._cmdWrite(var)

    @property
    def volume(self):
        """
        设置或返回音量设置,范围0~30
        """
        return self._vol

    @volume.setter
    def volume(self, vol):
        # set volume range 0~30
        self._vol = vol
        var = bytearray([0xFF, 0x06, 0x06, 0x00, 0x00, self._vol])
        self._cmdWrite(var)

    def resetDevice(self):
        """复位MP3"""
        var = bytearray([0xFF, 0x06, 0x0C, 0x00, 0x00, 0x00])
        self._cmdWrite(var)

class MP3_(object):
    """
    MP3模块
    WT2003H4-16S
    2022.02.12
    """
    def __init__(self, tx=-1, rx=-1, uart_num=1):
        self.uart = UART(uart_num, 9600, stop=2, tx=tx, rx=rx)
        self._vol = 15
        self.is_paused = False
        self.set_output_mode(1)
        self.volume(15)

    def _cmdWrite(self, cmd):
        sum = 0
        len = 0
        for i in cmd:
            sum += i
            len += 1

        len += 2
        sum += len
        sum = sum & 0xff

        pakage = [0x7E, len]
        pakage += cmd
        pakage += ([sum, 0xEF])
        self.uart.write(bytearray(pakage))
        # print(len)
        # print(pakage)
        sleep_ms(100)

    def play_song(self, num):
        """
        播放歌曲
        :param int num: 歌曲编号,类型为数字
        """
        var = [0xA2, (num >> 8) & 0xff, num & 0xff]
        self._cmdWrite(var)

    def set_output_mode(self, mode):
        """设置音频输出模式：0：speaker 1: DAC"""
        var = [0xB6, mode]
        self._cmdWrite(var)  
    
    def set_play_mode(self, mode):
        """指定播放模式"""
        var = [0xAF, mode]
        self._cmdWrite(var)

    def pause(self):
        """暂停播放"""
        if self.is_paused == False:
            self.is_paused = True
            var = [0xAA]
            self._cmdWrite(var)

    def stop(self):
        """停止播放"""
        var = [0xAB]
        self._cmdWrite(var)

    def play(self):
        """
        播放,用于暂停后的继续播放
        """
        if self.is_paused:
            self.is_paused = False
            var = [0xAA]
            self._cmdWrite(var)

    def playNext(self):
        """播下一首"""
        var = [0xAC]
        self._cmdWrite(var)

    def playPrev(self):
        """播上一首"""
        var = [0xAD]
        self._cmdWrite(var)

    def volume(self, vol):
        """设置音量 0~30"""
        self._vol = vol
        var = [0xAE, vol]
        self._cmdWrite(var)
        sleep_ms(50)
        # while True:
        #     if(self.uart.any()):
        #         buff = self.uart.read(2)
                # print(buff)
                # break
    
    def song_num(self):
        """查询 SD 卡内音乐文件总数"""
        var = [0xC5]
        self._cmdWrite(var)
        while True:
            if(self.uart.any()):
                buff = self.uart.read(3)
                num = (buff[1] << 8) + buff[2]
                if(buff[0]==197):
                    return num
                else:
                    return 0

class IRRecv(object):
    """
    红外接收模块

    :param rx: 接收引脚设置
    :param uart_id: 串口号:1、2
    """

    def __init__(self, rx, uart_id=1):

        self.uart = UART(uart_id, baudrate=115200, rx=rx)

    def recv(self):
        """
        接收数据

        :return int: 返回红外值,类型整形
        """
        if self.uart.any():
            temp = self.uart.read()
            if temp is not None:
                return ustruct.unpack("B", temp)[0]
            else:
                return None


class IRTrans(object):
    """
    红外发射模块

    :param tx: 发送引脚设置
    :param uart_id: 串口号:1、2
    """

    def __init__(self, tx, uart_id=2):
        self.uart = UART(uart_id, baudrate=115200, tx=tx)

    def transmit(self, byte):
        """
        发送数据

        :param byte byte: 发送数据,单字节
        """
        self.uart.write(byte)


class DelveBit(object):
    """
    实验探究类的blue:bit,适用的模块有电压、电流、磁场、电导率、PH、光电门、气压、力传感器

    :param address: 模块的I2C地址,可再模块拨动选择不同的地址避免冲突。
    :param i2c: I2C实例对象,默认i2c=i2c
    """

    def __init__(self, address, i2c=i2c):
        self.i2c = i2c
        self.address = address

    def common_measure(self):
        """
        获取实验探究类传感器测量值的通用函数

        :return int: 返回传感器测量值,单位:电压(V)、电流(A)、磁场(mT)、电导率(uS/cm)、PH(pH)、光电门(s)、气压(kPa)、力传感器(N)
        """

        self.i2c.scan()
        temp = self.i2c.readfrom(self.address, 2)
        data = ustruct.unpack(">h", temp)
        sleep_ms(20)
        return round(data[0] / 100, 2)

    def _trigger_receive(self):
        self.i2c.scan()
        temp = self.i2c.readfrom(self.address, 5, True)
        if temp[0] in [0, 1]:
            return temp
        else:
            temp = b'\xff'
            return temp

    def photo_gate(self):
        """
        Photogate Timer 是用来记录刚触发时刻和触发结束时刻的时间。计算信号的正脉宽时间,当输入信号由低变高为触发开始点,由高变低位触发触发结束点,计算之间的时间差。

        :return int: 返回正脉宽时间,单位秒
        """
        old_start = b'\xff'
        while True:
            start = self._trigger_receive()
            if start[0] == 1 and old_start[0] == 255:
                trigger_begin = start[1] * 16777216 + start[2] * 65536 + start[
                    3] * 256 + start[4]
                old_end = start
                while True:
                    end = self._trigger_receive()
                    if old_end[0] == 0 and end[0] == 255:
                        trigger_end = old_end[1] * 16777216 + old_end[
                            2] * 65536 + old_end[3] * 256 + old_end[4]
                        trigger_time = (trigger_end - trigger_begin) / 2041667
                        # print("time:", trigger_time, trigger_begin,
                        #       trigger_end)
                        return trigger_time
                    else:
                        old_end = end
                        continue
            else:
                old_start = start
                continue


class EncoderMotor(object):
    """
    blue:bit编码电机驱动,提供pwm、cruise、position 三种驱动方式。

    :param address: 模块的I2C地址,可再模块拨动选择不同的地址避免冲突。
    :param i2c: I2C实例对象,默认i2c=i2c
    """

    PWM_MODE = b'\x05'
    """pwm模式"""

    CRUISE_MODE = b'\x0a'
    """巡航模式"""

    POSITION_MODE = b'\x0f'
    """定位模式"""

    def __init__(self, address, i2c=i2c):
        self.i2c = i2c
        self.address = address

    def _effect(self, mode):
        """
        生效
        """
        write_buf = b'\x00' + mode
        self.i2c.writeto(self.address, write_buf)
        sleep_ms(10)

    def motor_stop(self):
        """
        停止编码电机转动
        """

        self.i2c.writeto(self.address, b'\x00\x00')
        sleep_ms(10)

    def set_pwm(self, speed1, speed2):
        """
        pwm模式

        :param speed1: 设置M1通道编码电机速度,范围-1023~1023
        :param speed2: 设置M2通道编码电机速度,范围-1023~1023
        """
        if speed1 > 1023 or speed1 < -1023 or speed2 > 1023 or speed2 < -1023:
            raise ValueError("Speed out of range:-1023~1023")
        write_buf = b'\x06' + ustruct.pack('>HH', speed1, speed2)
        self.i2c.writeto(self.address, write_buf)
        sleep_ms(10)
        self._effect(self.PWM_MODE)

    def set_cruise(self, speed1, speed2):
        """
        Cruise巡航模式,设定速度后,当编码电机受阻时,会根据反馈,自动调整扭力,稳定在恒定的速度。

        :param speed1: 设置M1通道编码电机速度,范围-1023~1023
        :param speed2: 设置M2通道编码电机速度,范围-1023~1023
        """
        if speed1 > 1023 or speed1 < -1023 or speed2 > 1023 or speed2 < -1023:
            raise ValueError("Speed out of range:-1023~1023")
        write_buf = b'\x0a' + ustruct.pack('>HH', speed1, speed2)
        self.i2c.writeto(self.address, write_buf)
        sleep_ms(10)
        self._effect(self.CRUISE_MODE)

    def set_position(self, turn1, turn2):
        """
        定位模式,可设置编码编码电机定点位置,范围-1023~1023。

        :param turn1: 设置M1通道编码电机定位,-1023~1023
        :param turn2: 设置M2通道编码电机定位,-1023~1023
        """
        if turn1 > 1023 or turn1 < -1023 or turn2 > 1023 or turn2 < -1023:
            raise ValueError("Position out of range:0~1023")
        write_buf = b'\x10' + ustruct.pack('>ll', turn1, turn2)
        self.i2c.writeto(self.address, write_buf)
        sleep_ms(10)
        self._effect(self.POSITION_MODE)


class Rfid():
    """
    Rfid类,提供读写block和电子钱包操作。

    :param i2c: I2C实例对象
    :param serial_number: RFID卡序列号

    """

    import rfid

    def __init__(self, i2c, serial_number):
        self.i2c = i2c
        self._serial_number = serial_number
        self.purse_block = None

    def _get_serNum(self, serial_number):
        serNumCheck = 0
        buf = serial_number.to_bytes(4, 'little')
        for i in range(4):
            serNumCheck ^= buf[i]
        serNum_list = [int(i) for i in buf]
        serNum_list.append(serNumCheck)
        return (tuple(serNum_list))

    def serial_number(self):
        """
        获取序列号
        """
        return self._serial_number

    def _judge_block(self, block_number):
        """判断block是否可用。

        RFID卡内储存空间分为16 个扇区，每个扇区由4 块（块0、块1、块2、块3）组成，（我们也
        将16 个扇区的64 个块按绝对地址编号为0~63。第0 扇区的块0（即绝对地址0 块），它用于存放厂商代码，已经固化，不可更改。
        每个扇区的块0、块1、块2 为数据块，可用于存贮数据。

        :param block_number: 块编号
        """
        unused_blocked = [i*2 ^ 2-1 for i in range(1, 16)]
        unused_blocked.append(0)
        if block_number in unused_blocked:
            raise Exception(
                "This block {} can't be accessed!" .format(block_number))
        else:
            return True

    def auth(self, block_number=1):
        serNum = self._get_serNum(self._serial_number)
        if self._judge_block(block_number):
            self.rfid.init(self.i2c)
            if self.rfid.find_card():
                self.rfid.anticoll()
                if self.rfid.select_tag(serNum):
                    return self.rfid.auth(serNum, block_number)

    def read_block(self, block_number=1):
        """读取块数据,长度16字节

        :param block_number: 块编号
        """
        self.auth(block_number)
        return self.rfid.read_block(block_number)

    def write_block(self, buf, block_number=1):
        """写块数据,长度16字节

        :param bytes buf: 块编号
        :param int block_number: 块编号
        """
        self.auth(block_number)
        return self.rfid.write_block(block_number, buf)

    def set_purse(self, block_number=1):
        """
        设置电子钱包,默认使用block 1。

        :param int block_number: 块编号
        """
        if block_number != 1:
            self.purse_block = block_number
        else:
            self.purse_block = 1
        self.auth(self.purse_block)
        return self.rfid.set_purse(self.purse_block)

    def get_balance(self):
        """
        获取电子钱包余额。使用该函数前,必须对数据块进行 ``set_purse()`` 设置。

        :return: 返回余额
        """
        if self.purse_block is None:
            self.purse_block = 1
        self.auth(self.purse_block)
        return self.rfid.balance(self.purse_block)

    def increment(self, value):
        """
        给电子钱包充值。使用该函数前,必须对数据块进行 ``set_purse()`` 设置。

        :param int value: 充值 
        """
        if self.purse_block is None:
            self.purse_block = 1
        self.auth(self.purse_block)
        return self.rfid.increment(self.purse_block, value)

    def decrement(self, value):
        """
        给电子钱包扣费。使用该函数前,必须对数据块进行 ``set_purse()`` 设置。

        :param int value: 扣费 
        """
        if self.purse_block is None:
            self.purse_block = 1
        self.auth(self.purse_block)
        return self.rfid.decrement(self.purse_block, value)


class Scan_Rfid():
    """扫描Rfid卡类.
    """
    import rfid

    @classmethod
    def scanning(cls, i2c=i2c):
        """
        扫描RFID卡,返回Rfid对象

        :param obj i2c: I2C实例对象
        :return: 返回Rfid对象
        """
        cls.rfid.init(i2c)
        if cls.rfid.find_card():
            serial_tuple = cls.rfid.anticoll()
            if serial_tuple:
                serial_num = int.from_bytes(bytes(serial_tuple[:-1]), 'little')
                print("find card: {}" .format(serial_num))
                return Rfid(i2c, serial_num)

class GasSensor():
    '''
    乐动模块 烟雾传感器
    '''
    def __init__(self, pin):
        '''初始化参数，引脚'''
        self.pin = MPythonPin(pin, PinMode.ANALOG)
        self.threshold = 2000 

    def detect(self):
        '''是否探测到，布尔类型True/False'''
        tmp = self.pin.read_analog()
        if(tmp>=self.threshold):
            return True
        else:
            return False

    def get_raw_val(self):
        '''获取烟雾传感器裸数据，模拟值'''
        return self.pin.read_analog()

    def set_threshold(self, threshold):
        '''设置烟雾传感器阈值，模拟值'''
        self.threshold = threshold

class IRObstacle():
    '''
    乐动模块 红外感应传感器
    '''
    def __init__(self, pin):
        '''初始化参数，引脚'''
        self.pin = MPythonPin(pin, PinMode.ANALOG)
        self.threshold = 1500 #默认阈值

    def detect(self):
        '''是否探测到，布尔类型True/False'''
        tmp = self.pin.read_analog()
        if(tmp<=self.threshold):
            return True
        else:
            return False

    def get_raw_val(self):
        '''获取红外探测传感器裸数据，模拟值'''
        return self.pin.read_analog()

    def set_threshold(self, threshold):
        '''设置红外探测传感器阈值，模拟值'''
        self.threshold = threshold

class SoilHumiditySensor():
    '''乐动模块 土壤湿度'''
    def __init__(self, pin):
        self.pin = MPythonPin(pin, PinMode.ANALOG)
        self.threshold = 2500 

    def detect(self):
        '''是否探测到，布尔类型True/False'''
        tmp = self.get_raw_val()
        if(tmp<=self.threshold):
            return True
        else:
            return False

    def get_raw_val(self):
        '''获取土壤湿度传感器裸数据，模拟值:1600-2600 映射 4095-0 '''
        _soil_humidity =  self.pin.read_analog()
        if _soil_humidity > 2600:
            _soil_humidity = 2600
            return int(numberMap(_soil_humidity,1600,2600,4095,0))
        elif _soil_humidity < 1600:
            _soil_humidity = 1600
            return int(numberMap(_soil_humidity,1600,2600,4095,0))
        else:
            return int(numberMap(_soil_humidity,1600,2600,4095,0))

    def set_threshold(self, threshold):
        '''设置土壤湿度传感器阈值，模拟值'''
        self.threshold = threshold


    def __init__(self, tx=Pin.P16, rx=Pin.P15, uart_num=1):
        self.uart = UART(uart_num, baudrate=115200, rx=rx, tx=tx)
        self.identifying_word = -1

    def any(self):
        sleep_ms(10)
        if(self.uart.any()):
            self.recognition()
            return True
        else:
            return False
    
    def recognition(self):
        try:
            self.identifying_word = int(self.uart.read().decode('UTF-8','ignore'))
        except Exception as e:
            self.identifying_word = -1
            pass