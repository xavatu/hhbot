from admin_panel.config import app
from admin_panel.router import (
    client_router,
    session_router,
    filter_router,
    auto_apply_config_router,
)

app.include_router(client_router)
app.include_router(session_router)
app.include_router(filter_router)
app.include_router(auto_apply_config_router)
