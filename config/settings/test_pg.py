"""
تنظیمات تست روی PostgreSQL -- با یک دیتابیس تست کاملاً جدا.

Django برای تست یک دیتابیس موقت می‌سازد، migrationها را روی آن اجرا می‌کند،
تست‌ها را اجرا می‌کند و در پایان آن را حذف می‌کند. دیتابیس اصلی (samantajhiz)
هیچ‌وقت خوانده یا نوشته نمی‌شود.

اجرا:
    python manage.py test apps.products --settings=config.settings.test_pg
"""
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa

DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

TEST_DB_NAME = "test_nemadniru_isolated"

_main_db = DATABASES["default"]  # noqa: F405

# --- محافظ‌های ایمنی ---
if _main_db["NAME"] == TEST_DB_NAME:
    raise ImproperlyConfigured("نام دیتابیس تست نباید با دیتابیس اصلی یکی باشد.")
if _main_db["HOST"] not in ("localhost", "127.0.0.1", "::1"):
    raise ImproperlyConfigured(
        "تست PostgreSQL فقط روی سرور محلی مجاز است (DB_HOST=%r). "
        "از اجرای تست روی سرور واقعی جلوگیری شد." % _main_db["HOST"]
    )

DATABASES["default"]["TEST"] = {"NAME": TEST_DB_NAME}  # noqa: F405
DATABASES["default"]["CONN_MAX_AGE"] = 0  # noqa: F405

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
