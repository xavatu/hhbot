import uuid

from celery import Celery
from celery.schedules import crontab
from pydantic import ConfigDict, field_validator
from redbeat import RedBeatSchedulerEntry

from db.models import AutoApplyConfig
from fabric.schemas.generate import generate_pydantic_schema_from_model

AutoApplyConfigSchema = generate_pydantic_schema_from_model(
    AutoApplyConfig,
    config=ConfigDict(
        json_encoders={uuid.UUID: lambda v: str(v)}, from_attributes=True
    ),
)


class AutoApplyRedBeatTask(AutoApplyConfigSchema):
    session_id: str
    resume_id: str

    @field_validator("session_id", "resume_id", mode="before")
    @classmethod
    def uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    @property
    def task_name(self):
        return f"auto_apply_{self.id}"

    @property
    def redbeat_key(self):
        return f"redbeat:scheduled:{self.task_name}"

    @property
    def celery_crontab(self):
        expr = self.cron_schedule.strip()
        try:
            return crontab.from_string(expr)
        except Exception:
            raise

    def add_to_redbeat(self, app_celery: Celery):
        entry = RedBeatSchedulerEntry(
            name=self.task_name,
            task="tasks.run_auto_apply_task_sync",
            schedule=self.celery_crontab,
            args=[
                self.session_id,
                self.resume_id,
                self.filter_id,
                self.max_applications,
                self.similar_vacancies,
                self.message,
            ],
            app=app_celery,
        )
        entry.save()

    def remove_from_redbeat(self, app_celery: Celery):
        try:
            entry = RedBeatSchedulerEntry.from_key(
                self.redbeat_key, app=app_celery
            )
            entry.delete()
        except KeyError:
            raise

    def sync(self, app_celery: Celery):
        if self.enabled:
            self.add_to_redbeat(app_celery)
        else:
            self.remove_from_redbeat(app_celery)
