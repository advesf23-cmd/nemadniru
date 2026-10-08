from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0006_alter_brand_default_discount_percent_and_more"),
        ("products", "0006_filterableattribute"),
    ]

    operations = [
        migrations.AddField(
            model_name="categoryattributetemplate",
            name="filter_type",
            field=models.CharField(
                choices=[
                    ("none", "فیلتر نشود"),
                    ("select", "انتخاب یک مقدار"),
                    ("multiselect", "انتخاب چند مقدار"),
                    ("range", "بازه عددی"),
                    ("boolean", "بله / خیر"),
                ],
                default="none",
                help_text="مشخص می‌کند این مشخصه در جستجوی پیشرفته چگونه نمایش داده شود.",
                max_length=20,
                verbose_name="نوع فیلتر",
            ),
        ),
        migrations.AddField(
            model_name="categoryattributetemplate",
            name="is_filterable",
            field=models.BooleanField(
                default=False,
                help_text="اگر فعال باشد، این مشخصه در فیلتر محصولات همان دسته نمایش داده می‌شود.",
                verbose_name="نمایش در فیلتر",
            ),
        ),
        migrations.AddField(
            model_name="categoryattributetemplate",
            name="filter_choices",
            field=models.TextField(
                blank=True,
                help_text="برای فیلترهای انتخابی، هر مقدار را در یک خط بنویسید. می‌توانید «مقدار | عنوان» هم وارد کنید.",
                verbose_name="گزینه‌های فیلتر",
            ),
        ),
        migrations.AddField(
            model_name="categoryattributetemplate",
            name="filter_min",
            field=models.DecimalField(
                blank=True, decimal_places=4, max_digits=14, null=True, verbose_name="حداقل بازه"
            ),
        ),
        migrations.AddField(
            model_name="categoryattributetemplate",
            name="filter_max",
            field=models.DecimalField(
                blank=True, decimal_places=4, max_digits=14, null=True, verbose_name="حداکثر بازه"
            ),
        ),
        migrations.AddField(
            model_name="categoryattributetemplate",
            name="filter_step",
            field=models.DecimalField(
                blank=True, decimal_places=4, max_digits=14, null=True, verbose_name="گام بازه"
            ),
        ),
    ]
