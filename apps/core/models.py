from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """فیلدهای ایجاد و بروزرسانی برای استفاده در تمام مدل‌ها"""
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ بروزرسانی"), auto_now=True)

    class Meta:
        abstract = True


class SEOModel(models.Model):
    """فیلدهای سئو قابل استفاده در همه صفحات/محصولات/پروژه‌ها/مقالات"""
    meta_title = models.CharField(_("عنوان متا"), max_length=70, blank=True)
    meta_description = models.CharField(_("توضیحات متا"), max_length=160, blank=True)
    og_image = models.ImageField(_("تصویر Open Graph"), upload_to="seo/og/", blank=True, null=True)
    canonical_url = models.URLField(_("آدرس Canonical"), blank=True)

    class Meta:
        abstract = True


class SlugModel(models.Model):
    slug = models.SlugField(_("اسلاگ"), max_length=255, unique=True, allow_unicode=True, blank=True)

    class Meta:
        abstract = True

    def generate_unique_slug(self, source_field: str):
        base_slug = slugify(getattr(self, source_field), allow_unicode=True)
        slug = base_slug
        ModelClass = self.__class__
        counter = 1
        while ModelClass.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            counter += 1
            slug = f"{base_slug}-{counter}"
        return slug


class PublishableModel(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, _("پیش‌نویس")),
        (STATUS_PUBLISHED, _("منتشر شده")),
    ]
    status = models.CharField(_("وضعیت"), max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    is_featured = models.BooleanField(_("ویژه"), default=False)
    order = models.PositiveIntegerField(_("ترتیب نمایش"), default=0)

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# مدل‌های سراسری سایت (قابل ویرایش کامل از پنل ادمین بدون نیاز به تغییر کد)
# ---------------------------------------------------------------------------
class SiteSetting(TimeStampedModel):
    """تنظیمات کلی سایت -- Singleton (فقط یک رکورد)"""
    site_name = models.CharField(_("نام سایت"), max_length=150, default="سامان تجهیز اسپادان")
    logo = models.ImageField(_("لوگو"), upload_to="site/", blank=True, null=True)
    favicon = models.ImageField(_("فاویکون"), upload_to="site/", blank=True, null=True)
    phone = models.CharField(_("تلفن"), max_length=30, blank=True)
    email = models.EmailField(_("ایمیل"), blank=True)
    address = models.TextField(_("آدرس"), blank=True)
    working_hours = models.CharField(_("ساعات کاری"), max_length=150, blank=True)
    map_embed_url = models.URLField(_("لینک نقشه گوگل"), blank=True)
    instagram = models.URLField(blank=True)
    telegram = models.URLField(blank=True)
    whatsapp = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    footer_text = models.TextField(_("متن فوتر"), blank=True)
    default_meta_description = models.CharField(max_length=160, blank=True)
    google_analytics_id = models.CharField(max_length=30, blank=True)

    class Meta:
        verbose_name = _("تنظیمات سایت")
        verbose_name_plural = _("تنظیمات سایت")

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1  # الگوی Singleton
        super().save(*args, **kwargs)


class Statistic(TimeStampedModel):
    """آمار نمایش داده‌شده در بخش Home/About (مثل 300+ پروژه، 20+ سال تجربه)"""
    title = models.CharField(_("عنوان"), max_length=100)
    value = models.CharField(_("مقدار"), max_length=20, help_text=_("مثال: 300+, 100%, 20+"))
    icon = models.CharField(_("آیکون FontAwesome"), max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("آمار")
        verbose_name_plural = _("آمارها")

    def __str__(self):
        return f"{self.title}: {self.value}"


class Certificate(TimeStampedModel):
    """گواهینامه‌ها و مجوزها (ایزو، تاییدیه توانیر، پروانه اشتغال و ...)"""
    title = models.CharField(_("عنوان"), max_length=200)
    description = models.CharField(_("توضیح کوتاه"), max_length=255, blank=True)
    image = models.ImageField(_("تصویر گواهینامه"), upload_to="certificates/")
    icon = models.CharField(_("آیکون FontAwesome"), max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("گواهینامه")
        verbose_name_plural = _("گواهینامه‌ها")

    def __str__(self):
        return self.title


class Partner(TimeStampedModel):
    """برندهای همکار / تأمین‌کننده (Schneider, ABB, Siemens, ...)"""
    name = models.CharField(_("نام برند"), max_length=100)
    tagline = models.CharField(_("زیرعنوان"), max_length=100, blank=True)
    logo = models.ImageField(_("لوگو"), upload_to="partners/", blank=True, null=True)
    website = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("برند همکار")
        verbose_name_plural = _("برندهای همکار")

    def __str__(self):
        return self.name


class Testimonial(TimeStampedModel):
    client_name = models.CharField(_("نام مشتری"), max_length=100)
    company_name = models.CharField(_("نام شرکت"), max_length=150, blank=True)
    photo = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    text = models.TextField(_("متن نظر"))
    rating = models.PositiveSmallIntegerField(default=5)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("نظر مشتری")
        verbose_name_plural = _("نظرات مشتریان")

    def __str__(self):
        return self.client_name


class FAQ(TimeStampedModel):
    question = models.CharField(_("سوال"), max_length=255)
    answer = models.TextField(_("پاسخ"))
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("سوال متداول")
        verbose_name_plural = _("سوالات متداول")

    def __str__(self):
        return self.question


class HomeSlide(TimeStampedModel):
    """اسلایدر هدر صفحه اصلی -- کاملا قابل مدیریت از ادمین"""
    title = models.CharField(_("عنوان"), max_length=200)
    subtitle = models.CharField(_("زیرعنوان"), max_length=255, blank=True)
    image = models.ImageField(_("تصویر"), upload_to="slider/")
    button_text = models.CharField(max_length=50, blank=True)
    button_url = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("اسلاید صفحه اصلی")
        verbose_name_plural = _("اسلایدهای صفحه اصلی")

    def __str__(self):
        return self.title


class Menu(TimeStampedModel):
    title = models.CharField(max_length=50)
    url = models.CharField(max_length=255)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="children")
    location = models.CharField(
        max_length=20,
        choices=[("header", _("هدر")), ("footer", _("فوتر"))],
        default="header",
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("منو")
        verbose_name_plural = _("منوها")

    def __str__(self):
        return self.title
