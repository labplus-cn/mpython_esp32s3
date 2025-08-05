import usocket as socket
import ustruct as struct
from ubinascii import hexlify
from time import sleep_ms
from aes128 import *

DICT = {"host":"","protocol":"wss://","hostname":"-1","port":"-1","path":"-1","username":"-1","password":"-1","clientId":"-1","schoolId":"-1","classId":"-1","userId":"-1","send":"-1","receive":"-1"}


class MQTTException(Exception):
    pass

class MQTTClient:
    def __init__(self, client_id=None, server=None, port=0, user=None, password=None, keepalive=0, ssl=False, ssl_params={}, aesparam=None):
        self.aes_mode = 0
        if port == 0:
            port = 8883 if ssl else 1883
    
        if(aesparam): # 解密aes128参数
            self.aes_dict = self.aes_decrypt(aesparam)
        else:
            self.aes_dict = DICT
        
        # print(self.aes_dict)

        if((self.aes_dict["hostname"] != DICT["hostname"]) and (client_id == None)):
            self.client_id = self.aes_dict["clientId"]
            self.server = self.aes_dict["hostname"]
            # self.port = int(self.aes_dict["port"])
            self.port = 1883
            self.user = self.aes_dict["username"]
            self.pswd = self.aes_dict["password"]
            self.schoolId = self.aes_dict["schoolId"]
            self.classId = self.aes_dict["classId"]
            self.userId = self.aes_dict["userId"]
            self.sendId = self.aes_dict["send"]
            self.fixed_characters = 'EBG_CODE/shengsi/{}/{}/{}/{}/'.format(self.schoolId,self.classId,self.userId,self.sendId)
            if(self.sendId == "1" or self.sendId == 1 ):
                self.fixed_characters_sub = 'EBG_CODE/shengsi/{}/{}/{}/{}/'.format("+",self.classId,"+",self.sendId)
            elif(self.sendId == "0" or self.sendId == 0):
                self.fixed_characters_sub = 'EBG_CODE/shengsi/{}/{}/{}/{}/'.format("+","+",self.userId,self.sendId)
            else:
                self.fixed_characters_sub = 'EBG_CODE/shengsi/{}/{}/{}/{}/'.format("+","+","+","+")
            self.aes_mode = 1
            self.ssl = ssl
            self.ssl_params = ssl_params
            self.sock = None
            self.pid = 0
            self.cb = None
            self.keepalive = keepalive
            self.lw_topic = None
            self.lw_msg = None
            self.lw_qos = 0
            self.lw_retain = False
            # print('client_id:{}\nserver:{}\nport:{}\nusername:{}\npassword:{}'.format(self.client_id,self.server,self.port,self.user,self.pswd))
            # print('schoolId:{}\nclassId:{}\nuserId:{}\nsendId:{}'.format(self.schoolId,self.classId,self.userId,self.sendId))
        else:
            self.client_id = client_id
            self.sock = None
            self.server = server
            self.port = port
            self.ssl = ssl
            self.ssl_params = ssl_params
            self.pid = 0
            self.cb = None
            self.user = user
            self.pswd = password
            self.keepalive = keepalive
            self.lw_topic = None
            self.lw_msg = None
            self.lw_qos = 0
            self.lw_retain = False
            print('no aesparam mode!!!')
            # print('aes_mode:{}\n'.format(self.aes_mode))
        self.DELAY_500_MS = 500

    def _send_str(self, s):
        self.sock.write(struct.pack("!H", len(s)))
        self.sock.write(s)

    def _recv_len(self):
        n = 0
        sh = 0
        while 1:
            b = self.sock.read(1)[0]
            n |= (b & 0x7f) << sh
            if not b & 0x80:
                return n
            sh += 7

    def set_callback(self, f):
        self.cb = f

    def set_last_will(self, topic, msg, retain=False, qos=0):
        assert 0 <= qos <= 2
        assert topic
        self.lw_topic = topic
        self.lw_msg = msg
        self.lw_qos = qos
        self.lw_retain = retain

    def connect(self, clean_session=True):
        self.sock = socket.socket()
        addr = socket.getaddrinfo(self.server, self.port)[0][-1]
        self.sock.connect(addr)
        if self.ssl:
            import ussl
            self.sock = ussl.wrap_socket(self.sock, **self.ssl_params)
        premsg = bytearray(b"\x10\0\0\0\0\0")
        msg = bytearray(b"\x04MQTT\x04\x02\0\0")

        sz = 10 + 2 + len(self.client_id)
        msg[6] = clean_session << 1
        if self.user is not None:
            sz += 2 + len(self.user) + 2 + len(self.pswd)
            msg[6] |= 0xC0
        if self.keepalive:
            assert self.keepalive < 65536
            msg[7] |= self.keepalive >> 8
            msg[8] |= self.keepalive & 0x00FF
        if self.lw_topic:
            sz += 2 + len(self.lw_topic) + 2 + len(self.lw_msg)
            msg[6] |= 0x4 | (self.lw_qos & 0x1) << 3 | (self.lw_qos & 0x2) << 3
            msg[6] |= self.lw_retain << 5

        i = 1
        while sz > 0x7f:
            premsg[i] = (sz & 0x7f) | 0x80
            sz >>= 7
            i += 1
        premsg[i] = sz

        self.sock.write(premsg, i + 2)
        self.sock.write(msg)
        #print(hex(len(msg)), hexlify(msg, ":"))
        self._send_str(self.client_id)
        if self.lw_topic:
            self._send_str(self.lw_topic)
            self._send_str(self.lw_msg)
        if self.user is not None:
            self._send_str(self.user)
            self._send_str(self.pswd)
        resp = self.sock.read(4)
        assert resp[0] == 0x20 and resp[1] == 0x02
        if resp[3] != 0:
            raise MQTTException(resp[3])
        return resp[2] & 1

    def disconnect(self):
        self.sock.write(b"\xe0\0")
        self.sock.close()

    def ping(self):
        self.sock.write(b"\xc0\0")

    def publish(self, topic, msg, retain=False, qos=0):
        sleep_ms(self.DELAY_500_MS) # 延时500ms
        if(self.aes_mode == 1):
            topic = self.fixed_characters + str(topic)
        # print('publish topic:' + topic)
        pkt = bytearray(b"\x30\0\0\0")
        pkt[0] |= qos << 1 | retain
        sz = 2 + len(topic) + len(msg)
        if qos > 0:
            sz += 2
        assert sz < 2097152
        i = 1
        while sz > 0x7f:
            pkt[i] = (sz & 0x7f) | 0x80
            sz >>= 7
            i += 1
        pkt[i] = sz
        #print(hex(len(pkt)), hexlify(pkt, ":"))
        self.sock.write(pkt, i + 1)
        self._send_str(topic)
        if qos > 0:
            self.pid += 1
            pid = self.pid
            struct.pack_into("!H", pkt, 0, pid)
            self.sock.write(pkt, 2)
        self.sock.write(msg)
        if qos == 1:
            while 1:
                op = self.wait_msg()
                if op == 0x40:
                    sz = self.sock.read(1)
                    assert sz == b"\x02"
                    rcv_pid = self.sock.read(2)
                    rcv_pid = rcv_pid[0] << 8 | rcv_pid[1]
                    if pid == rcv_pid:
                        return
        elif qos == 2:
            assert 0

    def subscribe(self, topic, qos=0):
        if(self.aes_mode == 1):
            topic = self.fixed_characters_sub + str(topic)
        # print('subscribe topic:' + topic)
        assert self.cb is not None, "Subscribe callback is not set"
        pkt = bytearray(b"\x82\0\0\0")
        self.pid += 1
        struct.pack_into("!BH", pkt, 1, 2 + 2 + len(topic) + 1, self.pid)
        #print(hex(len(pkt)), hexlify(pkt, ":"))
        self.sock.write(pkt)
        self._send_str(topic)
        self.sock.write(qos.to_bytes(1, "little"))
        while 1:
            op = self.wait_msg()
            if op == 0x90:
                resp = self.sock.read(4)
                #print(resp)
                assert resp[1] == pkt[2] and resp[2] == pkt[3]
                if resp[3] == 0x80:
                    raise MQTTException(resp[3])
                return

    # Wait for a single incoming MQTT message and process it.
    # Subscribed messages are delivered to a callback previously
    # set by .set_callback() method. Other (internal) MQTT
    # messages processed internally.
    def wait_msg(self):
        res = self.sock.read(1)
        self.sock.setblocking(True)
        if res is None:
            return None
        if res == b"":
            raise OSError(-1)
        if res == b"\xd0":  # PINGRESP
            sz = self.sock.read(1)[0]
            assert sz == 0
            return None
        op = res[0]
        if op & 0xf0 != 0x30:
            return op
        sz = self._recv_len()
        topic_len = self.sock.read(2)
        topic_len = (topic_len[0] << 8) | topic_len[1]
        topic = self.sock.read(topic_len)
        # print('receive topic:') 
        # print(topic) 
        if(self.aes_mode == 1):
            # 去除特定信息 
            topic = topic.decode('utf-8', 'ignore')
            if(topic.find(self.fixed_characters) > -1):
                topic = topic.split(self.fixed_characters)[1]
            # topic = topic.encode('utf-8')  # 转为字节和原接口保持一致
            topic = bytes(topic, 'utf-8')

        sz -= topic_len + 2
        if op & 6:
            pid = self.sock.read(2)
            pid = pid[0] << 8 | pid[1]
            sz -= 2
        msg = self.sock.read(sz)
        self.cb(topic, msg)
        if op & 6 == 2:
            pkt = bytearray(b"\x40\x02\0\0")
            struct.pack_into("!H", pkt, 2, pid)
            self.sock.write(pkt)
        elif op & 6 == 4:
            assert 0

    # Checks whether a pending message from server is available.
    # If not, returns immediately with None. Otherwise, does
    # the same processing as wait_msg.
    def check_msg(self):
        self.sock.setblocking(False)
        return self.wait_msg()
    
    def aes_decrypt(self,encrypted):
        try:
            _encrypted=bytes.fromhex(encrypted)
            decrypt_str = aes_128_cbc_decrypt(_encrypted)
            aes_dict = ujson.loads(decrypt_str.strip()) #转为字典
            return aes_dict
        except Exception as e:
            print('aes decrypt erroe:' + str(e))
            return DICT
