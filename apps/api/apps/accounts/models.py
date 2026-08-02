from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
import uuid

from apps.core.models import TimestampedModel


class Role(TimestampedModel):
    """角色定义，角色是唯一的模块权限来源。"""

    name = models.CharField("角色名称", max_length=50, unique=True)
    code = models.CharField("角色编码", max_length=50, unique=True)
    description = models.TextField("角色描述", blank=True)
    modules = models.ManyToManyField(
        "modules.Module",
        blank=True,
        related_name="roles",
        verbose_name="可访问模块",
    )
    is_system = models.BooleanField("系统内置", default=False)
    sort_order = models.IntegerField("排序", default=0)

    class Meta:
        ordering = ["sort_order", "code"]
        verbose_name = "角色"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class UserRole(TimestampedModel):
    """用户-角色关联，用户可拥有多个角色。"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name="用户",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name="角色",
    )

    class Meta:
        unique_together = [("user", "role")]
        verbose_name = "用户角色"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user} → {self.role}"


class UserProfile(TimestampedModel):
    """用户扩展信息，支持首次强制改密。"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="用户",
    )
    display_name = models.CharField("显示名称", max_length=100, blank=True)
    email = models.EmailField("邮箱", blank=True)
    oidc_subject = models.UUIDField("OIDC Subject", default=uuid.uuid4, unique=True, editable=False)
    must_change_password = models.BooleanField("首次登录强制改密", default=False)
    last_password_change = models.DateTimeField("上次改密时间", null=True, blank=True)
    auth_revoked_at = models.DateTimeField("登录态统一失效时间", null=True, blank=True)

    # 通知偏好
    notify_account_security = models.BooleanField("账号与安全通知", default=True)
    notify_permission_change = models.BooleanField("权限变更通知", default=True)
    notify_module_activity = models.BooleanField("模块动态通知", default=True)

    class Meta:
        verbose_name = "用户资料"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.display_name or self.user.get_username()} 的资料"


class AuditLog(TimestampedModel):
    """审计日志，记录关键操作。"""

    ACTION_CHOICES = [
        ("create_account", "创建账号"),
        ("enable_account", "启用账号"),
        ("disable_account", "停用账号"),
        ("change_role", "变更角色"),
        ("reset_password", "重置密码"),
        ("force_change_password", "强制改密"),
        ("update_profile", "更新资料"),
    ]

    action = models.CharField("操作类型", max_length=30, choices=ACTION_CHOICES)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs_as_operator",
        verbose_name="操作人",
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs_as_target",
        verbose_name="目标用户",
    )
    detail = models.JSONField("操作详情", default=dict)
    ip_address = models.GenericIPAddressField("IP 地址", null=True, blank=True)
    result = models.CharField("操作结果", max_length=20, default="success")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "审计日志"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"[{self.created_at}] {self.get_action_display()} by {self.operator}"
