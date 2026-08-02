from functools import lru_cache
import os

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


def get_oidc_private_key(*, debug=False):
    env_key = os.getenv("OIDC_RSA_PRIVATE_KEY", "").strip()
    if env_key:
        return _normalize_pem(env_key)
    if debug:
        return _generate_ephemeral_private_key()
    return ""


def get_test_oidc_private_key():
    return _generate_ephemeral_private_key()
