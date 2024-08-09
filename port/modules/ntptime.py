try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct

# (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
NTP_DELTA = 3155673600

def time(host):
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1b
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2)
    res = s.sendto(NTP_QUERY, addr)
    msg = s.recv(48)
    s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    return val - NTP_DELTA

# There's currently no timezone support in MicroPython, so
# utime.localtime() will return UTC time (as if it was .gmtime())
# add timezone org,default 8
def settime(timezone=8, server='ntp.ntsc.ac.cn'):
    import machine
    import utime
    t1= utime.ticks_ms()
    while True:
        if utime.ticks_diff(utime.ticks_ms(), t1) > 5000:
            raise OSError('Timeout,ntp server not response.')
        try:
            t = time(server)
        except OSError:
            pass
        else:
            break
    t = t + (timezone * 60 * 60)
    tm = utime.localtime(t)
    tm = tm[0:3] + (0, ) + tm[3:6] + (0, )
    machine.RTC().datetime(tm)
    print(utime.localtime())
