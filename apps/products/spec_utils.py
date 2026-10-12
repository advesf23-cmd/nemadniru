from decimal import Decimal


def _norm_key(text):
    return "".join((text or "").casefold().split())


def display_attribute_value(pav):
    """مقدار قابل‌نمایش یک ProductAttributeValue (برای صفحه مقایسه و ...)."""
    if pav.value_number is not None:
        number = format(Decimal(pav.value_number).normalize(), "f")
        unit = pav.attribute.unit
        return f"{number} {unit}".strip() if unit else number
    if pav.value_boolean is not None:
        return "بله" if pav.value_boolean else "خیر"
    if pav.value_date:
        return pav.value_date.strftime("%Y/%m/%d")
    selected = [v.value for v in pav.selected_values.all()]
    if selected:
        return "، ".join(selected)
    if pav.value_file:
        return "دارای فایل"
    return (pav.value_text or "").strip()


def build_comparison_rows(products):
    """
    ردیف‌های جدول مقایسه را از هر دو ساختار می‌سازد:
      - مشخصات جدید (ProductAttributeValue عمومی، فقط ویژگی‌های «قابل مقایسه»)
      - مشخصات قدیمی (ProductSpecification)
    اگر یک مشخصه (با نام یکسان) در هر دو ساختار باشد، مقدار ساختار جدید اولویت دارد.
    فرض: products با prefetch_related("specifications", "attribute_values__attribute",
    "attribute_values__selected_values") آمده‌اند تا کوئری اضافه ایجاد نشود.
    """
    products = list(products)
    labels = {}
    order = []
    per_product = []

    for product in products:
        values = {}
        for spec in product.specifications.all():
            key = _norm_key(spec.key)
            if not key:
                continue
            labels.setdefault(key, spec.key)
            if key not in order:
                order.append(key)
            values[key] = spec.value
        for pav in product.attribute_values.all():
            attribute = pav.attribute
            if pav.variant_id is not None or not attribute.is_active or not attribute.is_comparable:
                continue
            shown = display_attribute_value(pav)
            if not shown:
                continue
            key = _norm_key(attribute.name)
            labels.setdefault(key, attribute.name)
            if key not in order:
                order.append(key)
            values[key] = shown  # ساختار جدید اولویت دارد
        per_product.append(values)

    return [
        {"key": labels[key], "values": [values.get(key, "") for values in per_product]}
        for key in order
    ]
