from db.models.client import Client, Session
from db.models.negotiation import Filter, AutoApplyConfig
from db.session import get_db_session
from fabric.router.default import generate_default_router

client_router = generate_default_router(
    model=Client,
    get_session=get_db_session,
    prefix="/clients",
    tags=["clients"],
    exclude_fields=["client_id"],
    allowed_methods=[
        "get_all",
        "get_one",
        "create",
        "update",
        "patch",
        "delete",
    ],
)
session_router = generate_default_router(
    model=Session,
    get_session=get_db_session,
    prefix="/sessions",
    tags=["sessions"],
    allowed_methods=[
        "get_all",
        "create",
        "delete",
    ],
)
filter_router = generate_default_router(
    model=Filter,
    get_session=get_db_session,
    prefix="/filters",
    tags=["filters"],
    allowed_methods=[
        "get_all",
        "get_one",
        "create",
        "update",
        "patch",
        "delete",
    ],
)
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
