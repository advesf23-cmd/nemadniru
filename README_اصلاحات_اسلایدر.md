# اصلاح افکت اسلایدر بنر اصلی (Push Transition به‌جای Fade)

## فایل جاوااسکریپت
`static/js/hero-slider.js` را با فایل پیوست‌شده (در همین پاسخ) **جایگزین کامل** کنید.
منطق چرخش کاملاً بازنویسی شد تا هر دو اسلاید هم‌زمان حرکت کنند (نه فقط تعویض کلاس).

## اصلاح لازم در static/css/header-hero-v2.css

چون فقط بخش کوچکی از فایل تغییر می‌کند، به‌جای فرستادن دوباره‌ی کل فایل
بزرگ، دقیقاً همین یک بخش را در `static/css/header-hero-v2.css` پیدا و
جایگزین کنید:

### این بخش را پیدا کنید (کد فعلی):
```css
.hero-slider-track { position: relative; width: 100%; height: 100%; }
.hero-slide {
  position: absolute;
  inset: 0;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.6s ease;
}
.hero-slide.active { opacity: 1; visibility: visible; }
```

### و آن را با این جایگزین کنید (کد جدید):
```css
.hero-slider-track { position: relative; width: 100%; height: 100%; overflow: hidden; }

/*
  افکت جدید اسلایدر: به‌جای محو شدن ساده (Fade)، اسلاید قبلی هم‌زمان به سمت
  راست خارج می‌شود و اسلاید بعدی از سمت چپ وارد می‌شود (Push Transition).
  حالت پیش‌فرض هر اسلاید (نه فعال، نه در حال خروج) همیشه «آماده‌ی ورود از چپ»
  است (translateX(-100%))؛ چون طبق خواسته‌ی شما، ورود همیشه از چپ اتفاق
  می‌افتد، فارغ از اینکه کدام اسلاید بعدی انتخاب شود.
*/
.hero-slide {
  position: absolute;
  inset: 0;
  transform: translateX(-100%);
  visibility: hidden;
  transition: transform 0.6s ease;
  z-index: 1;
}
.hero-slide.active {
  transform: translateX(0);
  visibility: visible;
  z-index: 3;
}
.hero-slide.leaving {
  transform: translateX(100%);
  visibility: visible;
  z-index: 2;
}
```

**نکته‌ی مهم:** مقدار `0.6s` در CSS بالا باید همیشه با مقدار
`TRANSITION_MS = 600` در ابتدای `hero-slider.js` یکی باشد (۶۰۰ میلی‌ثانیه
= ۰.۶ ثانیه؛ الان یکی هستند، نیازی به تغییر نیست -- فقط اگر بعداً سرعت
انیمیشن را عوض کردید، این دو عدد را با هم هماهنگ نگه دارید).

## نتیجه
- اسلاید فعلی هم‌زمان با ورود اسلاید بعدی، به سمت راست صفحه می‌رود و خارج می‌شود.
- اسلاید بعدی از سمت چپ صفحه وارد و در مرکز قرار می‌گیرد.
- این افکت هم برای چرخش خودکار (هر ۵ ثانیه) و هم برای کلیک روی دایره‌های
  پایین بنر یکسان اعمال می‌شود.

## فایل‌های تغییریافته
| فایل | نوع |
|---|---|
| `static/js/hero-slider.js` | جایگزین کامل |
| `static/css/header-hero-v2.css` | فقط بخش بالا (سه قانون `.hero-slider-track` / `.hero-slide` / `.hero-slide.active`) جایگزین شود؛ افزودن قانون جدید `.hero-slide.leaving` |

نیازی به Migration یا تغییر Template نیست. کافیست فایل‌ها را جایگزین/اصلاح
کنید و کش مرورگر را با Ctrl+F5 پاک کنید.
