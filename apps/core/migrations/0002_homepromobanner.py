# Generated for dashboard-managed homepage promotional banners.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomePromoBanner",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")),
                ("image", models.ImageField(upload_to="home_promo_banners/", verbose_name="تصویر تبلیغاتی")),
                ("title", models.CharField(blank=True, max_length=150, verbose_name="عنوان روی تصویر")),
                ("description", models.CharField(blank=True, max_length=300, verbose_name="متن توضیحی روی تصویر")),
                ("button_text", models.CharField(blank=True, default="مشاهده محصولات", max_length=60, verbose_name="متن دکمه")),
                ("link_url", models.CharField(blank=True, max_length=255, verbose_name="لینک مقصد")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
            ],
            options={
                "verbose_name": "بنر تبلیغاتی زیر محصولات",
                "verbose_name_plural": "دو بنر تبلیغاتی زیر محصولات",
                "ordering": ["order"],
            },
        ),
    ]
