/**
 * hero-slider.js -- اسلایدر بنر اصلی صفحه خانه
 * چرخش خودکار + کنترل با دایره‌های پایین بنر.
 *
 * انیمیشن گذار: اسلاید فعلی هم‌زمان به سمت راست خارج می‌شود و اسلاید بعدی از
 * سمت چپ وارد می‌شود (Push Transition).
 *
 * نکته‌ی فنی (رفع باگ نسخه‌ی قبل): برای اینکه اسلاید بعدی بی‌صدا (بدون
 * انیمیشن) در سمت چپ خارج از قاب قرار بگیرد، یک transform موقت به‌صورت
 * inline روی آن ست می‌شود. این استایل inline باید بلافاصله بعد از اضافه‌شدن
 * کلاس active پاک شود، وگرنه چون استایل inline همیشه از کلاس CSS قوی‌تر
 * است، اسلاید هیچ‌وقت به وسط قاب برنمی‌گردد و کل ناحیه سفید/خالی می‌ماند
 * (دقیقاً همان مشکلی که پیش آمده بود).
 */
(function () {
  "use strict";

  const TRANSITION_MS = 600; // باید با مدت transform در CSS (.hero-slide) هم‌خوان باشد

  document.addEventListener("DOMContentLoaded", function () {
    const slider = document.getElementById("heroSlider");
    if (!slider) return;

    const slides = Array.from(slider.querySelectorAll(".hero-slide"));
    const dots = Array.from(slider.querySelectorAll(".hero-dot"));
    if (slides.length <= 1) return;

    let current = slides.findIndex((s) => s.classList.contains("active"));
    if (current === -1) current = 0;

    let timer = null;
    let isAnimating = false;
    const interval = parseInt(slider.dataset.interval, 10) || 5000;

    function goToSlide(nextIndex) {
      if (isAnimating || nextIndex === current) return;
      isAnimating = true;

      const currentEl = slides[current];
      const nextEl = slides[nextIndex];

      // مرحله ۱: اسلاید بعدی را بی‌صدا (بدون انیمیشن) در سمت چپ خارج از قاب قرار می‌دهیم
      nextEl.style.transition = "none";
      nextEl.classList.remove("leaving");
      nextEl.style.transform = "translateX(-100%)";
      nextEl.style.visibility = "visible";

      // اجبار به بازمحاسبه‌ی چیدمان (Reflow) تا transition:none واقعاً اعمال
      // شود و مرورگر این حالت را به‌عنوان «نقطه‌ی شروع» ثبت کند
      void nextEl.offsetWidth;

      // مرحله ۲: transition را دوباره فعال می‌کنیم و بلافاصله استایل inline
      // مربوط به transform را پاک می‌کنیم تا کلاس active (که در CSS
      // transform: translateX(0) تعریف شده) بتواند کنترل را به دست بگیرد.
      // پاک‌نکردن همین یک خط، علت اصلی سفید ماندن قسمت اسلایدر در نسخه‌ی قبل بود.
      nextEl.style.transition = "";
      nextEl.style.transform = "";

      // مرحله ۳: هر دو حرکت هم‌زمان شروع می‌شوند: قبلی به راست، بعدی از چپ به مرکز
      currentEl.classList.remove("active");
      currentEl.classList.add("leaving");
      nextEl.classList.add("active");

      dots.forEach((d, i) => d.classList.toggle("active", i === nextIndex));

      setTimeout(() => {
        currentEl.classList.remove("leaving");
        currentEl.style.transform = "";
        currentEl.style.visibility = "";
        isAnimating = false;
      }, TRANSITION_MS + 50);

      current = nextIndex;
    }

    function nextSlide() {
      goToSlide((current + 1) % slides.length);
    }

    function startAutoplay() {
      stopAutoplay();
      timer = setInterval(nextSlide, interval);
    }

    function stopAutoplay() {
      if (timer) clearInterval(timer);
    }

    dots.forEach((dot) => {
      dot.addEventListener("click", () => {
        goToSlide(parseInt(dot.dataset.index, 10));
        startAutoplay();
      });
    });

    slider.addEventListener("mouseenter", stopAutoplay);
    slider.addEventListener("mouseleave", startAutoplay);

    startAutoplay();
  });
})();
