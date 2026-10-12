from django.apps import apps
from django.db.models import F


def normalize_attribute_text(text):
    """همان نرمال‌سازی AttributeValue.save() -- یک منبع واحد برای هر دو."""
    return " ".join((text or "").casefold().split())


def adjust_usage_count(attribute_id, text, delta, language_code="fa"):
    """
    شمارنده‌ی usage_count مقدار کاتالوگ را به‌صورت اتمیک تغییر می‌دهد.
    delta > 0: در صورت نبود، مقدار کاتالوگ ساخته می‌شود.
    delta < 0: هرگز زیر صفر نمی‌رود و مقدار جدید نمی‌سازد.
    """
    normalized = normalize_attribute_text(text)
    if not attribute_id or not normalized:
        return
    AttributeValue = apps.get_model("products", "AttributeValue")
    if delta > 0:
        known, _ = AttributeValue.objects.get_or_create(
            attribute_id=attribute_id,
            normalized_value=normalized,
            language_code=language_code,
            defaults={"value": (text or "").strip()},
        )
        AttributeValue.objects.filter(pk=known.pk).update(usage_count=F("usage_count") + delta)
    else:
        AttributeValue.objects.filter(
            attribute_id=attribute_id,
            normalized_value=normalized,
            language_code=language_code,
            usage_count__gt=0,
        ).update(usage_count=F("usage_count") + delta)
