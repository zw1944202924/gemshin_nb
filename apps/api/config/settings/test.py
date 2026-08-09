from .base import *  # noqa: F403,F401
from apps.oidc.keys import get_test_oidc_private_key


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test.sqlite3",  # noqa: F405
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

OAUTH2_PROVIDER = {
    **OAUTH2_PROVIDER,  # noqa: F405
    "OIDC_RSA_PRIVATE_KEY": get_test_oidc_private_key(),
    "ALWAYS_RELOAD_OAUTHLIB_CORE": True,
}
