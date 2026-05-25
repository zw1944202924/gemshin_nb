from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    def get(self, request):
        return Response({"status": "ok", "service": "api"})


urlpatterns = [
    path("api/v1/health/", HealthView.as_view(), name="health"),
]
