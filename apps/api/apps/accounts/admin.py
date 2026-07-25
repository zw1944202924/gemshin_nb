from django.contrib import admin

from apps.accounts.models import AuditLog, Role, UserProfile, UserRole


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "is_system", "sort_order"]
    list_filter = ["is_system"]
    search_fields = ["name", "code"]


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "created_at"]
    list_filter = ["role"]
    search_fields = ["user__username"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "display_name", "email", "must_change_password"]
    search_fields = ["user__username", "display_name", "email"]
    list_filter = ["must_change_password"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["action", "operator", "target_user", "result", "created_at"]
    list_filter = ["action", "result"]
    search_fields = ["operator__username", "target_user__username"]
    readonly_fields = ["action", "operator", "target_user", "detail", "ip_address", "result", "created_at"]
