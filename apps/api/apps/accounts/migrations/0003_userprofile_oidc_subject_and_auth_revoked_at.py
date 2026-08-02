from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_migrate_user_module_authorizations"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="auth_revoked_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="登录态统一失效时间"),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="oidc_subject",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="OIDC Subject"),
        ),
    ]
