from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("cart/", views.CartDetailView.as_view(), name="cart_detail"),
    path("cart/add/<int:product_id>/", views.AddToCartView.as_view(), name="add_to_cart"),
    path("cart/update/<int:item_id>/", views.UpdateCartItemView.as_view(), name="update_cart_item"),
    path("cart/remove/<int:item_id>/", views.RemoveCartItemView.as_view(), name="remove_cart_item"),
    path("cart/apply-coupon/", views.ApplyCouponView.as_view(), name="apply_coupon"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("order/success/<str:order_number>/", views.OrderSuccessView.as_view(), name="order_success"),
    path("my-orders/", views.MyOrdersView.as_view(), name="my_orders"),
    path("order/<str:order_number>/detail/", views.CustomerOrderDetailView.as_view(), name="order_detail"),
    path("order/<str:order_number>/invoice/", views.OrderInvoiceView.as_view(), name="order_invoice"),
    path("track-order/", views.OrderTrackingView.as_view(), name="order_tracking"),
    path("order/<str:order_number>/cancel/", views.CancelOrderView.as_view(), name="cancel_order"),
]
