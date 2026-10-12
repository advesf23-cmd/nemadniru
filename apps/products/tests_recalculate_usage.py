from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from .models import Attribute, AttributeValue, Product, ProductAttributeValue, ProductCategory


class RecalculateUsageCommandTests(TestCase):
    def setUp(self):
        category = ProductCategory.objects.create(name="C")
        self.p1 = Product.objects.create(category=category, name="P1", description="", status="published", cover_image="")
        self.p2 = Product.objects.create(category=category, name="P2", description="", status="published", cover_image="")
        self.attr = Attribute.objects.create(name="ولتاژ", code="voltage", data_type=Attribute.TEXT)
        ProductAttributeValue.objects.create(product=self.p1, attribute=self.attr, value_text="230 V")
        ProductAttributeValue.objects.create(product=self.p2, attribute=self.attr, value_text="230 V")
        self.av = AttributeValue.objects.get(attribute=self.attr, normalized_value="230 v")

    def run_cmd(self, *args):
        out = StringIO()
        call_command("recalculate_attribute_usage", *args, stdout=out)
        return out.getvalue()

    def test_consistent_data_reports_ok(self):
        self.assertIn("هم‌خوانند", self.run_cmd())

    def test_default_mode_does_not_modify(self):
        AttributeValue.objects.filter(pk=self.av.pk).update(usage_count=9)
        self.run_cmd()
        self.av.refresh_from_db()
        self.assertEqual(self.av.usage_count, 9)

    def test_apply_fixes_wrong_counter(self):
        AttributeValue.objects.filter(pk=self.av.pk).update(usage_count=9)
        self.run_cmd("--apply")
        self.av.refresh_from_db()
        self.assertEqual(self.av.usage_count, 2)

    def test_apply_zeroes_unused_row(self):
        stale = AttributeValue.objects.create(attribute=self.attr, value="400 V", usage_count=5)
        self.run_cmd("--apply")
        stale.refresh_from_db()
        self.assertEqual(stale.usage_count, 0)

    def test_missing_row_created_only_with_flag(self):
        AttributeValue.objects.filter(pk=self.av.pk).delete()
        self.run_cmd("--apply")
        self.assertFalse(AttributeValue.objects.filter(attribute=self.attr).exists())
        self.run_cmd("--apply", "--create-missing")
        self.assertEqual(AttributeValue.objects.get(attribute=self.attr).usage_count, 2)
