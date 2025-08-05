UTC=3155673600
UTC_P1=3155670000
UTC_P2=3155666400
UTC_P3=3155662800
UTC_P4=3155659200
UTC_P5=3155655600
UTC_P6=3155652000
UTC_P7=3155648400
UTC_P8=3155644800
UTC_P9=3155641200
UTC_P10=3155637600
UTC_P11=3155634000
UTC_P12=3155630400
UTC_R1=3155677200
UTC_R2=3155680800
UTC_R3=3155684400
UTC_R4=3155688000
UTC_R5=3155691600
UTC_R6=3155695200
UTC_R7=3155698800
UTC_R8=3155702400
UTC_R9=3155706000
UTC_R10=3155709600
UTC_R11=3155713200
UTC_R12=3155716800

import time
import machine
import ntptime

def sync_ntp(utc=8,host='ntp1.aliyun.com'):
    """通过网络校准时间""" 
    print("开始同步网络时间")
    try:
        NTP_DELTA = UTC_P8
        if(utc==0):
            NTP_DELTA = UTC
        elif(utc==1):
            NTP_DELTA = UTC_P1
        elif(utc==2):
            NTP_DELTA = UTC_P2
        elif(utc==3):
            NTP_DELTA = UTC_P3
        elif(utc==4):
            NTP_DELTA = UTC_P4
        elif(utc==5):
            NTP_DELTA = UTC_P5
        elif(utc==6):
            NTP_DELTA = UTC_P6
        elif(utc==7):
            NTP_DELTA = UTC_P7
        elif(utc==8):
            NTP_DELTA = UTC_P8
        elif(utc==9):
            NTP_DELTA = UTC_P9
        elif(utc==10):
            NTP_DELTA = UTC_P10
        elif(utc==11):
            NTP_DELTA = UTC_P11
        elif(utc==12):
            NTP_DELTA = UTC_P12
        elif(utc==-1):
            NTP_DELTA = UTC_R1
        elif(utc==-2):
            NTP_DELTA = UTC_R2
        elif(utc==-3):
            NTP_DELTA = UTC_R3
        elif(utc==-4):
            NTP_DELTA = UTC_R4
        elif(utc==-5):
            NTP_DELTA = UTC_R5
        elif(utc==-6):
            NTP_DELTA = UTC_R6
        elif(utc==-7):
            NTP_DELTA = UTC_R7
        elif(utc==-8):
            NTP_DELTA = UTC_R8
        elif(utc==-9):
            NTP_DELTA = UTC_R9
        elif(utc==-10):
            NTP_DELTA = UTC_R10
        elif(utc==-11):
            NTP_DELTA = UTC_R11
        elif(utc==-12):
            NTP_DELTA = UTC_R12

        ntptime.NTP_DELTA = NTP_DELTA  # 可选 UTC+8偏移时间（秒），不设置就是UTC0
        ntptime.host = host  # 可选，ntp服务器，默认是"pool.ntp.org" 这里使用阿里服务器
        ntptime.settime()  # 修改设备时间,到这就已经设置好了
        
        mytime=time.localtime()
        mytime=(mytime[0],mytime[1],mytime[2],mytime[6],mytime[3]+utc,mytime[4],mytime[5],mytime[7])
        machine.RTC().datetime(mytime)
        print(mytime)
        # print(time.localtime())
    except Exception as e:
        # print('sync ntp error:{}'.format(e))
        print("同步ntp时间错误",repr(e))