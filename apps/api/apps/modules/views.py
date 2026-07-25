from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.modules.models import Module
from apps.modules.serializers import ModuleSerializer


class ModuleListView(APIView):
    """返回当前用户已授权的模块列表。"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        authorized_modules = Module.objects.filter(
            user_authorizations__user=request.user
        )
        serializer = ModuleSerializer(authorized_modules, many=True)
        return Response({"modules": serializer.data})


class ModuleDetailView(APIView):
    """获取单个模块详情，必须满足用户授权约束。"""

    permission_classes = [IsAuthenticated]

    def get(self, request, code):
        try:
            module = Module.objects.get(code=code)
        except Module.DoesNotExist:
            return Response(
                {"detail": "模块不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 检查用户是否已获授权
        has_access = module.user_authorizations.filter(user=request.user).exists()
        if not has_access:
            return Response(
                {"detail": "无权访问该模块"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ModuleSerializer(module)
        return Response(serializer.data)
