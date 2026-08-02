from django.views.generic import TemplateView

from apps.core.models import Statistic, Certificate, Partner, Testimonial, FAQ, HomeSlide, PromoBanner
from apps.products.models import Product
from apps.services.models import Service
from apps.projects.models import Project
from apps.blog.models import Post
from apps.gallery.models import GalleryItem


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            "slides": HomeSlide.objects.filter(is_active=True),
            "promo_banners": PromoBanner.objects.filter(is_active=True),
            "statistics": Statistic.objects.all(),
            "certificates": Certificate.objects.all(),
            "partners": Partner.objects.all(),
            "testimonials": Testimonial.objects.all(),
            "faqs": FAQ.objects.all(),
            "featured_products": Product.objects.filter(status="published", is_featured=True)[:8],
            "services": Service.objects.filter(status="published")[:6],
            "latest_projects": Project.objects.filter(status="published")[:6],
            "latest_posts": Post.objects.filter(status="published")[:3],
            "hero_bg_image": GalleryItem.objects.filter(
                use_as_hero_background=True, media_type=GalleryItem.MEDIA_IMAGE
            ).first(),
        })
        return ctx
