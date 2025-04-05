import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from api import app
import logging
import sys


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

if __name__ == "__main__":
    asyncio.get_event_loop().set_debug(True)

    uvicorn.run(
        "main:app",
        host="127.0.0.1",  # Changed from "localhost" to "127.0.0.1" for better WebSocket support
        port=8000,
        reload=True,  # Enable auto-reload for development
        ws="auto",
        loop="asyncio",
        # ws="auto",  # Enable WebSocket support
        log_level="info"  # Set uvicorn log level to info
    )
