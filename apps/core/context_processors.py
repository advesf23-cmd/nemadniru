from .models import SiteSetting, Menu


def cart_summary(request):
    """تعداد آیتم‌های سبد خرید را در تمام قالب‌ها در دسترس قرار می‌دهد"""
    try:
        from apps.shop.models import Cart
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            cart = Cart.objects.filter(session_key=session_key).first() if session_key else None
        return {"cart_items_count": cart.total_items if cart else 0}
    except Exception:
        return {"cart_items_count": 0}


def site_settings(request):
    """تنظیمات سایت را در تمام قالب‌ها در دسترس قرار می‌دهد"""
    settings_obj, _ = SiteSetting.objects.get_or_create(pk=1)
    return {"site_settings": settings_obj}


def menus(request):
    """منوهای هدر و فوتر را در تمام قالب‌ها در دسترس قرار می‌دهد"""
    return {
        "header_menu": Menu.objects.filter(location="header", parent__isnull=True, is_active=True),
        "footer_menu": Menu.objects.filter(location="footer", parent__isnull=True, is_active=True),
    }
