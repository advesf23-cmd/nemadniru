import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel
from apps.products.models import Product


class Coupon(TimeStampedModel):
    DISCOUNT_PERCENT = "percent"
    DISCOUNT_FIXED = "fixed"
    DISCOUNT_TYPE_CHOICES = [(DISCOUNT_PERCENT, _("درصدی")), (DISCOUNT_FIXED, _("مبلغ ثابت"))]

    code = models.CharField(_("کد تخفیف"), max_length=30, unique=True)
    discount_type = models.CharField(_("نوع تخفیف"), max_length=10, choices=DISCOUNT_TYPE_CHOICES, default=DISCOUNT_PERCENT)
    discount_value = models.DecimalField(_("مقدار تخفیف"), max_digits=10, decimal_places=0)
    max_uses = models.PositiveIntegerField(_("حداکثر تعداد استفاده"), default=0, help_text=_("۰ = نامحدود"))
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField(_("معتبر از"), null=True, blank=True)
    valid_to = models.DateTimeField(_("معتبر تا"), null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("کد تخفیف")
        verbose_name_plural = _("کدهای تخفیف")

    def __str__(self):
        return self.code

    def is_valid(self):
        from django.utils import timezone
        if not self.is_active:
            return False
        now = timezone.now()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        return True

    def calculate_discount(self, subtotal):
        if self.discount_type == self.DISCOUNT_PERCENT:
            return subtotal * (self.discount_value / 100)
        return min(self.discount_value, subtotal)


class Cart(TimeStampedModel):
    """
    سبد خرید -- برای کاربر مهمان از session_key و برای کاربر واردشده از user استفاده می‌شود.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="carts"
    )
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = _("سبد خرید")
        verbose_name_plural = _("سبدهای خرید")

    def __str__(self):
        return f"سبد #{self.pk}"

    @property
    def subtotal(self):
        return sum((item.line_total for item in self.items.all()), 0)

    @property
    def discount_amount(self):
        if self.coupon and self.coupon.is_valid():
            return self.coupon.calculate_discount(self.subtotal)
        return 0

    @property
    def total(self):
        return max(self.subtotal - self.discount_amount, 0)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")
        verbose_name = _("آیتم سبد خرید")
        verbose_name_plural = _("آیتم‌های سبد خرید")

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"

    @property
    def unit_price(self):
        return self.product.final_price or 0

    @property
    def line_total(self):
        return self.unit_price * self.quantity


class Order(TimeStampedModel):
    STATUS_PENDING_PAYMENT = "pending_payment"
    STATUS_PROCESSING = "processing"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING_PAYMENT, _("در انتظار پرداخت")),
        (STATUS_PROCESSING, _("در حال پردازش")),
        (STATUS_SHIPPED, _("ارسال شده")),
        (STATUS_DELIVERED, _("تحویل داده شده")),
        (STATUS_CANCELLED, _("لغو شده")),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    full_name = models.CharField(_("نام و نام خانوادگی"), max_length=150)
    phone = models.CharField(_("شماره تماس"), max_length=20)
    email = models.EmailField(_("ایمیل"), blank=True)
    shipping_address = models.TextField(_("آدرس ارسال"))
    postal_code = models.CharField(_("کد پستی"), max_length=15, blank=True)
    notes = models.TextField(_("توضیحات سفارش"), blank=True)

    subtotal = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    discount_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING_PAYMENT)

    # فیلدهای آماده برای اتصال درگاه پرداخت واقعی (زرین‌پال/آی‌دی‌پی و ...)
    payment_gateway = models.CharField(max_length=50, blank=True)
    payment_ref_id = models.CharField(max_length=100, blank=True)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    # جلوگیری از ثبت سفارش تکراری در اثر دوبار کلیک/رفرش صفحه تسویه‌حساب
    checkout_token = models.CharField(max_length=64, unique=True, null=True, blank=True, editable=False)

    # مدیریت لغو سفارش
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.CharField(max_length=255, blank=True)
    stock_restored = models.BooleanField(default=False, editable=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("سفارش")
        verbose_name_plural = _("سفارشات")

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"STE-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def is_cancellable_by_customer(self):
        """مشتری فقط تا قبل از پرداخت/پردازش می‌تواند سفارش را خودش لغو کند"""
        return self.status == self.STATUS_PENDING_PAYMENT

    def cancel(self, reason="", restore_stock=True):
        """
        لغو سفارش -- در صورت نیاز موجودی انبار محصولات را برمی‌گرداند.
        idempotent است: اگر قبلاً موجودی برگردانده شده، دوباره برنمی‌گرداند.
        """
        from django.db.models import F as _F

        if self.status == self.STATUS_CANCELLED:
            return
        if restore_stock and not self.stock_restored:
            for item in self.items.select_related("product"):
                if item.product_id:
                    Product.objects.filter(pk=item.product_id).update(
                        stock_quantity=_F("stock_quantity") + item.quantity
                    )
            self.stock_restored = True
        self.status = self.STATUS_CANCELLED
        self.cancelled_at = timezone.now()
        if reason:
            self.cancel_reason = reason
        self.save(update_fields=["status", "cancelled_at", "cancel_reason", "stock_restored", "updated_at"])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)  # اسنپ‌شات در لحظه سفارش
    unit_price = models.DecimalField(max_digits=14, decimal_places=0)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = _("آیتم سفارش")
        verbose_name_plural = _("آیتم‌های سفارش")

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"
