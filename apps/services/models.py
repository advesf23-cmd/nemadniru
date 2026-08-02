from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel, SEOModel, SlugModel, PublishableModel


class Service(TimeStampedModel, SlugModel, SEOModel, PublishableModel):
    title = models.CharField(_("عنوان خدمت"), max_length=150)
    short_description = models.CharField(_("توضیح کوتاه"), max_length=300)
    description = models.TextField(_("توضیحات کامل"))
    icon = models.CharField(_("آیکون FontAwesome"), max_length=50, blank=True)
    cover_image = models.ImageField(_("تصویر"), upload_to="services/", blank=True, null=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("خدمت")
        verbose_name_plural = _("خدمات")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug("title")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("services:service_detail", kwargs={"slug": self.slug})


class ProcessStep(models.Model):
    """مراحل فرآیند کاری (مشاوره -> طراحی -> ساخت و تأمین -> اجرا و پشتیبانی)"""
    title = models.CharField(_("عنوان مرحله"), max_length=100)
    description = models.CharField(_("توضیح"), max_length=255, blank=True)
    step_number = models.PositiveIntegerField(_("شماره مرحله"))

    class Meta:
        ordering = ["step_number"]
        verbose_name = _("مرحله فرآیند")
        verbose_name_plural = _("مراحل فرآیند کاری")

    def __str__(self):
        return f"{self.step_number}. {self.title}"
