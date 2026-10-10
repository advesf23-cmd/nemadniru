from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View

from apps.contact.models import JobApplication, QuoteRequest
from .views import StaffRequiredMixin


class DashboardResumeDownloadView(StaffRequiredMixin, View):
    """Serve a resume only to authorized dashboard staff."""

    def get(self, request, pk):
        application = get_object_or_404(JobApplication, pk=pk)

        if not application.resume:
            raise Http404("Resume not found")

        try:
            file_handle = application.resume.open("rb")
        except (OSError, ValueError):
            raise Http404("Resume not found")

        filename = application.resume.name.rsplit("/", 1)[-1]
        response = FileResponse(
            file_handle,
            as_attachment=True,
            filename=filename,
            content_type="application/octet-stream",
        )
        response["Cache-Control"] = "private, no-store"
        response["X-Content-Type-Options"] = "nosniff"
        response["Referrer-Policy"] = "no-referrer"
        return response


class DashboardQuoteAttachmentDownloadView(StaffRequiredMixin, View):
    """Serve a quotation attachment only to authorized dashboard staff."""

    def get(self, request, pk):
        quote = get_object_or_404(QuoteRequest, pk=pk)

        if not quote.attachment:
            raise Http404("Attachment not found")

        try:
            file_handle = quote.attachment.open("rb")
        except (OSError, ValueError):
            raise Http404("Attachment not found")

        filename = quote.attachment.name.rsplit("/", 1)[-1]
        response = FileResponse(
            file_handle,
            as_attachment=True,
            filename=filename,
            content_type="application/octet-stream",
        )
        response["Cache-Control"] = "private, no-store"
        response["X-Content-Type-Options"] = "nosniff"
        response["Referrer-Policy"] = "no-referrer"
        return response
