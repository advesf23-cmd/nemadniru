import json
from pathlib import Path
from apps.products.models import Product, ProductSpecification, CategoryAttributeTemplate

PREFIX = "SEC-035 TEST  "
backup = json.loads(Path("SEC-035G3-technical-before.json").read_text(encoding="utf-8-sig"))
assert backup.get("stage") == "SEC-035G3-LOCAL-TEST-SPECIFICATIONS", "Unexpected backup stage"
assert len(backup.get("product_ids", [])) == 50, "Expected 50 backup IDs"
products = list(Product.objects.filter(id__in=backup["product_ids"]).order_by("sku"))
assert len(products) == 50, "Expected exactly 50 products"
assert len({p.category_id for p in products}) == 1, "Products span multiple categories"
category_id = products[0].category_id
assert CategoryAttributeTemplate.objects.filter(pk=1, category_id=category_id).exists(), "Original template id=1 missing"
assert not ProductSpecification.objects.filter(product__in=products, key__startswith=PREFIX).exists(), "Stage specifications already exist"
assert not CategoryAttributeTemplate.objects.filter(category_id=category_id, name__startswith=PREFIX).exists(), "Stage templates already exist"
print("PREFLIGHT PART 1: PASS")
print("PRODUCTS:", len(products))
print("CATEGORY_ID:", category_id)
print("ORIGINAL_TEMPLATE_ID_1: preserved; read-only check passed")
print("PREFIX_CONFLICTS: 0")
print("DATABASE_WRITES: 0")

template_defs = [
    {"name": PREFIX + "تعداد پل"},
    {"name": PREFIX + "جریان نامی"},
    {"name": PREFIX + "ولتاژ نامی"},
]
currents = [6, 10, 16, 20, 25]
voltages = [230, 400, 24, 110, 230]
poles = [1, 2, 3, 4, 2]
extras = {
    0: [("منحنی قطع", "C"), ("قدرت قطع", "6 kA")],
    1: [("قدرت قطع", "25 kA"), ("واحد حفاظتی", "حرارتی-مغناطیسی")],
    2: [("ولتاژ بوبین", "230 V"), ("کنتاکت کمکی", "1NO+1NC")],
    3: [("نوع حفاظت", "اضافهجریان و افت فاز"), ("محدوده تنظیم", "1 تا 10 A")],
    4: [("نوع شستی", "فشاری"), ("قطر نصب", "22 mm")],
    5: [("رنگ", "سبز"), ("منبع نور", "LED")],
    6: [("سطح مقطع سیم", "2.5 mm"), ("نوع اتصال", "پیچی")],
    7: [("نوع فیوز", "gG"), ("سایز", "1038 mm")],
    8: [("نوع عملکرد", "تأخیر در وصل"), ("محدوده زمان", "1 تا 10 s")],
    9: [("ولتاژ ورودی", "230 V"), ("توان خروجی", "60 W")],
}
NOTICE = "مقادیر ساختگی فقط برای آزمون محلی نه انتخاب یا خرید واقعی."
proposed = []
for p in products:
    suffix = int(p.sku.rsplit("-", 1)[1])
    family = (suffix - 1) % 10
    sample = (suffix - 1) // 10
    rows = [("یادداشت آزمون", NOTICE), ("ولتاژ نامی", f"{voltages[sample]} V")]
    if family in (0, 1, 2): rows.append(("تعداد پل", str(poles[sample])))
    if family in (0, 1, 2, 3, 6, 7): rows.append(("جریان نامی", f"{currents[sample]} A"))
    rows.extend(extras[family])
    proposed.extend((PREFIX + k, v) for k, v in rows)
key_max = ProductSpecification._meta.get_field("key").max_length
value_max = ProductSpecification._meta.get_field("value").max_length
name_max = CategoryAttributeTemplate._meta.get_field("name").max_length
assert len(proposed) == 245, f"Unexpected specification count: {len(proposed)}"
assert max(len(k) for k, v in proposed) <= key_max, "Specification key too long"
assert max(len(v) for k, v in proposed) <= value_max, "Specification value too long"
assert all(len(t["name"]) <= name_max for t in template_defs), "Template name too long"
print("PREFLIGHT PART 2: PASS")
print("SPECIFICATIONS_CHECKED:", len(proposed))
print("MAX_KEY_LENGTH:", max(len(k) for k, v in proposed), "/", key_max)
print("MAX_VALUE_LENGTH:", max(len(v) for k, v in proposed), "/", value_max)
print("MAX_TEMPLATE_NAME_LENGTH:", max(len(t["name"]) for t in template_defs), "/", name_max)
print("DATABASE_WRITES: 0")
