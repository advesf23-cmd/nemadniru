from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_site_announcement"),
    ]

    operations = [
        migrations.AddField(model_name="sitesetting", name="theme_primary_color", field=models.CharField(default="#0B2447", max_length=7, verbose_name="رنگ اصلی (کادرها و منوها)")),
        migrations.AddField(model_name="sitesetting", name="theme_accent_color", field=models.CharField(default="#F97316", max_length=7, verbose_name="رنگ تأکیدی (دکمه‌ها و لینک‌ها)")),
        migrations.AddField(model_name="sitesetting", name="theme_text_color", field=models.CharField(default="#1E293B", max_length=7, verbose_name="رنگ نوشته‌ها")),
        migrations.AddField(model_name="sitesetting", name="theme_background_color", field=models.CharField(default="#FFFFFF", max_length=7, verbose_name="رنگ پس‌زمینه صفحات")),
        migrations.AddField(model_name="sitesetting", name="theme_surface_color", field=models.CharField(default="#F4F6F8", max_length=7, verbose_name="رنگ پس‌زمینه کادرها")),
        migrations.AddField(model_name="sitesetting", name="theme_border_color", field=models.CharField(default="#E2E8F0", max_length=7, verbose_name="رنگ حاشیه کادرها")),
    ]
