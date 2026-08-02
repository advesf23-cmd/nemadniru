from django.contrib import admin
from .models import ContactMessage, QuoteRequest, JobPosition, JobApplication


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "subject", "is_read", "created_at")
    list_filter = ("is_read",)


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "company_name", "project_type", "is_read", "is_processed", "created_at")
    list_filter = ("is_read", "is_processed")


@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "employment_type", "is_active")
    list_filter = ("is_active", "employment_type")


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "position", "email", "is_reviewed", "created_at")
    list_filter = ("is_reviewed", "position")
