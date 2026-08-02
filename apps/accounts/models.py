from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """کاربر سفارشی -- امکان افزودن نقش‌ها بدون نیاز به Migration مجدد در آینده"""

    ROLE_SUPERADMIN = "super_admin"
    ROLE_ADMIN = "administrator"
    ROLE_EDITOR = "editor"
    ROLE_CONTENT_MANAGER = "content_manager"
    ROLE_CUSTOMER = "customer"

    ROLE_CHOICES = [
        (ROLE_SUPERADMIN, _("مدیر ارشد")),
        (ROLE_ADMIN, _("مدیر")),
        (ROLE_EDITOR, _("ویرایشگر")),
        (ROLE_CONTENT_MANAGER, _("مدیر محتوا")),
        (ROLE_CUSTOMER, _("مشتری")),
    ]

    role = models.CharField(_("نقش"), max_length=20, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)
    phone = models.CharField(_("شماره تماس"), max_length=20, blank=True)
    avatar = models.ImageField(_("تصویر پروفایل"), upload_to="avatars/", blank=True, null=True)
    company_name = models.CharField(_("نام شرکت"), max_length=150, blank=True)
    is_email_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("کاربر")
        verbose_name_plural = _("کاربران")

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_staff_role(self):
        return self.role in [self.ROLE_SUPERADMIN, self.ROLE_ADMIN, self.ROLE_EDITOR, self.ROLE_CONTENT_MANAGER]
