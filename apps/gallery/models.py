from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class GalleryCategory(models.Model):
    name = models.CharField(_("نام دسته‌بندی"), max_length=150)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("دسته‌بندی گالری")
        verbose_name_plural = _("دسته‌بندی‌های گالری")

    def __str__(self):
        return self.name


class GalleryItem(TimeStampedModel):
    MEDIA_IMAGE = "image"
    MEDIA_VIDEO = "video"
    MEDIA_CHOICES = [(MEDIA_IMAGE, _("تصویر")), (MEDIA_VIDEO, _("ویدیو"))]

    category = models.ForeignKey(
        GalleryCategory, on_delete=models.CASCADE, related_name="items", verbose_name=_("دسته‌بندی")
    )
    media_type = models.CharField(_("نوع رسانه"), max_length=10, choices=MEDIA_CHOICES, default=MEDIA_IMAGE)
    title = models.CharField(_("عنوان"), max_length=150, blank=True)
    image = models.ImageField(_("تصویر"), upload_to="gallery/images/", blank=True, null=True)
    video_url = models.URLField(_("لینک ویدیو (Youtube/Aparat)"), blank=True)
    order = models.PositiveIntegerField(default=0)
    use_as_hero_background = models.BooleanField(
        _("استفاده به‌عنوان پس‌زمینه صفحه اصلی"),
        default=False,
        help_text=_("این تصویر به‌صورت نیمه‌شفاف در پس‌زمینه بخش هیرو صفحه اصلی نمایش داده می‌شود. فقط یک تصویر می‌تواند فعال باشد."),
    )

    class Meta:
        ordering = ["order"]
        verbose_name = _("آیتم گالری")
        verbose_name_plural = _("آیتم‌های گالری")

    def __str__(self):
        return self.title or f"Gallery item #{self.pk}"

    def save(self, *args, **kwargs):
        # اطمینان از اینکه همیشه فقط یک تصویر به‌عنوان پس‌زمینه صفحه اصلی فعال است
        if self.use_as_hero_background and self.media_type == self.MEDIA_IMAGE:
            GalleryItem.objects.exclude(pk=self.pk).update(use_as_hero_background=False)
        super().save(*args, **kwargs)
