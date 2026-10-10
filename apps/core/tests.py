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

    def test_login_post_is_limited_after_twenty_requests_from_same_ip(self):
        for _ in range(20):
            request = self.factory.post(
                "/accounts/login/",
                REMOTE_ADDR="192.0.2.10",
            )
            self.assertEqual(self.middleware(request).status_code, 200)

        request = self.factory.post(
            "/accounts/login/",
            REMOTE_ADDR="192.0.2.10",
        )
        response = self.middleware(request)

        self.assertEqual(response.status_code, 429)
        self.assertEqual(response["Retry-After"], "900")

    def test_login_rate_limit_is_separate_for_different_ips(self):
        for _ in range(20):
            request = self.factory.post(
                "/accounts/login/",
                REMOTE_ADDR="192.0.2.10",
            )
            self.middleware(request)

        other_ip_request = self.factory.post(
            "/accounts/login/",
            REMOTE_ADDR="192.0.2.11",
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
