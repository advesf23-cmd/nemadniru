from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel, SEOModel, SlugModel


class Page(TimeStampedModel, SlugModel, SEOModel):
    """صفحات پویا (مثل درباره‌ما، حریم‌خصوصی، قوانین) -- کاملا قابل ساخت از ادمین بدون کدنویسی"""
    title = models.CharField(_("عنوان"), max_length=200)
    content = models.TextField(_("محتوا"))
    is_published = models.BooleanField(default=True)
    show_in_footer = models.BooleanField(_("نمایش در فوتر"), default=False)

    class Meta:
        ordering = ["title"]
        verbose_name = _("صفحه")
        verbose_name_plural = _("صفحات")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug("title")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("pages:page_detail", kwargs={"slug": self.slug})


class AboutContent(TimeStampedModel):
    """محتوای صفحه درباره ما -- Singleton: تاریخچه، ماموریت، چشم‌انداز، رویکرد"""
    history = models.TextField(_("تاریخچه شرکت"), blank=True)
    mission = models.TextField(_("ماموریت"), blank=True)
    vision = models.TextField(_("چشم‌انداز"), blank=True)
    approach = models.TextField(_("رویکرد ما"), blank=True)
    factory_intro = models.TextField(_("معرفی کارخانه"), blank=True)
    capabilities = models.TextField(_("توانمندی‌ها"), blank=True)

    class Meta:
        verbose_name = _("محتوای درباره ما")
        verbose_name_plural = _("محتوای درباره ما")

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "About Us Content"


class ManagementMember(TimeStampedModel):
    """اعضای هیئت مدیره / مدیریت شرکت"""
    full_name = models.CharField(_("نام و نام خانوادگی"), max_length=150)
    position = models.CharField(_("سمت"), max_length=150)
    photo = models.ImageField(_("تصویر"), upload_to="management/", blank=True, null=True)
    bio = models.TextField(_("بیوگرافی کوتاه"), blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("عضو مدیریت")
        verbose_name_plural = _("اعضای مدیریت")

    def __str__(self):
        return f"{self.full_name} - {self.position}"

    def get_absolute_url(self):
        return None


class CoreValue(TimeStampedModel):
    """ارزش‌های شرکت (فناوری، کیفیت، تعهد، پشتیبانی)"""
    title = models.CharField(_("عنوان"), max_length=100)
    description = models.CharField(_("توضیح"), max_length=255)
    icon = models.CharField(_("آیکون"), max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("ارزش سازمانی")
        verbose_name_plural = _("ارزش‌های سازمانی")

    def __str__(self):
        return self.title
