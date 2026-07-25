from django.contrib import admin

from apps.modules.models import Module, UserModuleAuthorization


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "status", "sort_order"]
    list_filter = ["status"]
    search_fields = ["code", "name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(UserModuleAuthorization)
class UserModuleAuthorizationAdmin(admin.ModelAdmin):
    list_display = ["user", "module", "granted_at"]
    list_filter = ["module"]
    search_fields = ["user__username", "user__first_name", "module__name"]
    raw_id_fields = ["user"]
    readonly_fields = ["granted_at"]
