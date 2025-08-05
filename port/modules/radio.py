try:
    from _espnow import *
    import network
    import time
    import struct
    import json,binascii
    import machine 
    import ubinascii
except ImportError:
    print("Radio ImportError")
    raise SystemExit

class MPythonESPNow(ESPNowBase):
    _data = [None, bytearray(MAX_DATA_LEN)]
    _none_tuple = (None, None)
    AP = 0
    STA = 1

    def __init__(self, wifi_ch=0) -> None:
        # 在STA和AP模式下初始化Wi-Fi
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_ap = network.WLAN(network.AP_IF)
        self.wlan_sta.active(True)
        self.wlan_ap.active(True)
        self.wifi_channel = wifi_ch
        if wifi_ch:
            while (
                self.wlan_sta.config("channel") != wifi_ch
                or self.wlan_ap.config("channel") != wifi_ch
            ):
                self.wlan_sta.config(channel=wifi_ch)
                self.wlan_ap.config(channel=wifi_ch)
                time.sleep(1)
        # 初始化 ESP-NOW
        super().__init__()
        while self.active():
            self.active(False)
            time.sleep(0.5)
        while not self.active():
            self.active(True)
            time.sleep(0.5)
        self.peer_list = [None] * 20
        self.broadcast = False
        self.bcast_peer = 'ff' * 6
    
    def set_add_peer(self, peer_mac):
        # 将提供的mac地址添加/注册为对等地址。
        peer_mac = binascii.unhexlify(peer_mac)
        # self.peer_list[peer_id - 1] = peer_mac
        self.add_peer(peer_mac, channel=self.wifi_channel, ifidx=0, encrypt=False, lmk=None)

    def set_add_peer_encrypt(self, peer_mac, peer_id=1, ifidx=0, encrypt=False, lmk=None):
        # 将提供的mac地址添加/注册为对等地址。
        peer_mac = binascii.unhexlify(peer_mac)
        self.peer_list[peer_id - 1] = peer_mac
        self.add_peer(peer_mac, channel=self.wifi_channel, ifidx=ifidx, encrypt=encrypt, lmk=lmk)

    def set_delete_peer(self, peer_id) -> None:
        # 取消注册与提供的peer_mac地址关联的对等体。
        peer = self.peer_list[peer_id - 1]
        if isinstance(peer, bytes):
            self.del_peer(peer)
            self.peer_list[peer_id - 1] = None

    def send_data(self, peer_id, msg) -> None:
        # 将msg中的数据发送到给定网络中存储的对等体mac地址
        peer = self.peer_list[peer_id - 1]
        msg = self.convert_to_bytes(msg)
        if peer is not None:
            self.send(peer, msg, False)
    
    def send_msg(self, peer_mac, msg) -> None: 
        # 发送字符串消息
        peer = self.hex_str_to_bytes(peer_mac)
        msg = self.convert_to_str_bytes(msg)
        try:
            self.send(peer, msg, False)
        except OSError as err:
            if len(err.args) < 2:
                raise err
            if err.args[1] == 'ESP_ERR_ESPNOW_NOT_INIT':
                self.active(True)
            elif err.args[1] == 'ESP_ERR_ESPNOW_NOT_FOUND':
                self.add_peer(peer)
            elif err.args[1] == 'ESP_ERR_ESPNOW_IF':
                self.wlan_sta = network.WLAN(network.STA_IF).active(True)
            else:
                raise err

    def broadcast_data(self, msg) -> None:
        # 所有设备还将接收发送到广播MAC地址的消息
        msg = self.convert_to_str_bytes(msg)
        peer = b"\xff\xff\xff\xff\xff\xff"
        if self.broadcast is False:
            self.add_peer(peer)
            self.broadcast = True
        self.send(peer, msg, False)

    def set_pmk_encrypt(self, pmk) -> None:
        #! Set the Primary Master Key (PMK) which is used to encrypt the Local Master Keys (LMK) for encrypting messages.
        self.set_pmk(pmk)

    def set_irq_callback(self, callback) -> None:
        #! Set a callback function to be called as soon as possible after a message has been received from another ESPNow device.
        super().irq(callback, self)
    
    def recv(self, timeout_ms=None):
        n = self.recvinto(self._data, timeout_ms)
        return [bytes(x) for x in self._data] if n else self._none_tuple

    def recv_data(self, timeout_ms=0) -> bytes:
        #! The callback function will be called with the ESPNow instance object as an argument.
        if self.any()>0:
            n = self.recvinto(self._data, timeout_ms)
            print(self._data)
            return [bytes(x) for x in self._data] if n else self._none_tuple 
    
    def recv_msg(self) -> bytes: 
        if self.any()>0:
            host_adr, recv_msg = self.recv()
            try:
                for peer, info in self.peers_table.items():
                    # mac_address = ':'.join('{:02x}'.format(b) for b in peer)
                    espnow_mac = host_adr.hex().upper()
                    espnow_data = recv_msg.decode('utf-8')
                    espnow_rssi = info[0]
                    time_ms = info[1]
                    # print(f"MAC: {espnow_mac}, RSSI: {espnow_rssi} dBm, Time: {time_ms} ms")
                return espnow_mac,espnow_data,espnow_rssi
            except: #8266没有检测信号的功能
                return host_adr,recv_msg,0

    def get_peer_list(self, encrypt=0) -> list:
        #! Get the parameters for all the registered peers (as a list).
        peer_lst = []
        for i in range(0, self.peer_count()[encrypt]):
            peer_lst.append(self._bytes_to_hex_str(self.get_peers()[i][0]))
        return peer_lst

    def get_mac(self, mode=0) -> str:
        #! Get the device network MAC address.
        return self.bytes_to_hex_str(self.wlan_ap.config("mac")) if mode else self.bytes_to_hex_str(self.wlan_sta.config("mac"))

    def get_remote_mac(self, select, ssid) -> None | bytes:
        #! To find remote mac by remote ssid.
        scan_detail = self.wlan_sta.scan()
        for i in range(0, len(scan_detail)):
            try:
                if scan_detail[i][0].decode("utf-8") == ssid:
                    return scan_detail[i][1] if select else scan_detail[i][2]
            except:
                return None

    def set_ap_ssid(self, ssid) -> None:
        #! Set the SSID configure in AP mode.
        self.wlan_ap.config(essid=ssid)

    def deinit(self) -> None:
        #! De-initialise the ESP-NOW software stack, disable callbacks, deallocate the recv data buffer and deregister all peers.
        self.active(False)

    def convert_to_bytes(self, msg) -> bytes:
        if isinstance(msg, list):
            msg = bytes(msg)
        elif isinstance(msg, int):
            msg = msg.to_bytes(4, "little")
        elif isinstance(msg, float):
            msg = struct.pack(">f", msg)
        return msg

    def _bytes_to(self, bytes, format=0) -> int | float:
        return struct.unpack(">f", bytes)[0] if format else int.from_bytes(bytes, "little")

    def _bytes_to_hex_str(self, bytes) -> str:
        #! To get a hex string from a bytes string.
        return binascii.hexlify(bytes).decode().upper()

    def _hex_str_to_bytes(self, hexstr) -> bytes:
        #! To get a bytes string from a hex string.
        return binascii.unhexlify(hexstr)

    def _to_bytes(self, variable) -> bytes:
        #! Get the current actual IP address, subnet mask and gateway of the module.
        return self.convert_to_bytes(variable)
    
    def hex_str_to_bytes(self,hex_str):
        # str 表示的十六进制字符串到 bytes 的转换
        return bytes.fromhex(hex_str)
    
    def bytes_to_hex_str(self,b):
        # bytes 到 十六进制字符串（str）的转换
        hex_str = b.hex().upper()
        return hex_str 
    
    def convert_to_str_bytes(self,d):
        # 统一转为字符串，再转为bytes
        return bytes(str(d), 'utf-8')