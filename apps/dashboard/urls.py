from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardHomeView.as_view(), name="home"),

    # محصولات
    path("products/", views.DashboardProductListView.as_view(), name="product_list"),
    path("products/add/", views.DashboardProductCreateView.as_view(), name="product_add"),
    path("products/<int:pk>/edit/", views.DashboardProductUpdateView.as_view(), name="product_edit"),
    path("products/<int:pk>/delete/", views.DashboardProductDeleteView.as_view(), name="product_delete"),
    path("products/categories/", views.DashboardProductCategoryListView.as_view(), name="product_category_list"),
    path("products/categories/add/", views.DashboardProductCategoryCreateView.as_view(), name="product_category_add"),
    path("products/categories/<int:pk>/edit/", views.DashboardProductCategoryUpdateView.as_view(), name="product_category_edit"),
    path("products/categories/<int:pk>/delete/", views.DashboardProductCategoryDeleteView.as_view(), name="product_category_delete"),
    path("products/filters/", views.DashboardCategoryAttributeListView.as_view(), name="category_attribute_list"),
    path("products/filters/add/", views.DashboardCategoryAttributeCreateView.as_view(), name="category_attribute_add"),
    path("products/filters/<int:pk>/edit/", views.DashboardCategoryAttributeUpdateView.as_view(), name="category_attribute_edit"),
    path("products/filters/<int:pk>/delete/", views.DashboardCategoryAttributeDeleteView.as_view(), name="category_attribute_delete"),
    path("products/reviews/", views.DashboardProductReviewListView.as_view(), name="product_review_list"),
    path("products/reviews/<int:pk>/approve/", views.DashboardApproveProductReviewView.as_view(), name="product_review_approve"),
    path("products/reviews/<int:pk>/delete/", views.DashboardDeleteProductReviewView.as_view(), name="product_review_delete"),

    # خدمات
    path("services/", views.DashboardServiceListView.as_view(), name="service_list"),
    path("services/add/", views.DashboardServiceCreateView.as_view(), name="service_add"),
    path("services/<int:pk>/edit/", views.DashboardServiceUpdateView.as_view(), name="service_edit"),
    path("services/<int:pk>/delete/", views.DashboardServiceDeleteView.as_view(), name="service_delete"),

    # پروژه‌ها
    path("projects/", views.DashboardProjectListView.as_view(), name="project_list"),
    path("projects/add/", views.DashboardProjectCreateView.as_view(), name="project_add"),
    path("projects/<int:pk>/edit/", views.DashboardProjectUpdateView.as_view(), name="project_edit"),
    path("projects/<int:pk>/delete/", views.DashboardProjectDeleteView.as_view(), name="project_delete"),

    # وبلاگ
    path("blog/", views.DashboardPostListView.as_view(), name="post_list"),
    path("blog/add/", views.DashboardPostCreateView.as_view(), name="post_add"),
    path("blog/<int:pk>/edit/", views.DashboardPostUpdateView.as_view(), name="post_edit"),
    path("blog/<int:pk>/delete/", views.DashboardPostDeleteView.as_view(), name="post_delete"),
    path("blog/comments/", views.DashboardCommentListView.as_view(), name="comment_list"),
    path("blog/comments/<int:pk>/approve/", views.DashboardApproveCommentView.as_view(), name="comment_approve"),
    path("blog/comments/<int:pk>/delete/", views.DashboardDeleteCommentView.as_view(), name="comment_delete"),

    # گالری
    path("gallery/", views.DashboardGalleryListView.as_view(), name="gallery_list"),
    path("gallery/add/", views.DashboardGalleryCreateView.as_view(), name="gallery_add"),
    path("gallery/<int:pk>/edit/", views.DashboardGalleryUpdateView.as_view(), name="gallery_edit"),
    path("gallery/<int:pk>/delete/", views.DashboardGalleryDeleteView.as_view(), name="gallery_delete"),
    path("gallery/<int:pk>/set-hero-background/", views.DashboardSetHeroBackgroundView.as_view(), name="gallery_set_hero_bg"),
    path("gallery/<int:pk>/remove-hero-background/", views.DashboardRemoveHeroBackgroundView.as_view(), name="gallery_remove_hero_bg"),

    # صندوق‌های ورودی (پیام‌ها / استعلام قیمت / استخدام)
    path("inbox/messages/", views.DashboardContactMessageListView.as_view(), name="message_list"),
    path("inbox/messages/<int:pk>/mark-read/", views.DashboardMarkMessageReadView.as_view(), name="message_mark_read"),
    path("inbox/quotes/", views.DashboardQuoteRequestListView.as_view(), name="quote_list"),
    path("inbox/quotes/<int:pk>/mark-processed/", views.DashboardMarkQuoteProcessedView.as_view(), name="quote_mark_processed"),
    path("inbox/product-inquiries/", views.DashboardProductInquiryListView.as_view(), name="inquiry_list"),
    path("inbox/product-inquiries/<int:pk>/mark-read/", views.DashboardMarkInquiryReadView.as_view(), name="inquiry_mark_read"),
    path("inbox/applications/", views.DashboardJobApplicationListView.as_view(), name="application_list"),
    path("inbox/applications/<int:pk>/mark-reviewed/", views.DashboardMarkApplicationReviewedView.as_view(), name="application_mark_reviewed"),

    # فرصت‌های شغلی
    path("careers/", views.DashboardJobPositionListView.as_view(), name="job_position_list"),
    path("careers/add/", views.DashboardJobPositionCreateView.as_view(), name="job_position_add"),
    path("careers/<int:pk>/edit/", views.DashboardJobPositionUpdateView.as_view(), name="job_position_edit"),

    # سفارشات فروشگاه
    path("orders/", views.DashboardOrderListView.as_view(), name="order_list"),
    path("orders/<int:pk>/", views.DashboardOrderDetailView.as_view(), name="order_detail"),
    path("orders/<int:pk>/update-status/", views.DashboardUpdateOrderStatusView.as_view(), name="order_update_status"),

    # کدهای تخفیف
    path("coupons/", views.DashboardCouponListView.as_view(), name="coupon_list"),
    path("coupons/add/", views.DashboardCouponCreateView.as_view(), name="coupon_add"),
    path("coupons/<int:pk>/edit/", views.DashboardCouponUpdateView.as_view(), name="coupon_edit"),

    # ---------------------------------------------------------------------
    # محتوای سایت (اپ core) -- تنظیمات سایت، اسلایدر، بنر تبلیغاتی،
    # گواهینامه‌ها، برندهای همکار، نظرات مشتریان، سوالات متداول، منوها
    # ---------------------------------------------------------------------
    path("site-settings/", views.DashboardSiteSettingUpdateView.as_view(), name="site_settings"),

    path("home-slides/", views.DashboardHomeSlideListView.as_view(), name="home_slide_list"),
    path("home-slides/add/", views.DashboardHomeSlideCreateView.as_view(), name="home_slide_add"),
    path("home-slides/<int:pk>/edit/", views.DashboardHomeSlideUpdateView.as_view(), name="home_slide_edit"),
    path("home-slides/<int:pk>/delete/", views.DashboardHomeSlideDeleteView.as_view(), name="home_slide_delete"),

    path("promo-banners/", views.DashboardPromoBannerListView.as_view(), name="promo_banner_list"),
    path("promo-banners/add/", views.DashboardPromoBannerCreateView.as_view(), name="promo_banner_add"),
    path("promo-banners/<int:pk>/edit/", views.DashboardPromoBannerUpdateView.as_view(), name="promo_banner_edit"),
    path("promo-banners/<int:pk>/delete/", views.DashboardPromoBannerDeleteView.as_view(), name="promo_banner_delete"),

    path("statistics/", views.DashboardStatisticListView.as_view(), name="statistic_list"),
    path("statistics/add/", views.DashboardStatisticCreateView.as_view(), name="statistic_add"),
    path("statistics/<int:pk>/edit/", views.DashboardStatisticUpdateView.as_view(), name="statistic_edit"),
    path("statistics/<int:pk>/delete/", views.DashboardStatisticDeleteView.as_view(), name="statistic_delete"),

    path("certificates/", views.DashboardCertificateListView.as_view(), name="certificate_list"),
    path("certificates/add/", views.DashboardCertificateCreateView.as_view(), name="certificate_add"),
    path("certificates/<int:pk>/edit/", views.DashboardCertificateUpdateView.as_view(), name="certificate_edit"),
    path("certificates/<int:pk>/delete/", views.DashboardCertificateDeleteView.as_view(), name="certificate_delete"),

    path("partners/", views.DashboardPartnerListView.as_view(), name="partner_list"),
    path("partners/add/", views.DashboardPartnerCreateView.as_view(), name="partner_add"),
    path("partners/<int:pk>/edit/", views.DashboardPartnerUpdateView.as_view(), name="partner_edit"),
    path("partners/<int:pk>/delete/", views.DashboardPartnerDeleteView.as_view(), name="partner_delete"),

    path("testimonials/", views.DashboardTestimonialListView.as_view(), name="testimonial_list"),
    path("testimonials/add/", views.DashboardTestimonialCreateView.as_view(), name="testimonial_add"),
    path("testimonials/<int:pk>/edit/", views.DashboardTestimonialUpdateView.as_view(), name="testimonial_edit"),
    path("testimonials/<int:pk>/delete/", views.DashboardTestimonialDeleteView.as_view(), name="testimonial_delete"),

    path("faqs/", views.DashboardFAQListView.as_view(), name="faq_list"),
    path("faqs/add/", views.DashboardFAQCreateView.as_view(), name="faq_add"),
    path("faqs/<int:pk>/edit/", views.DashboardFAQUpdateView.as_view(), name="faq_edit"),
    path("faqs/<int:pk>/delete/", views.DashboardFAQDeleteView.as_view(), name="faq_delete"),

    path("menus/", views.DashboardMenuListView.as_view(), name="menu_list"),
    path("menus/add/", views.DashboardMenuCreateView.as_view(), name="menu_add"),
    path("menus/<int:pk>/edit/", views.DashboardMenuUpdateView.as_view(), name="menu_edit"),
    path("menus/<int:pk>/delete/", views.DashboardMenuDeleteView.as_view(), name="menu_delete"),

    path("quick-circles/", views.DashboardQuickCircleListView.as_view(), name="quick_circle_list"),
    path("quick-circles/add/", views.DashboardQuickCircleCreateView.as_view(), name="quick_circle_add"),
    path("quick-circles/<int:pk>/edit/", views.DashboardQuickCircleUpdateView.as_view(), name="quick_circle_edit"),
    path("quick-circles/<int:pk>/delete/", views.DashboardQuickCircleDeleteView.as_view(), name="quick_circle_delete"),

    path("brands/", views.DashboardBrandListView.as_view(), name="brand_list"),
    path("brands/add/", views.DashboardBrandCreateView.as_view(), name="brand_add"),
    path("brands/<int:pk>/edit/", views.DashboardBrandUpdateView.as_view(), name="brand_edit"),
    path("brands/<int:pk>/delete/", views.DashboardBrandDeleteView.as_view(), name="brand_delete"),

]
