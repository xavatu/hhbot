import os

import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

host = os.getenv("API_HOST", "localhost")
port = os.getenv("API_PORT", "8000")
secret_key = os.getenv("SECRET_KEY", "secret-string")
port = int(port)

app = FastAPI(title="HHBOT")
app.add_middleware(SessionMiddleware, secret_key=secret_key)
config = uvicorn.Config(app, host=host, port=port)
server = uvicorn.Server(config)
