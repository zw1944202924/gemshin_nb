from django.db import migrations, models
import uuid


def populate_oidc_subjects(apps, schema_editor):
    UserProfile = apps.get_model("accounts", "UserProfile")

    for profile in UserProfile.objects.filter(oidc_subject__isnull=True).iterator():
        profile.oidc_subject = uuid.uuid4()
        profile.save(update_fields=["oidc_subject"])


def noop_reverse(apps, schema_editor):
    return None


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
            field=models.UUIDField(blank=True, null=True, editable=False, verbose_name="OIDC Subject"),
        ),
        migrations.RunPython(populate_oidc_subjects, noop_reverse),
        migrations.AlterField(
            model_name="userprofile",
            name="oidc_subject",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="OIDC Subject"),
        ),
    ]
