from django.views.generic import TemplateView, DetailView
from .models import Page, AboutContent, ManagementMember, CoreValue
from apps.core.models import Statistic, Certificate


class AboutView(TemplateView):
    template_name = "pages/about.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["about"], _ = AboutContent.objects.get_or_create(pk=1)
        ctx["management"] = ManagementMember.objects.all()
        ctx["values"] = CoreValue.objects.all()
        ctx["statistics"] = Statistic.objects.all()
        ctx["certificates"] = Certificate.objects.all()
        return ctx


class PageDetailView(DetailView):
    model = Page
    template_name = "pages/page_detail.html"
    context_object_name = "page"

    def get_queryset(self):
        return Page.objects.filter(is_published=True)
