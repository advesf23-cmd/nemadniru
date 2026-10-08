from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_site_menu_color"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesetting",
            name="theme_menu_text_color",
            field=models.CharField(
                default="#FFFFFF",
                max_length=7,
                verbose_name="رنگ نوشته منو",
            ),
        ),
    ]
