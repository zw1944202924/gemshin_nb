from django.urls import path

from apps.oidc.views import OidcLoginView


urlpatterns = [
    path("login/", OidcLoginView.as_view(), name="oidc-login"),
]
