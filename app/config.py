import os

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.middleware.sessions import SessionMiddleware

host = os.getenv("API_HOST", "localhost")
port = os.getenv("API_PORT", "8000")
secret_key = os.getenv("SECRET_KEY", "secret-string")
port = int(port)
app_title = "HHBOT"
app_version = "0.0"

app = FastAPI(title=app_title)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app_title,
        version=app_version,
        routes=app.routes,
    )

    for route in app.routes:
        if hasattr(route.endpoint, "_query_extra"):
            path = route.path
            method = list(route.methods)[0].lower()

            path_item = openapi_schema["paths"][path][method]
            path_item["parameters"].append(
                {
                    "name": "extra_params",
                    "in": "query",
                    "required": False,
                    "schema": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                    },
                    "style": "form",
                    "explode": True,
                }
            )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
app.add_middleware(SessionMiddleware, secret_key=secret_key)
config = uvicorn.Config(app, host=host, port=port)
server = uvicorn.Server(config)
