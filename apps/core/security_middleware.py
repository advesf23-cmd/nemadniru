import hashlib
import re

from django.core.cache import cache
from django.http import HttpResponse


class SensitiveEndpointRateLimitMiddleware:
    """
    Lightweight per-IP throttling for authentication and customer order lookups.
    In production, use the shared Redis cache configured by prod.py. Nginx must
    overwrite X-Real-IP and the Django app must not be exposed directly.
    """

    WINDOW_SECONDS = 15 * 60
    RULES = (
        (re.compile(r"^/accounts/login/?$"), frozenset({"POST"}), 20, "login"),
        (re.compile(r"^/shop/track-order/?$"), frozenset({"POST"}), 10, "order-track"),
        (re.compile(r"^/shop/order/success/[^/]+/?$"), frozenset({"GET"}), 30, "order-success"),
        (
            re.compile(r"^/shop/order/[^/]+/(?:detail|invoice)/?$"),
            frozenset({"GET"}),
            30,
            "order-read",
        ),
        (re.compile(r"^/shop/order/[^/]+/cancel/?$"), frozenset({"POST"}), 10, "order-cancel"),
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for pattern, methods, limit, bucket in self.RULES:
            if request.method in methods and pattern.match(request.path_info):
                client_ip = (
                    request.META.get("HTTP_X_REAL_IP")
                    or request.META.get("REMOTE_ADDR")
                    or "unknown"
                )
                ip_digest = hashlib.sha256(client_ip.encode("utf-8")).hexdigest()[:24]
                key = f"security-rate:{bucket}:{ip_digest}"

                if cache.add(key, 1, timeout=self.WINDOW_SECONDS):
                    count = 1
                else:
                    try:
                        count = cache.incr(key)
                    except ValueError:
                        cache.set(key, 1, timeout=self.WINDOW_SECONDS)
                        count = 1

                if count > limit:
                    response = HttpResponse(
                        "تعداد درخواست‌ها بیش از حد مجاز است. لطفاً کمی بعد دوباره تلاش کنید.",
                        status=429,
                        content_type="text/plain; charset=utf-8",
                    )
                    response["Retry-After"] = str(self.WINDOW_SECONDS)
                    return response
                break

        response = self.get_response(request)
        if request.path_info.startswith("/shop/order/") or request.path_info.startswith("/shop/track-order"):
            # Customer order pages contain personal and commercial information.
            response["Cache-Control"] = "private, no-store"
            response["Referrer-Policy"] = "no-referrer"
            response["X-Content-Type-Options"] = "nosniff"
        return response
