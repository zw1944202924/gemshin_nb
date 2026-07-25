from django.urls import path

from apps.modules.views import ModuleDetailView, ModuleListView

urlpatterns = [
    path("", ModuleListView.as_view(), name="module-list"),
    path("<str:code>/", ModuleDetailView.as_view(), name="module-detail"),
]
