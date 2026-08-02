from pathlib import Path
import os

import pymysql
from dotenv import load_dotenv

from apps.oidc.keys import get_oidc_private_key, is_test_settings_module

pymysql.install_as_MySQLdb()

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR.parent.parent / ".env")
load_dotenv(BASE_DIR / ".env", override=True)

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if host.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "oauth2_provider",
    "apps.core",
    "apps.accounts",
    "apps.chat",
    "apps.story",
    "apps.modules",
    "apps.oidc",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MYSQL_DATABASE", "app"),
        "USER": os.getenv("MYSQL_USER", "app"),
        "PASSWORD": os.getenv("MYSQL_PASSWORD", "app"),
        "HOST": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "PORT": os.getenv("MYSQL_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci'",
        },
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{os.getenv('REDIS_HOST', '127.0.0.1')}:{os.getenv('REDIS_PORT', '6379')}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.core.authentication.SignedTokenAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

LOGIN_URL = "oidc-login"
LOGIN_REDIRECT_URL = "/api/v1/oidc/authorize/"
LOGOUT_REDIRECT_URL = "/api/v1/oidc/login/"

AUTH_TOKEN_MAX_AGE_SECONDS = int(os.getenv("AUTH_TOKEN_MAX_AGE_SECONDS", "28800"))
CHAT_MODEL_CODE = os.getenv("CHAT_MODEL_CODE", "deepseek-chat")
CHAT_AUTO_TITLE_LENGTH = int(os.getenv("CHAT_AUTO_TITLE_LENGTH", "24"))
CHAT_CONTEXT_MESSAGE_LIMIT = int(os.getenv("CHAT_CONTEXT_MESSAGE_LIMIT", "10"))
CHAT_IDEMPOTENCY_TTL_SECONDS = int(os.getenv("CHAT_IDEMPOTENCY_TTL_SECONDS", str(24 * 60 * 60)))
CHAT_PROVIDER_CLASS = os.getenv("CHAT_PROVIDER_CLASS", "apps.chat.services.providers.deepseek.DeepSeekChatProvider")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_TIMEOUT_SECONDS = int(os.getenv("DEEPSEEK_TIMEOUT_SECONDS", "60"))

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001",
    ).split(",")
    if origin.strip()
]

OAUTH2_PROVIDER = {
    "OIDC_ENABLED": True,
    "OIDC_RP_INITIATED_LOGOUT_ENABLED": True,
    "OIDC_RP_INITIATED_LOGOUT_ALWAYS_PROMPT": False,
    "OIDC_RSA_PRIVATE_KEY": get_oidc_private_key(allow_ephemeral=is_test_settings_module()),
    "OAUTH2_VALIDATOR_CLASS": "apps.oidc.oauth_validators.GemshinOAuth2Validator",
    "SCOPES": {
        "openid": "OpenID Connect 登录标识",
        "profile": "基础档案信息",
        "email": "邮箱信息",
    },
    "DEFAULT_SCOPES": ["openid", "profile"],
    "OIDC_RESPONSE_TYPES_SUPPORTED": ["code"],
    "OAUTH2_RESPONSE_TYPES_SUPPORTED": ["code"],
    "OAUTH2_GRANT_TYPES_SUPPORTED": ["authorization_code", "refresh_token"],
    "PKCE_REQUIRED": True,
    "COMPLIANT_BCP_RFC9700_PKCE_METHOD": True,
    "REFRESH_TOKEN_REUSE_PROTECTION": True,
    "ROTATE_REFRESH_TOKEN": True,
}
