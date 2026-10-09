from django.core.management.base import BaseCommand
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Lower, Trim

from apps.products.models import (
    Attribute, AttributeSetAttribute, AttributeValue, Brand,
    CategoryAttributeTemplate, Product, ProductAttributeValue,
    ProductCategory, ProductSpecification, ProductVariant, VariantAttributeValue,
)
from apps.shop.models import Cart, CartItem, Coupon, Order, OrderItem


class Command(BaseCommand):
    """Read-only integrity audit; it never changes database records."""

    help = "Audit common database duplicates and integrity risks without modifying data."

    def handle(self, *args, **options):
        self.issues = 0
        self.stdout.write("Database integrity audit (read-only)")
        self.stdout.write("No records will be inserted, updated, or deleted.\n")

        self.duplicates(ProductAttributeValue.objects, ["product_id", "attribute_id"],
                        "Product attribute repeated on one product")
        self.duplicates(VariantAttributeValue.objects, ["variant_id", "attribute_id"],
                        "Variant attribute repeated on one variant")
        self.duplicates(
            ProductSpecification.objects.annotate(normalized_key=Lower(Trim("key"))),
            ["product_id", "normalized_key"],
            "Product specification key repeated (ignoring case/outer spaces)",
        )
        self.duplicates(
            CategoryAttributeTemplate.objects.annotate(normalized_name=Lower(Trim("name"))),
            ["category_id", "normalized_name"],
            "Category template name repeated within a category",
        )
        self.duplicates(AttributeSetAttribute.objects, ["attribute_set_id", "attribute_id"],
                        "Attribute repeated in one attribute set")
        self.duplicates(
            AttributeValue.objects.annotate(normalized_value_check=Lower(Trim("value"))),
            ["attribute_id", "normalized_value_check", "language_code"],
            "Known attribute value repeated (ignoring case/outer spaces)",
        )
        self.duplicates(CartItem.objects, ["cart_id", "product_id"],
                        "Same product repeated in one cart")
        self.duplicates(Cart.objects.filter(user__isnull=False), ["user_id"],
                        "Multiple carts for one signed-in user")
        self.duplicates(
            Cart.objects.filter(session_key__isnull=False).exclude(session_key=""),
            ["session_key"], "Multiple guest carts for one session",
        )
        self.duplicates(
            Product.objects.exclude(sku__isnull=True).exclude(sku=""),
            ["sku"], "Duplicate non-empty product SKU",
        )
        self.duplicates(ProductVariant.objects, ["sku"], "Duplicate variant SKU")

        blank_skus = Product.objects.filter(sku="").count()
        if blank_skus > 1:
            self.issue(
                f"{blank_skus} products store SKU as an empty string; a unique SKU field "
                "can reject additional blank values. Consider normalizing blanks to NULL."
            )
        else:
            self.ok("No multiple empty-string product SKUs")

        self.rows(
            "Product attribute linked to a variant belonging to another product",
            ProductAttributeValue.objects.filter(variant__isnull=False)
            .exclude(product_id=F("variant__product_id")),
            ["id", "product_id", "attribute_id", "variant_id"],
        )
        self.rows("Negative product price", Product.objects.filter(price__lt=0),
                  ["id", "name", "price"])
        self.rows("Negative product discount price", Product.objects.filter(discount_price__lt=0),
                  ["id", "name", "discount_price"])
        self.rows(
            "Discount price exceeds regular price",
            Product.objects.filter(price__isnull=False, discount_price__isnull=False)
            .filter(discount_price__gt=F("price")),
            ["id", "name", "price", "discount_price"],
        )
        self.rows(
            "Product discount percentage outside 0..100",
            Product.objects.filter(discount_percent_override__isnull=False)
            .filter(Q(discount_percent_override__lt=0) | Q(discount_percent_override__gt=100)),
            ["id", "name", "discount_percent_override"],
        )
        self.rows(
            "Brand discount percentage outside 0..100",
            Brand.objects.filter(Q(default_discount_percent__lt=0) | Q(default_discount_percent__gt=100)),
            ["id", "name", "default_discount_percent"],
        )
        self.rows(
            "Coupon percentage outside 0..100",
            Coupon.objects.filter(discount_type=Coupon.DISCOUNT_PERCENT)
            .filter(Q(discount_value__lt=0) | Q(discount_value__gt=100)),
            ["id", "code", "discount_value"],
        )
        self.rows(
            "Negative fixed coupon discount",
            Coupon.objects.filter(discount_type=Coupon.DISCOUNT_FIXED, discount_value__lt=0),
            ["id", "code", "discount_value"],
        )
        self.rows(
            "Coupon valid_from later than valid_to",
            Coupon.objects.filter(
                valid_from__isnull=False, valid_to__isnull=False, valid_from__gt=F("valid_to")
            ),
            ["id", "code", "valid_from", "valid_to"],
        )
        self.rows(
            "Attribute minimum exceeds maximum",
            Attribute.objects.filter(
                min_value__isnull=False, max_value__isnull=False, min_value__gt=F("max_value")
            ),
            ["id", "name", "min_value", "max_value"],
        )
        self.rows("Cart item quantity <= 0", CartItem.objects.filter(quantity__lte=0),
                  ["id", "cart_id", "product_id", "quantity"])
        self.rows("Order item quantity <= 0", OrderItem.objects.filter(quantity__lte=0),
                  ["id", "order_id", "product_id", "quantity"])

        # Detect category cycles, which can break recursive category navigation.
        parent_by_id = dict(ProductCategory.objects.values_list("id", "parent_id"))
        cycles, reported = [], set()
        for start_id in parent_by_id:
            path, positions, current_id = [], {}, start_id
            while current_id is not None and current_id in parent_by_id:
                if current_id in positions:
                    cycle = tuple(path[positions[current_id]:])
                    key = tuple(sorted(cycle))
                    if key not in reported:
                        reported.add(key)
                        cycles.append(cycle)
                    break
                positions[current_id] = len(path)
                path.append(current_id)
                current_id = parent_by_id[current_id]
        if cycles:
            for cycle in cycles:
                self.issue(f"Product category parent cycle: {cycle}")
        else:
            self.ok("No product-category parent cycles")

        # Order totals are snapshots and should match saved order-line snapshots.
        for order in Order.objects.all().iterator():
            line_total = (
                OrderItem.objects.filter(order_id=order.pk)
                .aggregate(total=Sum(F("unit_price") * F("quantity")))["total"] or 0
            )
            if order.subtotal != line_total:
                self.issue(
                    f"Order {order.order_number}: stored subtotal={order.subtotal}, "
                    f"order-line total={line_total}"
                )

        if self.issues:
            self.stdout.write("")
            self.stdout.write(self.style.ERROR(
                f"Audit finished: {self.issues} issue(s) found. No data was changed."
            ))
        else:
            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS(
                "Audit finished: no issues found by the checks included in this command."
            ))

    def ok(self, message):
        self.stdout.write(self.style.SUCCESS(f"[OK] {message}"))

    def issue(self, message):
        self.issues += 1
        self.stdout.write(self.style.ERROR(f"[ISSUE] {message}"))

    def duplicates(self, queryset, fields, label, limit=20):
        groups = (
            queryset.order_by().values(*fields).annotate(total=Count("pk"))
            .filter(total__gt=1).order_by("-total")
        )
        count = groups.count()
        if not count:
            self.ok(f"No duplicates: {label}")
            return
        self.issue(f"{label}: {count} duplicate group(s)")
        for group in groups[:limit]:
            keys = ", ".join(f"{field}={group.get(field)!r}" for field in fields)
            self.stdout.write(f"       {keys}; total={group['total']}")
        if count > limit:
            self.stdout.write(f"       (only first {limit} groups shown)")

    def rows(self, label, queryset, fields, limit=20):
        sample = list(queryset.values(*fields)[:limit])
        if not sample:
            self.ok(label)
            return
        count = queryset.count()
        self.issue(f"{label}: {count} row(s)")
        for row in sample:
            self.stdout.write("       " + ", ".join(f"{key}={value!r}" for key, value in row.items()))
        if count > limit:
            self.stdout.write(f"       (only first {limit} rows shown)")
