from machine import Pin, UART
from .k230_ai import *
import time
import gc

class EduSmartCamera:
    def __init__(self, rx=Pin.P0, tx=Pin.P1):
        self.uart = UART(2, baudrate=1152000, rx=rx, tx=tx ,rxbuf=256)
        self.mode = DEFAULT_MODE
        self.lock = False
        time.sleep(0.2)
        self.wait_for_ai_init()
        self.thread_listen()

    def wait_for_ai_init(self): 
        self.lock = True
        num = 0        
        while True:
            gc.collect()
            time.sleep_ms(50)
            num +=1
            CMD_TEMP = []
            if(num>5000):
                print('错误:通信超时，请检查接线情况及掌控拓展电源是否打开！')
                print('Error: Communication timeout, please check the wiring and control whether the expansion power is turned on!')
                break
            AI_Uart_CMD(self.uart,0x01,0xFF) # 发送k230
            if(self.uart.any()):
                head = self.uart.read(2)
                if(head and head[0] == 0xBB and head[1] == 0xAA):
                    CMD_TEMP.extend([0xBB,0xAA])
                    cmd_type = self.uart.read(1)
                    CMD_TEMP.append(cmd_type[0])
                    if(CMD_TEMP[2]==0x01):
                        res = self.uart.read(9)
                        if(res[0]==0x01 and res[1]==0xFF):
                            print("AI摄像头4.0初始化完成")
                            print("AI camera 4.0 init end")
                            time.sleep(0.3)
                            _cmd = self.uart.read()
                            del _cmd
                            gc.collect()
                            self.lock = False
                            break
                else:
                    _cmd = self.uart.read()
                    del _cmd
                    gc.collect()
    
    def model_init(self,cur_state):
        if(self.mode == cur_state):
            print('模式相同')
            return
        elif(cur_state==DEFAULT_MODE):
            for i in range(10):
                AI_Uart_CMD(self.uart,DEFAULT_MODE,0x01)
                time.sleep_ms(50) 
        elif(cur_state==FACE_DETECTION_MODE):
            self.face_detect = FACE_DETECT(self.uart)
        elif(cur_state==HAND_DETECTION):
            self.hand_detect = HandDetect(self.uart)
        elif(cur_state==HAND_KEYPOINT_CLASS):
            self.hand_keypoint_class = HandKeypointClass(self.uart)
        elif(cur_state==DYNAMIC_GESTURE):
            self.dynamic_gesture = DG(self.uart)
        elif(cur_state==LICENSE_PLATE_RECOGNITION):
            self.lpr = LPR(self.uart)
        elif(cur_state==PERSON_DETECTION):
            self.person_detect = PersonDetect(self.uart)
        elif(cur_state==PERSON_KEYPOINT_DETECT):
            self.person_keypoint_detect = PersonKeypointDetct(self.uart)
        elif(cur_state==PERSON_KEYPOINT_DETECT_PLUS):
            self.person_keypoint_detect_plus = PersonKeypointDetctPlus(self.uart)
        elif(cur_state==FACE_LANDMARK_LIVING_BODY):
            self.face_living_body = FaceLivingBodyDetct(self.uart)
        elif(cur_state==FACE_LANDMARK_EXPRESSION):
            self.face_expression = FaceExpressionDetct(self.uart)
        elif(cur_state==OBJECT_RECOGNIZATION_MODE):
            self.yolo_detect = YOLO80(self.uart)
        elif(cur_state==FALL_DETECTION):
            self.fall = FallDetection(self.uart)
        elif(cur_state==QRCODE_MODE):
            self.qrcode = QRCodeRecognization(self.uart)
        elif(cur_state==BARCODE_MODE):
            self.bar_code = BarCodeRecognization(self.uart)
        elif(cur_state==FACE_RECOGNITION_MODE):
            self.fcr = FaceRecogization(self.uart)
            
        self.mode = cur_state
    
    # def face_detect_init(self):
    #     self.face_detect = FACE_DETECT(self.uart)
    #     self.mode = FACE_DETECTION_MODE

    # def face_recognize_init(self):
    #     self.fcr = Face_recogization(self.uart)
    #     self.mode = FACE_RECOGNIZATION_MODE

    def init(self, *args, **kwargs):
        args_list = []
        self.model_choose = kwargs.get('model', None)
        for arg in args:
            args_list.append(arg)
        args_len = len(args_list)
        if(self.model_choose is None and args_len<1):
            print('参数错误')
        else:
            self.model_choose = args_list[0]
        
        if(self.model_choose=='FACE_RECOGNIZE'):
            self.model_init(31)
        elif(self.model_choose=='FACE_DETECT'):
            self.model_init(1)
        elif(self.model_choose=='BLINK_OPEN_DETECT'):
            self.model_init(27)
    
    def result(self):
        d = {"id":None,"similarity":None,"status": 0}
        if(self.mode == FACE_RECOGNITION_MODE):
            self.fcr.recognize()
            d = {"id":None,"similarity":None,"status": 0}
            if(self.fcr.id!=None):
                d = {"id":self.fcr.id ,"similarity":self.fcr.score,"status": 1}
            else:
                d = {"id":None,"similarity":None,"status": 0}
            return d
        elif(self.mode == FACE_DETECTION_MODE):
            self.face_detect.recognize()
            d = {"face_num":None,"similarity":None,"status": 0}
            if(self.face_detect.face_num!=None):
                d = {"face_num":self.face_detect.face_num ,"similarity":None,"status": 1}
            else:
                d = {"face_num":None,"similarity":None,"status": 0}
            return d
        elif(self.mode == FACE_LANDMARK_LIVING_BODY):
            self.face_living_body.recognize()
            d = {"blink_counter":None,"mouth_counter":None,"status": 0}
            if(self.face_living_body.mouth_blink_counter[0]!=0):
                d = {"blink_counter":self.face_living_body.mouth_blink_counter[0] ,"mouth_counter":self.face_living_body.mouth_blink_counter[1],"status": 1}
            return d
        else:
            return d

    def thread_listen(self):
        self._task = TASK(func=self.uart_thread,sec=0.01)
        self._task.start()

    def uart_thread(self):           
        gc.collect()
        try:          
            if(self.lock==False):
                CMD = uart_handle(self.uart)
                
                if(CMD==None or len(CMD)==0):
                    return

                if(self.mode==DEFAULT_MODE):
                    pass
                elif(self.mode==FACE_RECOGNITION_MODE and self.fcr!=None):
                    if(len(CMD)>0):
                        if(CMD[3]==FACE_RECOGNITION_MODE and CMD[4]==0x01):
                            if(CMD[5]==0xff):
                                self.fcr.lock = True
                                self.fcr.id,self.fcr.score = None,None
                            elif(CMD[5]==0xfe):
                                self.fcr.lock = True
                                self.fcr.id,self.fcr.score = -1,0
                            else:
                                self.fcr.lock = True
                                self.fcr.id,self.fcr.score = CMD[5],round(int(CMD[6])/100,3)
                elif(self.mode==FACE_DETECTION_MODE and self.face_detect!=None):
                    if(len(CMD)>0):
                        if(CMD[3]==FACE_DETECTION_MODE and CMD[4]==0x01):
                            if(CMD[5]==0xff):
                                self.face_detect.lock = True
                                self.face_detect.face_num = None
                            else:
                                self.face_detect.face_num = CMD[5]
                elif(self.mode==FACE_LANDMARK_LIVING_BODY and self.face_living_body!=None):
                    if(len(CMD)>0):
                        if(CMD[3]==FACE_LANDMARK_LIVING_BODY and CMD[4]==0x01):
                            if(CMD[5]==0xff):
                                self.face_living_body.lock = True
                                self.face_living_body.mouth_blink_counter = [0,0]
                            else:
                                self.face_living_body.lock = True
                                self.face_living_body.mouth_blink_counter = CMD[5],CMD[6]
        
        except Exception as e:
            print(e)
    