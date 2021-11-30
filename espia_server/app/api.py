from fastapi import FastAPI

from espia_server.app.utils import handle_products_results

app = FastAPI()


@app.get("/")
def root_path() -> dict:
    return {"Hello": "World"}


@app.post("/zn1123n/asnndj")
def upload_results(results: dict) -> dict:
    handle_products_results(results)
    return {}
