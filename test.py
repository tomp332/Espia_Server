import os
import json
import base64
import sys
from Cryptodome.Cipher import AES
import shutil


def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)


def generate_cipher(master_key, iv):
    return AES.new(master_key, AES.MODE_GCM, iv)


def decrypt_password(encrypted_password, master_key):
    try:
        iv = encrypted_password[3:15]
        payload = encrypted_password[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()  # remove suffix bytes
        return decrypted_pass
    except:
        return "Unknown"


if __name__ == '__main__':
    hex = sys.argv[1]
    password = bytes.fromhex(hex)
    hex = sys.argv[2]
    key = bytes.fromhex(hex)
    password = decrypt_password(password, key)
    print(password)
