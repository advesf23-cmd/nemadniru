from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_quickcircle_heading"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesetting",
            name="announcement_enabled",
            field=models.BooleanField(default=False, verbose_name="نمایش نوار اطلاع‌رسانی"),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="announcement_text",
            field=models.CharField(blank=True, max_length=500, verbose_name="متن نوار اطلاع‌رسانی"),
        ),
        migrations.AddField(
            model_name="sitesetting",
            name="announcement_color",
            field=models.CharField(default="#0d6efd", max_length=7, verbose_name="رنگ نوار اطلاع‌رسانی"),
        ),
    ]
