from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel, SEOModel, SlugModel, PublishableModel


class ProjectCategory(TimeStampedModel, SlugModel):
    """دسته‌بندی صنعت پروژه: نفت و گاز، فولاد و صنایع فلزی، صنایع غذایی، نیروگاه‌ها و ..."""
    name = models.CharField(_("نام دسته‌بندی"), max_length=150)
    icon = models.CharField(_("آیکون"), max_length=50, blank=True)
    color_hex = models.CharField(_("رنگ کارت (Hex)"), max_length=7, blank=True, default="#0B2447")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("دسته‌بندی پروژه")
        verbose_name_plural = _("دسته‌بندی‌های پروژه")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug("name")
        super().save(*args, **kwargs)


class Project(TimeStampedModel, SlugModel, SEOModel, PublishableModel):
    category = models.ForeignKey(
        ProjectCategory, on_delete=models.PROTECT, related_name="projects", verbose_name=_("دسته‌بندی صنعت")
    )
    title = models.CharField(_("عنوان پروژه"), max_length=200)
    client_name = models.CharField(_("نام کارفرما"), max_length=150, blank=True)
    location = models.CharField(_("محل اجرا"), max_length=150, blank=True)
    execution_year = models.PositiveIntegerField(_("سال اجرا"), null=True, blank=True)
    short_description = models.CharField(_("توضیح کوتاه"), max_length=300)
    description = models.TextField(_("شرح کامل پروژه"))
    cover_image = models.ImageField(_("تصویر شاخص"), upload_to="projects/covers/")

    class Meta:
        ordering = ["-is_featured", "order", "-execution_year"]
        verbose_name = _("پروژه")
        verbose_name_plural = _("پروژه‌ها")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug("title")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("projects:project_detail", kwargs={"slug": self.slug})


class ProjectImage(TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images", verbose_name=_("پروژه"))
    image = models.ImageField(_("تصویر"), upload_to="projects/gallery/")
    caption = models.CharField(_("عنوان تصویر"), max_length=150, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("تصویر پروژه")
        verbose_name_plural = _("گالری تصاویر پروژه")

    def __str__(self):
        return f"{self.project.title} - {self.order}"
