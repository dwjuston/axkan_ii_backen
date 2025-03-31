import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import app
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('server.log')
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # Changed from "api:app" to "main:app"
        host="127.0.0.1",  # Changed from "localhost" to "127.0.0.1" for better WebSocket support
        port=8000,
        reload=True,  # Enable auto-reload for development
        ws="auto",  # Enable WebSocket support
        log_level="info"  # Set uvicorn log level to info
    )
