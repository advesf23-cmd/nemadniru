# dest: apps/products/migrations/0006_filterableattribute.py
# پیش‌نیاز: میگریشن‌های ۰۰۰۳ تا ۰۰۰۵ دور قبل (Brand) باید اعمال شده باشند.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_finalize_brand_fk'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilterableAttribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='عنوان فیلتر در سایت')),
                ('spec_key', models.CharField(help_text='دقیقاً مطابق «عنوان مشخصه» در مشخصات فنی محصولات (مثلاً: جریان نامی)', max_length=100, verbose_name='نام مشخصه فنی')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('category', models.ForeignKey(blank=True, help_text='خالی = در همه‌ی صفحات محصولات نمایش داده شود', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='filter_attributes', to='products.productcategory', verbose_name='محدود به دسته‌بندی')),
            ],
            options={
                'verbose_name': 'فیلتر جستجوی پیشرفته',
                'verbose_name_plural': 'فیلترهای جستجوی پیشرفته',
                'ordering': ['order', 'id'],
            },
        ),
    ]
