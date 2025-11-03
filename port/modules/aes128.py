# import uos
# IV = uos.urandom(16)
from ucryptolib import aes
import ujson

#ByteToHex的转换，返回数据16进制字符串
def ByteToHex(bins):
    return ''.join( [ "%02X" % x for x in bins ] ).strip

KEY = bytes.fromhex('D448F32544D4119680594E706ED93C5C') #16bytes 128bits 密钥
IV  = bytes.fromhex('D448F32544D4119680594E706ED93C5C') 
MODE_CBC = 2

def aes_128_cbc_encrypt(data):
    # 加密
    # print("Using AES{}-CBC cipher".format(len(KEY * 8)))
    padded = data + " " * (16 - len(data) % 16) #填充 ' ' 
    # print('padded: {}'.format(padded))    
    cipher = aes(KEY, MODE_CBC, IV)
    encrypted = cipher.encrypt(padded)
    # print('Encrypted: {}'.format(encrypted))
    # print(ByteToHex(encrypted))
 
    return encrypted

def aes_128_cbc_decrypt(encrypted):
    # 解密
    # print("Using AES{}-CBC cipher".format(len(KEY * 8)))
    decipher = aes(KEY, MODE_CBC, IV)
    decrypt_str = decipher.decrypt(encrypted).decode('utf-8').replace(' ','')

    return decrypt_str
