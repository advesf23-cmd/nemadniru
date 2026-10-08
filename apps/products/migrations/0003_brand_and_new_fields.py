# dest: apps/products/migrations/0003_brand_and_new_fields.py

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_productreview'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')),
                ('slug', models.SlugField(allow_unicode=True, blank=True, max_length=255, unique=True, verbose_name='اسلاگ')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='نام برند')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='brands/', verbose_name='لوگو')),
                ('default_discount_percent', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='درصد تخفیف پیش‌فرض برند')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
            ],
            options={
                'verbose_name': 'برند',
                'verbose_name_plural': 'برندها',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='CategoryAttributeTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='نام مشخصه (مثلاً: جریان نامی)')),
                ('unit', models.CharField(blank=True, max_length=30, verbose_name='واحد (مثلاً: A، kA، V)')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='ترتیب')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attribute_templates', to='products.productcategory', verbose_name='دسته‌بندی')),
            ],
            options={
                'verbose_name': 'قالب مشخصه فنی دسته‌بندی',
                'verbose_name_plural': 'قالب‌های مشخصات فنی دسته‌بندی‌ها',
                'ordering': ['category', 'order'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='mpn',
            field=models.CharField(blank=True, db_index=True, default='', max_length=100, verbose_name='کد سازنده (MPN)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='technical_description',
            field=models.TextField(blank=True, default='', verbose_name='توضیحات فنی (متن آزاد)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='discount_percent_override',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='درصد تخفیف اختصاصی این محصول (اختیاری)'),
        ),
        # فیلد موقت brand_new -- در میگریشن بعدی با داده‌ی تبدیل‌شده از brand
        # متنی قدیمی پر می‌شود و در میگریشن سوم جای brand قدیمی می‌نشیند.
        migrations.AddField(
            model_name='product',
            name='brand_new',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='products', to='products.brand', verbose_name='برند / سازنده'
            ),
        ),
    ]
