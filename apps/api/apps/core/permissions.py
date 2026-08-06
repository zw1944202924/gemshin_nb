from apps.accounts.models import UserProfile
from rest_framework.permissions import IsAuthenticated


class MustChangePasswordGuard(IsAuthenticated):
    message = "请先完成密码修改"

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if not profile.must_change_password:
            return True

        allowed_methods = getattr(view, "allow_must_change_password_methods", ())
        return request.method in allowed_methods
