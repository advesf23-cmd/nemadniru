/**
 * hero-slider.js -- اسلایدر بنر اصلی صفحه خانه
 * چرخش خودکار (پیش‌فرض هر ۵ ثانیه، با data-interval قابل تغییر) + کنترل با دایره‌های پایین بنر
 */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    const slider = document.getElementById("heroSlider");
    if (!slider) return;

    const slides = Array.from(slider.querySelectorAll(".hero-slide"));
    const dots = Array.from(slider.querySelectorAll(".hero-dot"));
    if (slides.length <= 1) return;

    let current = 0;
    let timer = null;
    const interval = parseInt(slider.dataset.interval, 10) || 5000;

    function showSlide(index) {
      slides.forEach((s, i) => s.classList.toggle("active", i === index));
      dots.forEach((d, i) => d.classList.toggle("active", i === index));
      current = index;
    }

    function nextSlide() {
      showSlide((current + 1) % slides.length);
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
        showSlide(parseInt(dot.dataset.index, 10));
        startAutoplay(); // ریست تایمر بعد از کلیک دستی
      });
    });

    // توقف موقت چرخش هنگام Hover (تجربه کاربری بهتر)
    slider.addEventListener("mouseenter", stopAutoplay);
    slider.addEventListener("mouseleave", startAutoplay);

    startAutoplay();
  });
})();
