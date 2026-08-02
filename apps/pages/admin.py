from django.contrib import admin
from .models import Page, AboutContent, ManagementMember, CoreValue


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "show_in_footer")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(AboutContent)
class AboutContentAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not AboutContent.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ManagementMember)
class ManagementMemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "position", "order")
    list_editable = ("order",)


@admin.register(CoreValue)
class CoreValueAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    list_editable = ("order",)
