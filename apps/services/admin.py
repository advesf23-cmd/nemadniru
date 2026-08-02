from django.contrib import admin
from .models import Service, ProcessStep


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "is_featured", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ("step_number", "title")
    list_editable = ()
