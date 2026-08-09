from functools import lru_cache
import os

from django.core.exceptions import ImproperlyConfigured
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def _normalize_pem(value):
    return value.replace("\\n", "\n").strip()


@lru_cache(maxsize=1)
def _generate_ephemeral_private_key():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")


def is_test_settings_module():
    return os.getenv("DJANGO_SETTINGS_MODULE", "").endswith(".test")


def is_local_debug_environment(*, debug, allowed_hosts):
    local_hosts = {"127.0.0.1", "localhost"}
    normalized_hosts = {host.strip() for host in allowed_hosts if host.strip()}
    return debug and bool(normalized_hosts) and normalized_hosts.issubset(local_hosts)


def get_oidc_private_key(*, allow_ephemeral=False):
    env_key = os.getenv("OIDC_RSA_PRIVATE_KEY", "").strip()
    if env_key:
        return _normalize_pem(env_key)
    if allow_ephemeral:
        return _generate_ephemeral_private_key()
    raise ImproperlyConfigured("OIDC_RSA_PRIVATE_KEY is required outside local DEBUG or test settings.")


def get_test_oidc_private_key():
    return _generate_ephemeral_private_key()
