from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel, SEOModel, SlugModel, PublishableModel


class Brand(TimeStampedModel, SlugModel):
    """
    برند/سازنده -- طبق پیشنهاد سند Product Master، برند دیگر یک متن آزاد روی
    خود محصول نیست، بلکه یک بانک مرکزی مستقل است (Schneider, ABB, Siemens, ...)
    که محصولات به آن متصل می‌شوند. تخفیف پیش‌فرض برند هم این‌جا تعریف می‌شود؛
    اگر محصول خاصی تخفیف اختصاصی داشته باشد، تخفیف آن محصول اولویت دارد
    (به Product.discount_percent_override نگاه کنید).
    """
    name = models.CharField(_("نام برند"), max_length=100, unique=True)
    logo = models.ImageField(_("لوگو"), upload_to="brands/", blank=True, null=True)
    default_discount_percent = models.DecimalField(
        _("درصد تخفیف پیش‌فرض برند"), max_digits=5, decimal_places=2, default=0,
        help_text=_("مثلاً ۳۵ یعنی ۳۵٪ -- روی همه‌ی محصولات این برند اعمال می‌شود مگر محصولی تخفیف اختصاصی داشته باشد")
    )
    is_active = models.BooleanField(_("فعال"), default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("برند")
        verbose_name_plural = _("برندها")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug("name")
        super().save(*args, **kwargs)


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


class CategoryAttributeTemplate(models.Model):
    """
    قالب مشخصات فنی هر دسته‌بندی -- طبق پیشنهاد سند: «برای هر دسته، فیلدهای
    مخصوص خودش». این مدل فقط تعریف می‌کند که مثلاً دسته‌ی MCCB باید چه
    مشخصه‌هایی داشته باشد (تعداد پل، جریان نامی، قدرت قطع، ...)؛ مقدار واقعی
    هر مشخصه برای هر محصول همچنان در مدل موجود ProductSpecification
    (کلید/مقدار) ذخیره می‌شود -- یعنی این مدل یک «راهنما» برای پر کردن
    مشخصات فنی هر محصول است، نه ساختار داده‌ی جدید و جدا.

    کاربرد عملی: وقتی محصولی در دسته‌ی MCCB ثبت می‌کنید، از همین لیست
    (در پنل ادمین، کنار فیلد دسته‌بندی) می‌بینید که باید چه کلیدهایی
    (Poles, Rated Current, Breaking Capacity, ...) را به‌عنوان
    ProductSpecification برای آن محصول وارد کنید.
    """
    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, related_name="attribute_templates",
        verbose_name=_("دسته‌بندی")
    )
    name = models.CharField(_("نام مشخصه (مثلاً: جریان نامی)"), max_length=100)
    unit = models.CharField(_("واحد (مثلاً: A، kA، V)"), max_length=30, blank=True)
    order = models.PositiveIntegerField(_("ترتیب"), default=0)

    FILTER_TYPE_NONE = "none"
    FILTER_TYPE_SELECT = "select"
    FILTER_TYPE_MULTISELECT = "multiselect"
    FILTER_TYPE_RANGE = "range"
    FILTER_TYPE_BOOLEAN = "boolean"
    FILTER_TYPE_CHOICES = (
        (FILTER_TYPE_NONE, _("فیلتر نشود")),
        (FILTER_TYPE_SELECT, _("انتخاب یک مقدار")),
        (FILTER_TYPE_MULTISELECT, _("انتخاب چند مقدار")),
        (FILTER_TYPE_RANGE, _("بازه عددی")),
        (FILTER_TYPE_BOOLEAN, _("بله / خیر")),
    )
    filter_type = models.CharField(
        _("نوع فیلتر"), max_length=20, choices=FILTER_TYPE_CHOICES,
        default=FILTER_TYPE_NONE,
        help_text=_("مشخص می‌کند این مشخصه در جستجوی پیشرفته چگونه نمایش داده شود."),
    )
    is_filterable = models.BooleanField(
        _("نمایش در فیلتر"), default=False,
        help_text=_("اگر فعال باشد، این مشخصه در فیلتر محصولات همان دسته نمایش داده می‌شود."),
    )
    filter_choices = models.TextField(
        _("گزینه‌های فیلتر"), blank=True,
        help_text=_("برای فیلترهای انتخابی، هر مقدار را در یک خط بنویسید. می‌توانید «مقدار | عنوان» هم وارد کنید."),
    )
    filter_min = models.DecimalField(
        _("حداقل بازه"), max_digits=14, decimal_places=4, null=True, blank=True,
    )
    filter_max = models.DecimalField(
        _("حداکثر بازه"), max_digits=14, decimal_places=4, null=True, blank=True,
    )
    filter_step = models.DecimalField(
        _("گام بازه"), max_digits=14, decimal_places=4, null=True, blank=True,
    )

    class Meta:
        ordering = ["category", "order"]
        verbose_name = _("قالب مشخصه فنی دسته‌بندی")
        verbose_name_plural = _("قالب‌های مشخصات فنی دسته‌بندی‌ها")

    def __str__(self):
        return f"{self.category.name} -- {self.name}"


