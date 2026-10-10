import logging
import secrets

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings as dj_settings
from django.db import transaction, IntegrityError
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView

from apps.products.models import Product
from .models import Cart, CartItem, Order, OrderItem, Coupon

logger = logging.getLogger("apps.shop")


class InsufficientStockError(Exception):
    """وقتی در لحظه‌ی نهایی ثبت سفارش، موجودی یک آیتم کافی نباشد (سناریوی همزمانی)"""
    def __init__(self, product_name):
        self.product_name = product_name
        super().__init__(f"Insufficient stock for {product_name}")


def get_or_create_cart(request):
    """سبد خرید را برای کاربر واردشده یا مهمان (بر اساس session) برمی‌گرداند"""
    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key, user=None)
    return cart


def send_order_email(order, subject_prefix, extra_note=""):
    """
    ارسال ایمیل اطلاع‌رسانی سفارش -- به مشتری (در صورت وجود ایمیل) و به مدیر فروشگاه.
    خطای ارسال ایمیل هرگز نباید فرآیند خرید را مختل کند؛ فقط لاگ می‌شود.
    """
    items_text = "\n".join(
        f"- {item.product_name} × {item.quantity} = {item.line_total:,.0f} تومان"
        for item in order.items.all()
    )
    body = (
        f"شماره سفارش: {order.order_number}\n"
        f"مشتری: {order.full_name} -- {order.phone}\n"
        f"آدرس: {order.full_address}\n"
        f"وضعیت: {order.get_status_display()}\n"
        f"{extra_note}\n\n"
        f"اقلام سفارش:\n{items_text}\n\n"
        f"مبلغ نهایی: {order.total:,.0f} تومان"
    )
    recipients = []
    if order.email:
        recipients.append(order.email)
    admin_email = getattr(dj_settings, "CONTACT_RECEIVER_EMAIL", "")
    if admin_email:
        recipients.append(admin_email)

    if not recipients:
        return
    try:
        send_mail(
            subject=f"{subject_prefix} -- {order.order_number}",
            message=body,
            from_email=dj_settings.DEFAULT_FROM_EMAIL or None,
            recipient_list=recipients,
            fail_silently=False,
        )
    except Exception:
        logger.exception("ارسال ایمیل اطلاع‌رسانی سفارش %s ناموفق بود", order.order_number)


class CartDetailView(TemplateView):
    template_name = "shop/cart.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cart"] = get_or_create_cart(self.request)
        return ctx


class AddToCartView(View):
    """
    افزودن به سبد خرید -- طبق روال جدید خرید، ابتدا باید کاربر وارد حساب کاربری
    شده باشد. اگر وارد نشده باشد، به صفحه‌ی ورود هدایت می‌شود و پس از ورود یا
    ثبت‌نام، دقیقاً به همان صفحه‌ی محصول برمی‌گردد تا خرید را ادامه دهد.
    """

    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id, status="published", is_orderable=True)
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        if not request.user.is_authenticated:
            login_url = f"{reverse('accounts:login')}?next={product.get_absolute_url()}"
            if is_ajax:
                return JsonResponse({
                    "success": False,
                    "login_required": True,
                    "redirect_url": login_url,
                    "error": "برای خرید ابتدا باید وارد حساب کاربری خود شوید.",
                }, status=401)
            messages.warning(request, "برای خرید ابتدا باید وارد حساب کاربری خود شوید.")
            return redirect(login_url)

        cart = get_or_create_cart(request)

        try:
            quantity = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            quantity = 1
        quantity = max(1, quantity)

        # موجودی صفر -- اصلاً اجازه افزودن نمی‌دهیم
        if product.stock_quantity <= 0:
            msg = f"محصول «{product.name}» در حال حاضر موجود نیست."
            if is_ajax:
                return JsonResponse({"success": False, "error": msg}, status=400)
            messages.error(request, msg)
            return redirect(product.get_absolute_url())

        existing_item = CartItem.objects.filter(cart=cart, product=product).first()
        already_in_cart = existing_item.quantity if existing_item else 0
        requested_total = already_in_cart + quantity

        # اگر تعداد درخواستی (به‌اضافه‌ی آنچه از قبل در سبد است) از موجودی انبار بیشتر باشد
        if requested_total > product.stock_quantity:
            remaining = max(product.stock_quantity - already_in_cart, 0)
            if remaining <= 0:
                msg = f"شما به حداکثر موجودی «{product.name}» ({product.stock_quantity} عدد) در سبد خرید رسیده‌اید."
            else:
                msg = f"موجودی «{product.name}» تنها {product.stock_quantity} عدد است. حداکثر {remaining} عدد دیگر می‌توانید اضافه کنید."
            if is_ajax:
                return JsonResponse({"success": False, "error": msg}, status=400)
            messages.error(request, msg)
            return redirect(product.get_absolute_url())

        item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": quantity})
        if not created:
            item.quantity += quantity
            item.save()

        if is_ajax:
            return JsonResponse({"success": True, "cart_count": cart.total_items})
        messages.success(request, "محصول به سبد خرید اضافه شد.")
        return redirect("shop:cart_detail")


