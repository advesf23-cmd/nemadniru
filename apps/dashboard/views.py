from django.contrib import messages as django_messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView, View
)
from apps.products.models import (
     Product, ProductCategory, ProductInquiry, ProductReview, Brand
)

from apps.products.models import Product, ProductCategory, ProductInquiry, ProductReview
from apps.services.models import Service
from apps.projects.models import Project, ProjectCategory
from apps.blog.models import Post, BlogCategory, Comment
from apps.gallery.models import GalleryItem
from apps.contact.models import ContactMessage, QuoteRequest, JobApplication, JobPosition
from apps.shop.models import Order, Coupon
from apps.core.models import (
    SiteSetting, Statistic, Certificate, Partner, Testimonial, FAQ, HomeSlide, Menu, PromoBanner
)
from apps.core.models import (
    SiteSetting, Statistic, Certificate, Partner, Testimonial, FAQ,
    HomeSlide, Menu, PromoBanner, QuickCircle
    )

class StaffRequiredMixin(UserPassesTestMixin):
    """فقط کاربران دارای نقش مدیریتی (Super Admin/Admin/Editor/Content Manager) اجازه دسترسی دارند"""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff_role

    def handle_no_permission(self):
        django_messages.error(self.request, "شما دسترسی لازم برای ورود به داشبورد را ندارید.")
        return redirect("accounts:login")


class DashboardHomeView(StaffRequiredMixin, TemplateView):
    """صفحه اصلی داشبورد -- خلاصه آماری کامل و لینک‌های سریع"""
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            "products_count": Product.objects.count(),
            "services_count": Service.objects.count(),
            "projects_count": Project.objects.count(),
            "posts_count": Post.objects.count(),
            "unread_inquiries": ProductInquiry.objects.filter(is_read=False).count(),
            "unread_messages": ContactMessage.objects.filter(is_read=False).count(),
            "unread_quotes": QuoteRequest.objects.filter(is_read=False).count(),
            "new_applications": JobApplication.objects.filter(is_reviewed=False).count(),
            "pending_orders": Order.objects.filter(status=Order.STATUS_PENDING_PAYMENT).count(),
            "total_orders": Order.objects.count(),
            "recent_messages": ContactMessage.objects.all()[:5],
            "recent_quotes": QuoteRequest.objects.all()[:5],
        })
        return ctx


# ---------------------------------------------------------------------------
# مدیریت محصولات
# ---------------------------------------------------------------------------
class DashboardProductListView(StaffRequiredMixin, ListView):
    model = Product
    template_name = "dashboard/products/list.html"
    context_object_name = "products"
    paginate_by = 20

    def get_queryset(self):
        qs = Product.objects.select_related("category").all()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(name__icontains=q)
        return qs


class DashboardProductCreateView(StaffRequiredMixin, CreateView):
    model = Product
    fields = [
         "category", "brand", "name", "sku", "mpn",
         "short_description", "description", "technical_description",
         "cover_image",
         "price", "discount_price", "discount_percent_override",
         "stock_quantity", "is_orderable",
         "status", "is_featured", "order",
         "meta_title", "meta_description",
     ]

    template_name = "dashboard/products/form.html"
    success_url = reverse_lazy("dashboard:product_list")

    def form_valid(self, form):
        django_messages.success(self.request, "محصول با موفقیت ایجاد شد.")
        return super().form_valid(form)


class DashboardProductUpdateView(StaffRequiredMixin, UpdateView):
    model = Product
    fields = DashboardProductCreateView.fields
    template_name = "dashboard/products/form.html"
    success_url = reverse_lazy("dashboard:product_list")

    def form_valid(self, form):
        django_messages.success(self.request, "محصول با موفقیت بروزرسانی شد.")
        return super().form_valid(form)


class DashboardProductDeleteView(StaffRequiredMixin, DeleteView):
    model = Product
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:product_list")

    def form_valid(self, form):
        django_messages.success(self.request, "محصول حذف شد.")
        return super().form_valid(form)


