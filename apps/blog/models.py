from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel, SEOModel, SlugModel, PublishableModel
from apps.accounts.models import User


class BlogCategory(TimeStampedModel, SlugModel):
    name = models.CharField(_("نام دسته‌بندی"), max_length=150)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("دسته‌بندی مقاله")
        verbose_name_plural = _("دسته‌بندی‌های مقالات")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug("name")
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(_("برچسب"), max_length=50, unique=True)

    class Meta:
        verbose_name = _("برچسب")
        verbose_name_plural = _("برچسب‌ها")

    def __str__(self):
        return self.name


class Post(TimeStampedModel, SlugModel, SEOModel, PublishableModel):
    category = models.ForeignKey(
        BlogCategory, on_delete=models.PROTECT, related_name="posts", verbose_name=_("دسته‌بندی")
    )
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="posts", verbose_name=_("نویسنده")
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts", verbose_name=_("برچسب‌ها"))
    title = models.CharField(_("عنوان"), max_length=200)
    summary = models.CharField(_("خلاصه"), max_length=300)
    content = models.TextField(_("محتوا"))
    cover_image = models.ImageField(_("تصویر شاخص"), upload_to="blog/covers/")
    published_at = models.DateTimeField(_("تاریخ انتشار"), null=True, blank=True)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = _("مقاله")
        verbose_name_plural = _("مقالات")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug("title")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"slug": self.slug})


class Comment(TimeStampedModel):
    """نظرات کاربران روی مقالات -- نیازمند تأیید مدیر قبل از نمایش عمومی"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name=_("مقاله"))
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies", verbose_name=_("پاسخ به")
    )
    full_name = models.CharField(_("نام"), max_length=100)
    email = models.EmailField(_("ایمیل"), blank=True)
    text = models.TextField(_("متن نظر"))
    is_approved = models.BooleanField(_("تأیید شده"), default=False)

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("نظر")
        verbose_name_plural = _("نظرات")

    def __str__(self):
        return f"{self.full_name} - {self.post.title}"
