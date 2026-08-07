import os

from .base import *  # noqa: F403,F401

DEBUG = False

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = os.getenv("DJANGO_COOKIE_SECURE", "1") == "1"
CSRF_COOKIE_SECURE = os.getenv("DJANGO_COOKIE_SECURE", "1") == "1"

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
