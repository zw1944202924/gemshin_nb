from django.utils import timezone
from oauth2_provider.models import get_grant_model
from oauth2_provider.oauth2_validators import OAuth2Validator

from apps.oidc.session import ensure_user_profile, get_user_display_name, get_user_email


Grant = get_grant_model()


class GemshinOAuth2Validator(OAuth2Validator):
    oidc_claim_scope = dict(OAuth2Validator.oidc_claim_scope)
    oidc_claim_scope.update(
        {
            "preferred_username": "profile",
        }
    )

    def _is_session_valid(self, user, issued_at):
        if user is None or not user.is_active:
            return False

        profile = ensure_user_profile(user)
        if profile.auth_revoked_at is None:
            return True
        if issued_at is None:
            return False
        if timezone.is_naive(issued_at):
            issued_at = timezone.make_aware(issued_at, timezone.utc)
        return issued_at > profile.auth_revoked_at

    def validate_response_type(self, client_id, response_type, client, request, *args, **kwargs):
        if response_type != "code":
            return False
        return super().validate_response_type(client_id, response_type, client, request, *args, **kwargs)

    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        if grant_type not in {"authorization_code", "refresh_token"}:
            return False
        return super().validate_grant_type(client_id, grant_type, client, request, *args, **kwargs)

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        if not super().validate_code(client_id, code, client, request, *args, **kwargs):
            return False

        grant = Grant.objects.select_related("user").filter(code=code, application=client).first()
        return bool(grant and self._is_session_valid(grant.user, grant.created))

    def validate_bearer_token(self, token, scopes, request):
        if not super().validate_bearer_token(token, scopes, request):
            return False
        return self._is_session_valid(request.user, getattr(request.access_token, "created", None))

    def validate_refresh_token(self, refresh_token, client, request, *args, **kwargs):
        if not super().validate_refresh_token(refresh_token, client, request, *args, **kwargs):
            return False
        refresh_token_instance = getattr(request, "refresh_token_instance", None)
        return self._is_session_valid(request.user, getattr(refresh_token_instance, "created", None))

    def get_additional_claims(self):
        return {
            "sub": lambda request: str(ensure_user_profile(request.user).oidc_subject),
            "preferred_username": lambda request: request.user.get_username(),
            "name": lambda request: get_user_display_name(request.user),
            "email": lambda request: get_user_email(request.user) or None,
        }

    def get_oidc_claims(self, token, token_handler, request):
        claims = super().get_oidc_claims(token, token_handler, request)
        return {key: value for key, value in claims.items() if value not in ("", None)}
