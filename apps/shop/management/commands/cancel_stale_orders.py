import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.shop.models import Order
from apps.shop.views import send_order_email

logger = logging.getLogger("apps.shop")


class Command(BaseCommand):
    """
    سفارش‌هایی که مدتی طولانی در وضعیت «در انتظار پرداخت» مانده‌اند را به‌طور
    خودکار لغو می‌کند و موجودی انبار رزروشده برای آن‌ها را آزاد می‌کند.

    این دستور جایگزین یک تایمر رزرو ۱۰ دقیقه‌ای واقعی (که نیازمند اتصال
    درگاه پرداخت است) می‌شود: تا زمانی که درگاه پرداخت واقعی وصل نشده،
    موجودی همان لحظه‌ی ثبت سفارش کسر می‌شود (نه در لحظه‌ی ورود به درگاه)،
    و این دستور مسئول آزادسازی موجودیِ سفارش‌هایی است که مشتری هرگز
    پرداخت را کامل نکرده است.

    نحوه‌ی اجرا (باید طبق زمان‌بندی، نه دستی):

    -- روش ساده (Cron لینوکس)، هر ۵ دقیقه:
        */5 * * * * cd /path/to/project && venv/bin/python manage.py cancel_stale_orders

    -- روش پیشرفته‌تر (Celery Beat)، در celery.py پروژه یک periodic task
       تعریف کنید که همین management command را صدا بزند یا مستقیماً
       منطق مشابه را در یک Celery task پیاده‌سازی کنید.
    """
    help = "لغو خودکار سفارش‌های راکد در وضعیت «در انتظار پرداخت» و بازگرداندن موجودی رزروشده"

    def add_arguments(self, parser):
        parser.add_argument(
            "--minutes",
            type=int,
            default=30,
            help="سفارش‌های در انتظار پرداخت که بیش از این تعداد دقیقه از ثبتشان گذشته لغو می‌شوند (پیش‌فرض: ۳۰ دقیقه)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="فقط نمایش سفارش‌هایی که لغو خواهند شد، بدون اعمال تغییر واقعی",
        )

    def handle(self, *args, **options):
        minutes = options["minutes"]
        dry_run = options["dry_run"]
        cutoff = timezone.now() - timedelta(minutes=minutes)

        stale_orders = Order.objects.filter(
            status=Order.STATUS_PENDING_PAYMENT,
            created_at__lt=cutoff,
        )

        count = stale_orders.count()
        if count == 0:
            self.stdout.write("سفارش راکدی برای لغو یافت نشد.")
            return

        if dry_run:
            for order in stale_orders:
                self.stdout.write(f"[DRY-RUN] سفارش {order.order_number} لغو می‌شد (ثبت‌شده در {order.created_at}).")
            return

        cancelled = 0
        for order in stale_orders:
            order.cancel(reason=f"لغو خودکار -- بیش از {minutes} دقیقه بدون پرداخت")
            logger.info("Stale order %s auto-cancelled after %s minutes", order.order_number, minutes)
            send_order_email(
                order, "لغو خودکار سفارش",
                f"این سفارش به‌دلیل عدم تکمیل پرداخت طی {minutes} دقیقه به‌صورت خودکار لغو شد.",
            )
            cancelled += 1

        self.stdout.write(self.style.SUCCESS(f"{cancelled} سفارش راکد لغو و موجودی آن‌ها بازگردانده شد."))
