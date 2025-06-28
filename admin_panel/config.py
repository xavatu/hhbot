import os

import uvicorn
from fastapi import FastAPI

host = os.getenv("API_HOST", "localhost")
port = os.getenv("API_PORT", "8001")
port = int(port)
app_title = "Admin"

app = FastAPI(title=app_title)

config = uvicorn.Config(app, host=host, port=port)
server = uvicorn.Server(config)
