### Dependence ###############
# Author: crazygit
# Adapted from this gist: https://gist.github.com/crazygit/79eaacccd84f08a692615d19d960de37
# Last Accessed: 27 April 2020
##############################
import base64
import hashlib
import json
import os

from Cryptodome import Random
from Cryptodome.Cipher import AES
import pymongo

import env_vars

MONGO_URL = os.environ.get('MONGO_URL','No value loaded')

class AESCipher:
    bs = AES.block_size

    def __init__(self, key):
        self.key = hashlib.sha256(key.encode()).digest()

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        inner_padding = b"=" * (16 - len(enc[AES.block_size:]) % 16)
        return cipher.decrypt(enc[AES.block_size:] + inner_padding)

    @staticmethod
    def _unpad(s):
        print(ord(s[len(s)-1:]))
        return s[:-ord(s[len(s)-1:])]
    
def unpack(s):
    pos = str(s).find('\\')
    return str(s)[2:pos]

def decrypt_to_dict(encrypted_message, key):
    decrypted_data = None
    try:
        outer_padding =  "=" * (4 - len(encrypted_message) % 4)
        encrypted_message += outer_padding 
        aes_cipher = AESCipher(key)
        decrypted = aes_cipher.decrypt(encrypted_message)
        unpacked = unpack(decrypted).replace("'", "\"")
        raw_json = json.loads(unpacked)
        cleaned_data = {}
        for key, value in raw_json.items():
            if isinstance(value, str):
                cleaned_data[key] = value
            elif isinstance(value, dict):
                cleaned_data[key] = value.get('mValue') or ""
            elif isinstance(value, list):
                cleaned_data[key] = value
            else:
                cleaned_data[key] = value
        return cleaned_data
    except Exception as e:
        print("An error occurred", e)
    return decrypted_data

def retrieve_encrypted_data(data_key):
    encrypted_data = None
    try:
        myclient = pymongo.MongoClient(MONGO_URL)
        mydb = myclient["hyperion"]
        mycol = mydb["hyperion_auth"]
        record = mycol.find_one({"owner_id":data_key})
        return record['data'].replace("\n","")
    except Exception as e:
        print("An error occurred", e)
    return encrypted_data


#if __name__ == '__main__':
#    key = "42722742462086"
#    data = retrieve_encrypted_data(key)
#    print(data)
