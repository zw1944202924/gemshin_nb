from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from oauth2_provider.views import AuthorizationView


class OidcLoginView(LoginView):
    template_name = "oidc/login.html"
    redirect_authenticated_user = True


class OidcAuthorizationView(AuthorizationView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_active:
            logout(request)
        return super().dispatch(request, *args, **kwargs)
