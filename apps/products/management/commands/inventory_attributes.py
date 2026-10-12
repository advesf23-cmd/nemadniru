from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.models import Count

from apps.products.models import (
    Attribute, AttributeSet, CategoryAttributeTemplate, Product, ProductAttributeValue,
    ProductCategory, ProductSpecification, ProductVariant, VariantAttributeValue,
)


def _norm(text):
    return "".join((text or "").casefold().split())


def _pav_display(pav):
    if (pav.value_text or "").strip():
        return pav.value_text.strip()
    if pav.value_number is not None:
        number = format(Decimal(pav.value_number).normalize(), "f")
        return f"{number}{pav.attribute.unit or ''}"
    if pav.value_boolean is not None:
        return "بله" if pav.value_boolean else "خیر"
    if pav.value_date:
        return pav.value_date.isoformat()
    return ""


class Command(BaseCommand):
    """
    گزارش فقط‌خواندنی: وضعیت دو ساختار مشخصات (قدیمی: ProductSpecification /
    CategoryAttributeTemplate، جدید: Attribute / ProductAttributeValue) و میزان همپوشانی آن‌ها.
    هیچ داده‌ای تغییر نمی‌کند. خروجی مبنای تصمیم مهاجرت است.
    """
    help = "گزارش فقط‌خواندنی از همپوشانی ساختار قدیمی و جدید مشخصات محصول"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=30)

    def handle(self, *args, **options):
        limit = options["limit"]
        w = self.stdout.write

        w("گزارش فقط‌خواندنی -- ساختار قدیمی در برابر جدید مشخصات (هیچ تغییری اعمال نمی‌شود)\n")

        # ---------------- ۱) حجم داده ----------------
        total_products = Product.objects.count()
        with_spec = set(ProductSpecification.objects.values_list("product_id", flat=True).distinct())
        with_pav = set(ProductAttributeValue.objects.values_list("product_id", flat=True).distinct())
        w("[۱] حجم داده")
        w(f"  کل محصولات: {total_products}")
        w(f"  محصول دارای مشخصات قدیمی (ProductSpecification): {len(with_spec)}")
        w(f"  محصول دارای مشخصات جدید (ProductAttributeValue): {len(with_pav)}")
        w(f"  دارای هر دو: {len(with_spec & with_pav)}")
        w(f"  فقط قدیمی: {len(with_spec - with_pav)}   فقط جدید: {len(with_pav - with_spec)}")
        w(f"  بدون هیچ‌کدام: {total_products - len(with_spec | with_pav)}")
        w(f"  ردیف ProductSpecification: {ProductSpecification.objects.count()} "
          f"(کلید متفاوت: {ProductSpecification.objects.values('key').distinct().count()})")
        w(f"  ردیف ProductAttributeValue: {ProductAttributeValue.objects.count()}")
        w(f"  تنوع‌ها (ProductVariant): {ProductVariant.objects.count()}   "
          f"VariantAttributeValue: {VariantAttributeValue.objects.count()}")
        w(f"  ProductAttributeValue دارای variant: {ProductAttributeValue.objects.filter(variant__isnull=False).count()}\n")

        # ---------------- ۲) دسته‌بندی‌ها ----------------
        w("[۲] دسته‌بندی‌ها")
        w(f"  کل دسته‌بندی‌ها: {ProductCategory.objects.count()}")
        w(f"  دارای قالب مشخصات جدید (AttributeSet): {ProductCategory.objects.filter(attribute_set__isnull=False).count()}")
        old_cats = ProductCategory.objects.filter(attribute_templates__isnull=False).distinct()
        w(f"  دارای قالب قدیمی (CategoryAttributeTemplate): {old_cats.count()}")
        w(f"  قالب‌های قدیمی فیلترپذیر: {CategoryAttributeTemplate.objects.filter(is_filterable=True).count()}")
        w(f"  AttributeSet: {AttributeSet.objects.count()}   Attribute: {Attribute.objects.count()}\n")

        # ---------------- ۳) نگاشت نام‌ها ----------------
        attr_by_name = {_norm(a.name): a for a in Attribute.objects.all()}
        templates = CategoryAttributeTemplate.objects.select_related("category").all()
        unmapped_templates = [t for t in templates if _norm(t.name) not in attr_by_name]
        w("[۳] قالب‌های قدیمی که Attribute هم‌نام در ساختار جدید ندارند "
          f"({len(unmapped_templates)} از {templates.count()})")
        for t in unmapped_templates[:limit]:
            w(f"  دسته «{t.category.name}» -- «{t.name}» (واحد: {t.unit or '-'}, فیلتر: {t.get_filter_type_display()})")

        spec_keys = (ProductSpecification.objects.values("key").annotate(n=Count("id")).order_by("-n"))
        unmapped_keys = [r for r in spec_keys if _norm(r["key"]) not in attr_by_name]
        w(f"\n[۴] کلیدهای ProductSpecification بدون Attribute هم‌نام ({len(unmapped_keys)} از {spec_keys.count()})")
        for r in unmapped_keys[:limit]:
            w(f"  «{r['key']}» -- {r['n']} ردیف")

        # ---------------- ۵) تناقض مقدار ----------------
        pav_map = {}
        for pav in ProductAttributeValue.objects.select_related("attribute").filter(variant__isnull=True):
            pav_map[(pav.product_id, _norm(pav.attribute.name))] = pav
        both = conflicts = 0
        conflict_rows = []
        for spec in ProductSpecification.objects.select_related("product").iterator():
            pav = pav_map.get((spec.product_id, _norm(spec.key)))
            if not pav:
                continue
            both += 1
            if _norm(spec.value) != _norm(_pav_display(pav)):
                conflicts += 1
                conflict_rows.append((spec.product.name, spec.key, spec.value, _pav_display(pav)))
        w(f"\n[۵] مقدار یک مشخصه هم در قدیمی و هم در جدید ثبت شده: {both} مورد")
        w(f"    با مقدار متفاوت (تقریبی؛ بی‌توجه به فاصله و حروف): {conflicts}")
        for name, key, old, new in conflict_rows[:limit]:
            w(f"  {name} | {key}: قدیمی=«{old}» جدید=«{new}»")

        w("\nپایان گزارش.")
