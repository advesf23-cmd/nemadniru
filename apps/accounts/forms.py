from django import forms
from django.contrib.auth import password_validation

from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور")

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "phone", "password"]

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("کاربری با این ایمیل قبلاً ثبت‌نام کرده است.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password", "")
        # اعمال همان قوانین قدرت رمز عبور که در AUTH_PASSWORD_VALIDATORS تنظیمات تعریف شده‌اند
        # (حداقل طول، عدم شباهت به اطلاعات کاربر، رایج نبودن، غیرعددی‌بودن کامل)
        password_validation.validate_password(password, self.instance)
        return password
