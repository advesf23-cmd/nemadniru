from django.contrib import admin
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
    list_display = ("name", "parent", "is_active", "order")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


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
