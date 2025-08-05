from rfid import rfid_522

class Rfid():
    """扫描Rfid卡类.
    """

    def __init__(self, i2c, i2c_addr = 47):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.purse_block = 1
        self.rw_block_number = 2
        self._rfid = rfid_522(i2c = self.i2c, i2c_addr = self.i2c_addr)
        
    def _judge_block(self, block_number):
        """判断block是否可用。

        RFID卡内储存空间分为16 个扇区，每个扇区由4 块（块0、块1、块2、块3）组成，（我们也
        将16 个扇区的64 个块按绝对地址编号为0~63。第0 扇区的块0（即绝对地址0 块），它用于存放厂商代码，已经固化，不可更改。
        每个扇区的块0、块1、块2 为数据块，可用于存贮数据。

        :param block_number: 块编号
        """
        unused_blocked = [i*2 ^ 2-1 for i in range(1, 16)]
        unused_blocked.append(0)
        if block_number in unused_blocked:
            raise Exception(
                "This block {} can't be accessed!" .format(block_number))
        else:
            return True
        
    def card_auth(self, block_number):
        self._rfid.init(self.i2c)
        cardtype = self._rfid.find_card()
        if cardtype:
            self.serial_num_tuple = self._rfid.anticoll()
            if self.serial_num_tuple:
                if self._rfid.select_tag(self.serial_num_tuple):
                    return self._rfid.auth(self.serial_num_tuple, block_number)
        else:
            print("未检测到射频卡")
            return False
                
    def get_serial_num(self):
        self._rfid.init(self.i2c)
        cardtype = self._rfid.find_card()
        if cardtype:
            self.serial_num_tuple = self._rfid.anticoll()
            if self.serial_num_tuple:
                serial_num = int.from_bytes(bytes(self.serial_num_tuple[:-1]), 'little')
                return serial_num
        else:
            print("未检测到射频卡")
            return False
        
    def serial_number(self):
        return self.get_serial_num()
    
    def read_block(self, block_number = 2):
        if self._judge_block(block_number):
            self.card_auth(block_number)
            buff = self._rfid.read_block(block_number)
            self._rfid.halt()
            return buff

    def write_block(self, buf, block_number = 2):
        if self._judge_block(block_number):
            self.card_auth(block_number)
            self._rfid.write_block(block_number, buf)
            self._rfid.halt()

    def set_purse(self, block_number = 1):
        """
        设置电子钱包,默认使用block 1。

        :param int block_number: 块编号
        """
        if self._judge_block(block_number):
            self.purse_block = block_number
            self.card_auth(self.purse_block)
            self._rfid.set_purse(self.purse_block)
            self._rfid.halt()
            
    def get_balance(self):
        """
        获取电子钱包余额。使用该函数前,必须对数据块进行 ``set_purse()`` 设置。

        :return: 返回余额
        """
        if self.purse_block:
            self.card_auth(self.purse_block)
            puser =  self._rfid.balance(self.purse_block)
            self._rfid.halt()
            return puser

    def increment(self, value):
        """
        给电子钱包充值。使用该函数前,必须对数据块进行 ``set_purse()`` 设置。

        :param int value: 充值 
        """
        if self.purse_block:
            self.card_auth(self.purse_block)
            self._rfid.increment(self.purse_block, value)
            self._rfid.halt()

    def decrement(self, value):
        """
        给电子钱包扣费。使用该函数前,必须对数据块进行 ``set_purse()`` 设置。

        :param int value: 扣费 
        """
        if self.purse_block:    
            self.card_auth(self.purse_block)
            self._rfid.decrement(self.purse_block, value)
            self._rfid.halt()

    

            