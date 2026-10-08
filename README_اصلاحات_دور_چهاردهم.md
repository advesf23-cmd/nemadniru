# راهنمای دور چهاردهم

## بخش ۱) منوی دسته‌بندی کالاها به حالت قبل برگشت (Flyout تو در تو)

در دور قبل، منو را به یک پنل پهن چندستونه تبدیل کرده بودم که کل زیردرخت را یک‌جا نشان می‌داد.
حالا دوباره **هر سطح، Flyout مستقل خودش را با هاور باز می‌کند** (و اگر آن زیرمجموعه‌ها هم
زیرمجموعه داشته باشند، Flyout بعدی کنارش باز می‌شود) -- بدون محدودیت در تعداد سطوح.

| فایل | محل | تغییر |
|---|---|---|
| `templates/partials/_category_tree_items.html` | جایگزین | هر گره = `categories-dropdown-item` + `categories-submenu` (بازگشتی) |
| `templates/partials/header.html` | جایگزین | کل منو با یک `{% include %}` بازگشتی |
| `static/css/header-hero-v2.css` | جایگزین | حذف ستون‌بندی و کلاس‌های `mega-cat-*`؛ Flyout باریک تک‌ستونه |

نکته: `apps/core/context_processors.py` دور قبل (که کل درخت را با `sub_items` می‌سازد) **همان‌طور که
هست می‌ماند** و نیاز به تغییر ندارد.

---

## بخش ۲) سند Product Master -- چه چیزی پیاده شد و چه چیزی نه

سند را کامل خواندم. از ۷ توصیه‌ی نهایی‌اش:

| # | توصیه | وضعیت |
|---|---|---|
| ۱ | Product ID حفظ شود | ✅ از قبل برقرار (کلید اصلی دست‌نخورده) |
| ۲ | MPN فیلد مستقل | ✅ **پیاده شد** (`Product.mpn`، ایندکس‌شده، در جستجو هم لحاظ شد) |
| ۳ | SKU از MPN جدا شود | ✅ **پیاده شد** (SKU همان کد داخلی؛ MPN کد سازنده) |
| ۴ | Brand به جدول استاندارد | ✅ **پیاده شد** (مدل `Brand` + ForeignKey، با میگریشن خودکارِ داده) |
| ۵ | Category ساختاری و سلسله‌مراتبی | ✅ از قبل برقرار بود (`ProductCategory.parent`) |
| ۶ | مشخصات فنی ساختاریافته بر اساس دسته | ⚠️ **نیمه‌پیاده** (جزئیات پایین) |
| ۷ | جدا کردن قیمت/تخفیف/نرخ ارز (Pricing Engine) | ⚠️ **فقط بخش کوچکی** (جزئیات پایین) |

### آنچه کامل پیاده شد
- **`Brand`**: نام، لوگو، درصد تخفیف پیش‌فرض، فعال/غیرفعال. فیلد متنی قدیمی `Product.brand` با
  میگریشن ۳مرحله‌ای ایمن به ForeignKey تبدیل می‌شود (مقادیر متنی موجود **خودکار** به رکورد Brand
  تبدیل و وصل می‌شوند، چیزی گم نمی‌شود). فرم محصول حالا لیست کشویی برند نشان می‌دهد.
- **`Product.mpn`** و **`Product.technical_description`** (متن آزاد فنی، جدا از توضیحات فروش).
- **قانون اولویت تخفیف** طبق سند: `Product.discount_percent_override` (اگر پر باشد) روی
  `Brand.default_discount_percent` اولویت دارد؛ property جدید `effective_discount_percent`.
  `final_price` اگر `discount_price` دستی خالی باشد از همین درصد محاسبه می‌کند.
- جستجوی سایت و Autocomplete حالا روی **MPN و SKU** هم کار می‌کند.
- باگ جانبی: `ProductCategoryDetailView` با دسته‌ی ناموجود خطای ۵۰۰ می‌داد؛ حالا ۴۰۴ می‌دهد.

