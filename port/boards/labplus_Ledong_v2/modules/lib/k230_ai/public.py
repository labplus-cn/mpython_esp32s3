import gc
import _thread
import time

DISPLAY_WIDTH = 544
DISPLAY_HEIGHT = 368
DEFAULT_MODE = 0 # 默认UI
SENSOR_MODE = -1 # 摄像头
FACE_DETECTION_MODE = 1
OBJECT_RECOGNIZATION_MODE = 2 
HAND_DETECTION = 3
HAND_KEYPOINT_CLASS = 4
QRCODE_MODE = 5
PERSON_DETECTION = 6
FALL_DETECTION = 7 
LICENSE_PLATE_RECOGNITION = 8
CANNY_FIND_EDGES = 9
PERSON_KEYPOINT_DETECT = 10

PERSON_KEYPOINT_DETECT_PLUS = 11 
# COLOR_STATISTICS_MODE = 13 # 颜色的统计信息
# COLOR_EXTRACTO_MODE = 14 # LAB颜色提取器
APRILTAG_MODE = 15
COLOE_MODE = 16
SPEECH_RECOGNIZATION_MODE = 17
SELF_LEARNING_CLASSIFIER_MODE = 18 # 自学习
GUIDEPOST_MODE = 19 #清华教材交通标志识别
KPU_MODEL_MODE = 20 #自定义模型 

HAND_RECOGNIZATION_MODE = 21
BARCODE_MODE = 23

DYNAMIC_GESTURE = 25 #动态手势
FACE_LANDMARK = 26  # 人脸关键点
FACE_LANDMARK_LIVING_BODY = 27
FACE_LANDMARK_EXPRESSION = 28

COLOR_OBJECT_COUNT_MODE = 29
LAB_COLOR_OBJECT_COUNT_MODE = 22 #LAB


FACE_REG_MODE = 30 # 人脸注册
FACE_RECOGNITION_MODE = 31 #人脸识别
CLASSIFY_MODEL_MODE = 32 # 分类模型
DETECT_MODEL_MODE = 33  # 检测模型
HAND_KEYPOINT = 34

FACTORY_MODE = 99 

# OBJ_TYPE = ['飞机','自行车','鸟','船','瓶子','公交车','汽车','猫','椅子','奶牛','餐桌','狗','屋子','摩托','人','盆栽','羊','沙发','火车','电视']

YOLO80_ZH = ["人","自行车","汽车","摩托车","飞机","公共汽车","火车","卡车","船","交通灯","消防栓","停车标志","泊车计时器","长椅","鸟","猫","狗","马","绵羊","奶牛","大象","熊","斑马","长颈鹿","背包","雨伞","手提包","领带","手提箱","飞盘","滑雪板","运动球","风筝","棒球","蝙蝠","棒球手套","滑板","冲浪板","网球拍","瓶子","酒杯","杯子","叉子","刀","勺子","碗","香蕉","苹果","三明治","橙子","西兰花","胡萝卜","热狗","披萨","甜甜圈","蛋糕","椅子","沙发","盆栽","床","餐桌","厕所","电视","笔记本电脑","鼠标","遥控器","键盘","手机","微波炉","烤箱","烤面包机", "水槽","冰箱","书籍","时钟","花瓶","剪刀","泰迪熊","吹风机","牙刷"] 
HAND_KEYPOINT_CLASS_GESTURE = ['fist','five','gun','love','one','six','three','thumbUp','yeah']
FACE_LANDMARK_EXPRESSION_ZH = ['正常','开心','伤心','惊讶','生气']
DYNAMIC_GESTURE_STR = ['上','下','左','右'] 


MODE=['默认','数字识别','物体识别','人脸检测','人脸识别','自学习分类','颜色识别','二维码识别','语音识别','交通标志识别','KPU自定义模型','寻找色块识别','图像处理','LAB颜色提取器','AprilTag']

