from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class ContactMessage(TimeStampedModel):
    full_name = models.CharField(_("نام و نام خانوادگی"), max_length=150)
    email = models.EmailField(_("ایمیل"))
    phone = models.CharField(_("شماره تماس"), max_length=20, blank=True)
    subject = models.CharField(_("موضوع"), max_length=200, blank=True)
    message = models.TextField(_("پیام"))
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("پیام تماس")
        verbose_name_plural = _("پیام‌های تماس")

    def __str__(self):
        return f"{self.full_name} - {self.subject}"


class QuoteRequest(TimeStampedModel):
    """درخواست استعلام قیمت حرفه‌ای (صفحه Request Quote)"""
    full_name = models.CharField(_("نام و نام خانوادگی"), max_length=150)
    company_name = models.CharField(_("نام شرکت"), max_length=150, blank=True)
    phone = models.CharField(_("شماره تماس"), max_length=20)
    email = models.EmailField(_("ایمیل"), blank=True)
    project_type = models.CharField(_("نوع پروژه"), max_length=150, blank=True)
    budget_range = models.CharField(_("محدوده بودجه تقریبی"), max_length=100, blank=True)
    description = models.TextField(_("شرح درخواست"))
    attachment = models.FileField(_("فایل پیوست (نقشه/مشخصات)"), upload_to="quotes/", blank=True, null=True)
    is_read = models.BooleanField(default=False)
    is_processed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("درخواست استعلام قیمت")
        verbose_name_plural = _("درخواست‌های استعلام قیمت")

    def __str__(self):
        return f"{self.full_name} - {self.project_type}"


class JobPosition(TimeStampedModel):
    title = models.CharField(_("عنوان شغلی"), max_length=150)
    department = models.CharField(_("واحد"), max_length=100, blank=True)
    location = models.CharField(_("محل کار"), max_length=150, blank=True)
    employment_type = models.CharField(
        _("نوع همکاری"), max_length=50,
        choices=[("full_time", _("تمام‌وقت")), ("part_time", _("پاره‌وقت")), ("contract", _("پروژه‌ای"))],
        default="full_time",
    )
    description = models.TextField(_("شرح شغل"))
    requirements = models.TextField(_("شرایط احراز"), blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("فرصت شغلی")
        verbose_name_plural = _("فرصت‌های شغلی")

    def __str__(self):
        return self.title


class JobApplication(TimeStampedModel):
    position = models.ForeignKey(
        JobPosition, on_delete=models.CASCADE, related_name="applications", verbose_name=_("موقعیت شغلی")
    )
    full_name = models.CharField(_("نام و نام خانوادگی"), max_length=150)
    email = models.EmailField(_("ایمیل"))
    phone = models.CharField(_("شماره تماس"), max_length=20)
    resume = models.FileField(_("فایل رزومه"), upload_to="careers/resumes/")
    cover_letter = models.TextField(_("متن معرفی"), blank=True)
    is_reviewed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("درخواست استخدام")
        verbose_name_plural = _("درخواست‌های استخدام")

    def __str__(self):
        return f"{self.full_name} - {self.position}"
