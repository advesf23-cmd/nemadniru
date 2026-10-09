from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0099_dynamic_catalog"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="productattributevalue",
            name="uniq_product_attribute_variant",
        ),
        migrations.AddConstraint(
            model_name="productattributevalue",
            constraint=models.UniqueConstraint(
                fields=("product", "attribute"),
                name="uniq_product_attribute",
            ),
        ),
    ]
