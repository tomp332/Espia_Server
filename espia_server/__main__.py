import os
import pathlib

import uvicorn


def main():
    certs_dir = pathlib.Path(pathlib.Path(os.path.realpath(__file__)).parent / 'certs')
    uvicorn.run("espia_server.app.api:app",
                host="0.0.0.0",
                port=443,
                reload=True,
                ssl_keyfile=certs_dir / 'key.pem',
                ssl_certfile=certs_dir / 'cert.pem')


if __name__ == '__main__':
    main()
