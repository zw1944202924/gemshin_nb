from django.contrib.auth import get_user_model
from django.db import transaction
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
        # 预加载用户的模块信息
        user = User.objects.select_related("profile").prefetch_related("user_roles__role__modules").get(id=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile_data = request.data.get("profile", {})

        for field in ["display_name", "email", "notify_account_security", "notify_permission_change", "notify_module_activity"]:
            if field in profile_data:
                setattr(profile, field, profile_data[field])
        profile.save()

        log_audit(request, "update_profile", request.user, {"fields": list(profile_data.keys())})

        # 预加载用户的模块信息
        user = User.objects.select_related("profile").prefetch_related("user_roles__role__modules").get(id=request.user.id)
        serializer = UserSerializer(user)
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
        users = User.objects.select_related("profile").prefetch_related("user_roles__role__modules")

        if search:
            users = users.filter(username__icontains=search) | users.filter(profile__display_name__icontains=search)

        serializer = UserSerializer(users, many=True)
        return Response({"users": serializer.data})

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 批量校验角色是否存在，避免 500 错误
        role_ids = data["role_ids"]
        existing_roles = Role.objects.filter(id__in=role_ids)
        if existing_roles.count() != len(role_ids):
            existing_ids = set(existing_roles.values_list("id", flat=True))
            missing_ids = [rid for rid in role_ids if rid not in existing_ids]
            return Response(
                {"detail": f"以下角色不存在: {missing_ids}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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

        # 检查是否包含管理员角色，如果是则设置 is_staff=True
        has_admin_role = existing_roles.filter(code="admin").exists()
        if has_admin_role:
            user.is_staff = True
            user.save()

        for role in existing_roles:
            UserRole.objects.create(user=user, role=role)

        log_audit(request, "create_account", user, {
            "username": data["username"],
            "roles": [r.name for r in existing_roles],
        })

        # 重新获取用户对象并预加载关联数据，确保 roles 字段正确返回
        user = User.objects.select_related("profile").prefetch_related("user_roles__role__modules").get(id=user.id)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        try:
            user = User.objects.select_related("profile").prefetch_related("user_roles__role__modules").get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        return Response(UserSerializer(user).data)

    @transaction.atomic
    def patch(self, request, user_id):
        try:
            user = User.objects.select_for_update().get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        role_ids = request.data.get("role_ids")
        if role_ids is not None:
            # 批量校验角色是否存在，避免 500 错误
            existing_roles = Role.objects.filter(id__in=role_ids)
            if existing_roles.count() != len(role_ids):
                existing_ids = set(existing_roles.values_list("id", flat=True))
                missing_ids = [rid for rid in role_ids if rid not in existing_ids]
                return Response(
                    {"detail": f"以下角色不存在: {missing_ids}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # 检查更新后的角色集合是否包含管理员角色
            has_admin_role = existing_roles.filter(code="admin").exists()

            # 锁定当前活跃管理员集合，避免角色变更把系统打成 0 管理员。
            if user.is_active and user.is_staff and not has_admin_role:
                other_active_admin_count = User.objects.select_for_update().filter(
                    is_staff=True,
                    is_active=True,
                ).exclude(id=user.id).count()

                if other_active_admin_count < 1:
                    return Response(
                        {"detail": "不能移除最后一个管理员的角色，否则系统将没有管理员"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            user.user_roles.all().delete()
            for role in existing_roles:
                UserRole.objects.create(user=user, role=role)

            # 更新 is_staff 状态
            if user.is_staff != has_admin_role:
                user.is_staff = has_admin_role
                user.save()

            log_audit(request, "change_role", user, {
                "new_roles": [r.name for r in existing_roles],
            })

        profile_data = request.data.get("profile", {})
        if profile_data:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            for field in ["display_name", "email"]:
                if field in profile_data:
                    setattr(profile, field, profile_data[field])
            profile.save()

        # 重新获取用户对象并预加载关联数据，确保 roles 字段正确返回
        user = User.objects.select_related("profile").prefetch_related("user_roles__role__modules").get(id=user_id)
        return Response(UserSerializer(user).data)


class AdminUserDisableView(APIView):
    permission_classes = [IsAdminUser]

    @transaction.atomic
    def post(self, request, user_id):
        try:
            user = User.objects.select_for_update().get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        if user == request.user:
            return Response({"detail": "不能停用自己"}, status=status.HTTP_400_BAD_REQUEST)

        # 使用 select_for_update 锁定查询，防止并发停用最后一个管理员
        if user.is_staff:
            active_admin_count = User.objects.select_for_update().filter(
                is_staff=True, is_active=True
            ).count()
            if active_admin_count <= 1:
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
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))
        
        # 限制每页最大数量
        page_size = min(page_size, 100)
        
        offset = (page - 1) * page_size
        total = AuditLog.objects.count()
        logs = AuditLog.objects.select_related("operator", "target_user").all()[offset:offset + page_size]
        
        serializer = AuditLogSerializer(logs, many=True)
        return Response({
            "logs": serializer.data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size,
            }
        })
