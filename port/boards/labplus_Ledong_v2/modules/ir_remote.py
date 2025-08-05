from machine import Pin,PWM
import time
import utime
import _thread
import machine
import gc

class _Const:
    """ NEC Const """
    # 引导码：9000us 的载波+ 4500us  的空闲
    # 比特值“0”：560us 的载波+ 560us 的空闲
    # 比特值“1”：560us 的载波+ 1690us 的空闲
    NEC_HDR_MARK = 9000
    NEC_HDR_SPACE = 4500

    NEC_BIT_MARK = 560 
    NEC_ONE_SPACE = 1690
    NEC_ZERO_SPACE = 560

    NEC_RPT_SPACE = 2250

    TOLERANCE = 0.3
    STARTDATAINDEX = 2

class IRReceiver(object):
    CODE = {
        176: 0, 0: 1, 128: 2, 64: 3,32: 4, 160: 5, 96: 6,16: 7, 144: 8, 80: 9, 
        48:12, 112:14, 136: 17, 152: 25, 40:20, 104:22, 168:21
        }
 
    def __init__(self, pin):
        self.irRecv = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.irRecv.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=self.__handler)  # 配置中断信息
        self.ir_step = 0
        self.ir_count = 0
        self.buf64 = [0 for i in range(64)]
        self.recived_ok = False
        self.cmd = None
        self.cmd_last = None
        self.repeat = 0
        self.repeat_last = None
        self.t_ok = None
        self.t_ok_last = None
        self.start = 0
        self.start_last = 0        
        self.changed = False
 
    def __handler(self, source):
        """
        中断回调函数
        """
        thisComeInTime = utime.ticks_us()
 
        # 更新时间
        curtime = utime.ticks_diff(thisComeInTime, self.start)
        self.start = thisComeInTime
        
 
        if curtime >= 8500 and curtime <= 9500:
            self.ir_step = 1
            return
 
        if self.ir_step == 1:
            if curtime >= 4000 and curtime <= 5000:
                self.ir_step = 2
                self.recived_ok = False
                self.ir_count = 0
                self.repeat = 0
            elif curtime >= 2000 and curtime <= 3000:  # 长按重复接收
                self.ir_step = 3
                self.repeat += 1
 
        elif self.ir_step == 2:  # 接收4个字节
            self.buf64[self.ir_count] = curtime
            self.ir_count += 1
            if self.ir_count >= 64:
                self.recived_ok = True
                self.t_ok = self.start #记录最后ok的时间
                self.ir_step = 0
 
        elif self.ir_step == 3:  # 重复
            if curtime >= 500 and curtime <= 650:
                self.repeat += 1
 
    def __check_cmd(self):
        byte4 = 0
        for i in range(32):
            x = i * 2
            t = self.buf64[x] + self.buf64[x+1]
            byte4 <<= 1
            if t >= 1800 and t <= 2800:
                byte4 += 1
        user_code_hi = (byte4 & 0xff000000) >> 24
        user_code_lo = (byte4 & 0x00ff0000) >> 16
        data_code = (byte4 & 0x0000ff00) >> 8
        data_code_r = byte4 & 0x000000ff
        self.cmd = data_code
 
    def scan(self):        
        # 接收到数据
        if self.recived_ok:
            self.__check_cmd()
            self.recived_ok = False
            
        # 数据有变化
        if self.cmd != self.cmd_last or self.repeat != self.repeat_last or self.t_ok != self.t_ok_last:
            self.changed = True
        else:
            self.changed = False
 
        # 更新
        self.cmd_last = self.cmd
        self.repeat_last = self.repeat
        self.t_ok_last = self.t_ok
        # 对应按钮字符
        # print(self.cmd)
        s = self.CODE.get(self.cmd)
    
        return self.changed, s, self.repeat, self.t_ok, self.cmd

    def _ir_recv_daemon(self):
        while(True):
            # time.sleep_ms(100)
            try:
                changed, s, repeat, t_ok, cmd = self.scan()
            except Exception as e:
                pass
            if(changed and cmd!=None):
                if self.callback:
                    self.callback(cmd & 0xff, s)

    def daemon(self):
        _thread.start_new_thread(self._ir_recv_daemon, ())

    def set_callback(self,callback = None):
        self.callback = callback