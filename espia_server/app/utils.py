from app.browsers.firefox.firefox_utils import handle_all_firefox_modules
from app.browsers.chrome.chrome_utils import handle_all_chrome_modules

from colored import fg

import pathlib
import os



# For output purposes
block = fg('light_sky_blue_3a')
title = fg('blue')
main_title = fg('red')
data = fg('dark_green_sea')


uploads_path = pathlib.Path(pathlib.Path(os.path.realpath(__file__)).parent / 'uploads')
uploaded_products = []

def handle_new_uploaded_file(file_name: str) -> pathlib.Path:
    '''
    Returns the specified new path for an uploaded file

    :param file_name: string file name
    :return: pathlib object  to full upload path
    '''
    file_path = uploads_path / file_name
    file_path.parent.mkdir(exist_ok=True, parents=True)
    return file_path

def handle_products_results(results: dict) -> None:
    handle_all_chrome_modules(results)
    handle_all_firefox_modules(results)
    output_summary()

def output_summary():
    print(block + '[--]')
    print(title + '|Amount of files retrieved|' + data + len(uploaded_products))