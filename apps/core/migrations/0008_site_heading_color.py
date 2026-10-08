from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_site_menu_text_color"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesetting",
            name="theme_heading_color",
            field=models.CharField(
                default="#0B2447",
                max_length=7,
                verbose_name="رنگ تیترهای صفحات",
            ),
        ),
    ]