class UpdateCartItemView(View):
    def post(self, request, item_id):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        try:
            quantity = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            quantity = 1

        error = None
        if quantity <= 0:
            item.delete()
        else:
            if quantity > item.product.stock_quantity:
                quantity = item.product.stock_quantity
                error = f"موجودی «{item.product.name}» تنها {item.product.stock_quantity} عدد است."
            if quantity <= 0:
                item.delete()
            else:
                item.quantity = quantity
                item.save()

        if is_ajax:
            html = render_to_string("shop/_cart_items.html", {"cart": cart}, request=request)
            return JsonResponse({
                "success": error is None,
                "error": error,
                "html": html,
                "total": str(cart.total),
                "count": cart.total_items,
            })
        if error:
            messages.warning(request, error)
        return redirect("shop:cart_detail")


class RemoveCartItemView(View):
    def post(self, request, item_id):
        cart = get_or_create_cart(request)
        CartItem.objects.filter(pk=item_id, cart=cart).delete()
        messages.success(request, "محصول از سبد خرید حذف شد.")
        return redirect("shop:cart_detail")


class ApplyCouponView(View):
    def post(self, request):
        cart = get_or_create_cart(request)
        code = request.POST.get("code", "").strip()
        try:
            coupon = Coupon.objects.get(code__iexact=code)
            if coupon.is_valid():
                cart.coupon = coupon
                cart.save()
                messages.success(request, f"کد تخفیف «{code}» با موفقیت اعمال شد.")
            else:
                messages.error(request, "این کد تخفیف معتبر نیست یا منقضی شده است.")
        except Coupon.DoesNotExist:
            messages.error(request, "کد تخفیف وارد شده یافت نشد.")
        return redirect("shop:cart_detail")


