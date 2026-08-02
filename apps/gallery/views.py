from django.views.generic import ListView
from .models import GalleryItem, GalleryCategory


class GalleryListView(ListView):
    model = GalleryItem
    template_name = "gallery/gallery_list.html"
    context_object_name = "items"
    paginate_by = 18

    def get_queryset(self):
        qs = GalleryItem.objects.select_related("category")
        category_id = self.request.GET.get("category")
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = GalleryCategory.objects.all()
        return ctx
