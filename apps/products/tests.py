from django.test import TestCase
from django.urls import reverse

from .models import (
    CategoryAttributeTemplate,
    Product,
    ProductCategory,
    ProductSpecification,
    Attribute,
    AttributeValue,
    ProductAttributeValue,
)


class ProductAdvancedFilterTests(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(name="MCCB")
        self.poles_filter = CategoryAttributeTemplate.objects.create(
            category=self.category,
            name="تعداد پل",
            filter_type=CategoryAttributeTemplate.FILTER_TYPE_MULTISELECT,
            is_filterable=True,
            filter_choices="2|دو پل\n3|سه پل\n4|چهار پل",
        )
        self.current_filter = CategoryAttributeTemplate.objects.create(
            category=self.category,
            name="جریان نامی",
            unit="A",
            filter_type=CategoryAttributeTemplate.FILTER_TYPE_RANGE,
            is_filterable=True,
            filter_min=10,
            filter_max=630,
        )

        self.product_2p = Product.objects.create(
            category=self.category,
            name="MCCB 2P 100A",
            description="",
            status="published",
            cover_image="",
        )
        self.product_3p = Product.objects.create(
            category=self.category,
            name="MCCB 3P 250A",
            description="",
            status="published",
            cover_image="",
        )
        ProductSpecification.objects.create(
            product=self.product_2p, key="تعداد پل", value="2"
        )
        ProductSpecification.objects.create(
            product=self.product_2p, key="جریان نامی", value="100A"
        )
        ProductSpecification.objects.create(
            product=self.product_3p, key="تعداد پل", value="3"
        )
        ProductSpecification.objects.create(
            product=self.product_3p, key="جریان نامی", value="250A"
        )

    def test_multiselect_attribute_filter(self):
        url = reverse("products:category_detail", kwargs={"slug": self.category.slug})
        response = self.client.get(url, {f"attr_{self.poles_filter.pk}": "3"})
        self.assertEqual(response.status_code, 200)
        products = list(response.context["products"])
        self.assertEqual([p.pk for p in products], [self.product_3p.pk])

    def test_numeric_range_attribute_filter(self):
        url = reverse("products:category_detail", kwargs={"slug": self.category.slug})
        response = self.client.get(
            url,
            {
                f"attr_{self.current_filter.pk}_min": "150",
                f"attr_{self.current_filter.pk}_max": "300",
            },
        )
        self.assertEqual(response.status_code, 200)
        products = list(response.context["products"])
        self.assertEqual([p.pk for p in products], [self.product_3p.pk])


class ProductAttributeValueCatalogTests(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(name="Catalog Test")
        self.product = Product.objects.create(
            category=self.category,
            name="Catalog Test Product",
            description="",
            status="published",
            cover_image="",
        )
        self.second_product = Product.objects.create(
            category=self.category,
            name="Catalog Test Product 2",
            description="",
            status="published",
            cover_image="",
        )
        self.attribute = Attribute.objects.create(
            name="Test Voltage",
            code="test-voltage",
            data_type=Attribute.TEXT,
        )

    def test_new_text_value_is_added_to_catalog(self):
        ProductAttributeValue.objects.create(
            product=self.product,
            attribute=self.attribute,
            value_text="230 V",
        )

        known = AttributeValue.objects.get(
            attribute=self.attribute,
            normalized_value="230 v",
            language_code="fa",
        )
        self.assertEqual(known.value, "230 V")
        self.assertEqual(known.usage_count, 1)

    def test_saving_unchanged_value_does_not_change_count(self):
        assignment = ProductAttributeValue.objects.create(
            product=self.product,
            attribute=self.attribute,
            value_text="230 V",
        )

        assignment.save()
        assignment.refresh_from_db()

        known = AttributeValue.objects.get(
            attribute=self.attribute,
            normalized_value="230 v",
            language_code="fa",
        )
        self.assertEqual(known.usage_count, 1)

    def test_normalized_duplicate_reuses_catalog_value(self):
        ProductAttributeValue.objects.create(
            product=self.product,
            attribute=self.attribute,
            value_text="230 V",
        )
        ProductAttributeValue.objects.create(
            product=self.second_product,
            attribute=self.attribute,
            value_text="  230   v  ",
        )

        known_values = AttributeValue.objects.filter(
            attribute=self.attribute,
            normalized_value="230 v",
            language_code="fa",
        )
        self.assertEqual(known_values.count(), 1)
        self.assertEqual(known_values.get().usage_count, 2)

    def test_changing_value_updates_both_usage_counts(self):
        assignment = ProductAttributeValue.objects.create(
            product=self.product,
            attribute=self.attribute,
            value_text="230 V",
        )

        assignment.value_text = "400 V"
        assignment.save()

        old_value = AttributeValue.objects.get(
            attribute=self.attribute,
            normalized_value="230 v",
            language_code="fa",
        )
        new_value = AttributeValue.objects.get(
            attribute=self.attribute,
            normalized_value="400 v",
            language_code="fa",
        )

        self.assertEqual(old_value.usage_count, 0)
        self.assertEqual(new_value.usage_count, 1)