class CheckoutView(LoginRequiredMixin, TemplateView):
    """
    صفحه‌ی تسویه‌حساب -- طبق روال جدید خرید:
    ۱) کاربر باید وارد حساب کاربری شده باشد (LoginRequiredMixin؛ در غیر این
       صورت به صفحه‌ی ورود با next=همین صفحه هدایت می‌شود).
    ۲) قبل از ثبت نهایی سفارش (قبل از رفتن به مرحله‌ی پرداخت)، تمام فیلدهای
       مشخصات و آدرس (نام، شماره همراه، استان، شهرستان، آدرس دقیق پستی،
       جزئیات آدرس، کد پستی) اعتبارسنجی و الزامی می‌شوند.
    """
    template_name = "shop/checkout.html"
    login_url = "accounts:login"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cart"] = get_or_create_cart(self.request)

        if "checkout_token" not in self.request.session:
            self.request.session["checkout_token"] = secrets.token_hex(20)
        ctx["checkout_token"] = self.request.session["checkout_token"]

        # پیش‌پرکردن فرم با آخرین آدرس ثبت‌شده‌ی همین کاربر (در صورت وجود سفارش قبلی)
        # تا کاربر مجبور نباشد هر بار از صفر همه چیز را تایپ کند.
        last_order = Order.objects.filter(user=self.request.user).order_by("-created_at").first()
        ctx["prefill"] = {
            "full_name": self.request.user.get_full_name() or "",
            "phone": self.request.user.phone or "",
        }
        if last_order:
            ctx["prefill"].update({
                "full_name": last_order.full_name,
                "phone": last_order.phone,
                "province": last_order.province,
                "county": last_order.county,
                "shipping_address": last_order.shipping_address,
                "address_details": last_order.address_details,
                "postal_code": last_order.postal_code,
            })
        return ctx

    def post(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)

        submitted_token = request.POST.get("checkout_token", "")

        if submitted_token:
            existing_order = Order.objects.filter(checkout_token=submitted_token).first()
            if existing_order:
                return redirect("shop:order_success", order_number=existing_order.order_number)

        if not cart.items.exists():
            messages.error(request, "سبد خرید شما خالی است.")
            return redirect("shop:cart_detail")

        # ---------------------------------------------------------------
        # اعتبارسنجی کامل مشخصات و آدرس -- قبل از رفتن به مرحله‌ی پرداخت،
        # تمام این فیلدها باید پر شده باشند.
        # ---------------------------------------------------------------
        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        province = request.POST.get("province", "").strip()
        county = request.POST.get("county", "").strip()
        shipping_address = request.POST.get("shipping_address", "").strip()
        address_details = request.POST.get("address_details", "").strip()
        postal_code = request.POST.get("postal_code", "").strip()

        errors = []
        if not full_name:
            errors.append("لطفاً نام و نام خانوادگی را وارد کنید.")
        if not phone or not phone.isdigit() or len(phone) != 11 or not phone.startswith("09"):
            errors.append("شماره همراه باید ۱۱ رقم و با ۰۹ شروع شود.")
        if not province:
            errors.append("لطفاً استان را انتخاب کنید.")
        if not county:
            errors.append("لطفاً شهرستان را انتخاب کنید.")
        if not shipping_address:
            errors.append("لطفاً آدرس دقیق پستی را وارد کنید.")
        if not address_details:
            errors.append("لطفاً جزئیات آدرس (پلاک، واحد، طبقه) را وارد کنید.")
        if not postal_code.isdigit() or len(postal_code) != 10:
            errors.append("کد پستی باید دقیقاً ۱۰ رقم و فقط عدد باشد.")

        if errors:
            for err in errors:
                messages.error(request, err)
            ctx = self.get_context_data()
            ctx["form_data"] = request.POST
            return self.render_to_response(ctx)

        try:
            order = self._create_order_atomically(
                request, cart, submitted_token,
                full_name=full_name, phone=phone, province=province, county=county,
                shipping_address=shipping_address, address_details=address_details,
                postal_code=postal_code,
            )
        except InsufficientStockError as exc:
            messages.error(
                request,
                f"متأسفانه موجودی «{exc.product_name}» هم‌زمان توسط سفارش دیگری تمام شد. "
                f"لطفاً تعداد را در سبد خرید اصلاح کنید.",
            )
            return redirect("shop:cart_detail")
        except IntegrityError:
            existing_order = Order.objects.filter(checkout_token=submitted_token).first()
            if existing_order:
                return redirect("shop:order_success", order_number=existing_order.order_number)
            messages.error(request, "خطایی در ثبت سفارش رخ داد. لطفاً دوباره تلاش کنید.")
            return redirect("shop:cart_detail")

        request.session.pop("checkout_token", None)
        request.session["last_order_id"] = order.pk

        send_order_email(order, "سفارش جدید ثبت شد", "این سفارش هم‌اکنون در انتظار پرداخت است.")
        logger.info("Order %s created (total=%s, items=%s)", order.order_number, order.total, order.items.count())

        # -----------------------------------------------------------------
        # نقطه اتصال درگاه پرداخت واقعی (مثل زرین‌پال) اینجا قرار می‌گیرد:
        # gateway_url = zarinpal_request_payment(order)
        # return redirect(gateway_url)
        # -----------------------------------------------------------------
        return redirect("shop:order_success", order_number=order.order_number)

    @transaction.atomic
    def _create_order_atomically(self, request, cart, checkout_token, **address_fields):
        cart_items = list(cart.items.select_related("product"))

        order = Order.objects.create(
            user=request.user,
            full_name=address_fields["full_name"],
            phone=address_fields["phone"],
            email=request.POST.get("email", ""),
            province=address_fields["province"],
            county=address_fields["county"],
            shipping_address=address_fields["shipping_address"],
            address_details=address_fields["address_details"],
            postal_code=address_fields["postal_code"],
            notes=request.POST.get("notes", ""),
            subtotal=cart.subtotal,
            discount_amount=cart.discount_amount,
            total=cart.total,
            coupon=cart.coupon,
            checkout_token=checkout_token or None,
        )

        for item in cart_items:
            updated_rows = Product.objects.filter(
                pk=item.product_id, stock_quantity__gte=item.quantity
            ).update(stock_quantity=F("stock_quantity") - item.quantity)

            if updated_rows == 0:
                raise InsufficientStockError(item.product.name)

            OrderItem.objects.create(
                order=order, product=item.product, product_name=item.product.name,
                unit_price=item.unit_price, quantity=item.quantity,
            )

        if cart.coupon:
            Coupon.objects.filter(pk=cart.coupon_id).update(used_count=F("used_count") + 1)

        cart.items.all().delete()
        cart.coupon = None
        cart.save()

        return order


