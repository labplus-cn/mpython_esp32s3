from machine import Pin
from mpython import i2c
from esp32 import NVS
import time
from micropython import const

# MSA311 Register Map
MSA311_ADDR = const(0x62)  # I2C address 98
REG_SOFT_RESET = const(0x00)  # Soft reset register (bit5 and bit2 set to 1 for reset)
REG_PART_ID = const(0x01)
REG_ACC_X_LSB = const(0x02)
REG_ACC_X_MSB = const(0x03)
REG_ACC_Y_LSB = const(0x04)
REG_ACC_Y_MSB = const(0x05)
REG_ACC_Z_LSB = const(0x06)
REG_ACC_Z_MSB = const(0x07)
REG_MOTION_INT_STATUS = const(0x09)
REG_NEW_DATA_INT_STATUS = const(0x0A)
REG_TAP_ACTIVE_STATUS = const(0x0B)
REG_ORIENT_STATUS = const(0x0C)
REG_G_RANGE = const(0x0F)
REG_ODR = const(0x10)
REG_POWER_MODE = const(0x11)
REG_AXIS_SWAP_POLARITY = const(0x12)
REG_INT_SET0 = const(0x16)
REG_INT_SET1 = const(0x17)
REG_INT_MAP0 = const(0x19)
REG_INT_MAP1 = const(0x1A)
REG_INT_CONFIG = const(0x20)
REG_INT_LATCH = const(0x21)
REG_FREEFALL_DUR = const(0x22)
REG_FREEFALL_TH = const(0x23)
REG_FREEFALL_MODE = const(0x24)
REG_ACTIVE_DUR = const(0x27)
REG_ACTIVE_TH = const(0x28)
REG_TAP_DUR = const(0x2A)
REG_TAP_TH = const(0x2B)
REG_ORIENT_MODE = const(0x2C)
REG_OFFSET_X = const(0x38)
REG_OFFSET_Y = const(0x39)
REG_OFFSET_Z = const(0x3A)

# G-Range values
G_RANGE_2G = const(0x00)
G_RANGE_4G = const(0x01)
G_RANGE_8G = const(0x02)
G_RANGE_16G = const(0x03)

# ODR (Output Data Rate) values
ODR_1HZ = const(0x00)
ODR_1_95HZ = const(0x01)
ODR_3_9HZ = const(0x02)
ODR_7_81HZ = const(0x03)
ODR_15_63HZ = const(0x04)
ODR_31_25HZ = const(0x05)
ODR_62_5HZ = const(0x06)
ODR_125HZ = const(0x07)
ODR_250HZ = const(0x08)
ODR_500HZ = const(0x09)
ODR_1000HZ = const(0x0A)

# Interrupt types
INT_ACTIVE_X_EN = const(0x01)
INT_ACTIVE_Y_EN = const(0x02)
INT_ACTIVE_Z_EN = const(0x04)
INT_DOUBLE_TAP_EN = const(0x10)
INT_SINGLE_TAP_EN = const(0x20)
INT_ORIENT_EN = const(0x40)
INT_FREEFALL_EN = const(0x08)
INT_NEW_DATA_EN = const(0x10)

INT_FREEFALL_MAP = const(0x01)
INT_ACTIVE_MAP = const(0x04)
INT_DOUBLE_TAP_MAP = const(0x10)
INT_SINGLE_TAP_MAP = const(0x20)
INT_ORIENT_MAP = const(0x40)
INT_NEW_DATA_MAP = const(0x01)

INT_TYPE_TAP = const(0x02)
INT_TYPE_ORIENT = const(0x04)
INT_TYPE_FREEFALL = const(0x08)
INT_TYPE_DATA_READY = const(0x10)

# Interrupt output configuration
INT_OUT_PUSH_PULL = const(0x00)
INT_OUT_OPEN_DRAIN = const(0x01)

# Interrupt polarity
INT_POLARITY_ACTIVE_LOW = const(0x00)
INT_POLARITY_ACTIVE_HIGH = const(0x01)

