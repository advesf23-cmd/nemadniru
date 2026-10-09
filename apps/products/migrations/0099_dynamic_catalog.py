from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    # Independent branch from the original product schema; Django applies this
    # alongside subsequent legacy migrations without rewriting existing data.
    dependencies = [("products", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="AttributeSet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")),
                ("name", models.CharField(max_length=150, unique=True, verbose_name="نام قالب مشخصات")),
                ("description", models.TextField(blank=True, verbose_name="توضیحات")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
            ],
            options={"ordering": ["name"], "verbose_name": "قالب مشخصات", "verbose_name_plural": "قالب‌های مشخصات"},
        ),
        migrations.CreateModel(
            name="AttributeGroup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")),
                ("name", models.CharField(max_length=100, unique=True, verbose_name="نام گروه مشخصات")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="ترتیب")),
            ],
            options={"ordering": ["order", "name"], "verbose_name": "گروه مشخصات", "verbose_name_plural": "گروه‌های مشخصات"},
        ),
        migrations.CreateModel(
            name="Attribute",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")),
                ("name", models.CharField(max_length=150, unique=True, verbose_name="نام مشخصه")),
                ("code", models.SlugField(allow_unicode=True, max_length=160, unique=True, verbose_name="کد یکتا")),
                ("data_type", models.CharField(choices=[("text", "متن کوتاه"), ("long_text", "متن بلند"), ("number", "عدد"), ("boolean", "بله/خیر"), ("select", "انتخابی"), ("multiselect", "چندانتخابی"), ("color", "رنگ"), ("date", "تاریخ"), ("file", "فایل"), ("image", "تصویر")], default="text", max_length=20, verbose_name="نوع داده")),
                ("unit", models.CharField(blank=True, max_length=30, verbose_name="واحد")),
                ("is_required", models.BooleanField(default=False, verbose_name="اجباری")),
                ("is_filterable", models.BooleanField(default=False, verbose_name="قابل فیلتر")),
                ("is_comparable", models.BooleanField(default=True, verbose_name="قابل مقایسه")),
                ("is_searchable", models.BooleanField(default=False, verbose_name="قابل جستجو")),
                ("is_visible", models.BooleanField(default=True, verbose_name="نمایش در صفحه محصول")),
                ("min_value", models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True, verbose_name="حداقل مقدار عددی")),
                ("max_value", models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True, verbose_name="حداکثر مقدار عددی")),
                ("validation_regex", models.CharField(blank=True, max_length=255, verbose_name="عبارت اعتبارسنجی متن")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
                ("group", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="attributes", to="products.attributegroup", verbose_name="گروه")),
            ],
            options={"ordering": ["group__order", "name"], "verbose_name": "مشخصه", "verbose_name_plural": "مشخصه‌ها"},
        ),
        migrations.CreateModel(
            name="AttributeSetAttribute",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="ترتیب")),
                ("is_required_override", models.BooleanField(blank=True, null=True, verbose_name="اجباری در این قالب")),
                ("attribute", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="set_items", to="products.attribute")),
                ("attribute_set", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="products.attributeset")),
            ],
            options={"ordering": ["order", "id"], "verbose_name": "مشخصه قالب", "verbose_name_plural": "مشخصه‌های قالب"},
        ),
        migrations.CreateModel(
            name="AttributeValue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")),
                ("value", models.CharField(max_length=500, verbose_name="مقدار استاندارد")),
                ("normalized_value", models.CharField(editable=False, max_length=500, verbose_name="مقدار نرمال‌شده")),
                ("language_code", models.CharField(default="fa", max_length=10, verbose_name="زبان")),
                ("usage_count", models.PositiveIntegerField(default=0, verbose_name="تعداد استفاده")),
                ("attribute", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="known_values", to="products.attribute")),
            ],
            options={"ordering": ["value"], "verbose_name": "مقدار شناخته‌شده مشخصه", "verbose_name_plural": "مقادیر شناخته‌شده مشخصه‌ها"},
        ),
        migrations.CreateModel(
            name="ProductVariant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد", verbose_name="تاریخ ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")),
                ("name", models.CharField(max_length=150, verbose_name="نام تنوع")),
                ("sku", models.CharField(max_length=60, unique=True, verbose_name="SKU تنوع")),
                ("price", models.DecimalField(blank=True, decimal_places=0, max_digits=14, null=True, verbose_name="قیمت")),
                ("stock_quantity", models.PositiveIntegerField(default=0, verbose_name="موجودی")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="variants", to="products.product", verbose_name="محصول والد")),
            ],
            options={"ordering": ["id"], "verbose_name": "تنوع محصول", "verbose_name_plural": "تنوع‌های محصول"},
        ),
        migrations.CreateModel(
            name="ProductAttributeValue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")),
                ("value_text", models.TextField(blank=True, verbose_name="مقدار متنی")),
                ("value_number", models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True, verbose_name="مقدار عددی")),
                ("value_boolean", models.BooleanField(blank=True, null=True, verbose_name="مقدار بله/خیر")),
                ("value_date", models.DateField(blank=True, null=True, verbose_name="تاریخ")),
                ("value_file", models.FileField(blank=True, null=True, upload_to="products/attributes/", verbose_name="فایل")),
                ("attribute", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="product_values", to="products.attribute")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attribute_values", to="products.product")),
                ("variant", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="attribute_values", to="products.productvariant")),
                ("selected_values", models.ManyToManyField(blank=True, related_name="product_assignments", to="products.attributevalue", verbose_name="مقادیر انتخاب‌شده")),
            ],
            options={"verbose_name": "مقدار مشخصه محصول", "verbose_name_plural": "مقادیر مشخصات محصول"},
        ),
        migrations.CreateModel(
            name="VariantAttributeValue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")),
                ("value_text", models.TextField(blank=True)),
                ("value_number", models.DecimalField(blank=True, decimal_places=4, max_digits=18, null=True)),
                ("value_boolean", models.BooleanField(blank=True, null=True)),
                ("attribute", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="variant_values", to="products.attribute")),
                ("selected_values", models.ManyToManyField(blank=True, related_name="variant_assignments", to="products.attributevalue")),
                ("variant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="variant_values", to="products.productvariant")),
            ],
            options={"verbose_name": "مشخصه تنوع", "verbose_name_plural": "مشخصات تنوع‌ها"},
        ),
        migrations.AddField(
            model_name="productcategory",
            name="attribute_set",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="categories", to="products.attributeset", verbose_name="قالب مشخصات"),
        ),
        migrations.AddField(
            model_name="productcategory",
            name="inherit_parent_attributes",
            field=models.BooleanField(default=True, verbose_name="ارث‌بری مشخصات از والد"),
        ),
        migrations.AddConstraint(
            model_name="attributesetattribute",
            constraint=models.UniqueConstraint(fields=("attribute_set", "attribute"), name="uniq_attribute_in_set"),
        ),
        migrations.AddConstraint(
            model_name="attributevalue",
            constraint=models.UniqueConstraint(fields=("attribute", "normalized_value", "language_code"), name="uniq_attribute_value_language"),
        ),
        migrations.AddConstraint(
            model_name="productattributevalue",
            constraint=models.UniqueConstraint(fields=("product", "attribute", "variant"), name="uniq_product_attribute_variant"),
        ),
        migrations.AddConstraint(
            model_name="variantattributevalue",
            constraint=models.UniqueConstraint(fields=("variant", "attribute"), name="uniq_variant_attribute"),
        ),
        migrations.AddIndex(
            model_name="attribute",
            index=models.Index(fields=["data_type", "is_active"], name="prod_attr_type_active_idx"),
        ),
        migrations.AddIndex(
            model_name="attributevalue",
            index=models.Index(fields=["attribute", "normalized_value"], name="prod_attr_val_norm_idx"),
        ),
        migrations.AddIndex(
            model_name="attributevalue",
            index=models.Index(fields=["attribute", "usage_count"], name="prod_attr_val_usage_idx"),
        ),
        migrations.AddIndex(
            model_name="productvariant",
            index=models.Index(fields=["product", "is_active"], name="prod_variant_active_idx"),
        ),
        migrations.AddIndex(
            model_name="productattributevalue",
            index=models.Index(fields=["attribute", "value_number"], name="prod_pav_attr_num_idx"),
        ),
        migrations.AddIndex(
            model_name="productattributevalue",
            index=models.Index(fields=["attribute", "value_boolean"], name="prod_pav_attr_bool_idx"),
        ),
    ]