class OrderSuccessView(DetailView):
    model = Order
    template_name = "shop/order_success.html"
    context_object_name = "order"
    slug_field = "order_number"
    slug_url_kwarg = "order_number"

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            return queryset.filter(user=self.request.user)
        # Guest checkout is not supported by the current checkout flow. Keep
        # the success page tied to the order created in this browser session.
        order_id = self.request.session.get("last_order_id")
        return queryset.filter(pk=order_id) if order_id else queryset.none()


class MyOrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "shop/my_orders.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderTrackingView(TemplateView):
    """پیگیری سفارش بدون نیاز به ورود -- با شماره سفارش و شماره تلفن (برای سفارش‌های قدیمی مهمان)"""
    template_name = "shop/order_tracking.html"

    def post(self, request, *args, **kwargs):
        order_number = request.POST.get("order_number", "").strip()
        phone = request.POST.get("phone", "").strip()
        order = Order.objects.filter(order_number=order_number, phone=phone).first()
        ctx = self.get_context_data()
        if order:
            ctx["order"] = order
        else:
            messages.error(request, "سفارشی با این مشخصات یافت نشد.")
        return self.render_to_response(ctx)


class OrderAccessMixin:
    def get_order_or_none(self, request, order_number):
        qs = Order.objects.filter(order_number=order_number)
        if request.user.is_authenticated:
            # An authenticated user must not fall back to another customer's
            # phone-number-based access if the order is not theirs.
            return qs.filter(user=request.user).first()
        phone = request.GET.get("phone", "").strip()
        if phone:
            return qs.filter(phone=phone).first()
        return None


class CustomerOrderDetailView(OrderAccessMixin, View):
    STEPS = [
        ("pending_payment", "در انتظار پرداخت", "fa-clock"),
        ("processing", "در حال پردازش", "fa-gears"),
        ("shipped", "ارسال شده", "fa-truck"),
        ("delivered", "تحویل داده شده", "fa-circle-check"),
    ]

    def get(self, request, order_number):
        order = self.get_order_or_none(request, order_number)
        if not order:
            messages.error(request, "برای مشاهده جزئیات سفارش، از صفحه «پیگیری سفارش» اقدام کنید.")
            return redirect("shop:order_tracking")

        step_keys = [s[0] for s in self.STEPS]
        current_index = step_keys.index(order.status) if order.status in step_keys else -1
        completed_steps = step_keys[:current_index] if current_index >= 0 else []

        return render(request, "shop/order_detail.html", {
            "order": order,
            "order_steps": self.STEPS,
            "completed_steps": completed_steps,
        })


class OrderInvoiceView(OrderAccessMixin, View):
    """فاکتور قابل چاپ/دانلود (از طریق Print to PDF مرورگر) -- بدون وابستگی به کتابخانه PDF خارجی"""

    def get(self, request, order_number):
        order = self.get_order_or_none(request, order_number)
        if not order:
            messages.error(request, "برای دریافت فاکتور، از صفحه «پیگیری سفارش» اقدام کنید.")
            return redirect("shop:order_tracking")
        return render(request, "shop/order_invoice.html", {"order": order})


class CancelOrderView(View):
    def post(self, request, order_number):
        phone = request.POST.get("phone", "").strip()
        qs = Order.objects.filter(order_number=order_number)
        if request.user.is_authenticated:
            order = qs.filter(user=request.user).first()
        else:
            order = qs.filter(phone=phone).first()

        if not order:
            messages.error(request, "سفارشی با این مشخصات یافت نشد.")
            return redirect("shop:order_tracking")

        if not order.is_cancellable_by_customer:
            messages.error(request, "این سفارش دیگر قابل لغو نیست (در حال پردازش یا ارسال است).")
            return redirect("shop:order_tracking")

        order.cancel(reason="لغو توسط مشتری")
        logger.info("Order %s cancelled by customer", order.order_number)
        send_order_email(order, "سفارش لغو شد", "این سفارش توسط مشتری لغو شد و موجودی انبار بازگردانده شد.")
        messages.success(request, f"سفارش {order.order_number} با موفقیت لغو شد.")
        return redirect("shop:order_tracking")
