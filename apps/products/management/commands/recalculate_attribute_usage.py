from collections import Counter

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.products.attribute_utils import normalize_attribute_text
from apps.products.models import AttributeValue, ProductAttributeValue

LANGUAGE = "fa"


class Command(BaseCommand):
    """
    شمارنده‌ی AttributeValue.usage_count را با تعداد واقعی انتساب‌ها در
    ProductAttributeValue مقایسه می‌کند.

    پیش‌فرض: فقط گزارش (هیچ تغییری در دیتابیس داده نمی‌شود).
      --apply           شمارنده‌های ناهماهنگ را اصلاح می‌کند (داخل یک تراکنش).
      --create-missing  (همراه با --apply) برای مقادیر استفاده‌شده که ردیف کاتالوگ
                        ندارند، ردیف جدید می‌سازد.
      --limit N         حداکثر تعداد ردیف نمایش‌داده‌شده برای هر بخش گزارش (پیش‌فرض ۵۰).
    """
    help = "مقایسه (و در صورت درخواست اصلاح) usage_count مقادیر کاتالوگ مشخصات"

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="اعمال اصلاح‌ها (بدون این گزینه فقط گزارش)")
        parser.add_argument("--create-missing", action="store_true", help="ساخت ردیف کاتالوگ برای مقادیر ثبت‌نشده")
        parser.add_argument("--limit", type=int, default=50)

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        create_missing = options["create_missing"]
        limit = options["limit"]

        actual = Counter()
        display = {}
        for attribute_id, text in ProductAttributeValue.objects.values_list("attribute_id", "value_text").iterator():
            normalized = normalize_attribute_text(text)
            if not normalized:
                continue
            key = (attribute_id, normalized)
            actual[key] += 1
            display.setdefault(key, (text or "").strip())

        catalog = {
            (av.attribute_id, av.normalized_value): av
            for av in AttributeValue.objects.filter(language_code=LANGUAGE)
        }

        mismatched = []   # (av, actual_count)
        missing = []      # key
        for key, count in actual.items():
            av = catalog.get(key)
            if av is None:
                missing.append(key)
            elif av.usage_count != count:
                mismatched.append((av, count))
        unused_nonzero = [av for key, av in catalog.items() if key not in actual and av.usage_count != 0]

        self.stdout.write("بررسی شمارنده‌های مقادیر کاتالوگ مشخصات")
        self.stdout.write(f"حالت: {'اعمال تغییرات' if apply_changes else 'فقط گزارش (بدون تغییر)'}")
        self.stdout.write(f"تعداد مقدارهای متفاوت در انتساب‌ها: {len(actual)}")
        self.stdout.write(f"تعداد ردیف‌های کاتالوگ ({LANGUAGE}): {len(catalog)}\n")

        self.stdout.write(f"[1] شمارنده‌ی نادرست: {len(mismatched)}")
        for av, count in mismatched[:limit]:
            self.stdout.write(f"    id={av.pk} attribute={av.attribute_id} «{av.value}»: ذخیره‌شده={av.usage_count} واقعی={count}")

        self.stdout.write(f"[2] مقدار بدون ردیف کاتالوگ: {len(missing)}")
        for key in missing[:limit]:
            self.stdout.write(f"    attribute={key[0]} «{display[key]}» واقعی={actual[key]}")

        self.stdout.write(f"[3] ردیف کاتالوگ با شمارنده‌ی غیرصفر ولی بدون استفاده: {len(unused_nonzero)}")
        for av in unused_nonzero[:limit]:
            self.stdout.write(f"    id={av.pk} attribute={av.attribute_id} «{av.value}»: ذخیره‌شده={av.usage_count} واقعی=0")

        total_issues = len(mismatched) + len(missing) + len(unused_nonzero)
        if total_issues == 0:
            self.stdout.write(self.style.SUCCESS("\nهمه‌ی شمارنده‌ها با داده‌ی واقعی هم‌خوانند."))
            return

        if not apply_changes:
            self.stdout.write(self.style.WARNING(
                f"\n{total_issues} مورد ناهماهنگ پیدا شد. چیزی تغییر نکرد. "
                "برای اصلاح: --apply (و در صورت نیاز --create-missing)"
            ))
            return

        with transaction.atomic():
            for av, count in mismatched:
                AttributeValue.objects.filter(pk=av.pk).update(usage_count=count)
            for av in unused_nonzero:
                AttributeValue.objects.filter(pk=av.pk).update(usage_count=0)
            created = 0
            if create_missing:
                for key in missing:
                    AttributeValue.objects.create(
                        attribute_id=key[0], value=display[key], language_code=LANGUAGE, usage_count=actual[key]
                    )
                    created += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nاصلاح شد: {len(mismatched)} شمارنده‌ی نادرست، {len(unused_nonzero)} شمارنده‌ی بی‌مصرف به صفر، "
            f"{created} ردیف جدید. ({len(missing) - created} مقدار بدون ردیف کاتالوگ دست‌نخورده ماند)"
        ))
