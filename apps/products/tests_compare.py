from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import (
    Attribute, AttributeValue, Product, ProductAttributeValue, ProductCategory,
    ProductSpecification, ProductVariant,
)


def make_product(category, name):
    return Product.objects.create(category=category, name=name, description="", status="published", cover_image="")


class CompareMergedSpecsTests(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(name="MCCB")
        self.a = make_product(self.category, "A")
        self.b = make_product(self.category, "B")
        ProductSpecification.objects.create(product=self.a, key="جریان نامی", value="100A")
        ProductSpecification.objects.create(product=self.b, key="جریان نامی", value="250A")
        ProductSpecification.objects.create(product=self.a, key="قدرت قطع", value="25kA")

        self.current = Attribute.objects.create(name="جریان نامی", code="rated-current", data_type=Attribute.NUMBER, unit="A")
        self.voltage = Attribute.objects.create(name="ولتاژ", code="voltage", data_type=Attribute.TEXT)
        self.hidden = Attribute.objects.create(name="داخلی", code="internal", data_type=Attribute.TEXT, is_comparable=False)
        # ساختار جدید برای محصول A: هم‌نام با مشخصه‌ی قدیمی (باید اولویت بگیرد) + یک مشخصه‌ی فقط‌جدید
        ProductAttributeValue.objects.create(product=self.a, attribute=self.current, value_number=120)
        ProductAttributeValue.objects.create(product=self.a, attribute=self.voltage, value_text="230 V")
        ProductAttributeValue.objects.create(product=self.a, attribute=self.hidden, value_text="x")

        for p in (self.a, self.b):
            self.client.post(reverse("products:compare_toggle", kwargs={"pk": p.pk}))

    def rows(self):
        response = self.client.get(reverse("products:compare"))
        self.assertEqual(response.status_code, 200)
        return {r["key"]: r["values"] for r in response.context["comparison_rows"]}

    def test_new_structure_has_priority_over_old(self):
        rows = self.rows()
        self.assertEqual(rows["جریان نامی"][0], "120 A")
        self.assertEqual(rows["جریان نامی"][1], "250A")

    def test_old_only_and_new_only_specs_are_both_shown(self):
        rows = self.rows()
        self.assertEqual(rows["قدرت قطع"], ["25kA", ""])
        self.assertEqual(rows["ولتاژ"], ["230 V", ""])

    def test_non_comparable_attribute_is_hidden(self):
        self.assertNotIn("داخلی", self.rows())

    def test_selected_values_are_displayed(self):
        color = Attribute.objects.create(name="رنگ", code="color", data_type=Attribute.MULTISELECT)
        pav = ProductAttributeValue.objects.create(product=self.b, attribute=color)
        pav.selected_values.add(AttributeValue.objects.create(attribute=color, value="قرمز"))
        self.assertEqual(self.rows()["رنگ"], ["", "قرمز"])


class VariantRuleTests(TestCase):
    def test_variant_specific_values_must_not_use_general_model(self):
        category = ProductCategory.objects.create(name="C")
        product = make_product(category, "P")
        variant = ProductVariant.objects.create(product=product, name="v", sku="S-1")
        attr = Attribute.objects.create(name="رنگ", code="color2", data_type=Attribute.TEXT)
        pav = ProductAttributeValue(product=product, attribute=attr, value_text="x", variant=variant)
        with self.assertRaises(ValidationError):
            pav.full_clean()
