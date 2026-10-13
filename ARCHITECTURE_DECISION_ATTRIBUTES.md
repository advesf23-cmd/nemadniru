# تصمیم معماری: مشخصات محصول (PRD-ATTR)

محل پیشنهادی در پروژه: ریشه‌ی پروژه (کنار README.md).

## وضعیت پذیرفته‌شده
| نیاز | منبع داده |
|---|---|
| فیلتر دسته‌بندی | قدیمی: `CategoryAttributeTemplate` + `ProductSpecification` (تا زمانی که `Attribute` تنظیمات فیلتر نداشته باشد) |
| نمایش در صفحه محصول | هر دو (قدیمی در جدول «مشخصات فنی»، جدید در بخش گروه‌بندی‌شده) |
| مقایسه | هر دو؛ در تعارض، ساختار جدید اولویت دارد (`spec_utils.build_comparison_rows`) |
| مشخصات مخصوص تنوع | فقط `VariantAttributeValue` (در `ProductAttributeValue` فیلد `variant` ممنوع است) |

## قواعد
- مشخصه‌ی جدید که باید فیلتر شود، فعلاً با `CategoryAttributeTemplate` تعریف و با `ProductSpecification` پر شود.
- `usage_count` فقط توسط `ProductAttributeValue.save()` و سیگنال حذف تغییر می‌کند؛ در صورت شک: `manage.py recalculate_attribute_usage`.
- حذف ساختار قدیمی فقط بعد از انتقال تنظیمات فیلتر به `Attribute` (انواع فیلتر، گزینه‌ها، بازه) و تست برابری نتیجه.

## گام‌های بعدی (در صورت نیاز واقعی)
۱. افزودن فیلدهای فیلتر به `Attribute` (migration). ۲. دستور انتقال `ProductSpecification` به `ProductAttributeValue`. ۳. انتقال فیلترها. ۴. قفل‌کردن ساختار قدیمی در ادمین.
