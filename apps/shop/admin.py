from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, Coupon


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "total_items", "total")
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "product_name", "unit_price", "quantity"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "full_name", "phone", "total", "status", "is_paid", "created_at")
    list_filter = ("status", "is_paid")
    search_fields = ("order_number", "full_name", "phone")
    inlines = [OrderItemInline]
    readonly_fields = ["order_number", "subtotal", "discount_amount", "total"]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "discount_value", "used_count", "max_uses", "is_active")
    list_filter = ("is_active", "discount_type")
