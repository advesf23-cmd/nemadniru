from django.apps import AppConfig


class ProductsConfig(AppConfig):
    name = 'apps.products'

    def ready(self):
        # ثبت سیگنال‌های یکپارچگی مشخصات (شمارنده‌ی مقادیر، اعتبارسنجی M2M)
        from . import signals  # noqa: F401
