from .base import *
import vaulthelpers

# Instantiate key getter from HashiCorp Vault
api_keys = vaulthelpers.EnvironmentConfig(path="kv/api/", kv_version=2)


DEBUG = False

SECRET_KEY = api_keys.get("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = ["api.onews.diogosilva.tech", "localhost", "127.0.0.1"]


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


SECURE_REFERRER_POLICY = "strict-origin"


SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True


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
