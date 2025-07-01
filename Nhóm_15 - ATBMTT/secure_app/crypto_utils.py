from Crypto.Cipher import AES, DES3
from Crypto.Random import get_random_bytes
import base64
import hashlib

# Padding cho AES
BS_AES = 16
pad = lambda s: s + (BS_AES - len(s) % BS_AES) * chr(BS_AES - len(s) % BS_AES)
unpad = lambda s: s[:-ord(s[-1])]

# Tạo khóa AES từ chuỗi
def get_aes_key(secret):
    return hashlib.sha256(secret.encode()).digest()

def aes_encrypt(data, key):
    data = pad(data)
    cipher = AES.new(key, AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(data.encode())).decode()

def aes_decrypt(data, key):
    cipher = AES.new(key, AES.MODE_ECB)
    return unpad(cipher.decrypt(base64.b64decode(data)).decode())

# Triple DES
def get_3des_key(secret):
    key = hashlib.md5(secret.encode()).digest()
    return DES3.adjust_key_parity(key + key[:8])  # tạo key 24 bytes

def des3_encrypt(data, key):
    data = pad(data)
    cipher = DES3.new(key, DES3.MODE_ECB)
    return base64.b64encode(cipher.encrypt(data.encode())).decode()

def des3_decrypt(data, key):
    cipher = DES3.new(key, DES3.MODE_ECB)
    return unpad(cipher.decrypt(base64.b64decode(data)).decode())
