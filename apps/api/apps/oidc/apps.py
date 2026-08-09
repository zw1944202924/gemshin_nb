from django.apps import AppConfig


class OidcConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.oidc"
    verbose_name = "统一身份 OIDC"
