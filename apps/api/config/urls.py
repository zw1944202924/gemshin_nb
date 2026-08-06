from django.core.cache import cache
from django.db import connection
from django.urls import include, path
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.views import LoginView, LogoutView, ProtectedView, SessionView


class HealthView(APIView):
    def get(self, request):
        db_ok = True
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_ok = cursor.fetchone() == (1,)
        except Exception:
            db_ok = False

        redis_ok = True
        try:
            cache.set("__health_check__", "1", timeout=5)
            redis_ok = cache.get("__health_check__") == "1"
        except Exception:
            redis_ok = False

        status_code = 200 if db_ok and redis_ok else 503
        return Response(
            {
                "status": "ok" if db_ok and redis_ok else "degraded",
                "service": "api",
                "checks": {
                    "mysql": "ok" if db_ok else "fail",
                    "redis": "ok" if redis_ok else "fail",
                },
            },
            status=status_code,
        )


urlpatterns = [
    path("api/v1/health/", HealthView.as_view(), name="health"),
    path("api/v1/auth/login/", LoginView.as_view(), name="auth-login"),
    path("api/v1/auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("api/v1/auth/me/", SessionView.as_view(), name="auth-me"),
    path("api/v1/protected/", ProtectedView.as_view(), name="protected"),
    path("api/v1/accounts/", include("apps.accounts.urls")),
    path("api/v1/chat/", include("apps.chat.urls")),
    path("api/v1/story/", include("apps.story.urls")),
    path("api/v1/modules/", include("apps.modules.urls")),
]
