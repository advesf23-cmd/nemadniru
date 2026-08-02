from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, TemplateView

from .models import Product, ProductCategory, ProductInquiry, ProductReview

WISHLIST_SESSION_KEY = "wishlist_product_ids"
COMPARE_SESSION_KEY = "compare_product_ids"
COMPARE_MAX_ITEMS = 4


class ProductFilterMixin:
    """
    منطق مشترک فیلتر/جستجو/مرتب‌سازی محصولات -- هم برای درخواست معمولی
    و هم درخواست AJAX (فیلتر زنده بدون رفرش صفحه) استفاده می‌شود.
    """
    SORT_OPTIONS = {
        "newest": "-created_at",
        "price_asc": "price",
        "price_desc": "-price",
        "name": "name",
    }

    def get_base_queryset(self):
        return Product.objects.filter(status="published").select_related("category")

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
                Q(brand__icontains=search_query)
            )
        if brand:
            qs = qs.filter(brand__iexact=brand)
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)

        qs = qs.order_by(self.SORT_OPTIONS.get(sort, "-created_at"))
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
        ctx["brands"] = (
            Product.objects.filter(status="published")
            .exclude(brand="").values_list("brand", flat=True).distinct().order_by("brand")
        )
        ctx["current_sort"] = self.request.GET.get("sort", "newest")
        return ctx

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        # درخواست AJAX -- فقط بخش گرید محصولات را بازمی‌گرداند (بدون رفرش کامل صفحه)
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
        self.category = ProductCategory.objects.get(slug=self.kwargs["slug"], is_active=True)
        return self.apply_filters(self.get_base_queryset().filter(category=self.category))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = ProductCategory.objects.filter(is_active=True)
        ctx["current_category"] = self.category
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
    """اندپوینت سبک برای پیشنهاد جستجوی زنده (Autocomplete) در نوار جستجو"""

    def get(self, request, *args, **kwargs):
        q = request.GET.get("q", "").strip()
        results = []
        if len(q) >= 2:
            products = Product.objects.filter(status="published", name__icontains=q)[:6]
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
        return Product.objects.filter(status="published")

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
# علاقه‌مندی‌ها (Wishlist) -- مبتنی بر Session، برای کاربر مهمان و عضو کار می‌کند
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
        return Product.objects.filter(pk__in=ids, status="published").prefetch_related("specifications")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        products = ctx["products"]
        # جمع‌آوری تمام کلیدهای مشخصات فنی موجود بین محصولات انتخاب‌شده برای رندر جدول مقایسه
        spec_keys = []
        for product in products:
            for spec in product.specifications.all():
                if spec.key not in spec_keys:
                    spec_keys.append(spec.key)
        ctx["spec_keys"] = spec_keys
        return ctx
