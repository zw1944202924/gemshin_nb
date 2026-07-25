import getpass
import os

from django.core.management.base import BaseCommand, CommandError
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
            default=None,
            help="管理员用户名（默认从环境变量 ADMIN_USERNAME 读取）",
        )
        parser.add_argument(
            "--admin-password-env",
            type=str,
            default="ADMIN_PASSWORD",
            help="存储管理员密码的环境变量名（默认: ADMIN_PASSWORD）",
        )
        parser.add_argument(
            "--interactive-password",
            action="store_true",
            default=False,
            help="交互式输入密码（优先级高于环境变量）",
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
        admin_username = options["admin_username"] or os.environ.get("ADMIN_USERNAME")
        if not admin_username:
            raise CommandError("请通过 --admin-username 或环境变量 ADMIN_USERNAME 指定管理员用户名")
        
        # 获取密码：优先交互式输入，其次环境变量
        admin_password = None
        if options["interactive_password"]:
            admin_password = getpass.getpass(f"请输入管理员 {admin_username} 的密码: ")
            if not admin_password:
                raise CommandError("密码不能为空")
        else:
            password_env = options["admin_password_env"]
            admin_password = os.environ.get(password_env)
            if not admin_password:
                raise CommandError(
                    f"请通过环境变量 {password_env} 设置密码，或使用 --interactive-password 交互式输入"
                )
        
        try:
            user = User.objects.get(username=admin_username)
            self.stdout.write(f"用户 {admin_username} 已存在，将更新其管理员权限")
        except User.DoesNotExist:
            # 用户不存在时自动创建
            self.stdout.write(f"用户 {admin_username} 不存在，将创建新用户")
            user = User.objects.create_user(
                username=admin_username,
                password=admin_password,
                is_active=True,
            )
            self.stdout.write(self.style.SUCCESS(f"用户 {admin_username} 创建成功"))

        user.is_staff = True
        user.set_password(admin_password)
        user.save()

        # 确保有 profile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        # 核验账号设置为不需要强制改密，因为这是初始化部署操作
        profile.must_change_password = False
        profile.save()

        # 分配管理员角色
        admin_role = Role.objects.get(code="admin")
        UserRole.objects.get_or_create(user=user, role=admin_role)

        self.stdout.write(self.style.SUCCESS(f"管理员 {admin_username} 设置完成"))
