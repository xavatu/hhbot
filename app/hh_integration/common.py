from enum import StrEnum


class HHUrls(StrEnum):
    BASE = "https://hh.ru/"
    AUTHORIZE = "https://hh.ru/oauth/authorize"
    TOKEN = "https://hh.ru/oauth/token"
    RESUMES = "https://api.hh.ru/resumes"
    NEGOTIATIONS = "https://api.hh.ru/negotiations"
