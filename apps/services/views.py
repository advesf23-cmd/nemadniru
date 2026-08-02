from django.views.generic import ListView, DetailView
from .models import Service, ProcessStep


class ServiceListView(ListView):
    model = Service
    template_name = "services/service_list.html"
    context_object_name = "services"

    def get_queryset(self):
        return Service.objects.filter(status="published")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["process_steps"] = ProcessStep.objects.all()
        return ctx


class ServiceDetailView(DetailView):
    model = Service
    template_name = "services/service_detail.html"
    context_object_name = "service"

    def get_queryset(self):
        return Service.objects.filter(status="published")
