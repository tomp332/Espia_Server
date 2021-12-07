import uvicorn

if __name__ == '__main__':
    uvicorn.run("app.api:app", host="127.0.0.1", port=443, reload=True, ssl_keyfile='C:\\UsersPC\\Documents\\GitHub\\Espia_Server\\espia_server\\app\\certs\\key.pem', ssl_certfile='C:\\Users\\PC\\Documents\\GitHub\\Espia_Server\\espia_server\\app\\certs\\cert.pem')
