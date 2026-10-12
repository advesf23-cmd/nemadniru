from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed, post_delete
from django.dispatch import receiver

from .attribute_utils import adjust_usage_count
from .models import AttributeValue, ProductAttributeValue, VariantAttributeValue


@receiver(post_delete, sender=ProductAttributeValue)
def decrement_usage_on_delete(sender, instance, **kwargs):
    """حذف مستقیم، حذف cascade (مثلاً حذف محصول) و حذف گروهی -- همه شمارنده را کم می‌کنند."""
    adjust_usage_count(instance.attribute_id, instance.value_text, -1)


def _validate_selected_values(sender, instance, action, reverse, pk_set, **kwargs):
    if action != "pre_add" or not pk_set:
        return
    if not reverse:
        # instance = مقدار مشخصه‌ی محصول/تنوع، pk_set = مقادیر کاتالوگ
        foreign = AttributeValue.objects.filter(pk__in=pk_set).exclude(attribute_id=instance.attribute_id)
        if foreign.exists():
            raise ValidationError("مقدار انتخابی متعلق به مشخصه‌ی دیگری است.")
    else:
        # instance = مقدار کاتالوگ، pk_set = رکوردهای مقدار مشخصه
        model = ProductAttributeValue if sender is ProductAttributeValue.selected_values.through else VariantAttributeValue
        if model.objects.filter(pk__in=pk_set).exclude(attribute_id=instance.attribute_id).exists():
            raise ValidationError("مقدار انتخابی متعلق به مشخصه‌ی دیگری است.")


m2m_changed.connect(
    _validate_selected_values,
    sender=ProductAttributeValue.selected_values.through,
    dispatch_uid="validate_pav_selected_values",
)
m2m_changed.connect(
    _validate_selected_values,
    sender=VariantAttributeValue.selected_values.through,
    dispatch_uid="validate_vav_selected_values",
)
