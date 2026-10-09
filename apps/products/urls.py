from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="product_list"),
    path("search-suggest/", views.ProductSearchSuggestView.as_view(), name="search_suggest"),
    path("admin-attributes/", views.admin_category_attributes, name="admin_category_attributes"),
    path("admin-attribute-values/", views.admin_attribute_values, name="admin_attribute_values"),
    path("wishlist/", views.WishlistView.as_view(), name="wishlist"),
    path("wishlist/<int:pk>/toggle/", views.WishlistToggleView.as_view(), name="wishlist_toggle"),
    path("compare/", views.CompareView.as_view(), name="compare"),
    path("compare/<int:pk>/toggle/", views.CompareToggleView.as_view(), name="compare_toggle"),
    path("category/<str:slug>/", views.ProductCategoryDetailView.as_view(), name="category_detail"),
    path("inquiry/", views.ProductInquiryCreateView.as_view(), name="inquiry_create"),
    path("inquiry/success/", views.ProductInquirySuccessView.as_view(), name="inquiry_success"),
    path("<str:slug>/review/", views.AddProductReviewView.as_view(), name="add_review"),
    path("<str:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
]
