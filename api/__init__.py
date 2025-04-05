from math import trunc
from typing import Optional

from fastapi import FastAPI, Depends
from fastapi.security import APIKeyHeader
from fastapi import HTTPException, Security, status
from .routes import router, ws_router
import os

api_key_internal = os.getenv("API_KEY_INTERNAL")

API_KEY_NAME = "AXKAN"
API_KEY_HEADER = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def check_api_key(api_key_header: str = Security(API_KEY_HEADER)) -> bool:
    if api_key_header is None:
        raise HTTPException(status_code=403, detail="Internal API Key is missing")

    if api_key_header == api_key_internal:  # Replace with your actual API key validation logic
        return True
    else:
        raise HTTPException(status_code=401, detail="Invalid API Key")

app = FastAPI(title="Axkan II Game API")
app.include_router(router, prefix="/api/v1", dependencies=[Security(check_api_key)])
app.include_router(ws_router, prefix="/api/v1")

