# تغییرات: چند والد برای دسته‌بندی محصولات

## هدف
قبلاً هر دسته‌بندی محصول (`ProductCategory`) فقط یک والد داشت (`parent` از نوع `ForeignKey`).
اکنون هر دسته‌بندی می‌تواند هر تعداد والد داشته باشد (`parents` از نوع `ManyToManyField`)، هم در
Django Admin و هم در داشبورد اختصاصی.

## فایل‌های تغییرکرده

| فایل | تغییر |
|---|---|
| `apps/products/models.py` | `parent` (FK) حذف و `parents` (M2M به خود مدل، `symmetrical=False`) اضافه شد. متد `get_descendant_ids()` برای تشخیص حلقه افزوده شد. |
| `apps/products/migrations/0003_productcategory_parents.py` | جدید: افزودن فیلد `parents` (با `related_name` موقت `new_children`). |
| `apps/products/migrations/0004_copy_parent_to_parents.py` | جدید: کپی والد فعلی هر دسته به `parents` (بدون از دست رفتن داده). |
| `apps/products/migrations/0005_remove_productcategory_parent.py` | جدید: حذف `parent` قدیمی و تنظیم نهایی `related_name="children"`. |
| `apps/products/admin.py` | `filter_horizontal` برای انتخاب چند والد، ستون «والدها» در لیست، `prefetch_related`، و اعتبارسنجی ضدِ حلقه. |
| `apps/dashboard/views.py` | فرم `DashboardProductCategoryForm` با فیلد `parents` و اعتبارسنجی؛ `prefetch_related` در لیست. |
| `templates/dashboard/products/category_list.html` | ستون والد حالا همه‌ی والدها را نمایش می‌دهد. |

## نحوه اعمال
۱. فایل‌ها را با همان مسیرها در پروژه جایگزین/اضافه کنید.
۲. اجرا کنید:

```bash
python manage.py migrate
```

۳. در Django Admin به «دسته‌بندی‌های محصولات» بروید؛ فیلد «دسته‌بندی‌های والد» حالا یک ویجت دو ستونی
است و می‌توانید چند والد انتخاب کنید.

## توضیحات فنی

**چرا سه مایگریشن؟** تغییر ساختار و انتقال داده در یک مایگریشن روی PostgreSQL ممکن است خطای
`pending trigger events` بدهد. جدا کردن مرحله افزودن فیلد، کپی داده و حذف فیلد قدیمی امن‌تر است.

**چرا `related_name` موقت؟** تا قبل از حذف `parent`، نام `children` متعلق به همان FK است. فیلد جدید
ابتدا `new_children` می‌گیرد و در مرحله ۳ به `children` تغییر می‌کند.

**چرا `symmetrical=False`؟** بدون آن، اگر A والد B شود، B هم خودکار والد A می‌شود.

**جلوگیری از حلقه:** دسته‌بندی نمی‌تواند والد خودش یا والد یکی از زیرمجموعه‌هایش باشد؛
در ادمین و داشبورد پیام خطا نمایش داده می‌شود. (اعتبارسنجی فقط در فرم‌ها است، نه در سطح دیتابیس.)

**بازگشت (rollback):** مایگریشن‌ها برگشت‌پذیرند، ولی در برگشت فقط اولین والد هر دسته نگه داشته می‌شود.

## استفاده در کد
- والدهای یک دسته: `category.parents.all()`
- زیرمجموعه‌های یک دسته: `category.children.all()`
- هر جایی که قبلاً `category.parent` بود باید عوض شود (در پروژه فعلی جای دیگری استفاده نشده بود).

## نکته
اگر می‌خواهید **یک محصول** در چند دسته‌بندی قرار بگیرد (نه اینکه دسته چند والد داشته باشد)، فیلد
`Product.category` باید به M2M تبدیل شود و فیلترها/URLها/سایت‌مپ هم تغییر کنند. این کار انجام نشده است.
