from django.contrib.sessions.models import Session
from django.utils import timezone

from apps.accounts.models import UserProfile


def ensure_user_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def get_user_display_name(user):
    profile = ensure_user_profile(user)
    return profile.display_name or user.get_full_name() or user.get_username()


def get_user_email(user):
    profile = ensure_user_profile(user)
    return profile.email or user.email or ""


def clear_user_sessions(user_id):
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    for session in active_sessions.iterator():
        if session.get_decoded().get("_auth_user_id") == str(user_id):
            session.delete()


def revoke_user_oauth_tokens(user):
    from oauth2_provider.models import get_access_token_model, get_grant_model, get_id_token_model, get_refresh_token_model

    AccessToken = get_access_token_model()
    RefreshToken = get_refresh_token_model()
    Grant = get_grant_model()
    IDToken = get_id_token_model()

    for refresh_token in RefreshToken.objects.filter(user=user, revoked__isnull=True).iterator():
        refresh_token.revoke()

    AccessToken.objects.filter(user=user).delete()
    IDToken.objects.filter(user=user).delete()
    Grant.objects.filter(user=user).delete()


def invalidate_user_sessions(user):
    profile = ensure_user_profile(user)
    profile.auth_revoked_at = timezone.now()
    profile.save(update_fields=["auth_revoked_at", "updated_at"])
    revoke_user_oauth_tokens(user)
    clear_user_sessions(user.pk)
    return profile.auth_revoked_at
