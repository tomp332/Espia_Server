import os
import pathlib

import uvicorn

from espia_server.app.utils import config


def main():
    certs_dir = pathlib.Path(pathlib.Path(os.path.realpath(__file__)).parent / 'certs')
    uvicorn.run("espia_server.app.api:app",
                host=config['app'].get('SERVER_IP'),
                port=int(config['app'].get('SERVER_PORT')),
                reload=True,
                ssl_keyfile=certs_dir / f"{os.getenv('ESPIA_ENV')}" / 'key.pem',
                ssl_certfile=certs_dir / f"{os.getenv('ESPIA_ENV')}" / 'cert.pem')


if __name__ == '__main__':
    main()
