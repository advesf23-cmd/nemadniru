from django.urls import path
from . import views

app_name = "services"

urlpatterns = [
    path("", views.ServiceListView.as_view(), name="service_list"),
    path("<str:slug>/", views.ServiceDetailView.as_view(), name="service_detail"),
]
