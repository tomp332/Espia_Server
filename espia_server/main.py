import os
import pathlib

import uvicorn

if __name__ == '__main__':
    certs_dir = pathlib.Path(pathlib.Path(os.path.realpath(__file__)).parent / 'certs')
    uvicorn.run("app.api:app",
                host="127.0.0.1",
                port=443,
                reload=True,
                ssl_keyfile=certs_dir / 'key.pem',
                ssl_certfile=certs_dir / 'cert.pem'
                )
