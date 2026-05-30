from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header


TOKEN_SALT = "core.auth.token"
User = get_user_model()


def build_auth_token(user):
    return signing.dumps(
        {
            "user_id": user.pk,
            "password": user.password,
        },
        salt=TOKEN_SALT,
        compress=True,
    )


def resolve_user_from_token(token):
    try:
        payload = signing.loads(
            token,
            salt=TOKEN_SALT,
            max_age=settings.AUTH_TOKEN_MAX_AGE_SECONDS,
        )
    except signing.BadSignature as exc:
        raise exceptions.AuthenticationFailed("登录态无效或已过期") from exc

    user_id = payload.get("user_id")
    password = payload.get("password")
    if not user_id or not password:
        raise exceptions.AuthenticationFailed("登录态无效或已过期")

    try:
        user = User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist as exc:
        raise exceptions.AuthenticationFailed("登录态无效或已过期") from exc

    if user.password != password:
        raise exceptions.AuthenticationFailed("登录态无效或已过期")

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
