from django.conf import settings
from django.db import models


class Module(models.Model):
    """固定业务模块目录，预置三条记录，不随用户增删。"""

    code = models.CharField("模块编码", max_length=50, unique=True)
    name = models.CharField("模块名称", max_length=100)
    description = models.TextField("模块描述", blank=True)
    icon = models.CharField("图标标识", max_length=10, blank=True)
    status = models.CharField("状态", max_length=20, default="ready")
    sort_order = models.IntegerField("排序", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "code"]
        verbose_name = "业务模块"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class UserModuleAuthorization(models.Model):
    """
    用户-模块授权关系，控制用户可见哪些模块。
    
    .. deprecated:: MYW-56
        此模型已废弃，模块权限现在通过 Role 模型控制。
        请使用 accounts.Role 和 accounts.UserRole 替代。
        此模型保留仅用于数据迁移兼容，新代码不应使用。
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="module_authorizations",
        verbose_name="用户",
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="user_authorizations",
        verbose_name="模块",
    )
    granted_at = models.DateTimeField("授权时间", auto_now_add=True)

    class Meta:
        unique_together = [("user", "module")]
        ordering = ["-granted_at"]
        verbose_name = "用户模块授权（已废弃）"
        verbose_name_plural = "用户模块授权（已废弃）"

    def __str__(self):
        return f"{self.user} → {self.module}（已废弃）"
