from django import forms
from django.contrib import admin
from .models import (
    SiteSetting, Statistic, Certificate, Partner, Testimonial, FAQ, HomeSlide, Menu, PromoBanner, QuickCircle
)


class SiteSettingForm(forms.ModelForm):
    class Meta:
        model = SiteSetting
        fields = "__all__"
        widgets = {
            **{name: forms.TextInput(attrs={"type": "color", "style": "width: 80px; height: 40px; padding: 2px;"}) for name in ("announcement_color", "theme_primary_color", "theme_menu_color", "theme_menu_text_color", "theme_accent_color", "theme_text_color", "theme_background_color", "theme_surface_color", "theme_border_color")},
        }


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    form = SiteSettingForm
    fieldsets = (
        (None, {"fields": ("site_name", "logo", "favicon")}),
        ("نوار اطلاع‌رسانی", {"fields": ("announcement_enabled", "announcement_text", "announcement_color")}),
        ("رنگ‌بندی کلی سایت", {"fields": ("theme_primary_color", "theme_menu_color", "theme_menu_text_color", "theme_accent_color", "theme_text_color", "theme_background_color", "theme_surface_color", "theme_border_color")}),
        ("اطلاعات تماس", {"fields": ("phone", "email", "address", "working_hours", "map_embed_url")}),
        ("شبکه‌های اجتماعی", {"fields": ("instagram", "telegram", "whatsapp", "linkedin")}),
        ("سئو و کدهای سایت", {"fields": ("footer_text", "default_meta_description", "google_analytics_id", "quick_circles_heading")}),
    )

    def has_add_permission(self, request):
        return not SiteSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ("title", "value", "order")
    list_editable = ("order",)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    list_editable = ("order",)


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "tagline", "order")
    list_editable = ("order",)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("client_name", "company_name", "rating", "order")
    list_editable = ("order",)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order")
    list_editable = ("order",)


@admin.register(HomeSlide)
class HomeSlideAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "location", "parent", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("location", "is_active")

@admin.register(PromoBanner)
class PromoBannerAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    list_editable = ("order", "is_active")
 
@admin.register(QuickCircle)
class QuickCircleAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    list_editable = ("order", "is_active")
