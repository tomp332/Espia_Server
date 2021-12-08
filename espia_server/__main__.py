import os
import pathlib

import uvicorn

def main():
    certs_dir = pathlib.Path(pathlib.Path(os.path.realpath(__file__)).parent / 'certs')
    uvicorn.run("espia_server.app.api:app",
                host="127.0.0.1",
                port=443,
                reload=True,
                ssl_keyfile=certs_dir / 'key.pem',
                ssl_certfile=certs_dir / 'cert.pem')

if __name__ == '__main__':
    main()
