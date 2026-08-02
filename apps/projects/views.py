from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView

from .models import Project, ProjectCategory


class ProjectFilterMixin:
    SORT_OPTIONS = {
        "newest": "-execution_year",
        "oldest": "execution_year",
        "name": "title",
    }

    def get_base_queryset(self):
        return Project.objects.filter(status="published").select_related("category")

    def apply_filters(self, qs):
        request = self.request
        category_slug = request.GET.get("category")
        search_query = request.GET.get("q")
        year = request.GET.get("year")
        sort = request.GET.get("sort", "newest")

        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if search_query:
            qs = qs.filter(
                Q(title__icontains=search_query) |
                Q(client_name__icontains=search_query) |
                Q(location__icontains=search_query)
            )
        if year:
            qs = qs.filter(execution_year=year)

        return qs.order_by(self.SORT_OPTIONS.get(sort, "-execution_year"))


class ProjectListView(ProjectFilterMixin, ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 9

    def get_queryset(self):
        return self.apply_filters(self.get_base_queryset())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = ProjectCategory.objects.all()
        ctx["years"] = (
            Project.objects.filter(status="published")
            .exclude(execution_year__isnull=True)
            .values_list("execution_year", flat=True).distinct().order_by("-execution_year")
        )
        ctx["current_sort"] = self.request.GET.get("sort", "newest")
        return ctx

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.GET.get("ajax"):
            html = render_to_string("projects/_project_grid.html", context, request=request)
            pagination_html = render_to_string("projects/_pagination.html", context, request=request)
            return JsonResponse({
                "html": html,
                "pagination": pagination_html,
                "count": context["paginator"].count,
            })
        return self.render_to_response(context)


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"
    context_object_name = "project"
    slug_field = "slug"

    def get_queryset(self):
        return Project.objects.filter(status="published")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["related_projects"] = Project.objects.filter(
            category=self.object.category, status="published"
        ).exclude(pk=self.object.pk)[:3]
        return ctx
