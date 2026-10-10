from .base import *  # noqa
from decouple import config
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

# Never start production with known placeholder secrets or permissive hosts.
if SECRET_KEY.startswith("django-insecure-") or len(SECRET_KEY) < 50:
    raise ImproperlyConfigured("Set a strong, unique SECRET_KEY (at least 50 characters) in the production environment.")

_db_password = config("DB_PASSWORD", default="").strip()
if not _db_password or _db_password.lower() in {"postgres", "password", "changeme", "change-me"}:
    raise ImproperlyConfigured("Set a strong DB_PASSWORD in the production environment.")

if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS or all(
    host in {"localhost", "127.0.0.1"} for host in ALLOWED_HOSTS
):
    raise ImproperlyConfigured("Set ALLOWED_HOSTS to the real production hostnames; wildcards and localhost-only are not allowed.")

SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://127.0.0.1:6379/1"),
    }
}

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# پشت پراکسی/Nginx در پروداکشن، هدر X-Forwarded-Proto را برای تشخیص HTTPS معتبر می‌داند
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
