from django.conf import settings
from django.core.exceptions import ValidationError
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


class AttributeSet(TimeStampedModel):
    name = models.CharField(_("نام قالب مشخصات"), max_length=150, unique=True)
    description = models.TextField(_("توضیحات"), blank=True)
    is_active = models.BooleanField(_("فعال"), default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("قالب مشخصات")
        verbose_name_plural = _("قالب‌های مشخصات")

    def __str__(self):
        return self.name


class AttributeGroup(TimeStampedModel):
    name = models.CharField(_("نام گروه مشخصات"), max_length=100, unique=True)
    order = models.PositiveIntegerField(_("ترتیب"), default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("گروه مشخصات")
        verbose_name_plural = _("گروه‌های مشخصات")

    def __str__(self):
        return self.name


class Attribute(TimeStampedModel):
    TEXT = "text"
    LONG_TEXT = "long_text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECT = "select"
    MULTISELECT = "multiselect"
    COLOR = "color"
    DATE = "date"
    FILE = "file"
    IMAGE = "image"
    TYPE_CHOICES = [(v, label) for v, label in (
        (TEXT, _("متن کوتاه")), (LONG_TEXT, _("متن بلند")), (NUMBER, _("عدد")),
        (BOOLEAN, _("بله/خیر")), (SELECT, _("انتخابی")), (MULTISELECT, _("چندانتخابی")),
        (COLOR, _("رنگ")), (DATE, _("تاریخ")), (FILE, _("فایل")), (IMAGE, _("تصویر")),
    )]
    name = models.CharField(_("نام مشخصه"), max_length=150, unique=True)
    code = models.SlugField(_("کد یکتا"), max_length=160, unique=True, allow_unicode=True)
    data_type = models.CharField(_("نوع داده"), max_length=20, choices=TYPE_CHOICES, default=TEXT)
    unit = models.CharField(_("واحد"), max_length=30, blank=True)
    group = models.ForeignKey(AttributeGroup, null=True, blank=True, on_delete=models.SET_NULL, related_name="attributes", verbose_name=_("گروه"))
    is_required = models.BooleanField(_("اجباری"), default=False)
    is_filterable = models.BooleanField(_("قابل فیلتر"), default=False)
    is_comparable = models.BooleanField(_("قابل مقایسه"), default=True)
    is_searchable = models.BooleanField(_("قابل جستجو"), default=False)
    is_visible = models.BooleanField(_("نمایش در صفحه محصول"), default=True)
    min_value = models.DecimalField(_("حداقل مقدار عددی"), max_digits=18, decimal_places=4, null=True, blank=True)
    max_value = models.DecimalField(_("حداکثر مقدار عددی"), max_digits=18, decimal_places=4, null=True, blank=True)
    validation_regex = models.CharField(_("عبارت اعتبارسنجی متن"), max_length=255, blank=True)
    is_active = models.BooleanField(_("فعال"), default=True)

    class Meta:
        ordering = ["group__order", "name"]
        indexes = [models.Index(fields=["data_type", "is_active"])]
        verbose_name = _("مشخصه")
        verbose_name_plural = _("مشخصه‌ها")

    def __str__(self):
        return self.name


class AttributeSetAttribute(models.Model):
    attribute_set = models.ForeignKey(AttributeSet, on_delete=models.CASCADE, related_name="items")
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="set_items")
    order = models.PositiveIntegerField(_("ترتیب"), default=0)
    is_required_override = models.BooleanField(_("اجباری در این قالب"), null=True, blank=True)

    class Meta:
        ordering = ["order", "id"]
        constraints = [models.UniqueConstraint(fields=["attribute_set", "attribute"], name="uniq_attribute_in_set")]
        verbose_name = _("مشخصه قالب")
        verbose_name_plural = _("مشخصه‌های قالب")

    def __str__(self):
        return f"{self.attribute_set} — {self.attribute}"


class AttributeValue(TimeStampedModel):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="known_values")
    value = models.CharField(_("مقدار استاندارد"), max_length=500)
    normalized_value = models.CharField(_("مقدار نرمال‌شده"), max_length=500, editable=False)
    language_code = models.CharField(_("زبان"), max_length=10, default="fa")
    usage_count = models.PositiveIntegerField(_("تعداد استفاده"), default=0)

    class Meta:
        ordering = ["value"]
        constraints = [models.UniqueConstraint(fields=["attribute", "normalized_value", "language_code"], name="uniq_attribute_value_language")]
        indexes = [models.Index(fields=["attribute", "normalized_value"]), models.Index(fields=["attribute", "usage_count"])]
        verbose_name = _("مقدار شناخته‌شده مشخصه")
        verbose_name_plural = _("مقادیر شناخته‌شده مشخصه‌ها")

    def save(self, *args, **kwargs):
        self.normalized_value = " ".join(self.value.casefold().split())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.attribute}: {self.value}"


