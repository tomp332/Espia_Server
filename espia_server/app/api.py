from fastapi import FastAPI, File, UploadFile, Request

from app.utils import handle_products_results, handle_new_uploaded_file, uploaded_products, create_new_client_dir

app = FastAPI()


@app.get("/")
def root_path() -> dict:
    return {}


@app.post("/zn1123n/asnndj")
def upload_results(results: dict) -> dict:
    create_new_client_dir(results.get('Session-ID'))
    handle_products_results(results)
    return {}


@app.post("/zn1123n/asnndj/bbcsgq")
async def create_upload_file(request: Request, fileUpload: UploadFile = File(...)) -> dict:
    file_path = handle_new_uploaded_file(request.headers.get('Session'), fileUpload.filename)
    uploaded_products.append(fileUpload.filename)
    with open(file_path, 'wb') as f:
        content = await fileUpload.read()
        f.write(content)
    return {}
