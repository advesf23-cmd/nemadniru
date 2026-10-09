/**
 * hero-slider.js
 *
 * اسلایدر بنر اصلی صفحه خانه
 *
 * امکانات:
 * - چرخش خودکار
 * - دکمه‌های فلش
 * - دایره‌های پایین
 * - Peek سمت چپ = NEXT
 * - Peek سمت راست = PREV
 * - انیمیشن همزمان اسلاید اصلی و Peekها
 *
 * نکته مهم:
 *
 * در HTML فعلی:
 *
 * heroPeekNext = سمت چپ = NEXT
 * heroPeekPrev = سمت راست = PREV
 *
 * نام IDها عمداً تغییر داده نشده تا HTML فعلی شما نیاز به تغییر نداشته باشد.
 */

(function () {
  "use strict";


  /* =========================================================
     تنظیمات
     ========================================================= */

  const TRANSITION_MS = 700;


  document.addEventListener("DOMContentLoaded", function () {

    const slider = document.getElementById("heroSlider");

    if (!slider) {
      return;
    }


    /* =========================================================
       عناصر
       ========================================================= */

    const slides = Array.from(
      slider.querySelectorAll(".hero-slide")
    );

    const dots = Array.from(
      slider.querySelectorAll(".hero-dot")
    );


    /*
     * در HTML فعلی:
     *
     * heroPeekPrev = سمت راست = PREV
     * heroPeekNext = سمت چپ = NEXT
     */

    const peekPrev =
      document.getElementById("heroPeekPrev");

    const peekNext =
      document.getElementById("heroPeekNext");


    const prevBtn =
      document.getElementById("heroPrevBtn");

    const nextBtn =
      document.getElementById("heroNextBtn");


    /* =========================================================
       اگر فقط یک اسلاید داریم
       ========================================================= */

    if (slides.length <= 1) {

      if (peekPrev) {
        peekPrev.style.display = "none";
      }

      if (peekNext) {
        peekNext.style.display = "none";
      }

      if (prevBtn) {
        prevBtn.style.display = "none";
      }

      if (nextBtn) {
        nextBtn.style.display = "none";
      }

      return;
    }


    /* =========================================================
       وضعیت فعلی
       ========================================================= */

    let current =
      slides.findIndex(function (slide) {
        return slide.classList.contains("active");
      });


    if (current === -1) {
      current = 0;
    }


    let timer = null;

    let isAnimating = false;


    const interval =
      parseInt(
        slider.dataset.interval,
        10
      ) || 5000;


    /* =========================================================
       گرفتن URL تصویر
       ========================================================= */

    function imageUrlOf(slideEl) {

      if (!slideEl) {
        return "";
      }

      const img =
        slideEl.querySelector("img");

      if (!img) {
        return "";
      }

      return img.getAttribute("src") || "";
    }


    /* =========================================================
       محاسبه PREV
       ========================================================= */

    function getPrevIndex(index) {

      return (
        (index - 1 + slides.length) %
        slides.length
      );
    }


    /* =========================================================
       محاسبه NEXT
       ========================================================= */

    function getNextIndex(index) {

      return (
        (index + 1) %
        slides.length
      );
    }


    /* =========================================================
       تنظیم وضعیت دائمی Peekها
       =========================================================

       وضعیت باید همیشه بر اساس current واقعی محاسبه شود.

       مثال:

       A | B | C

       current = B

       سمت چپ  = C
       وسط      = B
       سمت راست = A
       ========================================================= */

    function updatePeeks() {

      if (!peekPrev || !peekNext) {
        return;
      }


      const prevIndex =
        getPrevIndex(current);

      const nextIndex =
        getNextIndex(current);


      const prevUrl =
        imageUrlOf(slides[prevIndex]);

      const nextUrl =
        imageUrlOf(slides[nextIndex]);


      /*
       * سمت راست = PREV
       */

      peekPrev.style.setProperty(
        "--peek-current",
        `url("${prevUrl}")`
      );

      peekPrev.style.setProperty(
        "--peek-next",
        `url("${prevUrl}")`
      );


      /*
       * سمت چپ = NEXT
       */

      peekNext.style.setProperty(
        "--peek-current",
        `url("${nextUrl}")`
      );

      peekNext.style.setProperty(
        "--peek-next",
        `url("${nextUrl}")`
      );
    }


    /* =========================================================
       آماده‌سازی Peek برای Transition
       =========================================================

       نکته مهم:

       اینجا دیگر بر اساس direction حدس نمی‌زنیم
       که تصویر بعدی چیست.

       مستقیماً از nextIndex استفاده می‌کنیم.

       این مشکل اصلی نسخه قبلی بود.

       مثال:

       قبل:

       A | B | C

       اگر هدف A باشد:

       بعد:

       Z | A | B

       بنابراین:

       oldPrev = A
       oldNext = C

       newPrev = Z
       newNext = B

       و همین دقیقاً چیزی است که این تابع محاسبه می‌کند.
       ========================================================= */

    function preparePeekTransition(
      nextIndex,
      direction
    ) {

      if (!peekPrev || !peekNext) {
        return;
      }


      /* -----------------------------------------
         وضعیت قبلی
         ----------------------------------------- */

      const oldPrevIndex =
        getPrevIndex(current);

      const oldNextIndex =
        getNextIndex(current);


      /* -----------------------------------------
         وضعیت نهایی
         ----------------------------------------- */

      const newPrevIndex =
        getPrevIndex(nextIndex);

      const newNextIndex =
        getNextIndex(nextIndex);


      /* -----------------------------------------
         URLهای قدیمی
         ----------------------------------------- */

      const oldPrevUrl =
        imageUrlOf(
          slides[oldPrevIndex]
        );

      const oldNextUrl =
        imageUrlOf(
          slides[oldNextIndex]
        );


      /* -----------------------------------------
         URLهای جدید
         ----------------------------------------- */

      const newPrevUrl =
        imageUrlOf(
          slides[newPrevIndex]
        );

      const newNextUrl =
        imageUrlOf(
          slides[newNextIndex]
        );


      /* -----------------------------------------
         پاک کردن animation قبلی
         ----------------------------------------- */

      peekPrev.classList.remove(
        "peek-motion-next",
        "peek-motion-prev"
      );

      peekNext.classList.remove(
        "peek-motion-next",
        "peek-motion-prev"
      );


      /* -----------------------------------------
         قرار دادن تصویر فعلی و تصویر بعدی
         -----------------------------------------

         نکته بسیار مهم:

         --peek-current
         تصویر قدیمی است.

         --peek-next
         تصویر جدید است.

         بنابراین هر دو قبل از شروع transition
         داخل CSS وجود دارند.
         ----------------------------------------- */


      /*
       * سمت راست = PREV
       */

      peekPrev.style.setProperty(
        "--peek-current",
        `url("${oldPrevUrl}")`
      );

      peekPrev.style.setProperty(
        "--peek-next",
        `url("${newPrevUrl}")`
      );


      /*
       * سمت چپ = NEXT
       */

      peekNext.style.setProperty(
        "--peek-current",
        `url("${oldNextUrl}")`
      );

      peekNext.style.setProperty(
        "--peek-next",
        `url("${newNextUrl}")`
      );


      /*
       * Force reflow
       *
       * باعث می‌شود مرورگر مطمئن شود
       * وضعیت قبلی ثبت شده و animation
       * از ابتدای مسیر شروع شود.
       */

      void peekPrev.offsetWidth;
      void peekNext.offsetWidth;


      /* -----------------------------------------
         شروع حرکت Peek
         -----------------------------------------

         direction === "next"

         یعنی حرکت اصلی:

         چپ -> راست

         پس تصویر قدیمی Peek
         به سمت راست می‌رود.

         تصویر جدید
         از سمت چپ وارد می‌شود.
         ----------------------------------------- */

      if (direction === "next") {

        /*
         * حرکت اصلی اکنون راست -> چپ است؛
         * بنابراین Peekها هم باید به همین جهت حرکت کنند.
         */
        peekPrev.classList.add(
          "peek-motion-prev"
        );

        peekNext.classList.add(
          "peek-motion-prev"
        );

      }


      /* -----------------------------------------
         direction === "prev"

         حرکت اصلی چپ -> راست است؛
         Peekها نیز باید چپ -> راست حرکت کنند.
         ----------------------------------------- */

      else {

        peekPrev.classList.add(
          "peek-motion-next"
        );

        peekNext.classList.add(
          "peek-motion-next"
        );
      }
    }


    /* =========================================================
       رفتن به اسلاید
       ========================================================= */

    function goToSlide(
      nextIndex,
      direction = "next"
    ) {

      /*
       * اگر در حال انیمیشن هستیم،
       * حرکت جدید شروع نکن.
       */

      if (
        isAnimating ||
        nextIndex === current
      ) {
        return;
      }


      isAnimating = true;


      const currentEl =
        slides[current];

      const nextEl =
        slides[nextIndex];


      /* =====================================================
         جهت حرکت اسلاید اصلی
         =====================================================

         direction = next

         یعنی اسلاید فعلی به چپ می‌رود
         و اسلاید هدف از راست وارد می‌شود.


         direction = prev

         یعنی اسلاید فعلی به راست می‌رود
         و اسلاید هدف از چپ وارد می‌شود.
         ===================================================== */

      const incomingTransform =
        direction === "next"
          ? "translateX(100%)"
          : "translateX(-100%)";


      const outgoingTransform =
        direction === "next"
          ? "translateX(-100%)"
          : "translateX(100%)";


      /* =====================================================
         آماده‌سازی اسلاید جدید
         ===================================================== */

      nextEl.style.transition = "none";

      nextEl.style.transform =
        incomingTransform;

      nextEl.style.visibility =
        "visible";

      nextEl.classList.remove(
        "active",
        "leaving"
      );


      /*
       * Force reflow
       */

      void nextEl.offsetWidth;


      /* =====================================================
         آماده‌سازی Peekها
         ===================================================== */

      preparePeekTransition(
        nextIndex,
        direction
      );


      /* =====================================================
         شروع Transition اصلی
         ===================================================== */

      nextEl.style.transition = "";

      currentEl.style.transition = "";


      /*
       * خروج اسلاید فعلی
       */

      currentEl.style.transform =
        outgoingTransform;


      /*
       * ورود اسلاید جدید
       */

      nextEl.style.transform =
        "translateX(0)";


      currentEl.classList.remove(
        "active"
      );

      currentEl.classList.add(
        "leaving"
      );

      nextEl.classList.add(
        "active"
      );


      /* =====================================================
         به‌روزرسانی نقاط
         ===================================================== */

      dots.forEach(function (dot, index) {

        dot.classList.toggle(
          "active",
          index === nextIndex
        );

      });


      /* =====================================================
         پایان Transition
         ===================================================== */

      setTimeout(function () {


        /* -----------------------------------------
           پاکسازی اسلاید قبلی
           ----------------------------------------- */

        currentEl.classList.remove(
          "leaving"
        );

        currentEl.style.transform = "";

        currentEl.style.transition = "";

        currentEl.style.visibility = "";


        /* -----------------------------------------
           پاکسازی اسلاید جدید
           ----------------------------------------- */

        nextEl.style.transform = "";

        nextEl.style.transition = "";


        /* -----------------------------------------
           ثبت current جدید
           ----------------------------------------- */

        current = nextIndex;


        /* -----------------------------------------
           پاکسازی Peek animation
           ----------------------------------------- */

        if (peekPrev) {

          peekPrev.classList.remove(
            "peek-motion-next",
            "peek-motion-prev"
          );
        }


        if (peekNext) {

          peekNext.classList.remove(
            "peek-motion-next",
            "peek-motion-prev"
          );
        }


        /*
         * اکنون current تغییر کرده است.
         *
         * Peekها را از نو با وضعیت واقعی
         * اسلاید جدید تنظیم می‌کنیم.
         *
         * چون animation قبلی تمام شده،
         * این تغییر دیگر برای کاربر پرش ایجاد نمی‌کند.
         */

        updatePeeks();


        /* -----------------------------------------
           پایان قفل انیمیشن
           ----------------------------------------- */

        isAnimating = false;

      }, TRANSITION_MS + 50);
    }


    /* =========================================================
       حرکت به سمت اسلاید سمت چپ
       =========================================================

       طبق طراحی فعلی شما:

       سمت چپ = NEXT از نظر Peek بصری،
       اما nextSlide در سیستم فعلی یعنی:

       اسلاید سمت چپ وارد مرکز شود.

       بنابراین:

       current - 1
       ========================================================= */

    function nextSlide() {

      const prevIndex =
        (
          current - 1 + slides.length
        ) % slides.length;


      goToSlide(
        prevIndex,
        "next"
      );
    }


    /* =========================================================
       حرکت به سمت اسلاید سمت راست
       ========================================================= */

    function prevSlide() {

      const nextIndex =
        (
          current + 1
        ) % slides.length;


      goToSlide(
        nextIndex,
        "prev"
      );
    }


    /* =========================================================
       Autoplay
       ========================================================= */

    function startAutoplay() {

      stopAutoplay();

      timer = setInterval(
        function () {
          nextSlide();
        },
        interval
      );
    }


    function stopAutoplay() {

      if (timer) {

        clearInterval(timer);

        timer = null;
      }
    }


    /* =========================================================
       دکمه‌های پایین
       ========================================================= */

    dots.forEach(function (dot) {

      dot.addEventListener(
        "click",
        function () {

          const targetIndex =
            parseInt(
              dot.dataset.index,
              10
            );


          if (
            Number.isNaN(targetIndex) ||
            targetIndex === current ||
            isAnimating
          ) {
            return;
          }


          /*
           * فاصله در جهت جلو
           */

          const forwardDistance =
            (
              targetIndex -
              current +
              slides.length
            ) % slides.length;


          /*
           * فاصله در جهت عقب
           */

          const backwardDistance =
            (
              current -
              targetIndex +
              slides.length
            ) % slides.length;


          /*
           * چون در معماری فعلی:

           * "prev"
           * = حرکت راست به چپ

           * "next"
           * = حرکت چپ به راست

           * برای نزدیک‌ترین مسیر انتخاب می‌کنیم.
           */

          const direction =
            forwardDistance <= backwardDistance
              ? "prev"
              : "next";


          goToSlide(
            targetIndex,
            direction
          );


          startAutoplay();
        }
      );

    });


    /* =========================================================
       فلش سمت چپ
       ========================================================= */

    if (prevBtn) {

      prevBtn.addEventListener(
        "click",
        function () {

          prevSlide();

          startAutoplay();
        }
      );
    }


    /* =========================================================
       فلش سمت راست
       ========================================================= */

    if (nextBtn) {

      nextBtn.addEventListener(
        "click",
        function () {

          nextSlide();

          startAutoplay();
        }
      );
    }


    /* =========================================================
       کلیک روی Peek سمت چپ
       =========================================================

       در HTML فعلی:

       heroPeekNext
       =
       سمت چپ
       =
       اسلایدی که باید وارد مرکز شود.

       بنابراین nextSlide().
       ========================================================= */

    if (peekNext) {

      peekNext.addEventListener(
        "click",
        function () {

          nextSlide();

          startAutoplay();
        }
      );
    }


    /* =========================================================
       کلیک روی Peek سمت راست
       =========================================================

       در HTML فعلی:

       heroPeekPrev
       =
       سمت راست
       =
       اسلاید قبلی از نظر حرکت.

       بنابراین prevSlide().
       ========================================================= */

    if (peekPrev) {

      peekPrev.addEventListener(
        "click",
        function () {

          prevSlide();

          startAutoplay();
        }
      );
    }


    /* =========================================================
       توقف Autoplay هنگام Hover
       ========================================================= */

    slider.addEventListener(
      "mouseenter",
      function () {
        stopAutoplay();
      }
    );


    slider.addEventListener(
      "mouseleave",
      function () {
        startAutoplay();
      }
    );


    /* =========================================================
       مقداردهی اولیه
       ========================================================= */

    updatePeeks();

    startAutoplay();

  });

})();