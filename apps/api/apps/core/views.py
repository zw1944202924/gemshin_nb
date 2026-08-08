from django.conf import settings
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserProfile, UserRole
from apps.core.authentication import build_auth_token, revoke_auth_token
from apps.core.permissions import MustChangePasswordGuard


def serialize_user(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    roles = UserRole.objects.filter(user=user).select_related("role")
    role_list = [{"id": ur.role.id, "name": ur.role.name, "code": ur.role.code} for ur in roles]
    
    return {
        "id": user.pk,
        "username": user.get_username(),
        "display_name": profile.display_name or user.get_full_name() or user.get_username(),
        "email": profile.email,
        "is_admin": user.is_staff,
        "must_change_password": profile.must_change_password,
        "roles": role_list,
    }


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        password = request.data.get("password") or ""

        if not username or not password:
            return Response(
                {"detail": "请输入用户名和密码"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request=request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "用户名或密码错误"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 更新最后登录时间
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        return Response(
            {
                "token": build_auth_token(user),
                "expires_in": settings.AUTH_TOKEN_MAX_AGE_SECONDS,
                "user": serialize_user(user),
            }
        )


class LogoutView(APIView):
    permission_classes = [MustChangePasswordGuard]
    allow_must_change_password_methods = ("POST",)

    def post(self, request):
        if isinstance(request.auth, str):
            revoke_auth_token(request.auth)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SessionView(APIView):
    permission_classes = [MustChangePasswordGuard]
    allow_must_change_password_methods = ("GET",)

    def get(self, request):
        return Response({"user": serialize_user(request.user)})


class ProtectedView(APIView):
    permission_classes = [MustChangePasswordGuard]

    def get(self, request):
        return Response(
            {
                "message": f"你好，{request.user.get_full_name() or request.user.get_username()}",
                "scope": "authenticated",
            }
        )
