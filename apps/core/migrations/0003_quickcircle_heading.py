# dest: apps/core/migrations/0003_quickcircle_heading.py
# توجه: اگر شماره‌ی میگریشن قبلی شما برای PromoBanner چیز دیگری غیر از
# "0002_promobanner" بود، مقدار dependencies پایین را با همان نام واقعی
# فایل میگریشن قبلی‌تان جایگزین کنید.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_promobanner'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesetting',
            name='quick_circles_heading',
            field=models.CharField(blank=True, max_length=150, verbose_name='عنوان بالای دایره‌های سریع (زیر اسلایدر)'),
        ),
        migrations.CreateModel(
            name='QuickCircle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')),
                ('title', models.CharField(max_length=50, verbose_name='عنوان (زیر تصویر دایره)')),
                ('image', models.ImageField(upload_to='quick_circles/', verbose_name='تصویر (ترجیحاً مربعی)')),
                ('link_url', models.CharField(blank=True, max_length=255, verbose_name='لینک مقصد (اختیاری)')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
            ],
            options={
                'verbose_name': 'دایره سریع (زیر اسلایدر)',
                'verbose_name_plural': 'دایره‌های سریع (زیر اسلایدر)',
                'ordering': ['order'],
            },
        ),
    ]
