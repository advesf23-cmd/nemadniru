"""
config/urls.py -- روتینگ اصلی پروژه
هر اپ URLهای خودش را در فایل جداگانه (apps/<app>/urls.py) نگه می‌دارد.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.generic import TemplateView

from apps.core.sitemaps import sitemaps

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots_txt"),
    path("dashboard/", include("apps.dashboard.urls", namespace="dashboard")),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("products/", include("apps.products.urls", namespace="products")),
    path("services/", include("apps.services.urls", namespace="services")),
    path("projects/", include("apps.projects.urls", namespace="projects")),
    path("blog/", include("apps.blog.urls", namespace="blog")),
    path("gallery/", include("apps.gallery.urls", namespace="gallery")),
    path("contact/", include("apps.contact.urls", namespace="contact")),
    path("", include("apps.pages.urls", namespace="pages")),
    path("shop/", include("apps.shop.urls", namespace="shop")),
    path("", include("apps.core.urls", namespace="core")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
