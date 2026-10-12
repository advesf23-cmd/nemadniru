"""
تنظیمات ایزوله‌ی تست -- هرگز به دیتابیس PostgreSQL اصلی (samantajhiz) وصل نمی‌شود.

اجرا:
    python manage.py test apps.products --settings=config.settings.test
"""
from .base import *  # noqa

DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

# SQLite درون‌حافظه‌ای: هیچ فایل یا دیتابیس واقعی لمس نمی‌شود.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
