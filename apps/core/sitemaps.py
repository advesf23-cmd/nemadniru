from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.products.models import Product, ProductCategory
from apps.projects.models import Project
from apps.services.models import Service
from apps.blog.models import Post
from apps.pages.models import Page


class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return ["core:home", "pages:about", "products:product_list", "services:service_list",
                "projects:project_list", "blog:post_list", "gallery:gallery_list",
                "contact:contact", "contact:quote_request", "contact:careers"]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Product.objects.filter(status="published")

    def lastmod(self, obj):
        return obj.updated_at


class ProductCategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return ProductCategory.objects.filter(is_active=True)

    def location(self, obj):
        return obj.get_absolute_url()


class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Project.objects.filter(status="published")

    def lastmod(self, obj):
        return obj.updated_at


class ServiceSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Service.objects.filter(status="published")

    def lastmod(self, obj):
        return obj.updated_at


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Post.objects.filter(status="published")

    def lastmod(self, obj):
        return obj.updated_at


class PageSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.4

    def items(self):
        return Page.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {
    "static": StaticViewSitemap,
    "products": ProductSitemap,
    "product_categories": ProductCategorySitemap,
    "projects": ProjectSitemap,
    "services": ServiceSitemap,
    "blog": PostSitemap,
    "pages": PageSitemap,
}
