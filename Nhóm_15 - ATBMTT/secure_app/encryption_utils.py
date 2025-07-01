from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
import hashlib
import base64

# Khóa cố định dài 24 byte (phải bảo mật trong thực tế)
SECRET_KEY = b'123456789qwertyuioasdfg'

# Đệm dữ liệu cho đủ block 8 byte (DES block size)
def pad(text):
    while len(text) % 8 != 0:
        text += ' '
    return text

def encrypt_data(plain_text):
    if isinstance(plain_text, bytes):
        plain_text = plain_text.decode('utf-8')  # chuyển bytes -> str

    plain_text = pad(plain_text)
    cipher = DES3.new(SECRET_KEY, DES3.MODE_ECB)
    encrypted = cipher.encrypt(plain_text.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')


def decrypt_data(encrypted_text):
    encrypted = base64.b64decode(encrypted_text)
    cipher = DES3.new(SECRET_KEY, DES3.MODE_ECB)
    decrypted = cipher.decrypt(encrypted)
    return decrypted.decode('utf-8').rstrip()

def hash_password(password):
    # SHA-256 hash
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(input_password, stored_hash):
    return hash_password(input_password) == stored_hash
