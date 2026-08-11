import logging

from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.core.cache import cache
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import User
from .forms import RegisterForm, ProfileForm

logger = logging.getLogger("apps.accounts")

LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 15 * 60  # ۱۵ دقیقه قفل پس از تلاش‌های ناموفق مکرر


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _login_attempts_key(request, username):
    return f"login_attempts:{_client_ip(request)}:{username.lower()}"


def _safe_next_url(request):
    """
    مقدار next را (از GET یا POST) می‌خواند و فقط در صورتی که آدرس امن و متعلق
    به همین سایت باشد برمی‌گرداند -- برای جلوگیری از Open Redirect.
    """
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return next_url
    return None


class RegisterView(CreateView):
    """
    ثبت‌نام کاربر جدید. بعد از ثبت‌نام موفق، کاربر بلافاصله و خودکار وارد
    حساب کاربری‌اش می‌شود و مستقیماً به همان صفحه‌ای که برای ادامه‌ی خرید از
    آن‌جا آمده بود (پارامتر next) هدایت می‌شود.
    """
    model = User
    form_class = RegisterForm
    template_name = "accounts/register.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["next"] = _safe_next_url(self.request) or ""
        return ctx

    def form_valid(self, form):
        form.instance.set_password(form.cleaned_data["password"])
        form.instance.role = User.ROLE_CUSTOMER
        response = super().form_valid(form)
        login(self.request, self.object, backend="django.contrib.auth.backends.ModelBackend")
        logger.info("New user registered and auto-logged-in: %s", self.object.username)
        return response

    def get_success_url(self):
        return _safe_next_url(self.request) or reverse_lazy("core:home")


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username", "").strip()
        if username:
            key = _login_attempts_key(request, username)
            attempts = cache.get(key, 0)
            if attempts >= LOGIN_MAX_ATTEMPTS:
                logger.warning("Login blocked (too many attempts) for %s from %s", username, _client_ip(request))
                form = self.get_form()
                form.add_error(
                    None,
                    "به‌دلیل تلاش‌های ناموفق مکرر، ورود برای این حساب موقتاً (به مدت ۱۵ دقیقه) مسدود شده است.",
                )
                return self.render_to_response(self.get_context_data(form=form))
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        username = form.cleaned_data.get("username", "")
        if username:
            cache.delete(_login_attempts_key(self.request, username))
        logger.info("Successful login for %s from %s", username, _client_ip(self.request))
        return super().form_valid(form)

    def form_invalid(self, form):
        username = self.request.POST.get("username", "").strip()
        if username:
            key = _login_attempts_key(self.request, username)
            attempts = cache.get(key, 0) + 1
            cache.set(key, attempts, LOGIN_LOCKOUT_SECONDS)
            logger.warning(
                "Failed login attempt #%s for %s from %s", attempts, username, _client_ip(self.request)
            )
        return super().form_invalid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")
