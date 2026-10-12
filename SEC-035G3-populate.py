# SEC-035G3-LOCAL-TEST-SPECIFICATIONS
import json
from pathlib import Path
from django.db import transaction
from apps.products.models import Product, ProductSpecification, CategoryAttributeTemplate

PREFIX = "SEC-035 TEST  "
NOTICE = "مقادیر ساختگی فقط برای آزمون محلی نه انتخاب یا خرید واقعی."
backup_path = Path("SEC-035G3-technical-before.json")
products_backup_path = Path("SEC-035-products-before.json")

if not backup_path.exists() or not products_backup_path.exists():
    raise SystemExit("ABORT: required backup file missing")

backup = json.loads(backup_path.read_text(encoding="utf-8-sig"))
if backup.get("stage") != "SEC-035G3-LOCAL-TEST-SPECIFICATIONS":
    raise SystemExit("ABORT: unexpected backup stage")
if len(backup.get("product_ids", [])) != 50:
    raise SystemExit("ABORT: expected exactly 50 product IDs")

products = list(Product.objects.filter(id__in=backup["product_ids"]).order_by("sku"))
if len(products) != 50 or len({p.category_id for p in products}) != 1:
    raise SystemExit("ABORT: expected 50 products in one category")
if ProductSpecification.objects.filter(product__in=products, key__startswith=PREFIX).exists():
    raise SystemExit("ABORT: stage specifications already exist")
if CategoryAttributeTemplate.objects.filter(category_id=products[0].category_id, name__startswith=PREFIX).exists():
    raise SystemExit("ABORT: stage templates already exist")

template_defs = [
    {"name": PREFIX + "تعداد پل", "unit": "", "order": 900, "filter_type": "multiselect",
     "is_filterable": True, "filter_choices": "1|یک پل\n2|دو پل\n3|سه پل\n4|چهار پل"},
    {"name": PREFIX + "جریان نامی", "unit": "A", "order": 901, "filter_type": "range",
     "is_filterable": True, "filter_min": 1, "filter_max": 1000, "filter_step": 1},
    {"name": PREFIX + "ولتاژ نامی", "unit": "V", "order": 902, "filter_type": "range",
     "is_filterable": True, "filter_min": 12, "filter_max": 1000, "filter_step": 1},
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

spec_rows = []
for product in products:
    suffix = int(product.sku.rsplit("-", 1)[1])
    family = (suffix - 1) % 10
    sample = (suffix - 1) // 10
    rows = [
        ("یادداشت آزمون", NOTICE),
        ("ولتاژ نامی", f"{voltages[sample]} V"),
    ]
    if family in (0, 1, 2):
        rows.append(("تعداد پل", str(poles[sample])))
    if family in (0, 1, 2, 3, 6, 7):
        rows.append(("جریان نامی", f"{currents[sample]} A"))
    rows.extend(extras[family])
    for name, value in rows:
        spec_rows.append(ProductSpecification(
            product=product, key=PREFIX + name, value=value
        ))

with transaction.atomic():
    CategoryAttributeTemplate.objects.bulk_create([
        CategoryAttributeTemplate(
            category_id=products[0].category_id, **definition
        )
        for definition in template_defs
    ])
    ProductSpecification.objects.bulk_create(spec_rows)

print("STAGE: SEC-035G3-LOCAL-TEST-SPECIFICATIONS")
print("PRODUCTS:", len(products))
print("TEST_TEMPLATES_CREATED:", len(template_defs))
print("TEST_SPECIFICATIONS_CREATED:", len(spec_rows))
print("NOTICE_ROWS:", len(products))
print("PRODUCT_FIELDS_MODIFIED: 0")
