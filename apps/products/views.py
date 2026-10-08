from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, TemplateView

from .models import Product, ProductCategory, ProductInquiry, ProductReview, ProductSpecification, CategoryAttributeTemplate

WISHLIST_SESSION_KEY = "wishlist_product_ids"
COMPARE_SESSION_KEY = "compare_product_ids"
COMPARE_MAX_ITEMS = 4


class ProductFilterMixin:
    """
    منطق مشترک فیلتر/جستجو/مرتب‌سازی محصولات -- هم برای درخواست معمولی
    و هم درخواست AJAX. brand حالا یک ForeignKey به مدل Brand است (نه متن
    آزاد)، پس فیلتر و جستجو روی brand__name انجام می‌شود.
    """
    SORT_OPTIONS = {
        "newest": "-created_at",
        "price_asc": "price",
        "price_desc": "-price",
        "name": "name",
    }

    def get_base_queryset(self):
        return Product.objects.filter(status="published").select_related("category", "brand")

    def apply_filters(self, qs):
        request = self.request
        category_slug = request.GET.get("category")
        search_query = request.GET.get("q")
        brand = request.GET.get("brand")
        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")
        sort = request.GET.get("sort", "newest")

        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if search_query:
            qs = qs.filter(
                Q(name__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(brand__name__icontains=search_query) |
                Q(mpn__icontains=search_query) |
                Q(sku__icontains=search_query)
            )
        if brand:
            qs = qs.filter(brand__name__iexact=brand)
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)

        # فیلترهای فنی کاملاً داینامیک هستند و تعریف آن‌ها از داشبورد می‌آید.
        # کلید پارامترها با attr_<id> ساخته می‌شود تا نام مشخصه بتواند فارسی/تکراری باشد.
        category_for_filters = None
        if category_slug:
            category_for_filters = ProductCategory.objects.filter(
                slug=category_slug, is_active=True
            ).first()
        elif getattr(self, "category", None):
            category_for_filters = self.category

        if category_for_filters:
            filter_templates = CategoryAttributeTemplate.objects.filter(
                category=category_for_filters,
                is_filterable=True,
            ).order_by("order", "name")
            for template in filter_templates:
                param = f"attr_{template.pk}"
                raw_values = request.GET.getlist(param)
                if not raw_values:
                    continue
                if template.filter_type in (
                    CategoryAttributeTemplate.FILTER_TYPE_SELECT,
                    CategoryAttributeTemplate.FILTER_TYPE_MULTISELECT,
                ):
                    values = [value.strip() for value in raw_values if value.strip()]
                    if values:
                        qs = qs.filter(
                            specifications__key=template.name,
                            specifications__value__in=values,
                        )
                elif template.filter_type == CategoryAttributeTemplate.FILTER_TYPE_BOOLEAN:
                    values = {value.lower() for value in raw_values}
                    if values & {"1", "true", "yes", "بله"}:
                        qs = qs.filter(
                            specifications__key=template.name,
                            specifications__value__iregex=r"^(1|true|yes|بله|دارد|موجود)$",
                        )
                    elif values & {"0", "false", "no", "خیر"}:
                        qs = qs.exclude(
                            specifications__key=template.name,
                            specifications__value__iregex=r"^(1|true|yes|بله|دارد|موجود)$",
                        )
                elif template.filter_type == CategoryAttributeTemplate.FILTER_TYPE_RANGE:
                    min_value = request.GET.get(f"{param}_min")
                    max_value = request.GET.get(f"{param}_max")
                    if min_value or max_value:
                        from django.db.models import DecimalField, Value
                        from django.db.models.functions import Cast, Replace, Trim
                        spec_qs = ProductSpecification.objects.filter(
                            product_id=OuterRef("pk"),
                            key=template.name,
                        ).annotate(
                            numeric_value=Cast(
                                Trim(Replace("value", Value(template.unit or ""), Value(""))),
                                DecimalField(max_digits=20, decimal_places=6),
                            )
                        )
                        if min_value:
                            spec_qs = spec_qs.filter(numeric_value__gte=min_value)
                        if max_value:
                            spec_qs = spec_qs.filter(numeric_value__lte=max_value)
                        qs = qs.filter(Exists(spec_qs))

        qs = qs.distinct().order_by(self.SORT_OPTIONS.get(sort, "-created_at"))
        return qs