# Interrupt latch values
LATCH_NONE = const(0x00)          # Non-latched
LATCH_250MS = const(0x01)         # Temporary latched 250ms
LATCH_500MS = const(0x02)         # Temporary latched 500ms
LATCH_1S = const(0x03)            # Temporary latched 1s
LATCH_2S = const(0x04)            # Temporary latched 2s
LATCH_4S = const(0x05)            # Temporary latched 4s
LATCH_8S = const(0x06)            # Temporary latched 8s
LATCH_PERMANENT = const(0x07)     # Latched
LATCH_NONE_2 = const(0x08)        # Non-latched
LATCH_1MS = const(0x09)           # Temporary latched 1ms
LATCH_1MS_2 = const(0x0A)         # Temporary latched 1ms
LATCH_2MS = const(0x0B)           # Temporary latched 2ms
LATCH_25MS = const(0x0C)          # Temporary latched 25ms
LATCH_50MS = const(0x0D)          # Temporary latched 50ms
LATCH_100MS = const(0x0E)         # Temporary latched 100ms
LATCH_PERMANENT_2 = const(0x0F)   # Latched

# Interrupt source
INT_SRC_ACTIVE = const(0x04)
INT_SRC_TAP = const(0x30)
INT_SRC_ORIENT = const(0x40)
INT_SRC_FREEFALL = const(0x01)
INT_SRC_DATA_READY = const(0x01)

# Tap configuration
TAP_AXIS_X = const(0x01)
TAP_AXIS_Y = const(0x02)
TAP_AXIS_Z = const(0x04)
TAP_AXIS_ALL = const(0x07)

# Orientation configuration
ORIENT_AXIS_X = const(0x01)
ORIENT_AXIS_Y = const(0x02)
ORIENT_AXIS_Z = const(0x04)
ORIENT_AXIS_ALL = const(0x07)

# Freefall configuration
FREEFALL_AXIS_X = const(0x01)
FREEFALL_AXIS_Y = const(0x02)
FREEFALL_AXIS_Z = const(0x04)
FREEFALL_AXIS_ALL = const(0x07)

