from django.urls import path
from . import views

app_name = "contact"

urlpatterns = [
    path("", views.ContactPageView.as_view(), name="contact"),
    path("quote-request/", views.QuoteRequestCreateView.as_view(), name="quote_request"),
    path("careers/", views.CareersListView.as_view(), name="careers"),
    path("careers/apply/", views.JobApplicationCreateView.as_view(), name="job_apply"),
]
