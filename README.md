# Espia Server
## Setup and Installation
### Step 1 [Optional] - Create and Activate a Virtual Environment (python 3.9 >= )
1. Run the following command: `python3.9 -m venv <env_dir_path>`
2. Activate the environment  
2.1. Windows:  `\<env_dir_path>\Scripts\Activate.bat` or `\<env_dir_path>\Scripts\Activate.ps1`  
2.2. Linux:  `. <env_dir_path>/bin/activate`
### Step 2 - Install required packages
1. Run `python -m pip install -r requirements.txt`
2. sudo setcap CAP_NET_BIND_SERVICE=+eip /usr/bin/python3.9 (for letting a user run server on priv port)

## Package option:
1. By default the latest docker image is exported on 443, which means that if for some reason you want the main server to be exported on a different port, re-build the image locally.
2. Overide the default config.ini file :
```
[app]
SERVER_IP=0.0.0.0
SERVER_PORT=443

[mailgun]
API_KEY=<Mailgun api key>
MAILGUN_DOMAIN=<Mailgun email domain>
MAILGUN_USER=<Mailgun username>
DESTINATION_EMAIL=<Destination email for results to be sent to>
```
1. Run the image:
```
docker run -p 443:443 -v <your config.ini file absolute path that was created>:/server/espia_server/configs/config.ini ghcr.io/tomp332/espia-server:latest
```
