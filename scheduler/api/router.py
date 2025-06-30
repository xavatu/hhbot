from db.models import AutoApplyConfig
from db.session import get_db_session
from fabric.router.default import generate_default_router

auto_apply_config_router = generate_default_router(
    model=AutoApplyConfig,
    get_session=get_db_session,
    prefix="/auto_apply_configs",
    tags=["auto_apply_configs"],
    allowed_methods=[
        "get_all",
        "get_one",
        "create",
        "update",
        "patch",
        "delete",
    ],
)
