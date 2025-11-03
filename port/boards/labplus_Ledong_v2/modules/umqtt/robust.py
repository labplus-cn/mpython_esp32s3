import utime
from time import sleep_ms
from . import simple

class MQTTClient(simple.MQTTClient):
    DELAY = 2
    DEBUG = False

    def delay(self, i):
        utime.sleep(self.DELAY)

    def log(self, in_reconnect, e):
        if self.DEBUG:
            if in_reconnect:
                print("mqtt reconnect: %r" % e)
            else:
                print("mqtt: %r" % e)

    def reconnect(self):
        i = 0
        while 1:
            try:
                return super().connect(False)
            except OSError as e:
                self.log(True, e)
                i += 1
                self.delay(i)

    def publish(self, topic, msg, retain=False, qos=0):
        sleep_ms(5)
        while 1:
            try:
                return super().publish(topic, msg, retain, qos)
            except OSError as e:
                self.log(False, e)
            self.reconnect()

    def wait_msg(self):
        while 1:
            try:
                return super().wait_msg()
            except OSError as e:
                self.log(False, e)
            self.reconnect()


import ubinascii

def get_urlSafe(text, type):
    if type:
        utf8_bytes = text.encode('utf-8')
        base64_bytes = ubinascii.b2a_base64(utf8_bytes)
        base64_str = base64_bytes.decode().strip()
        url_safe_str = base64_str.replace('+', '-').replace('/', '_').rstrip('=')
        return url_safe_str
    else:
        url_safe_str = text.decode('utf-8', 'ignore')
        base64_str = url_safe_str.replace('-', '+').replace('_', '/')
        padding_needed = 4 - (len(base64_str) % 4)
        if padding_needed != 4:
            base64_str += '=' * padding_needed
        utf8_bytes = ubinascii.a2b_base64(base64_str.encode())
        return utf8_bytes