(function () {
  const cfg = window.ANALYTICS_CONFIG || {};
  window.dataLayer = window.dataLayer || [];

  function getCtx() {
    const body = document.body || {};
    const ds = body.dataset || {};
    return {
      page_type: ds.pageType || "unknown",
      service: ds.service || "all"
    };
  }

  function sendEvent(name, params) {
    const payload = Object.assign({ event: name }, getCtx(), params || {});
    window.dataLayer.push(payload);

    if (typeof window.gtag === "function") {
      window.gtag("event", name, payload);
    }

    if (typeof window.ym === "function" && cfg.yandexMetrikaId) {
      try {
        window.ym(Number(cfg.yandexMetrikaId), "reachGoal", name, payload);
      } catch (e) {
        // no-op
      }
    }
  }

  document.addEventListener("click", function (event) {
    const tel = event.target.closest("a[href^='tel:']");
    if (tel) {
      sendEvent("call_click", { href: tel.getAttribute("href") });
      return;
    }

    const direct = event.target.closest("[data-event]");
    if (direct) {
      const { event: ev, ctaId, formId, caseId, pageType, service } = direct.dataset;
      sendEvent(ev, {
        cta_id: ctaId || "",
        form_id: formId || "",
        case_id: caseId || "",
        page_type: pageType || getCtx().page_type,
        service: service || getCtx().service
      });
      return;
    }

    const caseCard = event.target.closest(".case-card");
    if (caseCard) {
      sendEvent("case_view", {
        case_id: caseCard.dataset.caseId || caseCard.getAttribute("href") || ""
      });
      return;
    }

    const faqHead = event.target.closest(".faq-head");
    if (faqHead) {
      sendEvent("faq_expand", {
        faq_id: faqHead.dataset.faqId || faqHead.textContent.trim().slice(0, 120)
      });
      return;
    }

    const primaryBtn = event.target.closest(".btn:not(.btn-outline)");
    if (primaryBtn) {
      sendEvent("cta_click_primary", {
        cta_id: primaryBtn.dataset.ctaId || primaryBtn.textContent.trim().slice(0, 80)
      });
    }
  });

  document.addEventListener("submit", function (event) {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) return;

    sendEvent("form_submit", {
      form_id: form.dataset.formId || form.id || "lead_form",
      page_type: (form.dataset.pageType || getCtx().page_type),
      service: (form.dataset.service || getCtx().service)
    });
  });

  let sent50 = false;
  let sent90 = false;
  window.addEventListener("scroll", function () {
    const doc = document.documentElement;
    const total = doc.scrollHeight - doc.clientHeight;
    if (total <= 0) return;
    const depth = (window.scrollY / total) * 100;

    if (!sent50 && depth >= 50) {
      sent50 = true;
      sendEvent("scroll_50", {});
    }

    if (!sent90 && depth >= 90) {
      sent90 = true;
      sendEvent("scroll_90", {});
    }
  }, { passive: true });

  const priceBlocks = document.querySelectorAll("[data-track-price]");
  if (priceBlocks.length && "IntersectionObserver" in window) {
    const timers = new Map();
    const viewed = new Set();
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        const el = entry.target;
        const id = el.dataset.trackPrice || "price_block";

        if (viewed.has(id)) return;

        if (entry.isIntersecting) {
          const t = window.setTimeout(() => {
            viewed.add(id);
            sendEvent("price_view", { block_id: id });
          }, 5000);
          timers.set(el, t);
        } else if (timers.has(el)) {
          window.clearTimeout(timers.get(el));
          timers.delete(el);
        }
      });
    }, { threshold: 0.6 });

    priceBlocks.forEach((el) => observer.observe(el));
  }
})();
