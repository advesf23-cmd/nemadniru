from django.contrib import admin
from django.db.models import Case, When
from .models import (
    ProductCategory, Brand, CategoryAttributeTemplate, Product,
    ProductImage, ProductSpecification, ProductDownload, ProductInquiry, ProductReview,
    Attribute, AttributeGroup, AttributeSet, AttributeSetAttribute, AttributeValue,
    ProductAttributeValue, ProductVariant, VariantAttributeValue
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1
    autocomplete_fields = ("attribute",)
    fields = ("attribute", "value_text", "value_number", "value_boolean", "value_date", "value_file", "variant")


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0


class ProductDownloadInline(admin.TabularInline):
    model = ProductDownload
    extra = 1


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    """نمایش دسته‌بندی‌ها به‌صورت درختی: هر زیرمجموعه دقیقاً زیر والدش (با تورفتگی) نمایش داده می‌شود."""
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
        return f"{'— ' * depth}{obj.name}"
    indented_name.short_description = "نام دسته‌بندی"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
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


class CategoryAttributeTemplateInline(admin.TabularInline):
    """امکان تعریف قالب مشخصات فنی هر دسته، مستقیم از همان صفحه‌ی دسته‌بندی"""
    model = CategoryAttributeTemplate
    extra = 1


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "default_discount_percent", "is_active")
    list_editable = ("default_discount_percent", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(CategoryAttributeTemplate)
class CategoryAttributeTemplateAdmin(admin.ModelAdmin):
    list_display = ("category", "name", "unit", "filter_type", "is_filterable", "order")
    list_filter = ("category", "filter_type", "is_filterable")
    list_editable = ("filter_type", "is_filterable", "order")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "sku", "mpn", "status", "is_featured", "stock_quantity", "created_at")
    list_filter = ("category", "brand", "status", "is_featured")
    list_editable = ("is_featured",)
    search_fields = ("name", "sku", "mpn", "brand__name")
    autocomplete_fields = ["brand"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, ProductSpecificationInline, ProductAttributeValueInline, ProductVariantInline, ProductDownloadInline]
    fieldsets = (
        (None, {"fields": ("category", "brand", "name", "slug", "status", "is_featured", "order")}),
        ("شناسه‌های محصول", {"fields": ("sku", "mpn")}),
        ("توضیحات", {"fields": ("short_description", "description", "technical_description")}),
        ("تصویر", {"fields": ("cover_image",)}),
        ("قیمت و موجودی", {"fields": ("price", "discount_price", "discount_percent_override", "stock_quantity", "is_orderable")}),
        ("سئو", {"fields": ("meta_title", "meta_description", "og_image", "canonical_url"), "classes": ("collapse",)}),
    )


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


@admin.register(AttributeGroup)
class AttributeGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    search_fields = ("name",)
    list_editable = ("order",)


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "data_type", "group", "is_required", "is_filterable", "is_active")
    list_filter = ("data_type", "group", "is_required", "is_filterable", "is_active")
    search_fields = ("name", "code")
    prepopulated_fields = {"code": ("name",)}


class AttributeSetAttributeInline(admin.TabularInline):
    model = AttributeSetAttribute
    extra = 1
    autocomplete_fields = ("attribute",)


@admin.register(AttributeSet)
class AttributeSetAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "updated_at")
    search_fields = ("name",)
    list_filter = ("is_active",)
    inlines = [AttributeSetAttributeInline]


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ("attribute", "value", "language_code", "usage_count")
    list_filter = ("attribute", "language_code")
    search_fields = ("value", "normalized_value", "attribute__name")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "sku", "price", "stock_quantity", "is_active")
    list_filter = ("is_active",)
    search_fields = ("product__name", "name", "sku")


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("product", "attribute", "value_text", "value_number", "variant")
    list_filter = ("attribute",)
    search_fields = ("product__name", "attribute__name", "value_text")


@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("variant", "attribute", "value_text", "value_number")
    list_filter = ("attribute",)
    search_fields = ("variant__name", "attribute__name", "value_text")
