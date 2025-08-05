# NeoPixel driver for MicroPython
# MIT license; Copyright (c) 2016 Damien P. George, 2021 Jim Mussared

from machine import bitstream


class NeoPixel:
    # G R B W
    ORDER = (1, 0, 2, 3)

    def __init__(self, pin, n, bpp=3, timing=1,brightness=1.0):
        self.pin = pin
        self.n = n
        self.bpp = bpp
        self.buf = bytearray(n * bpp)
        self.pin.init(pin.OUT)
        self._brightness = brightness
        # Timing arg can either be 1 for 800kHz or 0 for 400kHz,
        # or a user-specified timing ns tuple (high_0, low_0, high_1, low_1).
        self.timing = (
            ((400, 850, 800, 450) if timing else (800, 1700, 1600, 900))
            if isinstance(timing, int)
            else timing
        )

    def __len__(self):
        return self.n

    def __setitem__(self, i, v):
        offset = i * self.bpp
        for i in range(self.bpp):
            self.buf[offset + self.ORDER[i]] = v[i]

    def __getitem__(self, i):
        offset = i * self.bpp
        return tuple(self.buf[offset + self.ORDER[i]] for i in range(self.bpp))

    def fill(self, v):
        b = self.buf
        l = len(self.buf)
        bpp = self.bpp
        for i in range(bpp):
            c = v[i]
            j = self.ORDER[i]
            while j < l:
                b[j] = int(c * self._brightness)
                j += bpp

    def write(self):
        # BITSTREAM_TYPE_HIGH_LOW = 0
        if self._brightness > 0.99:
            # neopixel_write(self.pin, self.buf, self.timing)
            bitstream(self.pin, 0, self.timing, self.buf)
        else:
            # neopixel_write(self.pin, bytearray([int(i * self._brightness) for i in self.buf]), self.timing)
            bitstream(self.pin, 0, self.timing, bytearray([int(i * self._brightness) for i in self.buf]))
        
    def brightness(self, brightness):
        self._brightness = min(max(brightness, 0.0), 1.0)
