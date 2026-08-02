# راهنمای اعمال طراحی جدید صفحه اصلی

## فایل‌های جدید (کپی مستقیم -- جایگزین یا اضافه کنید)

| فایل | محل قرارگیری در پروژه |
|---|---|
| `templates/partials/header.html` | جایگزین فایل موجود `templates/partials/header.html` شود |
| `templates/partials/hero_slider.html` | فایل **جدید** در `templates/partials/hero_slider.html` |
| `templates/core/home.html` | جایگزین فایل موجود `templates/core/home.html` شود |
| `static/css/header-hero-v2.css` | فایل **جدید** در `static/css/header-hero-v2.css` |
| `static/js/hero-slider.js` | فایل **جدید** در `static/js/hero-slider.js` |
| `apps/core/views.py` | جایگزین فایل موجود `apps/core/views.py` شود |
| `apps/core/context_processors.py` | جایگزین فایل موجود `apps/core/context_processors.py` شود |
| `apps/core/migrations/0002_promobanner.py` | فایل **جدید** در `apps/core/migrations/0002_promobanner.py` |

## فایل‌هایی که باید **دستی ویرایش** کنید (فقط افزودن چند خط)

### ۱. `apps/core/models.py`
محتوای `apps/core/models_ADDITION.py` را کپی و به **انتهای** فایل اضافه کنید (مدل جدید `PromoBanner`).

### ۲. `apps/core/admin.py`
طبق راهنمای داخل `apps/core/admin_ADDITION.py`:
- خط import را با افزودن `PromoBanner` به‌روزرسانی کنید.
- بلوک `PromoBannerAdmin` را به انتهای فایل اضافه کنید.

### ۳. `config/settings/base.py`
در بخش `TEMPLATES → OPTIONS → context_processors` این خط را اضافه کنید (کنار بقیه context processor های `apps.core`):

```python
"apps.core.context_processors.header_categories",
```

یعنی این بخش باید این‌طور شود:
```python
"context_processors": [
    "django.template.context_processors.debug",
    "django.template.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "apps.core.context_processors.site_settings",
    "apps.core.context_processors.menus",
    "apps.core.context_processors.cart_summary",
    "apps.core.context_processors.header_categories",
],
```

### ۴. `templates/base.html`
هیچ تغییری لازم نیست -- `header.html` همان‌جایی که الان با `{% include "partials/header.html" %}` صدا زده می‌شود باقی می‌ماند.

## پس از کپی فایل‌ها -- دستورات لازم

```bash
python manage.py makemigrations core   # اختیاری، چون میگریشن آماده هم دادم؛ برای اطمینان بزنید
python manage.py migrate
python manage.py collectstatic --noinput   # فقط در پروداکشن لازم است
```

## نحوه‌ی مدیریت محتوای جدید از پنل

- **بنر اسلایدر (۱۶۰۰×۴۰۰ پیکسل):** از پنل Django Admin یا داشبورد → مدل `HomeSlide` (از قبل در پروژه بود، فقط الان واقعاً در صفحه اصلی نمایش داده می‌شود). هر چند اسلاید فعال (`is_active=True`) اضافه کنید، به‌ترتیب `order` و به‌صورت خودکار (هر ۵ ثانیه) در گردش نمایش داده می‌شوند. دایره‌های پایین بنر خودکار بر اساس تعداد اسلایدها ساخته می‌شوند.
- **۴ کادر تبلیغاتی:** از پنل Django Admin → مدل جدید `PromoBanner`. هر رکورد یک تصویر (ترجیحاً مربعی) + لینک اختیاری دارد. اگر رکوردی وجود نداشته باشد، جای‌خالی خاکستری با متن راهنما نمایش داده می‌شود.
- **منوی «دسته‌بندی کالاها»:** به‌صورت خودکار از دسته‌بندی‌های اصلی محصولات (`ProductCategory` با `parent=None` و `is_active=True`) پر می‌شود؛ نیازی به کار دستی نیست.

## نکاتی درباره‌ی طراحی

- رنگ‌بندی طبق تصویر نمونه (قرمز/فیروزه‌ای) پیاده‌سازی **نشد**، چون آن رنگ‌ها در تصویر شما صرفاً جای‌گیرنده (Placeholder) بودند نه هویت بصری نهایی؛ به‌جایش از پالت رسمی سایت شما (سرمه‌ای/نارنجی) استفاده شد تا با بقیه صفحات هماهنگ بماند. اگر دقیقاً همان رنگ‌های تصویر را می‌خواهید، در فایل `static/css/header-hero-v2.css` مقادیر `var(--color-navy)` و `var(--color-orange)` را در بخش‌های مربوط به هدر و بنر با کد رنگ دلخواه جایگزین کنید.
- چیدمان (راست به چپ لوگو/جستجو/آیکون‌ها در ردیف اول، و دسته‌بندی/حساب‌کاربری/تماس/وبلاگ در ردیف دوم) دقیقاً مطابق تصویر شما پیاده‌سازی شده است.
- ابعاد بنر اصلی (۱۶۰۰×۴۰۰) با `aspect-ratio: 1600/400` در CSS رعایت شده؛ یعنی اگر تصویری با همین نسبت آپلود کنید، بدون کراپ ناخواسته به‌درستی نمایش داده می‌شود.