class Product(TimeStampedModel, SlugModel, SEOModel, PublishableModel):
    category = models.ForeignKey(
        ProductCategory, on_delete=models.PROTECT, related_name="products", verbose_name=_("دسته‌بندی")
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="products",
        verbose_name=_("برند / سازنده")
    )
    name = models.CharField(_("نام محصول"), max_length=200)
    short_description = models.CharField(_("توضیح کوتاه"), max_length=300, blank=True)
    description = models.TextField(_("توضیحات کامل"))

    # طبق پیشنهاد سند: «توضیحات فنی» جدا از توضیحات کامل بازاریابی/فروش نگه
    # داشته می‌شود -- همان متن آزاد قبلی (مثلاً "3P / In: 160A / Icu: 25kA")
    # در کنار مشخصات ساختاریافته (ProductSpecification) باقی می‌ماند.
    technical_description = models.TextField(_("توضیحات فنی (متن آزاد)"), blank=True)

    cover_image = models.ImageField(_("تصویر شاخص"), upload_to="products/covers/")

    # --- شناسه‌های محصول: SKU (کد داخلی فروشگاه) و MPN (کد سازنده) حالا
    # کاملاً مستقل از هم هستند، طبق تأکید اصلی سند ---
    sku = models.CharField(_("کد محصول داخلی (SKU)"), max_length=50, blank=True, unique=True, null=True)
    mpn = models.CharField(
        _("کد سازنده (MPN)"), max_length=100, blank=True, db_index=True,
        help_text=_("کدی که خودِ سازنده/برند به این محصول داده (مثلاً روی کاتالوگ یا PDF قیمت)")
    )

    # --- فیلدهای فروشگاه ---
    price = models.DecimalField(_("قیمت (تومان)"), max_digits=14, decimal_places=0, null=True, blank=True)
    discount_price = models.DecimalField(_("قیمت با تخفیف"), max_digits=14, decimal_places=0, null=True, blank=True)

    # طبق پیشنهاد سند: تخفیف اختصاصی محصول (اگر مقدار داشته باشد) روی تخفیف
    # پیش‌فرض برند اولویت دارد. این فیلد صرفاً یک لایه‌ی کمکی/اطلاعاتی کنار
    # discount_price فعلی است، نه جایگزین کامل آن -- برای جایگزینی کامل با
    # موتور قیمت‌گذاری مستقل، به یادداشت انتهای این فایل مراجعه کنید.
    discount_percent_override = models.DecimalField(
        _("درصد تخفیف اختصاصی این محصول (اختیاری)"), max_digits=5, decimal_places=2,
        null=True, blank=True,
        help_text=_("اگر پر شود، به‌جای تخفیف پیش‌فرض برند برای همین محصول استفاده می‌شود")
    )

    stock_quantity = models.PositiveIntegerField(_("موجودی انبار"), default=0)
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
    def effective_discount_percent(self):
        """
        طبق قانون سند: تخفیف اختصاصی محصول (در صورت تعریف) اولویت دارد؛
        در غیر این صورت تخفیف پیش‌فرض برند اعمال می‌شود.
        """
        if self.discount_percent_override is not None:
            return self.discount_percent_override
        if self.brand_id and self.brand.default_discount_percent:
            return self.brand.default_discount_percent
        return 0

    @property
    def final_price(self):
        # قیمت صریح discount_price (اگر دستی وارد شده) همچنان اولویت اول است
        # تا رفتار فعلی سایت (که همه‌جا از همین property استفاده می‌کند)
        # تغییر نکند؛ اگر discount_price خالی باشد ولی تخفیف درصدی (برند/
        # محصول) تعریف شده باشد، از همان برای محاسبه استفاده می‌شود.
        if self.discount_price:
            return self.discount_price
        if self.price and self.effective_discount_percent:
            from decimal import Decimal
            factor = (Decimal("100") - Decimal(self.effective_discount_percent)) / Decimal("100")
            return (self.price * factor).quantize(Decimal("1"))
        return self.price

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
    """
    مشخصات فنی ساختاریافته به‌صورت کلید/مقدار (Poles=3, Rated Current=160A, ...).
    این همان مدلی است که سند Product Master به‌عنوان «Structured Attributes»
    پیشنهاد داده بود؛ قبلاً هم وجود داشت و کاملاً منطبق بود، فقط الان با
    CategoryAttributeTemplate یک «راهنمای» تکمیل هم دارد.
    """
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