class ProductListView(ProductFilterMixin, ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        return self.apply_filters(self.get_base_queryset())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = ProductCategory.objects.filter(is_active=True)
        # لیست نام برندهایی که حداقل یک محصول منتشرشده دارند (برای فیلتر سایدبار)
        ctx["brands"] = (
            Product.objects.filter(status="published", brand__isnull=False, brand__is_active=True)
            .values_list("brand__name", flat=True).distinct().order_by("brand__name")
        )
        ctx["current_sort"] = self.request.GET.get("sort", "newest")
        return ctx

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.GET.get("ajax"):
            html = render_to_string("products/_product_grid.html", context, request=request)
            pagination_html = render_to_string("products/_pagination.html", context, request=request)
            return JsonResponse({
                "html": html,
                "pagination": pagination_html,
                "count": context["paginator"].count,
            })
        return self.render_to_response(context)


class ProductCategoryDetailView(ProductFilterMixin, ListView):
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(ProductCategory, slug=self.kwargs["slug"], is_active=True)
        return self.apply_filters(self.get_base_queryset().filter(category=self.category))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = ProductCategory.objects.filter(is_active=True)
        ctx["current_category"] = self.category
        ctx["brands"] = (
            Product.objects.filter(status="published", category=self.category, brand__isnull=False, brand__is_active=True)
            .values_list("brand__name", flat=True).distinct().order_by("brand__name")
        )
        ctx["current_sort"] = self.request.GET.get("sort", "newest")
        return ctx

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.GET.get("ajax"):
            html = render_to_string("products/_product_grid.html", context, request=request)
            pagination_html = render_to_string("products/_pagination.html", context, request=request)
            return JsonResponse({
                "html": html,
                "pagination": pagination_html,
                "count": context["paginator"].count,
            })
        return self.render_to_response(context)


class ProductSearchSuggestView(TemplateView):
    """اندپوینت سبک برای پیشنهاد جستجوی زنده (Autocomplete) -- شامل جستجو بر اساس MPN هم می‌شود"""

    def get(self, request, *args, **kwargs):
        q = request.GET.get("q", "").strip()
        results = []
        if len(q) >= 2:
            products = Product.objects.filter(
                Q(name__icontains=q) | Q(mpn__icontains=q) | Q(sku__icontains=q),
                status="published",
            ).select_related("category")[:6]
            results = [
                {
                    "name": p.name,
                    "url": p.get_absolute_url(),
                    "image": p.cover_image.url if p.cover_image else "",
                    "category": p.category.name,
                }
                for p in products
            ]
        return JsonResponse({"results": results})


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"

    def get_queryset(self):
        return Product.objects.filter(status="published").select_related("brand", "category")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["related_products"] = Product.objects.filter(
            category=self.object.category, status="published"
        ).exclude(pk=self.object.pk)[:4]
        ctx["reviews"] = self.object.reviews.filter(is_approved=True)
        return ctx


class AddProductReviewView(View):
    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug, status="published")
        full_name = request.POST.get("full_name", "").strip()
        comment = request.POST.get("comment", "").strip()
        try:
            rating = int(request.POST.get("rating", 5))
        except (TypeError, ValueError):
            rating = 5
        rating = min(max(rating, 1), 5)

        if full_name and comment:
            ProductReview.objects.create(
                product=product,
                user=request.user if request.user.is_authenticated else None,
                full_name=full_name, rating=rating, comment=comment,
            )
            messages.success(request, "نظر شما ثبت شد و پس از تأیید مدیر نمایش داده خواهد شد.")
        else:
            messages.error(request, "لطفاً نام و متن نظر را وارد کنید.")
        return redirect(product.get_absolute_url() + "#reviews")


class ProductInquiryCreateView(CreateView):
    model = ProductInquiry
    fields = ["product", "full_name", "company_name", "phone", "email", "quantity", "message"]
    template_name = "products/product_inquiry_form.html"
    success_url = reverse_lazy("products:inquiry_success")

    def get_initial(self):
        initial = super().get_initial()
        product_id = self.request.GET.get("product")
        if product_id:
            initial["product"] = product_id
        return initial


class ProductInquirySuccessView(TemplateView):
    template_name = "products/inquiry_success.html"


# ---------------------------------------------------------------------------
# علاقه‌مندی‌ها (Wishlist) -- مبتنی بر Session
# ---------------------------------------------------------------------------
class WishlistToggleView(TemplateView):
    def post(self, request, *args, **kwargs):
        product_id = str(kwargs.get("pk"))
        wishlist = request.session.get(WISHLIST_SESSION_KEY, [])
        if product_id in wishlist:
            wishlist.remove(product_id)
            added = False
        else:
            wishlist.append(product_id)
            added = True
        request.session[WISHLIST_SESSION_KEY] = wishlist
        request.session.modified = True
        return JsonResponse({"added": added, "count": len(wishlist)})


class WishlistView(ListView):
    template_name = "products/wishlist.html"
    context_object_name = "products"

    def get_queryset(self):
        ids = self.request.session.get(WISHLIST_SESSION_KEY, [])
        return Product.objects.filter(pk__in=ids, status="published")


# ---------------------------------------------------------------------------
# مقایسه محصولات (Compare) -- حداکثر ۴ محصول، مبتنی بر Session
# ---------------------------------------------------------------------------
class CompareToggleView(TemplateView):
    def post(self, request, *args, **kwargs):
        product_id = str(kwargs.get("pk"))
        compare_list = request.session.get(COMPARE_SESSION_KEY, [])
        if product_id in compare_list:
            compare_list.remove(product_id)
            added = False
        elif len(compare_list) < COMPARE_MAX_ITEMS:
            compare_list.append(product_id)
            added = True
        else:
            return JsonResponse({
                "added": False, "count": len(compare_list),
                "error": f"حداکثر {COMPARE_MAX_ITEMS} محصول قابل مقایسه است.",
            })
        request.session[COMPARE_SESSION_KEY] = compare_list
        request.session.modified = True
        return JsonResponse({"added": added, "count": len(compare_list)})


class CompareView(ListView):
    template_name = "products/compare.html"
    context_object_name = "products"

    def get_queryset(self):
        ids = self.request.session.get(COMPARE_SESSION_KEY, [])
        return (
            Product.objects.filter(pk__in=ids, status="published")
            .select_related("brand").prefetch_related("specifications")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        products = ctx["products"]
        spec_keys = []
        for product in products:
            for spec in product.specifications.all():
                if spec.key not in spec_keys:
                    spec_keys.append(spec.key)
        ctx["spec_keys"] = spec_keys
        return ctx
