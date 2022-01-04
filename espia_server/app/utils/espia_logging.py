import logging
import pathlib

from colored import fg

# For output purposes
block = fg('light_sky_blue_3a')
title = fg('blue')
main_title = fg('red')
data = fg('dark_green_sea')
error_message = fg('red')

logging_path = f'{pathlib.Path(__file__).parent}/logs'
logging.basicConfig(filename=f'{logging_path}/espia_server.log', format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')


def log_error(message):
    print(f"{error_message}[-] {message}")
    logging.error(message)


def log_info(message):
    print(f"{title}[+] {message}")
    logging.info(message)
