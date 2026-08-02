from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ["*"]

# در توسعه از SQLite هم می‌توان استفاده کرد در صورت نبود PostgreSQL محلی (اختیاری):
# DATABASES["default"] = {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}

INTERNAL_IPS = ["127.0.0.1"]















import os as _os
if _os.environ.get("USE_SQLITE_FOR_CHECK"):
    DATABASES["default"] = {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
