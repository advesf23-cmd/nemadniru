# dest: apps/core/migrations/0002_promobanner.py
# (یا هر شماره بعدی که با migrate --check صحیح باشد -- بعد از افزودن مدل، دستور
#  `python manage.py makemigrations core` را هم می‌توانید اجرا کنید تا خودکار ساخته شود)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromoBanner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')),
                ('image', models.ImageField(upload_to='promo_banners/', verbose_name='تصویر تبلیغاتی')),
                ('title', models.CharField(blank=True, max_length=150, verbose_name='عنوان (اختیاری، فقط برای مدیریت داخلی)')),
                ('link_url', models.CharField(blank=True, max_length=255, verbose_name='لینک مقصد (اختیاری)')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
            ],
            options={
                'verbose_name': 'بنر تبلیغاتی',
                'verbose_name_plural': 'بنرهای تبلیغاتی (۴ کادر زیر اسلایدر)',
                'ordering': ['order'],
            },
        ),
    ]