class ProductCategory(TimeStampedModel, SlugModel, SEOModel):
    name = models.CharField(_("نام دسته‌بندی"), max_length=150)
    attribute_set = models.ForeignKey(AttributeSet, null=True, blank=True, on_delete=models.SET_NULL, related_name="categories", verbose_name=_("قالب مشخصات"))
    inherit_parent_attributes = models.BooleanField(_("ارث‌بری مشخصات از والد"), default=True)
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


class ProductVariant(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants", verbose_name=_("محصول والد"))
    name = models.CharField(_("نام تنوع"), max_length=150)
    sku = models.CharField(_("SKU تنوع"), max_length=60, unique=True)
    price = models.DecimalField(_("قیمت"), max_digits=14, decimal_places=0, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(_("موجودی"), default=0)
    is_active = models.BooleanField(_("فعال"), default=True)

    class Meta:
        ordering = ["id"]
        indexes = [models.Index(fields=["product", "is_active"])]
        verbose_name = _("تنوع محصول")
        verbose_name_plural = _("تنوع‌های محصول")

    def __str__(self):
        return f"{self.product.name} — {self.name}"


class ProductAttributeValue(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="attribute_values")
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT, related_name="product_values")
    value_text = models.TextField(_("مقدار متنی"), blank=True)
    value_number = models.DecimalField(_("مقدار عددی"), max_digits=18, decimal_places=4, null=True, blank=True)
    value_boolean = models.BooleanField(_("مقدار بله/خیر"), null=True, blank=True)
    value_date = models.DateField(_("تاریخ"), null=True, blank=True)
    value_file = models.FileField(_("فایل"), upload_to="products/attributes/", null=True, blank=True)
    selected_values = models.ManyToManyField(AttributeValue, blank=True, related_name="product_assignments", verbose_name=_("مقادیر انتخاب‌شده"))
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.CASCADE, related_name="attribute_values")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["product", "attribute", "variant"], name="uniq_product_attribute_variant")]
        indexes = [models.Index(fields=["attribute", "value_number"]), models.Index(fields=["attribute", "value_boolean"])]
        verbose_name = _("مقدار مشخصه محصول")
        verbose_name_plural = _("مقادیر مشخصات محصول")

    def clean(self):
        super().clean()
        if not self.attribute_id:
            return
        attribute = self.attribute
        value = (self.value_text or "").strip()
        if attribute.is_required and not value and self.value_number is None and self.value_boolean is None and self.value_date is None and not self.value_file and not self.selected_values.exists():
            raise ValidationError({"value_text": "این مشخصه اجباری است."})
        if self.value_number is not None:
            if attribute.min_value is not None and self.value_number < attribute.min_value:
                raise ValidationError({"value_number": f"مقدار باید حداقل {attribute.min_value} باشد."})
            if attribute.max_value is not None and self.value_number > attribute.max_value:
                raise ValidationError({"value_number": f"مقدار نباید بیشتر از {attribute.max_value} باشد."})
        if value and attribute.validation_regex:
            import re
            if not re.fullmatch(attribute.validation_regex, value):
                raise ValidationError({"value_text": "مقدار واردشده با الگوی اعتبارسنجی مشخصه مطابقت ندارد."})
        if value and attribute.data_type == Attribute.COLOR:
            import re
            if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
                raise ValidationError({"value_text": "کد رنگ باید به شکل #RRGGBB باشد."})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.value_text.strip() and self.attribute_id:
            from django.db.models import F
            known, created = AttributeValue.objects.get_or_create(
                attribute=self.attribute,
                normalized_value=" ".join(self.value_text.casefold().split()),
                language_code="fa",
                defaults={"value": self.value_text.strip()},
            )
            if created:
                AttributeValue.objects.filter(pk=known.pk).update(usage_count=1)
            else:
                AttributeValue.objects.filter(pk=known.pk).update(usage_count=F("usage_count") + 1)

    def __str__(self):
        return f"{self.product}: {self.attribute}"


class VariantAttributeValue(TimeStampedModel):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="variant_values")
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT, related_name="variant_values")
    value_text = models.TextField(blank=True)
    value_number = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    value_boolean = models.BooleanField(null=True, blank=True)
    selected_values = models.ManyToManyField(AttributeValue, blank=True, related_name="variant_assignments")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["variant", "attribute"], name="uniq_variant_attribute")]
        verbose_name = _("مشخصه تنوع")
        verbose_name_plural = _("مشخصات تنوع‌ها")


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