AI ={
    'reset':[0xff, 0x01, 0x02],
    'sw_mode':[],
    'config':[0x99,0x01,0x02],
    'lcd':[0x10,0x01,0x02],
    'image':[0x64,0x01],
    'sensor':[0x64,0x01],
    'DEFAULT_MODE':[DEFAULT_MODE,0x01],
    'light':[],
    'button':[],
    'button_A':[],
    'button_B':[],
    'FACE_DETECTION_MODE':[FACE_DETECTION_MODE,0x01],
    'OBJECT_RECOGNIZATION_MODE':[OBJECT_RECOGNIZATION_MODE,0x01],
    'HAND_DETECTION':[HAND_DETECTION,0x01],
    'HAND_RECOGNIZATION_MODE':[HAND_RECOGNIZATION_MODE,0x01],
    'HAND_KEYPOINT_CLASS':[HAND_KEYPOINT_CLASS,0x01],
    'LICENSE_PLATE_RECOGNITION':[LICENSE_PLATE_RECOGNITION,0x01],
    'PERSON_DETECTION':[PERSON_DETECTION,0x01],
    'PERSON_KEYPOINT_DETECT':[PERSON_KEYPOINT_DETECT,0x01],
    'PERSON_KEYPOINT_DETECT_PLUS':[PERSON_KEYPOINT_DETECT_PLUS,0x01],
    'FACE_LANDMARK':[FACE_LANDMARK,0x01],
    'FACE_LANDMARK_LIVING_BODY':[FACE_LANDMARK_LIVING_BODY,0x01],
    'FACE_LANDMARK_EXPRESSION':[FACE_LANDMARK_EXPRESSION,0x01],
    'QRCODE_MODE':[QRCODE_MODE,0x01],
    'BARCODE_MODE':[BARCODE_MODE,0x01],
    'FALL_DETECTION':[FALL_DETECTION,0x01],
    'FACE_RECOGNITION_MODE':[FACE_RECOGNITION_MODE,0x01],
    'LAB_COLOR_OBJECT_COUNT_MODE':[LAB_COLOR_OBJECT_COUNT_MODE,0x01],
    'COLOR_OBJECT_COUNT_MODE':[COLOR_OBJECT_COUNT_MODE,0x01],
    'DYNAMIC_GESTURE':[DYNAMIC_GESTURE,0x01],
    'CLASSIFY_MODEL_MODE':[CLASSIFY_MODEL_MODE,0x01],
    'DETECT_MODEL_MODE':[DETECT_MODEL_MODE,0x01],
    'kpu_model_yolo':[0x10,0x01,0x02,0x03],
    'factory':[99,0x01,0x02,0x03,0x04,0x05]
}


def CheckCode(tmp):
    sum = 0
    for i in range(len(tmp)):
        sum += tmp[i]
    return sum & 0xff

def uart_handle(uart):
    CMD = []
    HEAD = []
    # while True:
    if(uart.any()):
        head = uart.read(3)
    
        if b"\xbb" in head:
            for i in range(len(head)):
                HEAD.append(head[i])
        
            if(HEAD[0] == 0xBB):
                CMD.extend([HEAD[0],HEAD[1],HEAD[2]])
                if(CMD[2]==0x01):
                    res = uart.read(9)
                    
                    for i in range(9):
                        CMD.append(res[i])                  
                    checksum = CheckCode(CMD[:11])
                    if(res and checksum == CMD[11]):
                        _cmd = uart.read(12*5)
                        del _cmd
                        return CMD
                elif(CMD[2]==0x02):
                    res = uart.read(18)
                    
                    str_len = res[17]
                    time.sleep_ms(1)
                    str_temp = uart.read(str_len)
                    checksum  = uart.read(1)
                    for i in range(18):
                        CMD.append(res[i])
        
                    CMD.append(str_temp)
                    CMD.append(checksum[0])
                
                    return CMD
            elif(HEAD[1] == 0xBB):
                CMD.extend([HEAD[1],HEAD[2]])
                CMD.append(uart.read(1))
                if(CMD[2]==0x01):
                    res = uart.read(9)
                    
                    for i in range(9):
                        CMD.append(res[i])                  
                    checksum = CheckCode(CMD[:11])
                    if(res and checksum == CMD[11]):
                        _cmd = uart.read(12*5)
                        del _cmd
                        return CMD

                elif(CMD[2]==0x02):
                    res = uart.read(18)
                    str_len = res[17]
                    time.sleep_ms(1)
                    str_temp = uart.read(str_len)
                    checksum  = uart.read(1)

                    for i in range(18):
                        CMD.append(res[i])
                
                    CMD.append(str_temp)
                    CMD.append(checksum[0])

                    return CMD
            elif(HEAD[2] == 0xBB):
                CMD.append(HEAD[2])
                tmp = uart.read(2)
                for i in range(2):
                    CMD.append(tmp[i]) 
                if(CMD[2]==0x01):
                    res = uart.read(9)
                    
                    for i in range(9):
                        CMD.append(res[i])                  
                    checksum = CheckCode(CMD[:11])
                    if(res and checksum == CMD[11]):
                        _cmd = uart.read(12*5)
                        del _cmd
                        return CMD
                
                elif(CMD[2]==0x02):
                    res = uart.read(18)
                    str_len = res[17]
                    time.sleep_ms(1)
                    str_temp = uart.read(str_len)
                    checksum  = uart.read(1)

                    for i in range(18):
                        CMD.append(res[i])
                    
                    CMD.append(str_temp)
                    CMD.append(checksum[0])
            
                    return CMD
        else:
            # _cmd = uart.read(12*3)
            # del _cmd
            # print('&===111===&')
            return []
    else:
        # print('&===222===&')
        return []

