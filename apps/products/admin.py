from django.contrib import admin
from django.db.models import Case, When
from .models import (
    ProductCategory, Product, ProductImage, ProductSpecification, ProductDownload, ProductInquiry, ProductReview
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


class ProductDownloadInline(admin.TabularInline):
    model = ProductDownload
    extra = 1


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    """
    نمایش دسته‌بندی‌ها به‌صورت درختی: هر زیرمجموعه دقیقاً زیر والدش (با تورفتگی)
    نمایش داده می‌شود، نه در یک لیست تخت و پراکنده.
    """
    list_display = ("indented_name", "parent", "is_active", "order")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("parent")
        ordered_ids = self._tree_ordered_ids(qs)
        if not ordered_ids:
            return qs
        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ordered_ids)])
        return qs.filter(pk__in=ordered_ids).order_by(preserved_order)

    @staticmethod
    def _tree_ordered_ids(qs):
        """آی‌دی‌ها را به ترتیب درختی (والد، سپس بلافاصله فرزندانش، سپس نوه‌ها و ...) برمی‌گرداند."""
        items = list(qs)
        by_parent = {}
        for item in items:
            by_parent.setdefault(item.parent_id, []).append(item)
        for children in by_parent.values():
            children.sort(key=lambda c: (c.order, c.name))

        ordered_ids = []

        def walk(parent_id):
            for child in by_parent.get(parent_id, []):
                ordered_ids.append(child.pk)
                walk(child.pk)

        walk(None)
        return ordered_ids

    def indented_name(self, obj):
        depth = 0
        p = obj.parent
        while p is not None:
            depth += 1
            p = p.parent
        prefix = "— " * depth
        return f"{prefix}{obj.name}"
    indented_name.short_description = "نام دسته‌بندی"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """در فرم افزودن/ویرایش، فیلد «دسته‌بندی والد» را هم به‌صورت تورفته (درختی) نمایش می‌دهد."""
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "parent":
            all_categories = list(ProductCategory.objects.all())
            ordered_ids = self._tree_ordered_ids(ProductCategory.objects.all())
            by_id = {c.pk: c for c in all_categories}
            choices = [("", "---------")]
            for pk in ordered_ids:
                obj = by_id[pk]
                depth = 0
                p = obj.parent
                while p is not None:
                    depth += 1
                    p = p.parent
                choices.append((obj.pk, f"{'— ' * depth}{obj.name}"))
            field.choices = choices
        return field



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "status", "is_featured", "stock_quantity", "created_at")
    list_filter = ("category", "status", "is_featured", "brand")
    list_editable = ("is_featured",)
    search_fields = ("name", "sku", "brand")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, ProductSpecificationInline, ProductDownloadInline]


@admin.register(ProductInquiry)
class ProductInquiryAdmin(admin.ModelAdmin):
    list_display = ("full_name", "product", "phone", "is_read", "created_at")
    list_filter = ("is_read",)
    readonly_fields = [f.name for f in ProductInquiry._meta.fields]


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("full_name", "product", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "rating")
    search_fields = ("full_name", "comment")
    actions = ["approve_reviews"]

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "تأیید نظرات انتخاب‌شده"
