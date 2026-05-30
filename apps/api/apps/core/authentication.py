import hashlib
import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header


TOKEN_CACHE_PREFIX = "core.auth.token"
User = get_user_model()


def _cache_key(token):
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return f"{TOKEN_CACHE_PREFIX}:{digest}"


def build_auth_token(user):
    token = secrets.token_urlsafe(32)
    cache.set(
        _cache_key(token),
        {"user_id": user.pk},
        timeout=settings.AUTH_TOKEN_MAX_AGE_SECONDS,
    )
    return token


def revoke_auth_token(token):
    cache.delete(_cache_key(token))


def resolve_user_from_token(token):
    payload = cache.get(_cache_key(token))
    if not payload:
        raise exceptions.AuthenticationFailed("登录态无效或已过期")

    user_id = payload.get("user_id")
    if not user_id:
        raise exceptions.AuthenticationFailed("登录态无效或已过期")

    try:
        user = User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist as exc:
        raise exceptions.AuthenticationFailed("登录态无效或已过期") from exc

    return user


class SignedTokenAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth:
            return None

        if auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) != 2:
            raise exceptions.AuthenticationFailed("认证头格式不正确")

        token = auth[1].decode("utf-8")
        user = resolve_user_from_token(token)
        return (user, token)

    def authenticate_header(self, request):
        return self.keyword
