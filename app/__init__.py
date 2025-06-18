from app.config import server, app
from app.hh_integration.auto_apply.service import auto_apply, auto_apply_router
from app.hh_integration.client.oauth import oauth_router
from app.hh_integration.negotiation.service import negotiation_router
from app.hh_integration.resume.service import resume_router

app.include_router(oauth_router)
app.include_router(resume_router)
app.include_router(negotiation_router)
app.include_router(auto_apply_router)
