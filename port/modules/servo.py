# servo module for MicroPython on ESP32
# MIT license; Copyright (c) 2024.11.19 zhaohuijiang diskman88@163.com

from machine import PWM, Pin

pins_remap_esp32 = (1, 2, 3, 4, 5, 0, 7, 8, 15, 16, 6, 46, 21, 17, 18, 48, 47, -1, -1, 34, 35, 33, -1, 9, 10, 11, 12, 13, 14)
class Servo(object):
    def __init__(self,pin, freq = 50, angle = 0, min_us = 750, max_us = 2250, actuation_range = 180):
        self.freq = freq
        self.angle = angle
        self.min_us = min_us
        self.max_us = max_us
        self.actuation_range = actuation_range
        self.pin_id = pins_remap_esp32[pin]
        self.pwm = PWM(Pin(self.pin_id, Pin.OUT))
        self.pwm.freq(self.freq)
        self.write_angle(0)

    def freq(self, freq = 50):
        self.freq = freq
        self.pwm.freq(freq)

    def write_angle(self, angle):
        self.angle = angle
        if self.angle > self.actuation_range:
            self.angle = self.actuation_range
        if self.angle < 0:
            self.angle = 0
        us_range = self.max_us - self.min_us
        us = self.min_us + (int)(self.angle * us_range / self.actuation_range)
        duty = (int)((us * 1023)/ 20000)
        self.pwm.duty(duty)

# ser = Servo(0)
# ser.write_angle(30)
