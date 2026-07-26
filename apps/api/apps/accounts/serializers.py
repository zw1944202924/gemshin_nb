from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.models import AuditLog, Role, UserProfile, UserRole
from apps.modules.models import Module
from apps.modules.serializers import ModuleSerializer

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    module_ids = serializers.PrimaryKeyRelatedField(
        queryset=Module.objects.all(),
        many=True,
        write_only=True,
        source="modules",
    )

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "code",
            "description",
            "modules",
            "module_ids",
            "is_system",
            "sort_order",
            "created_at",
        ]
        read_only_fields = ["id", "is_system", "created_at"]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "display_name",
            "email",
            "must_change_password",
            "notify_account_security",
            "notify_permission_change",
            "notify_module_activity",
        ]
        read_only_fields = ["must_change_password"]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    roles = serializers.SerializerMethodField()
    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "is_active",
            "is_staff",
            "is_admin",
            "profile",
            "roles",
            "role_ids",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "username", "date_joined", "last_login"]
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
        }

    def get_is_admin(self, obj):
        return obj.is_staff

    def get_roles(self, obj):
        # 通过 user_roles 反向关联获取用户的所有角色，预加载模块
        roles = Role.objects.filter(user_roles__user=obj).prefetch_related("modules")
        return RoleSerializer(roles, many=True).data

    def create(self, validated_data):
        profile_data = validated_data.pop("profile", {})
        role_ids = validated_data.pop("role_ids", [])
        password = validated_data.pop("password", None)

        user = User.objects.create_user(
            username=validated_data["username"],
            password=password,
            is_staff=validated_data.get("is_staff", False),
            is_active=validated_data.get("is_active", True),
        )

        if profile_data:
            UserProfile.objects.create(user=user, **profile_data)
        else:
            UserProfile.objects.create(user=user)

        for role in role_ids:
            UserRole.objects.create(user=user, role=role)

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)
        role_ids = validated_data.pop("role_ids", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data is not None:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        if role_ids is not None:
            instance.user_roles.all().delete()
            for role in role_ids:
                UserRole.objects.create(user=instance, role=role)

        return instance


class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(min_length=8, write_only=True)
    display_name = serializers.CharField(max_length=100, required=False, default="")
    email = serializers.EmailField(required=False, default="")
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
    )
    must_change_password = serializers.BooleanField(default=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def validate_role_ids(self, value):
        if not value:
            raise serializers.ValidationError("至少选择一个角色")
        existing = Role.objects.filter(id__in=value).count()
        if existing != len(value):
            raise serializers.ValidationError("部分角色不存在")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(min_length=8, required=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("旧密码不正确")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8, required=True)
    must_change_password = serializers.BooleanField(default=True)


class AuditLogSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source="operator.get_username", read_only=True)
    target_username = serializers.CharField(source="target_user.get_username", read_only=True)
    action_display = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "action",
            "action_display",
            "operator",
            "operator_name",
            "target_user",
            "target_username",
            "detail",
            "ip_address",
            "result",
            "created_at",
        ]
        read_only_fields = fields
