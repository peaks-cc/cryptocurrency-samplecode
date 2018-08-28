from Crypto import Random
from Crypto.Cipher import AES

import random
import string
import hashlib

class AESUtil:

    def __init__(self):
        k_seed = ''.join(random.choices(string.ascii_letters + string.digits, k=AES.block_size))
        self.secret_key = hashlib.sha256(k_seed.encode('utf-8')).digest()

    def get_aes_key(self):
        return self.secret_key

    def pad(self, target):
        target_len = len(target.encode("utf-8"))
        return target + (AES.block_size - target_len % AES.block_size) * chr(0)

    def encrypt(self, message):
        message = self.pad(message)
        print(message.encode('utf-8'))
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.secret_key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(message)

    def decrypt(self, ciphertext):
        iv = ciphertext[:AES.block_size]
        cipher = AES.new(self.secret_key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext[AES.block_size:])
        return plaintext.rstrip(b"\0")

    def decrypt_with_key(self, ciphertext, key):
        iv = ciphertext[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext[AES.block_size:])
        return plaintext.rstrip(b"\0")