from fastapi import FastAPI
from .routes import router

app = FastAPI(title="Axkan II Game API")
app.include_router(router, prefix="/api/v1") 