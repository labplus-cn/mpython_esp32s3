import machine
import AIcamera
from mpython import button_a
from utils import set_key_config

isDetect = False

def cb(_):
    global isDetect
    isDetect = True



def on_button_a_pressed(_):
    machine.reset()

button_a.event_pressed = on_button_a_pressed

def init():
    set_key_config({
        'button_a_key_cb': lambda: None,
        'button_b_key_cb': lambda: None
    })
    AIcamera.init(AIcamera.FACE_DETECTION,cb)