from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView
from django.core.mail import send_mail
from django.conf import settings as dj_settings

from .models import ContactMessage, QuoteRequest, JobPosition, JobApplication
from .forms import QuoteRequestForm, JobApplicationForm


class ContactPageView(CreateView):
    model = ContactMessage
    fields = ["full_name", "email", "phone", "subject", "message"]
    template_name = "contact/contact.html"
    success_url = reverse_lazy("contact:contact")

    def form_valid(self, form):
        response = super().form_valid(form)
        try:
            send_mail(
                subject=f"پیام جدید از سایت: {form.instance.subject}",
                message=form.instance.message,
                from_email=dj_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[dj_settings.CONTACT_RECEIVER_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass
        messages.success(self.request, "پیام شما با موفقیت ارسال شد.")
        return response


class QuoteRequestCreateView(CreateView):
    model = QuoteRequest
    form_class = QuoteRequestForm
    template_name = "contact/quote_request.html"
    success_url = reverse_lazy("contact:quote_request")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "درخواست استعلام قیمت شما ثبت شد. کارشناسان ما به‌زودی تماس می‌گیرند.")
        return response


class CareersListView(ListView):
    model = JobPosition
    template_name = "contact/careers.html"
    context_object_name = "positions"

    def get_queryset(self):
        return JobPosition.objects.filter(is_active=True)


class JobApplicationCreateView(CreateView):
    model = JobApplication
    form_class = JobApplicationForm
    template_name = "contact/job_application_form.html"
    success_url = reverse_lazy("contact:careers")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "رزومه شما با موفقیت ثبت شد.")
        return response
