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
