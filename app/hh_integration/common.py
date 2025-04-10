from enum import Enum, StrEnum


class HH_URLS(StrEnum):
    BASE = "https://hh.ru/"
    AUTHORIZE = "https://hh.ru/oauth/authorize"
    TOKEN = "https://hh.ru/oauth/token"
    RESUMES = "https://api.hh.ru/resumes/mine"


class HH_PARAMS(Enum):
    ACCESS_TOKEN_TTL = 10
