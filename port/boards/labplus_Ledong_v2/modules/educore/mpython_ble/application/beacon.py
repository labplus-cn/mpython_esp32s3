import bluetooth
from bluetooth import UUID
import struct
from ..const import ADType
from ..advertising import advertising_payload, AD_Structure

import time
import math


class iBeacon:
    """ iBeacon """

    def __init__(self, proximity_uuid, major, minor, company_id=0x004C, tx_power=0xC5):
        self.ibeacon = bluetooth.BLE()
        self.ibeacon.active(True)
        print("BLE iBeacon activated!")
        print("uuid:" + str(proximity_uuid))
        # iBeacon frame
        assert isinstance(proximity_uuid, UUID), TypeError("proximity uuid must be type of UUID")
        proximity_uuid = list(bytes(proximity_uuid))
        proximity_uuid.reverse()
        proximity_uuid = bytes(proximity_uuid)
        ibeacon_type = 0x02
        adv_data_length = 0x15
        manuf_specific_data = struct.pack('<H2B', company_id, ibeacon_type, adv_data_length)
        manuf_specific_data += proximity_uuid
        manuf_specific_data += struct.pack(">2HB", major, minor, tx_power)
        manuf_specific = AD_Structure(ad_type=ADType.AD_TYPE_MANUFACTURER_SPECIFIC_DATA, ad_data=manuf_specific_data)
        self._adv_payload = advertising_payload(ad_structure=[manuf_specific])

    def advertise(self, toggle=True, interval_us=500000):
        if toggle:
            self.ibeacon.gap_advertise(interval_us, adv_data=self._adv_payload, connectable=False)
        else:
            self.ibeacon.gap_advertise(interval_us=None)


class Trilateration:
    @staticmethod
    def calculate_position(beacons):
        """
        三边定位算法
        Args:
            beacons (list): 包含每个信标的已知位置和测量距离的列表
                每个信标是一个字典，格式为: {'x': float, 'y': float, 'distance': float}
                x, y: 信标的坐标位置（单位：米）
                distance: 测量到的到信标的距离（单位：米）
        Returns:
            tuple: (x, y) 估计位置坐标（单位：米）
        Raises:
            ValueError: 当信标数量少于3个时抛出
        """
        if len(beacons) < 3:
            raise ValueError("至少需要3个信标进行定位")
        
        # 使用最小二乘法求解
        A = []
        b = []
        try:
            # 以第一个信标为基准
            x1, y1, d1 = beacons[0]['x'], beacons[0]['y'], beacons[0]['distance']
            
            for beacon in beacons[1:]:
                xi, yi, di = beacon['x'], beacon['y'], beacon['distance']
                
                # 构建线性方程组
                A.append([2*(xi - x1), 2*(yi - y1)])
                b.append([x1**2 - xi**2 + y1**2 - yi**2 + di**2 - d1**2])
        except Exception as e:
            print(f"{str(e)}")
        
        # 解线性方程组 Ax = b
        try:
            AT = [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]
            ATA = [[sum(a*b for a,b in zip(AT_row, A_col)) for A_col in zip(*A)] for AT_row in AT]
            inv_ATA = Trilateration.invert_2x2(ATA)
            ATb = [sum(a*b for a,b in zip(AT_row, b)) for AT_row in AT]
            x = sum(inv_ATA[0][i] * ATb[i] for i in range(2))
            y = sum(inv_ATA[1][i] * ATb[i] for i in range(2))
            
            return (x, y)
        except:
            # 如果矩阵不可逆，返回信标的质心
            avg_x = sum(b['x'] for b in beacons) / len(beacons)
            avg_y = sum(b['y'] for b in beacons) / len(beacons)
            print("矩阵不可逆，返回信标质心位置")
            return (avg_x, avg_y)
        
    @staticmethod
    def calculate_position_robust(beacons):
        """不使用numpy的鲁棒三边定位"""
        if len(beacons) < 3:
            raise ValueError("至少需要3个信标进行定位")
        
        best_error = float('inf')
        best_position = None
        
        # 尝试不同的基准信标
        for ref_idx in range(min(3, len(beacons))):
            x_ref, y_ref, d_ref = beacons[ref_idx]['x'], beacons[ref_idx]['y'], beacons[ref_idx]['distance']
            
            A = []
            b = []
            for i, beacon in enumerate(beacons):
                if i == ref_idx:
                    continue
                xi, yi, di = beacon['x'], beacon['y'], beacon['distance']
                A.append([2*(xi - x_ref), 2*(yi - y_ref)])
                b.append(x_ref**2 - xi**2 + y_ref**2 - yi**2 + di**2 - d_ref**2)
            
            # 使用最小二乘法求解
            x = Trilateration.least_squares(A, b)
            
            if x is not None:
                # 计算残差评估解的质量
                error = 0
                for i in range(len(A)):
                    error += (A[i][0]*x[0] + A[i][1]*x[1] - b[i])**2
                
                if error < best_error:
                    best_error = error
                    best_position = (-x[0], -x[1])
        
        if best_position is not None:
            return best_position
        
        # 所有尝试都失败时返回信标质心
        avg_x = sum(b['x'] for b in beacons) / len(beacons)
        avg_y = sum(b['y'] for b in beacons) / len(beacons)
        print("所有方法失败，返回信标质心位置")
        return (avg_x, avg_y)
    

    @staticmethod
    def least_squares(A, b):
        """手动实现最小二乘法解Ax=b"""
        # 计算A^T A
        at_a = [
            [sum(A[i][0]*A[i][0] for i in range(len(A))), 
            sum(A[i][0]*A[i][1] for i in range(len(A)))],
            [sum(A[i][1]*A[i][0] for i in range(len(A))), 
            sum(A[i][1]*A[i][1] for i in range(len(A)))]
        ]
        
        # 计算A^T b
        at_b = [
            sum(A[i][0]*b[i] for i in range(len(A))),
            sum(A[i][1]*b[i] for i in range(len(A)))
        ]
        
        try:
            # 求逆
            inv = Trilateration.invert_2x2(at_a)
            
            # 计算解 x = (A^T A)^-1 A^T b
            x = [
                inv[0][0]*at_b[0] + inv[0][1]*at_b[1],
                inv[1][0]*at_b[0] + inv[1][1]*at_b[1]
            ]
            return x
        except ValueError:
            return None


    
    @staticmethod
    def invert_2x2(matrix):
        """
        求2x2矩阵的逆
        Args:
            matrix (list): 2x2矩阵，格式为 [[a, b], [c, d]]
        Returns:
            list: 2x2逆矩阵
        Raises:
            ValueError: 当矩阵不可逆（行列式为0）时抛出
        """
        det = matrix[0][0]*matrix[1][1] - matrix[0][1]*matrix[1][0]
        if det == 0:
            raise ValueError("矩阵不可逆")
        
        return [
            [matrix[1][1]/det, -matrix[0][1]/det],
            [-matrix[1][0]/det, matrix[0][0]/det]
        ]