class DashboardProductCategoryListView(StaffRequiredMixin, ListView):
    model = ProductCategory
    template_name = "dashboard/products/category_list.html"
    context_object_name = "categories"


class DashboardProductCategoryCreateView(StaffRequiredMixin, CreateView):
    model = ProductCategory
    fields = ["name", "parent", "icon", "image", "description", "order", "is_active"]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:product_category_list")


class DashboardProductCategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = ProductCategory
    fields = DashboardProductCategoryCreateView.fields
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:product_category_list")


class DashboardProductCategoryDeleteView(StaffRequiredMixin, DeleteView):
    model = ProductCategory
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:product_category_list")


class DashboardProductReviewListView(StaffRequiredMixin, ListView):
    model = ProductReview
    template_name = "dashboard/products/review_list.html"
    context_object_name = "reviews"
    paginate_by = 20

    def get_queryset(self):
        return ProductReview.objects.select_related("product").order_by("-created_at")


class DashboardApproveProductReviewView(StaffRequiredMixin, View):
    def post(self, request, pk):
        review = get_object_or_404(ProductReview, pk=pk)
        review.is_approved = True
        review.save(update_fields=["is_approved"])
        django_messages.success(request, "نظر تأیید و منتشر شد.")
        return redirect("dashboard:product_review_list")


class DashboardDeleteProductReviewView(StaffRequiredMixin, View):
    def post(self, request, pk):
        review = get_object_or_404(ProductReview, pk=pk)
        review.delete()
        django_messages.success(request, "نظر حذف شد.")
        return redirect("dashboard:product_review_list")


# ---------------------------------------------------------------------------
# مدیریت خدمات
# ---------------------------------------------------------------------------
class DashboardServiceListView(StaffRequiredMixin, ListView):
    model = Service
    template_name = "dashboard/services/list.html"
    context_object_name = "services"


class DashboardServiceCreateView(StaffRequiredMixin, CreateView):
    model = Service
    fields = [
        "title", "short_description", "description", "icon", "cover_image",
        "status", "is_featured", "order", "meta_title", "meta_description",
    ]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:service_list")


class DashboardServiceUpdateView(StaffRequiredMixin, UpdateView):
    model = Service
    fields = DashboardServiceCreateView.fields
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:service_list")


class DashboardServiceDeleteView(StaffRequiredMixin, DeleteView):
    model = Service
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:service_list")


# ---------------------------------------------------------------------------
# مدیریت پروژه‌ها
# ---------------------------------------------------------------------------
class DashboardProjectListView(StaffRequiredMixin, ListView):
    model = Project
    template_name = "dashboard/projects/list.html"
    context_object_name = "projects"
    paginate_by = 20


class DashboardProjectCreateView(StaffRequiredMixin, CreateView):
    model = Project
    fields = [
        "category", "title", "client_name", "location", "execution_year",
        "short_description", "description", "cover_image",
        "status", "is_featured", "order", "meta_title", "meta_description",
    ]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:project_list")


class DashboardProjectUpdateView(StaffRequiredMixin, UpdateView):
    model = Project
    fields = DashboardProjectCreateView.fields
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:project_list")


class DashboardProjectDeleteView(StaffRequiredMixin, DeleteView):
    model = Project
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:project_list")


# ---------------------------------------------------------------------------
# مدیریت وبلاگ
# ---------------------------------------------------------------------------
class DashboardPostListView(StaffRequiredMixin, ListView):
    model = Post
    template_name = "dashboard/blog/list.html"
    context_object_name = "posts"
    paginate_by = 20


class DashboardPostCreateView(StaffRequiredMixin, CreateView):
    model = Post
    fields = [
        "category", "tags", "title", "summary", "content", "cover_image",
        "published_at", "status", "is_featured", "order", "meta_title", "meta_description",
    ]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:post_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class DashboardPostUpdateView(StaffRequiredMixin, UpdateView):
    model = Post
    fields = DashboardPostCreateView.fields
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:post_list")


