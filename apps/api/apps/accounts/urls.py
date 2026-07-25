from django.urls import path

from apps.accounts.views import (
    AdminResetPasswordView,
    AdminUserDetailView,
    AdminUserDisableView,
    AdminUserEnableView,
    AdminUserListView,
    AuditLogListView,
    ChangePasswordView,
    ProfileView,
    RoleListView,
)

urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("admin/users/", AdminUserListView.as_view(), name="admin-user-list"),
    path("admin/users/<int:user_id>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("admin/users/<int:user_id>/disable/", AdminUserDisableView.as_view(), name="admin-user-disable"),
    path("admin/users/<int:user_id>/enable/", AdminUserEnableView.as_view(), name="admin-user-enable"),
    path("admin/users/<int:user_id>/reset-password/", AdminResetPasswordView.as_view(), name="admin-reset-password"),
    path("admin/roles/", RoleListView.as_view(), name="admin-role-list"),
    path("admin/audit-logs/", AuditLogListView.as_view(), name="admin-audit-logs"),
]
