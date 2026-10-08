# dest: apps/products/migrations/0004_migrate_brand_data.py
#
# این میگریشن داده‌ای (Data Migration) است: برای هر مقدار متفاوتِ غیرخالیِ
# فیلد متنی قدیمی brand، یک رکورد Brand می‌سازد (اگر از قبل نساخته باشد) و
# محصول را از طریق brand_new به همان رکورد وصل می‌کند. هیچ داده‌ای حذف
# نمی‌شود -- فیلد متنی قدیمی brand دست‌نخورده باقی می‌ماند تا میگریشن بعدی.

from django.db import migrations
from django.utils.text import slugify


def migrate_brands_forward(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    Brand = apps.get_model('products', 'Brand')

    distinct_names = (
        Product.objects.exclude(brand__exact="")
        .order_by("brand")
        .values_list("brand", flat=True)
        .distinct()
    )

    name_to_brand_id = {}
    for raw_name in distinct_names:
        name = raw_name.strip()
        if not name:
            continue
        brand, _created = Brand.objects.get_or_create(
            name__iexact=name,
            defaults={
                "name": name,
                "slug": slugify(name, allow_unicode=True) or f"brand-{len(name_to_brand_id) + 1}",
            },
        )
        name_to_brand_id[raw_name] = brand.id

    for raw_name, brand_id in name_to_brand_id.items():
        Product.objects.filter(brand=raw_name).update(brand_new_id=brand_id)


def migrate_brands_backward(apps, schema_editor):
    # برگشت‌پذیر کردن کامل این تبدیل لازم نیست (داده‌ی اصلی brand متنی هنوز
    # دست‌نخورده است)؛ فقط لینک brand_new را پاک می‌کنیم.
    Product = apps.get_model('products', 'Product')
    Product.objects.update(brand_new=None)


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_brand_and_new_fields'),
    ]

    operations = [
        migrations.RunPython(migrate_brands_forward, migrate_brands_backward),
    ]
