# from mpython import *
# import audio

# r = audio.recorder()
# r.start('file://test.wav', format=r.WAV, maxtime=5, endcb=None)
# r.start('file://test.amr', format=r.AMR, maxtime=5, endcb=None)

from mpython import *
import audio
import os
import gc
import machine

my_wifi = wifi()
my_wifi.connectWiFi("labplus_dev", "helloworld")

#  audio.play('http://cdn.makeymonkey.com/test/32_%E6%8B%94%E8%90%9D%E5%8D%9C.mp3')
# audio.play('http://downsc.chinaz.net/Files/DownLoad/sound1/201906/11582.mp3')
# audio.play('https://dl.espressif.cn/dl/audio/ff-16b-2c-44100hz.mp3')
# audio.play("https://github.com/schreibfaul1/ESP32-audioI2S/raw/master/additional_info/Testfiles/sample.opus")
# audio.play('https://github.com/schreibfaul1/ESP32-audioI2S/raw/master/additional_info/Testfiles/Pink-Panther.wav')
# audio.play('https://samplelib.com/lib/preview/wav/sample-3s.wav')
# audio.play('http://192.168.10.24:8000/music/test.mp3')
# audio.play('http://192.168.10.24:8000/music/test_44100.aac')
# def cb(state):
#     print(state)

# p = audio.player(cb)
# # p.play('file://test.wav', pos=0, sync=False)
# # p.play('file://pluck-pcm16.wav', pos=0, sync=False)
# p.play('file://pluck-pcm8.wav', pos=0, sync=False)
# p.play('file://test.mp3', pos=0, sync=False)
# # p.play('file://test.amr', pos=0, sync=False)
# from mpython import *
# import audio
# import network

# my_wifi = wifi()

# my_wifi.connectWiFi("labplus_dev", "helloworld")

# # p.play('http://cdn.makeymonkey.com/test/32_%E6%8B%94%E8%90%9D%E5%8D%9C.mp3', pos=0, sync=False)
# # p.play('https://dl.espressif.cn/dl/audio/ff-16b-2c-44100hz.mp3', pos=0, sync=False)
# p.play('http://downsc.chinaz.net/Files/DownLoad/sound1/201906/11582.mp3', pos=0, sync=False)

# p.play('https://samplelib.com/lib/preview/wav/sample-3s.wav', pos=0, sync=False)

# # import os
# # os.umount('/')
# # os.VfsFat.mkfs(bdev)
# # os.mount(bdev, '/')
