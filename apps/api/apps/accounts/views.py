from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import AuditLog, Role, UserProfile, UserRole
from apps.accounts.serializers import (
    AuditLogSerializer,
    ChangePasswordSerializer,
    CreateUserSerializer,
    ResetPasswordSerializer,
    RoleSerializer,
    UserSerializer,
)

User = get_user_model()


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_audit(request, action, target_user=None, detail=None):
    AuditLog.objects.create(
        action=action,
        operator=request.user,
        target_user=target_user,
        detail=detail or {},
        ip_address=get_client_ip(request),
    )


class IsAdminUser(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.is_staff


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile_data = request.data.get("profile", {})

        for field in ["display_name", "email", "notify_account_security", "notify_permission_change", "notify_module_activity"]:
            if field in profile_data:
                setattr(profile, field, profile_data[field])
        profile.save()

        log_audit(request, "update_profile", request.user, {"fields": list(profile_data.keys())})

        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.must_change_password = False
        profile.last_password_change = timezone.now()
        profile.save()

        log_audit(request, "force_change_password", request.user)

        return Response({"detail": "密码修改成功"})


class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        search = request.query_params.get("search", "")
        users = User.objects.select_related("profile").prefetch_related("user_roles__role")

        if search:
            users = users.filter(username__icontains=search) | users.filter(profile__display_name__icontains=search)

        serializer = UserSerializer(users, many=True)
        return Response({"users": serializer.data})

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = User.objects.create_user(
            username=data["username"],
            password=data["password"],
            is_active=True,
        )

        profile = UserProfile.objects.create(
            user=user,
            display_name=data.get("display_name", ""),
            email=data.get("email", ""),
            must_change_password=data.get("must_change_password", True),
        )

        for role_id in data["role_ids"]:
            role = Role.objects.get(id=role_id)
            UserRole.objects.create(user=user, role=role)

        log_audit(request, "create_account", user, {
            "username": data["username"],
            "roles": [r.name for r in Role.objects.filter(id__in=data["role_ids"])],
        })

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        try:
            user = User.objects.select_related("profile").prefetch_related("user_roles__role").get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        return Response(UserSerializer(user).data)

    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        role_ids = request.data.get("role_ids")
        if role_ids is not None:
            user.user_roles.all().delete()
            for role_id in role_ids:
                role = Role.objects.get(id=role_id)
                UserRole.objects.create(user=user, role=role)
            log_audit(request, "change_role", user, {
                "new_roles": [r.name for r in Role.objects.filter(id__in=role_ids)],
            })

        profile_data = request.data.get("profile", {})
        if profile_data:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            for field in ["display_name", "email"]:
                if field in profile_data:
                    setattr(profile, field, profile_data[field])
            profile.save()

        return Response(UserSerializer(user).data)


class AdminUserDisableView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        if user == request.user:
            return Response({"detail": "不能停用自己"}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_staff and User.objects.filter(is_staff=True, is_active=True).count() <= 1:
            return Response({"detail": "不能停用最后一个管理员"}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = False
        user.save()
        log_audit(request, "disable_account", user)

        return Response({"detail": "账号已停用"})


class AdminUserEnableView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = True
        user.save()
        log_audit(request, "enable_account", user)

        return Response({"detail": "账号已启用"})


class AdminResetPasswordView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.must_change_password = serializer.validated_data.get("must_change_password", True)
        profile.save()

        log_audit(request, "reset_password", user, {
            "must_change_password": profile.must_change_password,
        })

        return Response({"detail": "密码已重置"})


class RoleListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        roles = Role.objects.prefetch_related("modules")
        serializer = RoleSerializer(roles, many=True)
        return Response({"roles": serializer.data})


class AuditLogListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        logs = AuditLog.objects.select_related("operator", "target_user").all()[:100]
        serializer = AuditLogSerializer(logs, many=True)
        return Response({"logs": serializer.data})
