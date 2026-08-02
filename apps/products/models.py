from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel, SEOModel, SlugModel, PublishableModel


class ProductCategory(TimeStampedModel, SlugModel, SEOModel):
    name = models.CharField(_("نام دسته‌بندی"), max_length=150)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children",
        verbose_name=_("دسته‌بندی والد"),
    )
    icon = models.CharField(_("آیکون"), max_length=50, blank=True)
    image = models.ImageField(_("تصویر"), upload_to="products/categories/", blank=True, null=True)
    description = models.TextField(_("توضیحات"), blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("دسته‌بندی محصول")
        verbose_name_plural = _("دسته‌بندی‌های محصولات")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug("name")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:category_detail", kwargs={"slug": self.slug})


class Product(TimeStampedModel, SlugModel, SEOModel, PublishableModel):
    category = models.ForeignKey(
        ProductCategory, on_delete=models.PROTECT, related_name="products", verbose_name=_("دسته‌بندی")
    )
    name = models.CharField(_("نام محصول"), max_length=200)
    short_description = models.CharField(_("توضیح کوتاه"), max_length=300, blank=True)
    description = models.TextField(_("توضیحات کامل"))
    cover_image = models.ImageField(_("تصویر شاخص"), upload_to="products/covers/")
    brand = models.CharField(_("برند / سازنده"), max_length=100, blank=True)

    # --- فیلدهای آماده برای فروشگاه آینده (بدون نیاز به تغییر ساختاری بزرگ) ---
    price = models.DecimalField(_("قیمت (تومان)"), max_digits=14, decimal_places=0, null=True, blank=True)
    discount_price = models.DecimalField(_("قیمت با تخفیف"), max_digits=14, decimal_places=0, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(_("موجودی انبار"), default=0)
    sku = models.CharField(_("کد محصول (SKU)"), max_length=50, blank=True, unique=True, null=True)
    is_orderable = models.BooleanField(_("قابل سفارش آنلاین"), default=False, help_text=_("برای فاز فروشگاه"))

    class Meta:
        ordering = ["-is_featured", "order", "-created_at"]
        verbose_name = _("محصول")
        verbose_name_plural = _("محصولات")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug("name")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:product_detail", kwargs={"slug": self.slug})

    @property
    def final_price(self):
        return self.discount_price or self.price

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

    @property
    def average_rating(self):
        result = self.reviews.filter(is_approved=True).aggregate(avg=models.Avg("rating"))
        return round(result["avg"], 1) if result["avg"] else 0

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images", verbose_name=_("محصول"))
    image = models.ImageField(_("تصویر"), upload_to="products/gallery/")
    alt_text = models.CharField(_("متن جایگزین (Alt)"), max_length=150, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("تصویر محصول")
        verbose_name_plural = _("گالری تصاویر محصول")

    def __str__(self):
        return f"{self.product.name} - {self.order}"


class ProductSpecification(models.Model):
    """مشخصات فنی به‌صورت کلید/مقدار قابل مدیریت از ادمین (مثل: ولتاژ، جریان، استاندارد)"""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="specifications", verbose_name=_("محصول")
    )
    key = models.CharField(_("عنوان مشخصه"), max_length=100)
    value = models.CharField(_("مقدار"), max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("مشخصه فنی")
        verbose_name_plural = _("مشخصات فنی")

    def __str__(self):
        return f"{self.key}: {self.value}"


class ProductDownload(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="downloads", verbose_name=_("محصول"))
    title = models.CharField(_("عنوان فایل"), max_length=150)
    file = models.FileField(_("فایل"), upload_to="products/downloads/")

    class Meta:
        verbose_name = _("فایل دانلودی محصول")
        verbose_name_plural = _("فایل‌های دانلودی محصول")

    def __str__(self):
        return self.title


class ProductReview(TimeStampedModel):
    """نظر و امتیاز مشتری روی محصول -- نیازمند تأیید مدیر قبل از نمایش عمومی"""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", verbose_name=_("محصول"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="product_reviews"
    )
    full_name = models.CharField(_("نام"), max_length=100)
    rating = models.PositiveSmallIntegerField(_("امتیاز"), choices=RATING_CHOICES, default=5)
    comment = models.TextField(_("متن نظر"))
    is_approved = models.BooleanField(_("تأیید شده"), default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("نظر محصول")
        verbose_name_plural = _("نظرات محصولات")

    def __str__(self):
        return f"{self.full_name} - {self.product.name} ({self.rating}★)"


class ProductInquiry(TimeStampedModel):
    """فرم استعلام قیمت / درخواست محصول"""
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="inquiries"
    )
    full_name = models.CharField(_("نام و نام خانوادگی"), max_length=150)
    company_name = models.CharField(_("نام شرکت"), max_length=150, blank=True)
    phone = models.CharField(_("شماره تماس"), max_length=20)
    email = models.EmailField(_("ایمیل"), blank=True)
    quantity = models.PositiveIntegerField(_("تعداد مورد نیاز"), default=1)
    message = models.TextField(_("توضیحات"), blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("استعلام قیمت محصول")
        verbose_name_plural = _("استعلام‌های قیمت")

    def __str__(self):
        return f"{self.full_name} - {self.product}"
