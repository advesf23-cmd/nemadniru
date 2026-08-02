from django.contrib import admin
from .models import GalleryCategory, GalleryItem


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order")


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "media_type", "order", "use_as_hero_background")
    list_editable = ("order", "use_as_hero_background")
    list_filter = ("category", "media_type")