### آنچه نیمه‌پیاده است (و دلیلش)
**مشخصات فنی بر اساس دسته (#۶):** مدل `CategoryAttributeTemplate` اضافه شد تا برای هر دسته تعریف
کنید چه مشخصه‌هایی دارد (مثلاً MCCB ← تعداد پل، جریان نامی، قدرت قطع، Trip Unit؛ با واحد).
مقدار هر محصول همچنان در `ProductSpecification` (کلید/مقدار موجود) ذخیره می‌شود. اما **فرم محصول به‌صورت
خودکار با انتخاب دسته، فیلدهای همان دسته را نمی‌سازد** -- این یعنی یک فرم پویا (Formset + JS) که
جدا از این دور است. فعلاً قالب‌ها راهنمای ادمین برای وارد کردن کلیدها هستند.

**موتور قیمت‌گذاری (#۷):** تخفیف برند/محصول اضافه شد ولی **موتور مستقل کامل** (لیست قیمت تأمین‌کننده،
نرخ ارز، هزینه واردات، حاشیه سود، تاریخچه‌ی قیمت، و خواندن PDF/OCR با تطبیق MPN) پیاده **نشد**.
دلیل: این یک زیرسیستم جداگانه با چند مدل، رابط ورود داده و منطق محاسباتی است؛ اگر ناقص و عجولانه
ساخته شود روی قیمت‌های واقعی فروشگاه اثر می‌گذارد. توصیه‌ی من این است که به‌عنوان فاز جداگانه
طراحی شود (پیشنهاد: مدل‌های `PriceList`, `PriceListItem(mpn, list_price)`, `ExchangeRate`,
`PricingRule`، و یک Management Command برای اعمال قیمت). اگر خواستید، دور بعد همین را شروع می‌کنیم.

---

## فایل‌ها و محل جایگذاری

### جایگزینی مستقیم
| فایل | محل |
|---|---|
| `apps/products/models.py` | `apps/products/models.py` |
| `apps/products/admin.py` | `apps/products/admin.py` |
| `apps/products/views.py` | `apps/products/views.py` |
| `apps/products/migrations/0003_brand_and_new_fields.py` | **جدید** در پوشه migrations |
| `apps/products/migrations/0004_migrate_brand_data.py` | **جدید** |
| `apps/products/migrations/0005_finalize_brand_fk.py` | **جدید** |
| `templates/partials/header.html` | جایگزین |
| `templates/partials/_category_tree_items.html` | جایگزین |
| `static/css/header-hero-v2.css` | جایگزین |
| `templates/dashboard/products/brand_list.html` | **جدید** |

### ویرایش دستی (فقط افزودن بخش‌های کوچک)
| فایل | راهنما |
|---|---|
| `apps/dashboard/views.py` | `views_ADDITION_brands.py` (import + لیست fields فرم محصول + ۴ ویوی برند) |
| `apps/dashboard/urls.py` + `templates/dashboard/base_dashboard.html` | `urls_ADDITION_brands.py` (۴ مسیر + یک لینک سایدبار) |
| `templates/products/product_detail.html` | `product_detail_PATCH.txt` (نمایش MPN و توضیحات فنی) |

## ترتیب اجرا (مهم)

۱. **قبل از migrate از دیتابیس بکاپ بگیرید** (میگریشن ۰۰۰۵ ستون متنی قدیمی brand را حذف می‌کند):
```bash
pg_dump -U postgres samantajhiz > backup_before_brand.sql
```
۲. فایل‌ها را جایگزین/اضافه کنید.
۳. `python manage.py migrate products`
۴. در Django Admin → برندها، بررسی کنید برندهای قدیمی‌تان به‌درستی ساخته شده‌اند و درصد تخفیف برند را (در صورت نیاز) تنظیم کنید.

## تست پیشنهادی
- منوی دسته‌بندی را با یک درخت ۳ سطحی تست کنید: هاور روی هر سطح، Flyout بعدی را باز کند.
- یک محصول با MPN بسازید و در جستجوی سایت با همان MPN پیدایش کنید.
- برای برندی ۳۵٪ تخفیف بگذارید و محصولی از آن برند را بدون `discount_price` ببینید: قیمت نهایی باید ۳۵٪ کمتر شود؛ سپس برای یک محصول تخفیف اختصاصی ۴۰٪ بگذارید و ببینید اولویت با محصول است.
