from django.db import migrations


def migrate_user_module_authorizations_to_roles(apps, schema_editor):
    """将现有的用户-模块授权迁移到角色系统。"""
    Role = apps.get_model("accounts", "Role")
    UserRole = apps.get_model("accounts", "UserRole")
    UserProfile = apps.get_model("accounts", "UserProfile")
    UserModuleAuthorization = apps.get_model("modules", "UserModuleAuthorization")
    Module = apps.get_model("modules", "Module")
    User = apps.get_model("auth", "User")
    
    # 创建默认角色
    admin_role, _ = Role.objects.get_or_create(
        code="admin",
        defaults={
            "name": "管理员",
            "description": "账户管理 + 所有业务模块",
            "is_system": True,
            "sort_order": 1,
        }
    )
    
    comic_role, _ = Role.objects.get_or_create(
        code="comic_creator",
        defaults={
            "name": "AI 漫剧制作者",
            "description": "AI 漫剧制作模块",
            "is_system": True,
            "sort_order": 2,
        }
    )
    
    stock_role, _ = Role.objects.get_or_create(
        code="stock_investor",
        defaults={
            "name": "AI 股票投资者",
            "description": "AI 股票分析模块",
            "is_system": True,
            "sort_order": 3,
        }
    )
    
    blog_role, _ = Role.objects.get_or_create(
        code="content_creator",
        defaults={
            "name": "AI 内容创作者",
            "description": "个人博客 / 个人内容库",
            "is_system": True,
            "sort_order": 4,
        }
    )
    
    guest_role, _ = Role.objects.get_or_create(
        code="guest",
        defaults={
            "name": "游客",
            "description": "无业务模块",
            "is_system": True,
            "sort_order": 5,
        }
    )
    
    # 关联模块到角色
    try:
        comic_module = Module.objects.get(code="comic")
        comic_role.modules.add(comic_module)
        admin_role.modules.add(comic_module)
    except Module.DoesNotExist:
        pass
    
    try:
        stock_module = Module.objects.get(code="stock")
        stock_role.modules.add(stock_module)
        admin_role.modules.add(stock_module)
    except Module.DoesNotExist:
        pass
    
    try:
        blog_module = Module.objects.get(code="blog")
        blog_role.modules.add(blog_module)
        admin_role.modules.add(blog_module)
    except Module.DoesNotExist:
        pass
    
    # 为所有用户创建 profile（如果不存在）
    for user in User.objects.all():
        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "display_name": user.get_full_name() or user.get_username(),
                "must_change_password": False,
            }
        )
    
    # 迁移现有授权
    for auth in UserModuleAuthorization.objects.select_related("user", "module").all():
        user = auth.user
        module = auth.module
        
        # 根据模块分配角色
        if module.code == "comic":
            role = comic_role
        elif module.code == "stock":
            role = stock_role
        elif module.code == "blog":
            role = blog_role
        else:
            continue
        
        UserRole.objects.get_or_create(user=user, role=role)
    
    # 管理员用户分配管理员角色
    for user in User.objects.filter(is_staff=True):
        UserRole.objects.get_or_create(user=user, role=admin_role)


def reverse_migration(apps, schema_editor):
    """反向迁移：删除创建的角色。"""
    Role = apps.get_model("accounts", "Role")
    Role.objects.filter(code__in=["admin", "comic_creator", "stock_investor", "content_creator", "guest"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("modules", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(migrate_user_module_authorizations_to_roles, reverse_migration),
    ]
