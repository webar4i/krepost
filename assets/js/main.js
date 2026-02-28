    document.addEventListener("DOMContentLoaded", () => {
      
      // 1. Lenis Smooth Scroll
      const lenis = new Lenis({ duration: 1.2, easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)) });
      function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }
      requestAnimationFrame(raf);

      // 2. Custom Cursor (Blend mode)
      const cursor = document.querySelector('.cursor');
      if (window.innerWidth > 768 && cursor) {
        let mouseX = window.innerWidth / 2, mouseY = window.innerHeight / 2;
        window.addEventListener('mousemove', (e) => {
          mouseX = e.clientX; mouseY = e.clientY;
          cursor.style.transform = `translate3d(${mouseX}px, ${mouseY}px, 0)`;
        });

        document.querySelectorAll('a, button, input, select, .hover-target').forEach(el => {
          el.addEventListener('mouseenter', () => document.body.classList.add('hovering'));
          el.addEventListener('mouseleave', () => document.body.classList.remove('hovering'));
        });
        
        document.querySelectorAll('.hover-img-target').forEach(el => {
          el.addEventListener('mouseenter', () => document.body.classList.add('hovering-img'));
          el.addEventListener('mouseleave', () => document.body.classList.remove('hovering-img'));
        });
      }

      // 3. Desktop Mega Menu (structure from reports)
      const megaWrap = document.querySelector('.nav-mega-wrap');
      const megaTrigger = document.querySelector('.nav-mega-trigger');
      const megaMenu = document.querySelector('.mega-menu');
      const desktopNavLinks = document.querySelectorAll('.nav a');
      const megaLinks = document.querySelectorAll('.mega-menu a');

      const closeMegaMenu = () => {
        if (!megaWrap || !megaTrigger) return;
        megaWrap.classList.remove('is-open');
        megaTrigger.setAttribute('aria-expanded', 'false');
      };

      const positionMegaMenu = () => {
        if (!megaMenu || !megaWrap) return;

        const isOpen = megaWrap.classList.contains('is-open');
        const baselineTransform = isOpen ? 'translate3d(0px, 0, 0)' : 'translate3d(0px, 8px, 0)';
        const previousInlineTransition = megaMenu.style.transition;
        megaMenu.style.transition = 'none';
        megaMenu.style.transform = baselineTransform;

        const rootPad = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--pad'));
        const viewportPadding = Number.isFinite(rootPad) ? Math.max(8, rootPad) : 12;
        const rect = megaMenu.getBoundingClientRect();
        let shiftX = 0;

        if (rect.left < viewportPadding) {
          shiftX += viewportPadding - rect.left;
        }
        if (rect.right > window.innerWidth - viewportPadding) {
          shiftX -= rect.right - (window.innerWidth - viewportPadding);
        }

        megaMenu.style.setProperty('--mega-shift-x', `${Math.round(shiftX)}px`);
        megaMenu.style.transform = `translate3d(${Math.round(shiftX)}px, ${isOpen ? 0 : 8}px, 0)`;
        void megaMenu.offsetWidth;
        megaMenu.style.transition = previousInlineTransition;
      };

      const scheduleMegaMenuPosition = () => {
        requestAnimationFrame(() => {
          positionMegaMenu();
          requestAnimationFrame(positionMegaMenu);
        });
        setTimeout(positionMegaMenu, 120);
      };

      const openMegaMenu = () => {
        if (!megaWrap || !megaTrigger) return;
        megaWrap.classList.add('is-open');
        megaTrigger.setAttribute('aria-expanded', 'true');
        scheduleMegaMenuPosition();
      };

      if (megaWrap && megaTrigger && megaMenu) {
        megaTrigger.addEventListener('click', (event) => {
          event.stopPropagation();
          const isOpen = megaWrap.classList.contains('is-open');
          if (isOpen) {
            closeMegaMenu();
          } else {
            openMegaMenu();
          }
        });

        document.addEventListener('click', (event) => {
          if (!megaWrap.contains(event.target)) closeMegaMenu();
        });

        megaLinks.forEach((link) => link.addEventListener('click', closeMegaMenu));
        desktopNavLinks.forEach((link) => link.addEventListener('click', closeMegaMenu));

        window.addEventListener('resize', () => {
          if (window.innerWidth <= 1024) closeMegaMenu();
          if (window.innerWidth > 1024) positionMegaMenu();
        });

        positionMegaMenu();
        window.addEventListener('load', positionMegaMenu);
        if (document.fonts && typeof document.fonts.ready?.then === 'function') {
          document.fonts.ready.then(positionMegaMenu);
        }
      }

      // 4. Mobile Navigation (conversion-first on small screens)
      const menuToggle = document.querySelector('.menu-toggle');
      const mobileNavOverlay = document.querySelector('.mobile-nav-overlay');
      const mobileClose = document.querySelector('.mobile-close');
      const mobileNavLinks = document.querySelectorAll('.mobile-nav a');

      const closeMobileNav = () => {
        document.body.classList.remove('menu-open');
        if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false');
        lenis.start();
      };

      const openMobileNav = () => {
        document.body.classList.add('menu-open');
        if (menuToggle) menuToggle.setAttribute('aria-expanded', 'true');
        lenis.stop();
      };

      if (menuToggle && mobileNavOverlay && mobileClose) {
        menuToggle.addEventListener('click', () => {
          const isOpen = document.body.classList.contains('menu-open');
          if (isOpen) {
            closeMobileNav();
          } else {
            openMobileNav();
          }
        });

        mobileNavOverlay.addEventListener('click', closeMobileNav);
        mobileClose.addEventListener('click', closeMobileNav);
        mobileNavLinks.forEach((link) => link.addEventListener('click', closeMobileNav));

        window.addEventListener('keydown', (event) => {
          if (event.key !== 'Escape') return;
          if (document.body.classList.contains('menu-open')) closeMobileNav();
          closeMegaMenu();
        });

        window.addEventListener('resize', () => {
          if (window.innerWidth > 1024 && document.body.classList.contains('menu-open')) {
            closeMobileNav();
          }
          if (window.innerWidth <= 1024 && document.body.classList.contains('show-follower')) {
            document.body.classList.remove('show-follower');
          }
        });
      }

      // 5. Image Follower for Services (ARHDM/Behance Style Effect)
      const follower = document.querySelector('.hover-img-follower');
      const svcTriggers = document.querySelectorAll('.svc-hover-trigger');
      const followerImgs = follower ? follower.querySelectorAll('img') : [];

      if (window.innerWidth > 1024 && follower && svcTriggers.length) {
        let fX = window.innerWidth / 2, fY = window.innerHeight / 2;
        let tX = fX, tY = fY;
        
        window.addEventListener('mousemove', (e) => { tX = e.clientX; tY = e.clientY; });

        const renderFollower = () => {
          fX += (tX - fX) * 0.1; fY += (tY - fY) * 0.1; // Smooth lerp
          follower.style.transform = `translate3d(${fX}px, ${fY}px, 0) scale(${document.body.classList.contains('show-follower') ? 1 : 0.8})`;
          requestAnimationFrame(renderFollower);
        };
        requestAnimationFrame(renderFollower);

        svcTriggers.forEach(trigger => {
          trigger.addEventListener('mouseenter', () => {
            document.body.classList.add('show-follower');
            const imgId = trigger.getAttribute('data-img');
            followerImgs.forEach(img => img.classList.remove('active'));
            document.getElementById(`img-${imgId}`).classList.add('active');
          });
          trigger.addEventListener('mouseleave', () => {
            document.body.classList.remove('show-follower');
          });
        });
      }

      // 6. Scroll Reveals (Intersection Observer)
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) entry.target.classList.add('in-view');
        });
      }, { threshold: 0.15, rootMargin: "0px 0px -50px 0px" });
      document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

      // 7. Image Parallax
      const parImgs = document.querySelectorAll('.hero-img.parallax-img');
      lenis.on('scroll', (e) => {
        parImgs.forEach(img => {
          img.style.transform = `translate3d(0, ${e.animatedScroll * 0.08}px, 0) scale(1.05)`;
        });
      });

      // 8. FAQ Accordion Logic
      document.querySelectorAll('.faq-head').forEach(head => {
        head.addEventListener('click', () => {
          const parent = head.parentElement;
          const isActive = parent.classList.contains('active');
          document.querySelectorAll('.faq-item').forEach(el => el.classList.remove('active'));
          if (!isActive) parent.classList.add('active');
        });
      });

    });
