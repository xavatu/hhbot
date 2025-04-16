from app.config import server, app
from app.hh_integration.client.oauth import oauth_router
from app.hh_integration.resume.service import resume_router

app.include_router(oauth_router)
app.include_router(resume_router)
