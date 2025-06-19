from typing import Optional

from pydantic import BaseModel, Field


class Negotiation(BaseModel):
    message: Optional[str] = Field(None, max_length=10_000)
    resume_id: str
    vacancy_id: str
