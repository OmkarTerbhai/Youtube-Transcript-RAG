from fastapi import FastAPI;
from app.controllers import health_controller, ingestion_controller, query_controller, csv_controller;

app = FastAPI()

@app.get("/")
def hello() -> dict[str, str]:
    return {"message": "Hello, World!"}

app.include_router(health_controller.router);
app.include_router(ingestion_controller.router);
app.include_router(query_controller.router);
app.include_router(csv_controller.router);



def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)