class MSA311:
    def __init__(self, i2c, addr=MSA311_ADDR, g_range=G_RANGE_2G, odr=ODR_1000HZ):
        self.i2c = i2c
        self.addr = addr
        self._g_range = g_range  # Default g-range
        self._acc_scale = 2.0/32768.0  # Default scale for 2G range
        self._odr = odr
        self.orient = 0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.offset_z = 0.0
        # Initialize callbacks
        self.freefall_callback = None
        self.active_callback = None
        self.tap_callback = None
        self.orientation_callback = None
        
        # Initialize the sensor
        self._init_sensor(self._g_range, self._odr)
        self.get_nvs_offset()
        # print("offset_x:", self.offset_x)
        # print("offset_y:", self.offset_y) 
        # print("offset_z:", self.offset_z)
        time.sleep_ms(100)
        
        # Set up interrupt handler
        self.int_pin = Pin(48, Pin.IN)
        self.int_pin.irq(trigger=Pin.IRQ_FALLING, handler=self._interrupt_handler)
    
    def _write_reg(self, reg, val):
        self.i2c.writeto_mem(self.addr, reg, bytes([val]))
    
    def _read_reg(self, reg, length=1):
        if length == 1:
            return self.i2c.readfrom_mem(self.addr, reg, 1)[0]
        else:
            return self.i2c.readfrom_mem(self.addr, reg, length)
    
    def _read_modify_write(self, reg, mask, val):
        current = self._read_reg(reg)
        # Clear the bits we want to modify
        current &= ~mask
        # Set the new values
        current |= (val & mask)
        # Write back
        self._write_reg(reg, current)
    
    def set_odr(self, odr):
        self._write_reg(REG_ODR, odr)
        
    def set_power_mode(self, power_mode):
        self._write_reg(REG_POWER_MODE, power_mode)    
    
    def set_g_range(self, g_range):
        self._write_reg(REG_G_RANGE, g_range)
        # print("g_range: {}".format(self._read_reg(REG_G_RANGE)))
        self._g_range = g_range
        
        # Update acceleration scale based on g-range
        self._acc_scale = {
            G_RANGE_2G: 2.0/32768.0,
            G_RANGE_4G: 4.0/32768.0,
            G_RANGE_8G: 8.0/32768.0,
            G_RANGE_16G: 16.0/32768.0
        }[g_range]
  
        # print("acc_scale: {}".format(self._acc_scale))  
        
    def set_axis_swap_polarity(self, xy_swap=False, x_pol=0, y_pol=0, z_pol=0):
        swap_polarity = 0
        if xy_swap:
            swap_polarity |= 0x01
        if z_pol:
            swap_polarity |= 0x02
        if y_pol:
            swap_polarity |= 0x04  
        if x_pol:
            swap_polarity |= 0x08
        self._write_reg(REG_AXIS_SWAP_POLARITY, swap_polarity)
      
    def config_interrupt(self, od_lvl= 0x00, latch = 0x00):
        self._write_reg(REG_INT_CONFIG, od_lvl)
        self._write_reg(REG_INT_LATCH, latch)
        self._write_reg(REG_INT_MAP0, 0x00)
        
    def _init_sensor(self, g_range, odr):
        # Soft reset - set bit5 and bit2 to 1
        self._write_reg(REG_SOFT_RESET, 0x24)  # 0x24 = 0b00100100
        time.sleep_ms(10)  # Wait for reset to complete
            
        # Check part ID
        part_id = self._read_reg(REG_PART_ID) 
        if part_id != 0x13:  # MSA311 part ID
            raise RuntimeError(f"Invalid msa311 part ID: {part_id}")
            
        # Set default configuration
        self.set_g_range(g_range)
        self.set_odr(odr)
        self.set_power_mode(0x5e)
        self.set_axis_swap_polarity(xy_swap=False, x_pol=True, y_pol=True, z_pol=True)
        self.config_interrupt()
    
    def read_accel(self):
        # Read raw data
        data = self._read_reg(REG_ACC_X_LSB, 6)
        
        # Convert to 16-bit values
        x = (data[1] << 8) | data[0]
        y = (data[3] << 8) | data[2]
        z = (data[5] << 8) | data[4]
        
        # Convert to signed values
        x = x if x < 32768 else x - 65536
        y = y if y < 32768 else y - 65536
        z = z if z < 32768 else z - 65536
        
        # Scale based on g-range
        return (x * self._acc_scale - self.offset_x, y * self._acc_scale - self.offset_y, z * self._acc_scale - self.offset_z)
        
    def _interrupt_handler(self, pin):
        # Read interrupt status registers
        motion_int_status = self._read_reg(REG_MOTION_INT_STATUS)
        # new_data_status = self._read_reg(REG_NEW_DATA_INT_STATUS)
        # tap_status = self._read_reg(REG_TAP_ACTIVE_STATUS)
        # print("REG_TAP_ACTIVE_STATUS: {}".format(tap_status))
        
        # Check for freefall detection
        # if motion_int_status & INT_SRC_FREEFALL and self.freefall_callback:
        #     self.freefall_callback()
            
        # # Check for active (motion) detection
        if (motion_int_status & INT_SRC_ACTIVE) and self.active_callback:
            self.active_callback()
            
        # Check for tap detection
        if (motion_int_status & INT_SRC_TAP) and self.tap_callback:
            self.tap_callback()
            
        # # Check for orientation change
        if( motion_int_status & INT_SRC_ORIENT) and self.orientation_callback:
            self.orient = self._read_reg(REG_ORIENT_STATUS)
            self.orientation_callback()
           
    def _set_callback(self, int_type, callback):
        if int_type & INT_SRC_FREEFALL:
            self.freefall_callback = callback
        if int_type & (INT_ACTIVE_X_EN | INT_ACTIVE_Y_EN |INT_ACTIVE_Z_EN):
            self.active_callback = callback
        if int_type & INT_SRC_TAP:
            self.tap_callback = callback
        if int_type & INT_SRC_ORIENT:
            self.orientation_callback = callback
        
    def configure_tap_detection(self, int_enable = True, threshold=0x0A, duration=0x04, callback=None):
        # Configure tap detection
        self._write_reg(REG_TAP_TH, threshold)
        self._write_reg(REG_TAP_DUR, duration)
        
        int_map = self._read_reg(REG_INT_MAP0) 
        int_map &= ~(INT_DOUBLE_TAP_MAP | INT_SINGLE_TAP_MAP)
        
        # Enable tap detection for specified axes
        int_set = self._read_reg(REG_INT_SET0)
        int_set &= ~(INT_SINGLE_TAP_EN | INT_DOUBLE_TAP_EN)  # Clear existing tap settings
        
        if int_enable:
            int_map |= INT_DOUBLE_TAP_MAP 
            int_map |= INT_SINGLE_TAP_MAP
            int_set |= INT_SINGLE_TAP_EN  # Enable single tap detection
            int_set |= INT_DOUBLE_TAP_EN
            
        self._write_reg(REG_INT_MAP0, int_map)
        self._write_reg(REG_INT_SET0, int_set)
        
        self._set_callback(INT_SRC_TAP, callback) 
        
        print("int_set0: {}".format(self._read_reg(REG_INT_SET0)))
        print("int_map0: {}".format(self._read_reg(REG_INT_MAP0)))
         
    def configure_orientation_detection(self, int_enable = True, mode=0x18, callback=None):  
        self._write_reg(REG_ORIENT_MODE, mode)
        
        int_map = self._read_reg(REG_INT_MAP0) 
        int_map &= ~INT_ORIENT_MAP        
        # Enable orientation detection
        int_set = self._read_reg(REG_INT_SET0)
        int_set &= ~INT_ORIENT_EN  # Clear existing orientation settings
        if int_enable:
            int_set |= INT_ORIENT_EN  # Enable orientation detection interrupt
            int_map |= INT_ORIENT_MAP
            
        self._write_reg(REG_INT_SET0, int_set)
        self._write_reg(REG_INT_MAP0, int_map)
        
        self._set_callback(INT_SRC_ORIENT, callback)
        
    def configure_freefall_detection(self, int_enable = True, threshold=0x30, duration=0x09, mode=0x01, callback=None):
        # Configure freefall detection
        self._write_reg(REG_FREEFALL_TH, threshold)
        self._write_reg(REG_FREEFALL_DUR, duration)
        self._write_reg(REG_FREEFALL_MODE, mode)
        
        int_map = self._read_reg(REG_INT_MAP0) 
        int_map &= ~INT_FREEFALL_MAP        
        # Enable freefall detection
        int_set = self._read_reg(REG_INT_SET1)
        int_set &= ~INT_FREEFALL_EN  # Clear existing freefall settings
        if int_enable:
            int_set |= INT_FREEFALL_EN  # Enable freefall detection
            int_map |= INT_FREEFALL_MAP
            
        self._write_reg(REG_INT_SET1, int_set)
        self._write_reg(REG_INT_MAP0, int_map)
        
        self._set_callback(INT_SRC_FREEFALL, callback)          
        
    def configure_active_detection(self, int_enable = True, axes=ORIENT_AXIS_ALL, threshold=0x0A, duration=0x00, callback=None):
        self._write_reg(REG_ACTIVE_TH, threshold)
        self._write_reg(REG_ACTIVE_DUR, duration)

        int_map = self._read_reg(REG_INT_MAP0) 
        int_map &= ~INT_ACTIVE_MAP        
        # Enable active detection for specified axes
        int_set = self._read_reg(REG_INT_SET0)
        int_set &= ~(INT_ACTIVE_X_EN | INT_ACTIVE_Y_EN | INT_ACTIVE_Z_EN)  # Clear existing active settings
        if int_enable:
            int_map |= INT_ACTIVE_MAP
            int_set |= axes       
        self._write_reg(REG_INT_SET0, int_set)
        self._write_reg(REG_INT_MAP0, int_map)
        
        self._set_callback(axes, callback)
    
    def auto_calibrate(self):
                # Read raw data
        data = self._read_reg(REG_ACC_X_LSB, 6)
        
        # Convert to 16-bit values
        x = (data[1] << 8) | data[0]
        y = (data[3] << 8) | data[2]
        z = (data[5] << 8) | data[4]
        
        x = x if x < 32768 else x - 65536
        y = y if y < 32768 else y - 65536
        z = z if z < 32768 else z - 65536
        z = z - (16384 >> self._g_range)
            
        self.offset_x = x * self._acc_scale
        self.offset_y = y * self._acc_scale
        self.offset_z = z * self._acc_scale
        print("offset_x:", self.offset_x)
        print("offset_y:", self.offset_y) 
        print("offset_z:", self.offset_z)
        
        self._set_nvs_offset(self.offset_x, self.offset_y, self.offset_z)
        
    def get_nvs_offset(self):
        try:
            tmp = NVS("offset_a")
            self.x_offset = round(tmp.get_i32("x")/1e5, 5)
            self.y_offset = round(tmp.get_i32("y")/1e5, 5)
            self.z_offset = round(tmp.get_i32("z")/1e5, 5)
        except OSError as e:
            self.x_offset = 0
            self.y_offset = 0
            self.z_offset = 0
    
    def _set_nvs_offset(self, offset_x, offset_y, offset_z):
        try:
            nvs = NVS("offset_a")
            nvs.set_i32('x', int(offset_x*1e5))
            nvs.set_i32('y', int(offset_y*1e5))
            nvs.set_i32('z', int(offset_z*1e5))
            nvs.commit()
        except OSError as e:
            print('Gyroscope set_nvs_offset error:',e)
        