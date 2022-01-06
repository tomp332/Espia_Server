import os
import pathlib

import uvicorn

from espia_server.app.utils.espia_logging import log_info
from espia_server.app.utils.tool_utils import config


def main():
    certs_dir = pathlib.Path(pathlib.Path(os.path.realpath(__file__)).parent / 'certs')
    log_info(
        f"Started Espia Server with configuration -> {config['app'].get('SERVER_IP')}:{config['app'].get('SERVER_PORT')}")
    uvicorn.run("espia_server.app.api:app",
                host=config['app'].get('SERVER_IP'),
                port=int(config['app'].get('SERVER_PORT')),
                reload=True,
                log_level="info",
                ssl_keyfile=certs_dir / 'public_key.pem',
                ssl_certfile=certs_dir / 'private_key.pem')


if __name__ == '__main__':
    main()
