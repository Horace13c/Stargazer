# %%
import pandas as pd
import sys
import base64
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
import os
import time
import getpass

# %%
BLOCK_SIZE = 16


def get_private_key_salt(password, salt=None):
    if salt == None:
        saltBin = os.urandom(16)
        salt = saltBin.hex()
    else:
        saltBin = bytes.fromhex(salt)

    kdf = PBKDF2(password, saltBin, 64, 100000)
    key = kdf[:32]

    return [key, salt]


def encrypt(raw, private_key):
    iv = os.urandom(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(pad(raw.encode('utf-8'), BLOCK_SIZE)))


def encrypt_cols(encryption_dict, password):
    encrypted_dict = {}
    encrypted_dict['salt'] = []
    for dict_key in encryption_dict.keys():
        encrypted_dict[dict_key] = []
        for index in range(0, len(encryption_dict[dict_key])):
            try:
                key_salt_pair = get_private_key_salt(password, encrypted_dict['salt'][index])
            except IndexError:
                key_salt_pair = get_private_key_salt(password)
                encrypted_dict['salt'].append(key_salt_pair[1])
            cipher_text = encrypt(str(encryption_dict[dict_key][index]), key_salt_pair[0])
            encrypted_dict[dict_key].append(cipher_text.decode("utf-8"))

    return encrypted_dict


def prep_encryption_cols(encrypt_list):
    encryption_dict = {}
    for col_name in encrypt_list:
        try:
            encryption_dict[col_name] = df[col_name]
        except KeyError:
            print('No column with name \'' + col_name + '\' Found. De-identification Failed!')
            sys.exit()
    return encryption_dict


def encryption(df, encrypt_list, password):
    encryption_dict = prep_encryption_cols(encrypt_list)
    encrypted_dict = encrypt_cols(encryption_dict, password)

    for key in encrypted_dict.keys():
        df[key] = encrypted_dict[key]
