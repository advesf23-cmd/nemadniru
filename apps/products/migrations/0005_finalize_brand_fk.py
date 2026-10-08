# dest: apps/products/migrations/0005_finalize_brand_fk.py

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_migrate_brand_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='brand',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='brand_new',
            new_name='brand',
        ),
    ]
