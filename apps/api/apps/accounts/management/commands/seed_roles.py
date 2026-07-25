from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.accounts.models import Role, UserRole, UserProfile
from apps.modules.models import Module

User = get_user_model()

ROLES = [
    {
        "name": "管理员",
        "code": "admin",
        "description": "账户管理 + 所有业务模块",
        "modules": ["comic", "stock", "blog"],
        "is_system": True,
        "sort_order": 1,
    },
    {
        "name": "AI 漫剧制作者",
        "code": "comic_creator",
        "description": "AI 漫剧制作模块",
        "modules": ["comic"],
        "is_system": True,
        "sort_order": 2,
    },
    {
        "name": "AI 股票投资者",
        "code": "stock_investor",
        "description": "AI 股票分析模块",
        "modules": ["stock"],
        "is_system": True,
        "sort_order": 3,
    },
    {
        "name": "AI 内容创作者",
        "code": "content_creator",
        "description": "个人博客 / 个人内容库",
        "modules": ["blog"],
        "is_system": True,
        "sort_order": 4,
    },
    {
        "name": "游客",
        "code": "guest",
        "description": "无业务模块",
        "modules": [],
        "is_system": True,
        "sort_order": 5,
    },
]


class Command(BaseCommand):
    help = "初始化角色数据并设置管理员账号"

    def add_arguments(self, parser):
        parser.add_argument(
            "--admin-username",
            type=str,
            default="zhangwei",
            help="管理员用户名",
        )
        parser.add_argument(
            "--admin-password",
            type=str,
            default=None,
            help="管理员密码（如不提供则不修改密码）",
        )

    def handle(self, *args, **options):
        # 创建角色
        for role_data in ROLES:
            role, created = Role.objects.update_or_create(
                code=role_data["code"],
                defaults={
                    "name": role_data["name"],
                    "description": role_data["description"],
                    "is_system": role_data["is_system"],
                    "sort_order": role_data["sort_order"],
                },
            )
            
            # 关联模块
            if role_data["modules"]:
                modules = Module.objects.filter(code__in=role_data["modules"])
                role.modules.set(modules)
            
            status = "创建" if created else "更新"
            self.stdout.write(self.style.SUCCESS(f"{status}角色: {role.name}"))

        # 设置管理员账号
        admin_username = options["admin_username"]
        admin_password = options["admin_password"]
        
        try:
            user = User.objects.get(username=admin_username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"用户 {admin_username} 不存在"))
            return

        user.is_staff = True
        if admin_password:
            user.set_password(admin_password)
        user.save()

        # 确保有 profile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.must_change_password = False
        profile.save()

        # 分配管理员角色
        admin_role = Role.objects.get(code="admin")
        UserRole.objects.get_or_create(user=user, role=admin_role)

        self.stdout.write(self.style.SUCCESS(f"管理员 {admin_username} 设置完成"))
