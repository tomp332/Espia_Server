from fastapi import FastAPI, File, UploadFile

from app.utils import handle_products_results, handle_new_uploaded_file, uploaded_products

app = FastAPI()


@app.get("/")
def root_path() -> dict:
    return


@app.post("/zn1123n/asnndj")
def upload_results(results: dict) -> dict:
    handle_products_results(results)
    return

@app.post("/zn1123n/asnndj/bbcsgq")
async def create_upload_file(fileUpload: UploadFile = File(...)):
    file_path = handle_new_uploaded_file(fileUpload.filename)
    uploaded_products.append(fileUpload.filename)
    with open(file_path, 'wb') as f:
        content = await fileUpload.read()
        f.write(content)
    return