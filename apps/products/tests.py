from django.test import TestCase
from django.urls import reverse

from .models import (
    CategoryAttributeTemplate,
    Product,
    ProductCategory,
    ProductSpecification,
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