class BeaconScanner:
    def __init__(self):
        """
        初始化蓝牙信标扫描器
        """
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.beacon_data = {}  # 使用普通字典替代defaultdict
        self.known_beacons = {}  # 已知信标的位置信息
        self.beacons_for_positioning = []

    def add_known_beacon(self, uuid, x, y, tx_power=-59):
        """
        添加已知位置的信标
        Args:
            uuid (str): 信标的UUID，格式为 "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            x (float): 信标的x坐标（单位：米）
            y (float): 信标的y坐标（单位：米）
            tx_power (int, optional): 信标的发射功率，默认为-59dBm
        """
        self.known_beacons[uuid] = {'x': x, 'y': y, 'tx_power': tx_power}
        if uuid not in self.beacon_data:
            self.beacon_data[uuid] = []
    
    def parse_ibeacon(self, adv_data):
        """
        解析iBeacon广播数据
        Args:
            adv_data (bytes): 原始广播数据
        Returns:
            dict: 解析后的信标信息，包含以下字段：
                - type: 信标类型
                - uuid: 信标UUID
                - major: major值
                - minor: minor值
                - tx_power: 发射功率
            如果数据无效则返回None
        """
        if len(adv_data) < 25:
            return None
        
        if adv_data[0:4] != b'\x4C\x00\x02\x15':
            return None
        
        uuid_bytes = adv_data[4:20]
        uuid = uuid_bytes.hex()
        formatted_uuid = f"{uuid[0:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:32]}"
        
        major = int.from_bytes(adv_data[20:22], 'big')
        minor = int.from_bytes(adv_data[22:24], 'big')
        
        tx_power = adv_data[24]
        if tx_power > 127:
            tx_power = tx_power - 256
        
        return {
            "type": "iBeacon",
            "uuid": formatted_uuid,
            "major": major,
            "minor": minor,
            "tx_power": tx_power
        }
    
    def estimate_distance(self, rssi, tx_power=-59, n=2.0):
        """
        根据RSSI值估算到信标的距离
        Args:
            rssi (int): 接收信号强度指示值（单位：dBm）
            tx_power (int, optional): 信标发射功率，默认为-59dBm
            n (float, optional): 路径损耗指数，默认为2.0
                2.0: 自由空间
                2.5-3.5: 办公室环境
                3.5-4.0: 复杂室内环境
                4.0-5.0: 金属密集环境
        Returns:
            float: 估算的距离（单位：米）
        """
        if rssi >= tx_power:
            return 0.1
        
        ratio = (tx_power - rssi) / (10 * n)
        distance = math.pow(10, ratio)
        return max(distance, 0.1)
    
    # 使用事件编号 5 表示扫描结果事件
    def scan_callback(self, event, data):
        if event == 5:  # 对应 IRQ_SCAN_RESULT
            addr_type, addr, adv_type, rssi, adv_data = data
            adv_data = bytes(adv_data)
            beacon_info = self.parse_ibeacon(adv_data[5:])  # 跳过前面的AD结构头
            
            if beacon_info and beacon_info['uuid'] in self.known_beacons:
                uuid = beacon_info['uuid']
                
                # 初始化该UUID的数据列表（如果不存在）
                if uuid not in self.beacon_data:
                    self.beacon_data[uuid] = []
                
                # 存储最近的10个RSSI值用于平滑
                self.beacon_data[uuid].append(rssi)
                if len(self.beacon_data[uuid]) > 10:
                    self.beacon_data[uuid].pop(0)

    def get_smoothed_distance(self, uuid, n=2.0):
        """
        获取平滑后的距离估计
        Args:
            uuid (str): 信标的UUID
            n (float, optional): 路径损耗指数，默认为2.0
        Returns:
            float: 平滑后的距离估计（单位：米），如果没有数据则返回None
        """
        if uuid not in self.beacon_data or not self.beacon_data[uuid]:
            return None,None
        
        readings = self.beacon_data[uuid]

        tx_power = self.known_beacons[uuid].get('tx_power', -59)
        
        # 计算有效RSSI平均值（排除异常值）
        avg_rssi = sum(readings) / len(readings)
        valid_readings = [r for r in readings if abs(r - avg_rssi) <= 10]
        
        if len(valid_readings) < len(readings) * 0.5:
            valid_readings = readings
        
        avg_rssi = sum(valid_readings) / len(valid_readings)
        return self.estimate_distance(avg_rssi, tx_power, n),avg_rssi
    
    def get_position(self, n=3.0):
        """
        获取当前位置估计
        Args:
            n (float, optional): 路径损耗指数，默认为3.0
                2.0: 自由空间
                2.5-3.5: 办公室环境
                3.5-4.0: 复杂室内环境
                4.0-5.0: 金属密集环境
        Returns:
            tuple: (x, y) 估计位置坐标（单位：米），如果信标数量不足则返回None
        """
        beacons_for_positioning = []
        
        for uuid in self.known_beacons:
            if uuid in self.beacon_data:  # 只处理有扫描数据的信标
                distance,avg_rssi = self.get_smoothed_distance(uuid, n)
                if distance is not None:
                    beacon_info = {
                        'x': round(self.known_beacons[uuid]['x'],2),
                        'y': round(self.known_beacons[uuid]['y'],2),
                        'distance': round(distance,2),
                        'rssi': round(avg_rssi,2)
                    }
                    beacons_for_positioning.append(beacon_info)
        
        if len(beacons_for_positioning) >= 3:
            self.beacons_for_positioning = beacons_for_positioning 
            # return Trilateration.calculate_position(beacons_for_positioning)
            return Trilateration.calculate_position_robust(beacons_for_positioning)
        else:
            self.beacons_for_positioning = []
            return None
    
    def scan(self, duration=10):
        """
        执行蓝牙信标扫描
        Args:
            duration (int, optional): 扫描持续时间（单位：秒），默认为5秒
        """
        # 清空现有数据但保留数据结构
        for uuid in self.beacon_data:
            self.beacon_data[uuid].clear()
        
        self.ble.irq(self.scan_callback)
        self.ble.gap_scan(duration * 1000, 30000, 30000, True)
        time.sleep(duration)
        self.ble.gap_scan(None)
