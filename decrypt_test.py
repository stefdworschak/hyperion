### Dependence ###############
# pip install pycrypto==2.6.1
##############################
import base64
import hashlib
import json

from Cryptodome import Random
from Cryptodome.Cipher import AES


class AESCipher:
    bs = AES.block_size

    def __init__(self, key):
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, message):
        message = self._pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(message)).decode('utf-8')

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        print(len(enc[AES.block_size:]))
        inner_padding = b"=" * (16 - len(enc[AES.block_size:]) % 16)
        return cipher.decrypt(enc[AES.block_size:] + inner_padding)

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        print(ord(s[len(s)-1:]))
        return s[:-ord(s[len(s)-1:])]
    
def unpack(s):
    pos = str(s).find('\\')
    return str(s)[2:pos]

if __name__ == '__main__':
    #key = "lingyejunAesTest"
    key = "42722742462086"
    plain_message = 'Hello'
    with open("data.txt") as file:
        encrypted_message = file.read()
    outer_padding =  "=" * (4 - len(encrypted_message) % 4)
    print(len(encrypted_message))
    encrypted_message += outer_padding 
    aes_cipher = AESCipher(key)
    decrypted = aes_cipher.decrypt(encrypted_message)
    print(f'Android encrypted Message: {decrypted}')
    unpacked = unpack(decrypted).replace("'", "\"")
    d = json.loads(unpacked)
    print(d['address'])
