from machine import Pin, UART
from lib.k230_ai import *
import time
import gc
gc.collect()

class SmartCameraK230:
    def __init__(self, tx=Pin.P16, rx=Pin.P15):
        self.uart = UART(2, baudrate=1152000, rx=rx, tx=tx, rxbuf=256)
        # self.uart = UART(2, baudrate=1152000, rx=rx, tx=tx)
        self.mode = DEFAULT_MODE
        self.lock = False
        time.sleep(0.1)
        self.wait_for_ai_init()
        self.thread_listen()
        self.slc_parameter = [3, 15, 11, 1]
        self.a_status = 0
        self.b_status = 0
        self.tf_status = 0
        self.tf_sn = ''

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
    
    def switcher_mode(self, mode):
        self.model_init(mode) # mode 0默认 1人脸检测

    def color_obj_count_init(self,cur_mode):
        self.color_obj_count = ColorCount(self.uart, cur_mode=cur_mode)
        self.mode = COLOR_OBJECT_COUNT_MODE
    
    def lab_color_count_init(self,color):
        self.lab_color_count = LABColorCount(self.uart, color=color)
        self.mode = LAB_COLOR_OBJECT_COUNT_MODE

    def classify_kmodel_init(self, param={"kmodel_path":'/data/xxx.kmodel', "labels":["0","1","2"], "confidence_threshold":0.3, "nms_threshold":0.45, "max_boxes_num":50}):
        self.classify_model = ClassifyMODEL(self.uart, param)
        self.mode = CLASSIFY_MODEL_MODE 
    
    def detect_kmodel_init(self, param={"kmodel_path":'/data/xxx.kmodel', "labels":["0","1","2"], "confidence_threshold":0.3, "nms_threshold":0.45, "max_boxes_num":50}):
        self.detect_kmodel = DetectMODEL(self.uart, param)
        self.mode = DETECT_MODEL_MODE 
    
    # def led(self,mode=0):
    #     AI_Uart_CMD(self.uart, 0x01, 0xFA, [0x04,int(mode)])
    #     time.sleep_ms(20)
    
    # def factory_init(self):
    #     self.mode = FACTORY_MODE
    #     AI_Uart_CMD(self.uart, 0x01, FACTORY_MODE, [0x01])
    #     time.sleep(1)
    
    # def factory_lcd(self):
    #     AI_Uart_CMD(self.uart, 0x01, FACTORY_MODE, [0x02])
    #     time.sleep(1) 
    
    # def factory_sensor(self):
    #     AI_Uart_CMD(self.uart, 0x01, FACTORY_MODE, [0x03])
    #     time.sleep(1)  
    
    # def factory_rgb(self,r=0,g=0,b=0):
    #     AI_Uart_CMD(self.uart, 0x01, FACTORY_MODE, [0x04,int(r),int(g),int(b)])
    #     time.sleep(1)
    
    # def factory_light(self,light=1):
    #     AI_Uart_CMD(self.uart, 0x01, FACTORY_MODE, [0x05])
    #     time.sleep(1)   
    
    # def factory_write_sn(self,sn='sn'):
    #     _str = str([sn])
    #     AI_Uart_CMD_String(uart=self.uart, cmd=FACTORY_MODE, cmd_type=0x01, str_buf=_str)
    #     time.sleep(1)

    def thread_listen(self):
        self._task = TASK(func=self.uart_thread,sec=0.005)
        self._task.start()

    def uart_thread(self): 
        gc.collect()
        try:          
            if(self.lock==False):
                CMD = uart_handle(self.uart)
                # print(CMD)
                # print('uart_thread CMD==========')
                if(CMD==None or len(CMD)==0):
                    return

                if(self.mode==DEFAULT_MODE):
                    pass
                elif(self.mode==OBJECT_RECOGNIZATION_MODE and self.yolo_detect!=None):
                    if(len(CMD)>0):
                        if(CMD[3]==OBJECT_RECOGNIZATION_MODE and CMD[4]==0x01):
                            if(CMD[5]==0xff):
                                self.yolo_detect.lock = True
                                self.yolo_detect.id,self.yolo_detect.max_score,self.yolo_detect.objnum = None,0,0
                            else:
                                self.yolo_detect.id,self.yolo_detect.max_score,self.yolo_detect.objnum = CMD[5],round(int(CMD[6])/100,2),CMD[7]
                elif(self.mode==FACE_DETECTION_MODE and self.face_detect!=None):
                    if(len(CMD)>0):
                        if(CMD[3]==FACE_DETECTION_MODE and CMD[4]==0x01):
                            if(CMD[5]==0xff):
                                self.face_detect.lock = True
                                self.face_detect.face_num = None
                            else:
                                self.face_detect.face_num = CMD[5]
                elif(self.mode==HAND_DETECTION and self.hand_detect!=None):
                    if(len(CMD)>0):
                        if(CMD[3]==HAND_DETECTION and CMD[4]==0x01):
                            if(CMD[5]==0xff):
                                self.hand_detect.lock = True
                                self.hand_detect.flag = False
                            elif(CMD[5]==0xee):
                                self.hand_detect.lock = True
                                self.hand_detect.flag = True
                elif(self.mode==HAND_KEYPOINT_CLASS and self.hand_keypoint_class!=None):
                    if(len(CMD)>0):
                        if(CMD[3]==HAND_KEYPOINT_CLASS and CMD[4]==0x01):
                            if(CMD[5]==0xff):
                                self.hand_keypoint_class.lock = True
                                self.hand_keypoint_class.gesture_id = None
                                self.hand_keypoint_class.gesture_str = None
                            else:
                                self.hand_keypoint_class.gesture_id = CMD[5]
                                self.hand_keypoint_class.gesture_str = HAND_KEYPOINT_CLASS_GESTURE[CMD[5]]
                elif(self.mode==DYNAMIC_GESTURE and self.dynamic_gesture!=None):
                    if(len(CMD)>0):
                        if(CMD[3]==DYNAMIC_GESTURE and CMD[4]==0x01):
                            if(CMD[5]==0xff):
                                self.dynamic_gesture.lock = True
                                self.dynamic_gesture.gesture_id,self.dynamic_gesture.gesture_str = None,None
                            else:
                                self.dynamic_gesture.gesture_id = CMD[5]
                                self.dynamic_gesture.gesture_str = DYNAMIC_GESTURE_STR[CMD[5]]
                elif(self.mode==PERSON_DETECTION and self.person_detect!=None):
                    if(len(CMD)>0):
                        if(CMD[3]==PERSON_DETECTION and CMD[4]==0x01):
                            if(CMD[5]==0xff):
                                self.person_detect.lock = True
                                self.person_detect.flag = False
                            elif(CMD[5]==0xee):
                                self.person_detect.lock = True
                                self.person_detect.flag = True
                elif(self.mode==PERSON_KEYPOINT_DETECT and self.person_keypoint_detect!=None):
                    if(len(CMD)>0):
                        if(CMD[3]==PERSON_KEYPOINT_DETECT and CMD[4]==0x01):
                            if(CMD[5]==0xff):
                                self.person_keypoint_detect.lock = True
                                self.person_keypoint_detect.fallen = None
                            else:
                                self.person_keypoint_detect.fallen = CMD[5]
                elif(self.mode==PERSON_KEYPOINT_DETECT_PLUS and self.person_keypoint_detect_plus!=None):
                    if(len(CMD)>0):
                        if(CMD[3]==PERSON_KEYPOINT_DETECT_PLUS and CMD[4]==0x01):
                            if(CMD[5]==0xff):
                                self.person_keypoint_detect_plus.id = None
                            else:
                                self.person_keypoint_detect_plus.id = CMD[5]
                elif(self.mode==FACE_LANDMARK_LIVING_BODY and self.face_living_body!=None):
                    if(len(CMD)>0):
                        if(CMD[3]==FACE_LANDMARK_LIVING_BODY and CMD[4]==0x01):
                            if(CMD[5]==0xff):
                                self.face_living_body.lock = True
                                self.face_living_body.mouth_blink_counter = [0,0]
                            else:
                                self.face_living_body.lock = True
                                self.face_living_body.mouth_blink_counter = CMD[5],CMD[6]
                elif(self.mode==FACE_LANDMARK_EXPRESSION and self.face_expression!=None):
                    if(len(CMD)>0):
                        if(CMD[3]==FACE_LANDMARK_EXPRESSION and CMD[4]==0x01):
                            if(CMD[5]==0xff):
                                self.face_expression.lock = True
                                self.face_expression.expression = 0
                                self.face_expression.expression_str = FACE_LANDMARK_EXPRESSION_ZH[0]
                            else:
                                self.face_expression.lock = True
                                self.face_expression.expression = CMD[5]
                                self.face_expression.expression_str = FACE_LANDMARK_EXPRESSION_ZH[CMD[5]]
                elif(self.mode==FALL_DETECTION and self.fall!=None):
                    if(len(CMD)>0):
                        if(CMD[3]==FALL_DETECTION and CMD[4]==0x01):
                            if(CMD[5]==0xff):
                                self.fall.lock = True
                                self.fall.id = None
                            else:
                                self.fall.lock = True
                                self.fall.id = CMD[5]
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
                elif(self.mode==COLOR_OBJECT_COUNT_MODE and self.color_obj_count!=None):
                    if(len(CMD)>0):
                        if(CMD[3]==COLOR_OBJECT_COUNT_MODE and CMD[4]==0x01):
                            if(CMD[5]==0xff):
                                self.color_obj_count.lock = True
                                self.color_obj_count.color_count = None
                            else:
                                self.color_obj_count.lock = True
                                self.color_obj_count.color_count = CMD[5]
                elif(self.mode==LAB_COLOR_OBJECT_COUNT_MODE and self.lab_color_count!=None):
                    if(len(CMD)>0):
                        if(CMD[3]==LAB_COLOR_OBJECT_COUNT_MODE and CMD[4]==0x01):
                            if(CMD[5]==0xff):
                                self.lab_color_count.lock = True
                                self.lab_color_count.flag = False
                                self.lab_color_count.color_count = None
                            elif(CMD[5]==0):
                                self.lab_color_count.lock = True
                                self.lab_color_count.flag = False
                                self.lab_color_count.color_count = CMD[5]
                            else:
                                self.lab_color_count.lock = True
                                self.lab_color_count.flag = True
                                self.lab_color_count.color_count = CMD[5]
                elif(self.mode==QRCODE_MODE and self.qrcode!=None):
                    try:
                        if(len(CMD)>0):
                            if(CMD[2]==0x01 and CMD[3]==QRCODE_MODE and CMD[4]==0x01):
                                if(CMD[5]==0xff):
                                    self.qrcode.lock = True
                                    self.qrcode.info = None
                            elif(CMD[2]==0x02 and CMD[3]==QRCODE_MODE and CMD[4]==0x01):
                                _str = str(CMD[-2].decode('UTF-8','ignore'))
                                # data = eval(_str)
                                self.qrcode.lock = True
                                self.qrcode.info = _str
                        else:
                            self.qrcode.info = None
                    except:
                        self.qrcode.info = None
                elif(self.mode==LICENSE_PLATE_RECOGNITION):
                    if(len(CMD)>0):
                        if(CMD[2]==0x02 and CMD[3]==LICENSE_PLATE_RECOGNITION and CMD[4]==0x01):
                            _str = str(CMD[-2].decode('UTF-8','ignore'))
                            self.lpr.lpr_str = _str
                            self.lpr.lock = True
                        elif(CMD[2]==0x01 and CMD[3]==LICENSE_PLATE_RECOGNITION and CMD[4]==0x01):
                            self.lpr.lpr_str = None
                            self.lpr.lock = True
                elif(self.mode==BARCODE_MODE):
                    if(len(CMD)>0):
                        if(CMD[2]==0x02 and CMD[3]==BARCODE_MODE and CMD[4]==0x01):
                            _str = str(CMD[-2].decode('UTF-8','ignore'))
                            data = eval(_str)
                            self.bar_code.type = data[0]
                            self.bar_code.info = data[1]
                            self.bar_code.lock = True
                        elif(CMD[2]==0x01 and CMD[3]==BARCODE_MODE and CMD[4]==0x01):
                            self.bar_code.type = None
                            self.bar_code.info = None
                            self.bar_code.lock = True
                # elif(self.mode==GUIDEPOST_MODE and self.guidepost!=None):#10
                #     if(len(CMD)>0):
                #         if(CMD[3]==GUIDEPOST_MODE and CMD[4]==0x02):
                #             if(CMD[5]==0xff):
                #                 self.guidepost.lock = True
                #                 self.guidepost.id,self.guidepost.max_score = None,0
                #             else:
                #                 max_index,self.guidepost.max_score = CMD[5],round(int(CMD[6])/100,2)
                #                 self.guidepost.id = self.guidepost.labels[max_index]
                #         elif(CMD[2]==0x02):
                #             pass
                #     else:
                #         self.guidepost.id,self.guidepost.max_score = None,0
                elif(self.mode==CLASSIFY_MODEL_MODE and self.classify_model!=None):
                    if(len(CMD)>0):
                        if(CMD[3]==CLASSIFY_MODEL_MODE and CMD[4]==0x01):
                            if(CMD[5]==0xff):
                                self.classify_model.lock = True
                                self.classify_model.id,self.classify_model.score = None,0
                            else:
                                self.classify_model.id ,self.classify_model.score = CMD[5],round(int(CMD[6])/100,2)
                    else:
                        self.classify_model.id,self.classify_model.score = None,0
                elif(self.mode==DETECT_MODEL_MODE and self.detect_kmodel!=None):
                    if(len(CMD)>0):
                        if(CMD[3]==DETECT_MODEL_MODE and CMD[4]==0x01):
                            if(CMD[5]==0xff):
                                self.detect_kmodel.lock = True
                                self.detect_kmodel.id,self.detect_kmodel.score = None,0
                            else:
                                self.detect_kmodel.id ,self.detect_kmodel.score = CMD[5],round(int(CMD[6])/100,2)
                    else:
                        self.detect_kmodel.id,self.detect_kmodel.score = None,0
                # elif(self.mode==APRILTAG_MODE and self.apriltag!=None):
                #     if(len(CMD)>0):
                #         if(CMD[2]==0x01 and CMD[3]==AI['apriltag'][0] and CMD[4]==AI['apriltag'][2] and CMD[5]==0xff):
                #             self.apriltag.lock = True
                #             self.apriltag.tag_family,self.apriltag.tag_id = None,None
                #         elif(CMD[2]==0x02 and CMD[3]==AI['apriltag'][0] and CMD[4]==AI['apriltag'][2]):
                #             self.apriltag.lock = True
                #             _str = str(CMD[-2].decode('UTF-8','ignore'))
                #             data = _str.split('|')
                #             self.apriltag.tag_family,self.apriltag.tag_id = int(data[0]),int(data[1])
                #     else:
                #         self.apriltag.tag_family,self.apriltag.tag_id = None,None
                # elif(self.mode==FACTORY_MODE):
                #     if(len(CMD)>0):
                #         if(CMD[2]==0x02 and CMD[3]==FACTORY_MODE and CMD[4]==0x01):
                #             _str = str(CMD[-2].decode('UTF-8','ignore'))
                #             data = eval(_str)
                #             self.a_status,self.b_status,self.tf_status = CMD[5],CMD[6],CMD[7]
                #             self.tf_sn = data[0]
                else:
                    pass
        except Exception as e:
            print(e)
    