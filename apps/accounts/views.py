import logging

from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.core.cache import cache
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import User
from .forms import RegisterForm

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


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        form.instance.set_password(form.cleaned_data["password"])
        form.instance.role = User.ROLE_CUSTOMER
        return super().form_valid(form)


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
    fields = ["first_name", "last_name", "email", "phone", "avatar", "company_name"]
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")
