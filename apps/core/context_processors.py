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


def header_categories(request):
    """
    دسته‌بندی‌های سطح‌بالای محصولات را به‌همراه **کل زیردرخت‌شان** (هر چند سطح
    که والد/فرزند تعریف شده باشد) برای منوی کشویی «دسته‌بندی کالاها» در
    دسترس قرار می‌دهد.

    رفع باگ قبلی: نسخه‌ی قبل فقط یک سطح زیرمجموعه (children) را Prefetch
    می‌کرد، پس اگر محصولات با چند سطح دسته/زیردسته/زیرِ‌زیردسته تعریف شده
    بودند، فقط اولین سطح در منو نشان داده می‌شد. این نسخه تمام دسته‌های
    فعال را یک‌بار می‌خواند (یک کوئری) و کل درخت را در پایتون می‌سازد، پس
    محدودیتی در تعداد سطوح ندارد.
    """
    try:
        from apps.products.models import ProductCategory

        all_categories = list(
            ProductCategory.objects.filter(is_active=True).order_by("order", "name")
        )
        children_by_parent_id = {}
        for category in all_categories:
            children_by_parent_id.setdefault(category.parent_id, []).append(category)

        def attach_sub_items(node):
            # sub_items یک attribute معمولی پایتونی است (نه related manager)،
            # پس در قالب با {{ node.sub_items }} بدون کوئری اضافه در دسترس است
            node.sub_items = children_by_parent_id.get(node.id, [])
            for child in node.sub_items:
                attach_sub_items(child)

        top_level = children_by_parent_id.get(None, [])[:12]
        for node in top_level:
            attach_sub_items(node)

        return {"header_categories": top_level}
    except Exception:
        return {"header_categories": []}
