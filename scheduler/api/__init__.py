from router import auto_apply_config_router

from .config import app
from .middleware import SyncRedBeatMiddleware

app.include_router(auto_apply_config_router)
app.add_middleware(SyncRedBeatMiddleware)
