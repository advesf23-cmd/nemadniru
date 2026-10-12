"""
تست‌های یکپارچگی مشخصات پویا و فیلتر عددی.
فایل جداگانه است تا با tests.py موجود (که ممکن است تست‌های بیشتری داشته باشد) تداخل نکند.

اجرا:
    python manage.py test apps.products --settings=config.settings.test
"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import (
    Attribute, AttributeValue, CategoryAttributeTemplate, Product, ProductAttributeValue,
    ProductCategory, ProductSpecification, ProductVariant,
)


def make_product(category, name="P"):
    return Product.objects.create(
        category=category, name=name, description="", status="published", cover_image=""
    )


class AttributeUsageCountTests(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(name="MCCB")
        self.product = make_product(self.category)
        self.attr = Attribute.objects.create(name="ولتاژ", code="voltage", data_type=Attribute.TEXT)

    def count(self, normalized):
        return AttributeValue.objects.get(attribute=self.attr, normalized_value=normalized).usage_count

    def test_create_sets_count_to_one(self):
        ProductAttributeValue.objects.create(product=self.product, attribute=self.attr, value_text="230 V")
        self.assertEqual(self.count("230 v"), 1)

    def test_resave_without_change_does_not_increment(self):
        pav = ProductAttributeValue.objects.create(product=self.product, attribute=self.attr, value_text="230 V")
        pav.save()
        pav.save()
        self.assertEqual(self.count("230 v"), 1)

    def test_changing_value_moves_count(self):
        pav = ProductAttributeValue.objects.create(product=self.product, attribute=self.attr, value_text="230 V")
        pav.value_text = "400 V"
        pav.save()
        pav.refresh_from_db()
        self.assertEqual(self.count("230 v"), 0)
        self.assertEqual(self.count("400 v"), 1)
        self.assertEqual(AttributeValue.objects.filter(attribute=self.attr).count(), 2)

    def test_delete_decrements(self):
        pav = ProductAttributeValue.objects.create(product=self.product, attribute=self.attr, value_text="230 V")
        pav.delete()
        self.assertEqual(self.count("230 v"), 0)

    def test_cascade_delete_of_product_decrements(self):
        ProductAttributeValue.objects.create(product=self.product, attribute=self.attr, value_text="230 V")
        self.product.delete()
        self.assertEqual(self.count("230 v"), 0)

    def test_two_products_same_value(self):
        other = make_product(self.category, "Q")
        ProductAttributeValue.objects.create(product=self.product, attribute=self.attr, value_text="230 V")
        ProductAttributeValue.objects.create(product=other, attribute=self.attr, value_text="230  v")
        self.assertEqual(self.count("230 v"), 2)
        self.assertEqual(AttributeValue.objects.filter(attribute=self.attr).count(), 1)


class AttributeValidationTests(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(name="MCCB")
        self.product = make_product(self.category, "A")
        self.other_product = make_product(self.category, "B")
        self.text_attr = Attribute.objects.create(name="رنگ", code="color-name", data_type=Attribute.TEXT)
        self.num_attr = Attribute.objects.create(name="جریان", code="current", data_type=Attribute.NUMBER)

    def test_variant_of_other_product_is_rejected(self):
        variant = ProductVariant.objects.create(product=self.other_product, name="v", sku="SKU-1")
        pav = ProductAttributeValue(product=self.product, attribute=self.text_attr, value_text="x", variant=variant)
        with self.assertRaises(ValidationError):
            pav.full_clean()

    def test_number_attribute_rejects_text_only_value(self):
        pav = ProductAttributeValue(product=self.product, attribute=self.num_attr, value_text="100")
        with self.assertRaises(ValidationError):
            pav.full_clean()

    def test_number_attribute_accepts_numeric_value(self):
        pav = ProductAttributeValue(product=self.product, attribute=self.num_attr, value_number=100)
        pav.full_clean()

    def test_selected_value_of_other_attribute_is_rejected(self):
        pav = ProductAttributeValue.objects.create(product=self.product, attribute=self.text_attr, value_text="x")
        foreign = AttributeValue.objects.create(attribute=self.num_attr, value="y")
        with self.assertRaises(ValidationError):
            pav.selected_values.add(foreign)

    def test_selected_value_of_same_attribute_is_accepted(self):
        pav = ProductAttributeValue.objects.create(product=self.product, attribute=self.text_attr, value_text="x")
        own = AttributeValue.objects.create(attribute=self.text_attr, value="z")
        pav.selected_values.add(own)
        self.assertEqual(pav.selected_values.count(), 1)


class RangeFilterRobustnessTests(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(name="MCCB")
        self.tpl = CategoryAttributeTemplate.objects.create(
            category=self.category, name="جریان نامی", unit="A",
            filter_type=CategoryAttributeTemplate.FILTER_TYPE_RANGE, is_filterable=True,
        )
        self.url = reverse("products:category_detail", kwargs={"slug": self.category.slug})
        self.products = {}
        for name, value in [("p100", "100A"), ("p250", "250 A"), ("p400", "400"), ("pbad", "نامشخص"), ("pnone", "")]:
            product = make_product(self.category, name)
            ProductSpecification.objects.create(product=product, key="جریان نامی", value=value)
            self.products[name] = product

    def names(self, response):
        return sorted(p.name for p in response.context["products"])

    def test_formats_with_and_without_space_are_numeric(self):
        r = self.client.get(self.url, {f"attr_{self.tpl.pk}_min": "200", f"attr_{self.tpl.pk}_max": "300"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.names(r), ["p250"])

    def test_non_numeric_spec_values_do_not_crash(self):
        r = self.client.get(self.url, {f"attr_{self.tpl.pk}_min": "50"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.names(r), ["p100", "p250", "p400"])

    def test_invalid_query_parameter_is_ignored(self):
        r = self.client.get(self.url, {f"attr_{self.tpl.pk}_min": "abc"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(self.names(r)), 5)
