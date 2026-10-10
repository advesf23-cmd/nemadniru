from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from .security_middleware import SensitiveEndpointRateLimitMiddleware


class SensitiveEndpointRateLimitTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        cache.clear()
        self.middleware = SensitiveEndpointRateLimitMiddleware(
            lambda request: HttpResponse("ok")
        )

    def tearDown(self):
        cache.clear()

    def _assert_limited_after(self, path, method, limit, **extra):
        for _ in range(limit):
            request = getattr(self.factory, method)(
                path, REMOTE_ADDR="192.0.2.10", **extra
            )
            self.assertEqual(self.middleware(request).status_code, 200)

        request = getattr(self.factory, method)(
            path, REMOTE_ADDR="192.0.2.10", **extra
        )
        response = self.middleware(request)
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response["Retry-After"], "900")

    def test_login_post_is_limited_after_twenty_requests_from_same_ip(self):
        self._assert_limited_after("/accounts/login/", "post", 20)

    def test_login_rate_limit_is_separate_for_different_ips(self):
        for _ in range(20):
            request = self.factory.post(
                "/accounts/login/", REMOTE_ADDR="192.0.2.10"
            )
            self.middleware(request)

        other_ip_request = self.factory.post(
            "/accounts/login/", REMOTE_ADDR="192.0.2.11"
        )
        self.assertEqual(self.middleware(other_ip_request).status_code, 200)

    def test_forwarded_for_header_does_not_override_remote_addr(self):
        for _ in range(20):
            request = self.factory.post(
                "/accounts/login/",
                REMOTE_ADDR="192.0.2.10",
                HTTP_X_FORWARDED_FOR="198.51.100.20",
            )
            self.middleware(request)

        request = self.factory.post(
            "/accounts/login/",
            REMOTE_ADDR="192.0.2.10",
            HTTP_X_FORWARDED_FOR="203.0.113.30",
        )
        self.assertEqual(self.middleware(request).status_code, 429)

    def test_order_tracking_post_is_limited_after_ten_requests(self):
        self._assert_limited_after("/shop/track-order/", "post", 10)

    def test_order_detail_get_is_limited_after_thirty_requests(self):
        self._assert_limited_after("/shop/order/STE-ABC123/detail/", "get", 30)

    def test_order_invoice_get_is_limited_after_thirty_requests(self):
        self._assert_limited_after("/shop/order/STE-ABC123/invoice/", "get", 30)

    def test_order_success_get_is_limited_after_thirty_requests(self):
        self._assert_limited_after("/shop/order/success/STE-ABC123/", "get", 30)

    def test_order_cancel_post_is_limited_after_ten_requests(self):
        self._assert_limited_after("/shop/order/STE-ABC123/cancel/", "post", 10)



class NginxPrivateUploadConfigTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        config_path = Path(settings.BASE_DIR) / "docker" / "nginx" / "nginx.conf"
        cls.nginx_config = config_path.read_text(encoding="utf-8")

    def test_private_upload_directories_have_explicit_deny_location(self):
        self.assertIn(
            r"location ~* ^/media/(?:quotes|careers/resumes)/",
            self.nginx_config,
        )
        self.assertIn("return 404;", self.nginx_config)

    def test_private_upload_deny_rule_precedes_public_media_alias(self):
        deny_position = self.nginx_config.index(
            r"location ~* ^/media/(?:quotes|careers/resumes)/"
        )
        public_media_position = self.nginx_config.index("location /media/ {")
        self.assertLess(deny_position, public_media_position)

    def test_nginx_overwrites_real_ip_header_from_connection_address(self):
        self.assertIn("proxy_set_header X-Real-IP $remote_addr;", self.nginx_config)
