from .base import *

from .vault import Vault

unseal_keys = get_env("VAULT_KEYS_CSV").split(",")


# Create Vault instance
VAULT = Vault(
    vault_url=get_env("VAULT_URL"),
    vault_token=get_env("VAULT_TOKEN"),
    ensure_unseal=True,
    unseal_keys=unseal_keys,
)


DEBUG = bool(VAULT.get_secret(mount_point="secret", path="api", key="DEBUG"))


SECRET_KEY = VAULT.get_secret(
    mount_point="secret", path="api", key="DJANGO_SECRET_KEY"
)

ALLOWED_HOSTS = ["api.onews.diogosilva.tech", "localhost", "127.0.0.1"]


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


SECURE_REFERRER_POLICY = "strict-origin"


SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False


# WHITE NOISE IS FOR SERVING STATIC ASSETS
# Fore more info, refeer to:
# http://whitenoise.evans.io/en/latest/
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

COMPRESS_OFFLINE = True
COMPRESS_CSS_FILTERS = [
    "compressor.filters.css_default.CssAbsoluteFilter",
    "compressor.filters.cssmin.CSSMinFilter",
]
COMPRESS_CSS_HASHING_METHOD = "content"
