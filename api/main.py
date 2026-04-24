from fastapi import FastAPI
from api.routes.analise_routes import router

app = FastAPI(
    title="API - Detecção de Rachaduras",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
def home():
    return {"status": "API online 🚀"}