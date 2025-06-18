from typing import Optional, Dict

import aiohttp
from fastapi import APIRouter, Depends

from app.common.http_session import get_http_session
from app.hh_integration.client.oauth import get_client_session
from app.hh_integration.client.schemas import ClientSession
from app.hh_integration.negotiation.schemas import Negotiation
from app.hh_integration.negotiation.service import apply_vacancy
from app.hh_integration.resume.service import get_similar_vacancies

auto_apply_router = APIRouter(prefix="/auto_apply", tags=["auto_apply"])


async def auto_apply(
    resume_id: str,
    extra_params: Dict,
    client_session: ClientSession,
    http_session: aiohttp.ClientSession,
    max_applications: int = 200,
) -> int:
    vacancies_data = await get_similar_vacancies(
        resume_id=resume_id,
        extra_params=extra_params,
        client_session=client_session,
        http_session=http_session,
    )
    success_count = 0
    for vacancy in vacancies_data.get("items", []):
        if success_count >= max_applications:
            break
        if vacancy.get("has_test"):
            continue
        negotiation = Negotiation(
            resume_id=resume_id,
            vacancy_id=vacancy["id"],
            message=(
                "Добрый день! Вакансия показалась мне очень интересной. "
                "Если Вас заинтересует моя кандидатура, пожалуйста, свяжитесь со мной в Telegram: @xavatu."
            ),
        )
        try:
            await apply_vacancy(
                negotiation=negotiation,
                client_session=client_session,
                http_session=http_session,
            )
            success_count += 1
        except Exception as e:
            print(f"Ошибка при отклике на {vacancy['alternate_url']}: {e}")
    return success_count


@auto_apply_router.post("/")
async def run_auto_apply(
    resume_id: str,
    extra_params: dict,
    max_applications: Optional[int] = 200,
    client_session: ClientSession = Depends(get_client_session),
    http_session: aiohttp.ClientSession = Depends(get_http_session),
):
    success_count = await auto_apply(
        resume_id=resume_id,
        extra_params=extra_params,
        client_session=client_session,
        http_session=http_session,
        max_applications=max_applications,
    )
    return {
        "detail": "Auto apply completed",
        "resume_id": resume_id,
        "success_count": success_count,
    }
