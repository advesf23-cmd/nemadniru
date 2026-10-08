from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_site_theme_colors"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesetting",
            name="theme_menu_color",
            field=models.CharField(default="#0B2447", max_length=7, verbose_name="رنگ منوها"),
        ),
        migrations.AlterField(
            model_name="sitesetting",
            name="theme_primary_color",
            field=models.CharField(default="#0B2447", max_length=7, verbose_name="رنگ اصلی کادرها"),
        ),
    ]
