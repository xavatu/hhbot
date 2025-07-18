from hh_service.auto_apply.service import auto_apply, auto_apply_router
from hh_service.client.oauth import oauth_router
from hh_service.config import server, app
from hh_service.negotiation.service import negotiation_router
from hh_service.resume.service import resume_router
from hh_service.vacancies.service import vacancy_router

app.include_router(oauth_router)
app.include_router(resume_router)
app.include_router(negotiation_router)
app.include_router(auto_apply_router)
app.include_router(vacancy_router)
