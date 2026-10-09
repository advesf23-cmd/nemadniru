from django.db.models import Case, DecimalField, ExpressionWrapper, F, Q, Value, When
from django.views.generic import TemplateView

from apps.core.models import Statistic, Certificate, Partner, Testimonial, FAQ, HomeSlide, PromoBanner, QuickCircle, HomePromoBanner
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
            "promo_banners": PromoBanner.objects.filter(is_active=True)[:4],
            "home_promo_banners": HomePromoBanner.objects.filter(is_active=True)[:2],
            "quick_circles": QuickCircle.objects.filter(is_active=True),
            "statistics": Statistic.objects.all(),
            "certificates": Certificate.objects.all(),
            "partners": Partner.objects.all(),
            "testimonials": Testimonial.objects.all(),
            "faqs": FAQ.objects.all(),
            "featured_products": Product.objects.filter(status="published", is_featured=True).select_related("category", "brand")[:8],
            "latest_products": Product.objects.filter(status="published").select_related("category", "brand").order_by("-created_at")[:8],
            "discounted_products": Product.objects.filter(status="published").filter(
                Q(discount_price__lt=F("price"))
                | Q(discount_percent_override__gt=0)
                | Q(brand__default_discount_percent__gt=0)
            ).select_related("category", "brand").annotate(
                homepage_discount_percent=Case(
                    When(
                        price__gt=F("discount_price"),
                        discount_price__isnull=False,
                        then=ExpressionWrapper(
                            (F("price") - F("discount_price")) * Value(100) / F("price"),
                            output_field=DecimalField(max_digits=7, decimal_places=2),
                        ),
                    ),
                    When(discount_percent_override__isnull=False, then=F("discount_percent_override")),
                    When(brand__default_discount_percent__gt=0, then=F("brand__default_discount_percent")),
                    default=Value(0),
                    output_field=DecimalField(max_digits=7, decimal_places=2),
                )
            ).order_by("-homepage_discount_percent", "-created_at")[:8],
            "services": Service.objects.filter(status="published")[:6],
            "latest_projects": Project.objects.filter(status="published")[:6],
            "latest_posts": Post.objects.filter(status="published")[:3],
            "hero_bg_image": GalleryItem.objects.filter(
                use_as_hero_background=True, media_type=GalleryItem.MEDIA_IMAGE
            ).first(),
        })
        return ctx
