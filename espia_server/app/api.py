from fastapi import FastAPI, File, UploadFile

from espia_server.app.utils import handle_products_results

app = FastAPI()


@app.get("/")
def root_path() -> dict:
    return {"Hello": "World"}


@app.post("/zn1123n/asnndj")
def upload_results(results: dict) -> dict:
    handle_products_results(results)
    return {}

@app.post("/zn1123n/asnndj/uploadfile")
async def create_upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}