def AI_Uart_CMD(uart, cmd=0, cmd_type=0, cmd_data=[0, 0, 0, 0, 0, 0, 0, 0]):
    gc.collect()
    data_type = 0x01
    check_sum = 0
    CMD = [0xAA, 0xBB, data_type, cmd, cmd_type]
    CMD.extend(cmd_data)
    for i in range(8-len(cmd_data)):
        CMD.append(0)
    for i in range(len(CMD)):
        check_sum = check_sum+CMD[i]

    CMD.append(check_sum & 0xFF)
    # print(CMD)
    uart.write(bytes(CMD))


def AI_Uart_CMD_String(uart=None, cmd=0xfe, cmd_type=0xfe, cmd_data=[0, 0, 0], str_len=0, str_buf=''):
    gc.collect()
    check_sum = 0
    CMD = [0xAA, 0xBB, 0x02, cmd, cmd_type]
    CMD.extend(cmd_data)
    for i in range(3-len(cmd_data)):
        CMD.append(0)
    for i in range(len(CMD)):
        check_sum = check_sum+CMD[i]
  
    str_temp = bytes(str_buf, 'utf-8')
    str_len = len(str_temp)
    
    for i in range(len(str_temp)):
        check_sum = check_sum + str_temp[i]  

    CMD = bytes(CMD) + bytes([str_len]) + str_temp + bytes([check_sum & 0xFF])
    uart.write(CMD)

def print_x16(date):
    for i in range(len(date)):
        print('{:2x}'.format(date[i]),end=' ')
    print('')

def hammingWeight(n):
    '''
    判断16bit中哪一位为1
    '''
    ans = 0
    for i in range(16):
        if n & 1 == 1:
          ans = i
        n >>= 1
    return ans

class TASK:
    """创建新线程并循环运行指定函数"""
    def __init__(self, func=lambda: None, sec=-1, *args, **kwargs):
        """
        * func 需要循环运行的函数
        * sec  每次循环的延迟，负数则只运行一次
        * args kwagrs 函数的参数
        * enable 使能运行
        """
        self._thread = _thread
        self.sec = sec
        self.func = func
        self.args, self.kwargs = args, kwargs
        self.enable = True
        self.lock = self._thread.allocate_lock()
        self.stop_lock = self._thread.allocate_lock()
        self.lock.acquire()
        self.stop_lock.acquire()
        self._thread.stack_size(8192)
        self.thread_id = self._thread.start_new_thread(self.__run, ())
        
    def __run(self):
        """
        请勿调用
        线程运行函数
        """
        while True:
            self.lock.acquire()
            try:
                self.func(*self.args, **self.kwargs)
            except Exception as e:
                print('Task_function_error:', e)
                pass
            if self.sec < 0 or not self.enable:
                self.stop_lock.release()
            else:
                time.sleep(self.sec)
                self.lock.release()

    def start(self):
        """运行线程"""
        self.lock.release()

    def stop(self):
        """暂停线程"""
        self.enable = False
        self.stop_lock.acquire()
        self.enable = True

    # def kill(self):
    #     pass