class DashboardPostDeleteView(StaffRequiredMixin, DeleteView):
    model = Post
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:post_list")


class DashboardCommentListView(StaffRequiredMixin, ListView):
    model = Comment
    template_name = "dashboard/blog/comments.html"
    context_object_name = "comments"
    paginate_by = 20

    def get_queryset(self):
        return Comment.objects.select_related("post").order_by("-created_at")


class DashboardApproveCommentView(StaffRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.is_approved = True
        comment.save(update_fields=["is_approved"])
        django_messages.success(request, "نظر تأیید و منتشر شد.")
        return redirect("dashboard:comment_list")


class DashboardDeleteCommentView(StaffRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.delete()
        django_messages.success(request, "نظر حذف شد.")
        return redirect("dashboard:comment_list")


# ---------------------------------------------------------------------------
# مدیریت گالری
# ---------------------------------------------------------------------------
class DashboardGalleryListView(StaffRequiredMixin, ListView):
    model = GalleryItem
    template_name = "dashboard/gallery/list.html"
    context_object_name = "items"


class DashboardGalleryCreateView(StaffRequiredMixin, CreateView):
    model = GalleryItem
    fields = ["category", "media_type", "title", "image", "video_url", "order", "use_as_hero_background"]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:gallery_list")


class DashboardGalleryUpdateView(StaffRequiredMixin, UpdateView):
    model = GalleryItem
    fields = ["category", "media_type", "title", "image", "video_url", "order", "use_as_hero_background"]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:gallery_list")


class DashboardSetHeroBackgroundView(StaffRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(GalleryItem, pk=pk, media_type=GalleryItem.MEDIA_IMAGE)
        item.use_as_hero_background = True
        item.save()
        django_messages.success(request, f"تصویر «{item.title or item.pk}» به‌عنوان پس‌زمینه صفحه اصلی تنظیم شد.")
        return redirect("dashboard:gallery_list")


class DashboardRemoveHeroBackgroundView(StaffRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(GalleryItem, pk=pk)
        item.use_as_hero_background = False
        item.save(update_fields=["use_as_hero_background"])
        django_messages.success(request, "پس‌زمینه صفحه اصلی حذف شد.")
        return redirect("dashboard:gallery_list")


class DashboardGalleryDeleteView(StaffRequiredMixin, DeleteView):
    model = GalleryItem
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:gallery_list")


# ---------------------------------------------------------------------------
# پیام‌ها، استعلام قیمت‌ها و درخواست‌های استخدام (Inbox های عملیاتی)
# ---------------------------------------------------------------------------
class DashboardContactMessageListView(StaffRequiredMixin, ListView):
    model = ContactMessage
    template_name = "dashboard/inbox/messages.html"
    context_object_name = "messages_list"
    paginate_by = 20


class DashboardMarkMessageReadView(StaffRequiredMixin, View):
    def post(self, request, pk):
        obj = get_object_or_404(ContactMessage, pk=pk)
        obj.is_read = True
        obj.save(update_fields=["is_read"])
        django_messages.success(request, "پیام خوانده‌شده علامت‌گذاری شد.")
        return redirect("dashboard:message_list")


class DashboardQuoteRequestListView(StaffRequiredMixin, ListView):
    model = QuoteRequest
    template_name = "dashboard/inbox/quotes.html"
    context_object_name = "quotes"
    paginate_by = 20


class DashboardMarkQuoteProcessedView(StaffRequiredMixin, View):
    def post(self, request, pk):
        obj = get_object_or_404(QuoteRequest, pk=pk)
        obj.is_read = True
        obj.is_processed = True
        obj.save(update_fields=["is_read", "is_processed"])
        django_messages.success(request, "درخواست استعلام قیمت پردازش‌شده علامت‌گذاری شد.")
        return redirect("dashboard:quote_list")


class DashboardProductInquiryListView(StaffRequiredMixin, ListView):
    model = ProductInquiry
    template_name = "dashboard/inbox/inquiries.html"
    context_object_name = "inquiries"
    paginate_by = 20


class DashboardMarkInquiryReadView(StaffRequiredMixin, View):
    def post(self, request, pk):
        obj = get_object_or_404(ProductInquiry, pk=pk)
        obj.is_read = True
        obj.save(update_fields=["is_read"])
        django_messages.success(request, "استعلام قیمت خوانده‌شده علامت‌گذاری شد.")
        return redirect("dashboard:inquiry_list")


class DashboardJobApplicationListView(StaffRequiredMixin, ListView):
    model = JobApplication
    template_name = "dashboard/inbox/applications.html"
    context_object_name = "applications"
    paginate_by = 20


class DashboardMarkApplicationReviewedView(StaffRequiredMixin, View):
    def post(self, request, pk):
        obj = get_object_or_404(JobApplication, pk=pk)
        obj.is_reviewed = True
        obj.save(update_fields=["is_reviewed"])
        django_messages.success(request, "درخواست استخدام بررسی‌شده علامت‌گذاری شد.")
        return redirect("dashboard:application_list")


class DashboardJobPositionListView(StaffRequiredMixin, ListView):
    model = JobPosition
    template_name = "dashboard/jobs/list.html"
    context_object_name = "positions"


class DashboardJobPositionCreateView(StaffRequiredMixin, CreateView):
    model = JobPosition
    fields = ["title", "department", "location", "employment_type", "description", "requirements", "is_active"]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:job_position_list")


class DashboardJobPositionUpdateView(StaffRequiredMixin, UpdateView):
    model = JobPosition
    fields = DashboardJobPositionCreateView.fields
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:job_position_list")


# ---------------------------------------------------------------------------
# مدیریت سفارشات فروشگاه و کدهای تخفیف
# ---------------------------------------------------------------------------
class DashboardOrderListView(StaffRequiredMixin, ListView):
    model = Order
    template_name = "dashboard/shop/order_list.html"
    context_object_name = "orders"
    paginate_by = 20

    def get_queryset(self):
        qs = Order.objects.all()
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs


class DashboardOrderDetailView(StaffRequiredMixin, DetailView):
    model = Order
    template_name = "dashboard/shop/order_detail.html"
    context_object_name = "order"


class DashboardUpdateOrderStatusView(StaffRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get("status")
        if new_status in dict(Order.STATUS_CHOICES):
            from apps.shop.views import send_order_email
            import logging
            logger = logging.getLogger("apps.shop")

            if new_status == Order.STATUS_CANCELLED:
                order.cancel(reason="لغو توسط مدیر فروشگاه")
                logger.info("Order %s cancelled by staff %s", order.order_number, request.user)
            else:
                order.status = new_status
                order.save(update_fields=["status", "updated_at"])
                logger.info("Order %s status changed to %s by staff %s", order.order_number, new_status, request.user)

            send_order_email(order, "بروزرسانی وضعیت سفارش", f"وضعیت سفارش شما به «{order.get_status_display()}» تغییر کرد.")
            django_messages.success(request, "وضعیت سفارش بروزرسانی شد.")
        return redirect("dashboard:order_detail", pk=pk)


class DashboardCouponListView(StaffRequiredMixin, ListView):
    model = Coupon
    template_name = "dashboard/shop/coupon_list.html"
    context_object_name = "coupons"


class DashboardCouponCreateView(StaffRequiredMixin, CreateView):
    model = Coupon
    fields = ["code", "discount_type", "discount_value", "max_uses", "valid_from", "valid_to", "is_active"]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:coupon_list")


class DashboardCouponUpdateView(StaffRequiredMixin, UpdateView):
    model = Coupon
    fields = DashboardCouponCreateView.fields
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:coupon_list")


# ===========================================================================
# مدیریت محتوای سراسری سایت (اپ core) -- تنظیمات سایت، اسلایدر صفحه اصلی،
# بنرهای تبلیغاتی، گواهینامه‌ها، برندهای همکار، نظرات مشتریان، سوالات متداول، منوها.
# قبلاً این‌ها فقط از Django Admin خام قابل مدیریت بودند؛ حالا در همین داشبورد هم هستند.
# ===========================================================================

class DashboardSiteSettingUpdateView(StaffRequiredMixin, UpdateView):
    """تنظیمات سایت -- Singleton (فقط یک رکورد، همیشه pk=1)"""
    model = SiteSetting
    fields = [
        "site_name", "logo", "favicon", "phone", "email", "address", "working_hours",
        "map_embed_url", "instagram", "telegram", "whatsapp", "linkedin",
        "footer_text", "default_meta_description", "google_analytics_id",
        "quick_circles_heading",
    ]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:site_settings")

    def get_object(self, queryset=None):
        obj, _ = SiteSetting.objects.get_or_create(pk=1)
        return obj

    def form_valid(self, form):
        django_messages.success(self.request, "تنظیمات سایت با موفقیت ذخیره شد.")
        return super().form_valid(form)



class DashboardHomeSlideListView(StaffRequiredMixin, ListView):
    model = HomeSlide
    template_name = "dashboard/core/home_slide_list.html"
    context_object_name = "slides"


class DashboardHomeSlideCreateView(StaffRequiredMixin, CreateView):
    model = HomeSlide
    fields = ["title", "subtitle", "image", "button_text", "button_url", "order", "is_active"]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:home_slide_list")


class DashboardHomeSlideUpdateView(StaffRequiredMixin, UpdateView):
    model = HomeSlide
    fields = DashboardHomeSlideCreateView.fields
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:home_slide_list")


class DashboardHomeSlideDeleteView(StaffRequiredMixin, DeleteView):
    model = HomeSlide
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:home_slide_list")


class DashboardPromoBannerListView(StaffRequiredMixin, ListView):
    model = PromoBanner
    template_name = "dashboard/core/promo_banner_list.html"
    context_object_name = "banners"


class DashboardPromoBannerCreateView(StaffRequiredMixin, CreateView):
    model = PromoBanner
    fields = ["image", "title", "link_url", "order", "is_active"]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:promo_banner_list")


class DashboardPromoBannerUpdateView(StaffRequiredMixin, UpdateView):
    model = PromoBanner
    fields = DashboardPromoBannerCreateView.fields
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:promo_banner_list")


class DashboardPromoBannerDeleteView(StaffRequiredMixin, DeleteView):
    model = PromoBanner
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:promo_banner_list")


class DashboardStatisticListView(StaffRequiredMixin, ListView):
    model = Statistic
    template_name = "dashboard/core/statistic_list.html"
    context_object_name = "statistics"


class DashboardStatisticCreateView(StaffRequiredMixin, CreateView):
    model = Statistic
    fields = ["title", "value", "icon", "order"]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:statistic_list")


class DashboardStatisticUpdateView(StaffRequiredMixin, UpdateView):
    model = Statistic
    fields = DashboardStatisticCreateView.fields
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:statistic_list")


class DashboardStatisticDeleteView(StaffRequiredMixin, DeleteView):
    model = Statistic
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:statistic_list")


class DashboardCertificateListView(StaffRequiredMixin, ListView):
    model = Certificate
    template_name = "dashboard/core/certificate_list.html"
    context_object_name = "certificates"


class DashboardCertificateCreateView(StaffRequiredMixin, CreateView):
    model = Certificate
    fields = ["title", "description", "image", "icon", "order"]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:certificate_list")


class DashboardCertificateUpdateView(StaffRequiredMixin, UpdateView):
    model = Certificate
    fields = DashboardCertificateCreateView.fields
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:certificate_list")


class DashboardCertificateDeleteView(StaffRequiredMixin, DeleteView):
    model = Certificate
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:certificate_list")


class DashboardPartnerListView(StaffRequiredMixin, ListView):
    model = Partner
    template_name = "dashboard/core/partner_list.html"
    context_object_name = "partners"


class DashboardPartnerCreateView(StaffRequiredMixin, CreateView):
    model = Partner
    fields = ["name", "tagline", "logo", "website", "order"]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:partner_list")


class DashboardPartnerUpdateView(StaffRequiredMixin, UpdateView):
    model = Partner
    fields = DashboardPartnerCreateView.fields
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:partner_list")


class DashboardPartnerDeleteView(StaffRequiredMixin, DeleteView):
    model = Partner
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:partner_list")


class DashboardTestimonialListView(StaffRequiredMixin, ListView):
    model = Testimonial
    template_name = "dashboard/core/testimonial_list.html"
    context_object_name = "testimonials"


class DashboardTestimonialCreateView(StaffRequiredMixin, CreateView):
    model = Testimonial
    fields = ["client_name", "company_name", "photo", "text", "rating", "order"]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:testimonial_list")


class DashboardTestimonialUpdateView(StaffRequiredMixin, UpdateView):
    model = Testimonial
    fields = DashboardTestimonialCreateView.fields
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:testimonial_list")


class DashboardTestimonialDeleteView(StaffRequiredMixin, DeleteView):
    model = Testimonial
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:testimonial_list")


class DashboardFAQListView(StaffRequiredMixin, ListView):
    model = FAQ
    template_name = "dashboard/core/faq_list.html"
    context_object_name = "faqs"


class DashboardFAQCreateView(StaffRequiredMixin, CreateView):
    model = FAQ
    fields = ["question", "answer", "order"]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:faq_list")


class DashboardFAQUpdateView(StaffRequiredMixin, UpdateView):
    model = FAQ
    fields = DashboardFAQCreateView.fields
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:faq_list")


class DashboardFAQDeleteView(StaffRequiredMixin, DeleteView):
    model = FAQ
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:faq_list")


class DashboardMenuListView(StaffRequiredMixin, ListView):
    model = Menu
    template_name = "dashboard/core/menu_list.html"
    context_object_name = "menu_items"


class DashboardMenuCreateView(StaffRequiredMixin, CreateView):
    model = Menu
    fields = ["title", "url", "parent", "location", "order", "is_active"]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:menu_list")


class DashboardMenuUpdateView(StaffRequiredMixin, UpdateView):
    model = Menu
    fields = DashboardMenuCreateView.fields
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:menu_list")


class DashboardMenuDeleteView(StaffRequiredMixin, DeleteView):
    model = Menu
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:menu_list")

class DashboardQuickCircleListView(StaffRequiredMixin, ListView):
    model = QuickCircle
    template_name = "dashboard/core/quick_circle_list.html"
    context_object_name = "circles"


class DashboardQuickCircleCreateView(StaffRequiredMixin, CreateView):
    model = QuickCircle
    fields = ["title", "image", "link_url", "order", "is_active"]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:quick_circle_list")


class DashboardQuickCircleUpdateView(StaffRequiredMixin, UpdateView):
    model = QuickCircle
    fields = DashboardQuickCircleCreateView.fields
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:quick_circle_list")


class DashboardQuickCircleDeleteView(StaffRequiredMixin, DeleteView):
    model = QuickCircle
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:quick_circle_list")

class DashboardBrandListView(StaffRequiredMixin, ListView):
    model = Brand
    template_name = "dashboard/products/brand_list.html"
    context_object_name = "brands"


class DashboardBrandCreateView(StaffRequiredMixin, CreateView):
    model = Brand
    fields = ["name", "logo", "default_discount_percent", "is_active"]
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:brand_list")


class DashboardBrandUpdateView(StaffRequiredMixin, UpdateView):
    model = Brand
    fields = DashboardBrandCreateView.fields
    template_name = "dashboard/generic_form.html"
    success_url = reverse_lazy("dashboard:brand_list")


class DashboardBrandDeleteView(StaffRequiredMixin, DeleteView):
    model = Brand
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:brand_list")
