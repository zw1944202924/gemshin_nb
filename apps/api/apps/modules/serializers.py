from rest_framework import serializers

from apps.modules.models import Module, UserModuleAuthorization


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["id", "code", "name", "description", "icon", "status"]
        read_only_fields = fields
