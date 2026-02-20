#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://krepostdom.ru"
PHONE_RAW = "+79035262526"
PHONE_DISPLAY = "+7 (903) 526-25-26"
EMAIL = "info@krepostdom.ru"

INDEX_PATH = ROOT / "index.html"
SEO_TABLE = ROOT / "reports/05_stage4_content_meta/seo_elements_table.csv"
AEO_TABLE = ROOT / "reports/03_stage2_semantics/aeo_qa_matrix.csv"

# URLs from plan: phase 1 + phase 2A + phase 2B
URLS = [
    "/services/",
    "/services/stroitelstvo-domov-pod-klyuch-mahachkala/",
    "/services/proektirovanie-domov-mahachkala/",
    "/services/proekt-inzhenernyh-setey-mahachkala/",
    "/services/otdelochnye-raboty-mahachkala/",
    "/tseny/",
    "/tseny/stroitelstvo-domov-v-dagestane/",
    "/tseny/otdelochnye-raboty-mahachkala/",
    "/raboty/",
    "/otzyvy/",
    "/faq/",
    "/guides/",
    "/guides/stroitelstvo/oshibki-pri-vybore-podryadchika/",
    "/guides/proektirovanie/chto-vhodit-v-proekt/",
    "/guides/inzheneriya/vodosnabzhenie-i-kanalizaciya/",
    "/guides/otdelka/chernovaya-vs-chistovaya/",
    "/o-kompanii/",
    "/kontakty/",
    "/guides/stroitelstvo/kak-vybrat-tehnologiyu-doma/",
    "/guides/proektirovanie/kak-sostavit-tz/",
    "/guides/proektirovanie/tipovoy-vs-individualnyy-proekt/",
    "/guides/inzheneriya/elektrika-i-slabotochka/",
    "/guides/inzheneriya/stoimost-proekta-setey/",
    "/guides/otdelka/etapy-i-sroki/",
]
EXISTING_ROUTES = set(["/"] + URLS)

PAGE_META_DEFAULTS = {
    "/services/": {
        "title": "Услуги строительства и проектирования в Махачкале | КРЕПОСТЬ",
        "description": "Услуги КРЕПОСТЬ: строительство домов под ключ, проектирование, инженерные сети и отделочные работы в Махачкале и Дагестане.",
        "h1": "Услуги КРЕПОСТЬ",
        "page_type": "service_category",
        "cluster": "Все направления",
        "intent": "Commercial",
        "primary_cta": "Получить смету",
    },
    "/raboty/": {
        "title": "Кейсы строительства и отделки в Махачкале | КРЕПОСТЬ",
        "description": "Реальные кейсы КРЕПОСТЬ: строительство домов, проектирование, инженерия и отделка. Задачи, решения, этапы и результат.",
        "h1": "Кейсы и портфолио",
        "page_type": "cases_hub",
        "cluster": "Доверие",
        "intent": "Commercial",
        "primary_cta": "Обсудить похожий проект",
    },
    "/otzyvy/": {
        "title": "Отзывы клиентов о КРЕПОСТЬ | Махачкала",
        "description": "Отзывы клиентов о строительстве, проектировании и отделке. Внешние площадки и верифицированные отзывы на сайте.",
        "h1": "Отзывы и репутация",
        "page_type": "reviews_hub",
        "cluster": "Доверие",
        "intent": "Commercial",
        "primary_cta": "Оставить заявку",
    },
    "/guides/": {
        "title": "Гайды по строительству, проектированию и отделке | КРЕПОСТЬ",
        "description": "Практические гайды: как выбрать подрядчика, контролировать смету, проектировать дом и планировать инженерные сети в Махачкале.",
        "h1": "Гайды и полезные материалы",
        "page_type": "guides_hub",
        "cluster": "Информационные кластеры",
        "intent": "Informational",
        "primary_cta": "Получить консультацию",
    },
    "/o-kompanii/": {
        "title": "О компании КРЕПОСТЬ | Строительство домов в Махачкале",
        "description": "КРЕПОСТЬ: команда полного цикла по строительству домов, проектированию, инженерии и отделке в Махачкале и Дагестане.",
        "h1": "О компании КРЕПОСТЬ",
        "page_type": "trust_page",
        "cluster": "Доверие",
        "intent": "Navigational",
        "primary_cta": "Получить смету",
    },
    "/kontakty/": {
        "title": "Контакты КРЕПОСТЬ | Махачкала и Республика Дагестан",
        "description": "Контакты КРЕПОСТЬ: телефон, email, зоны обслуживания по Махачкале и Дагестану. Заявка на предварительный расчет.",
        "h1": "Контакты и зоны обслуживания",
        "page_type": "trust_page",
        "cluster": "Локальное SEO",
        "intent": "Navigational",
        "primary_cta": "Связаться с нами",
    },
    "/guides/stroitelstvo/kak-vybrat-tehnologiyu-doma/": {
        "title": "Как выбрать технологию строительства дома в Дагестане | КРЕПОСТЬ",
        "description": "Сравнение технологий строительства дома: газобетон, кирпич, каркас и монолит. Критерии выбора под бюджет и сроки.",
        "h1": "Как выбрать технологию дома",
        "page_type": "guide_pillar",
        "cluster": "Строительство домов",
        "intent": "Informational",
        "primary_cta": "Получить консультацию по технологии",
    },
    "/guides/proektirovanie/kak-sostavit-tz/": {
        "title": "Как составить ТЗ на проектирование дома | КРЕПОСТЬ",
        "description": "Чек-лист технического задания на проект дома: исходные данные, этапы согласования, состав разделов и контроль сроков.",
        "h1": "Как составить ТЗ на проект",
        "page_type": "guide_pillar",
        "cluster": "Проектирование",
        "intent": "Informational",
        "primary_cta": "Заказать проект",
    },
    "/guides/proektirovanie/tipovoy-vs-individualnyy-proekt/": {
        "title": "Типовой или индивидуальный проект дома: что выбрать | КРЕПОСТЬ",
        "description": "Разбираем разницу между типовым и индивидуальным проектом: сроки, бюджет, риски и сценарии применения.",
        "h1": "Типовой vs индивидуальный проект",
        "page_type": "guide_pillar",
        "cluster": "Проектирование",
        "intent": "Informational",
        "primary_cta": "Обсудить проект",
    },
    "/guides/inzheneriya/elektrika-i-slabotochka/": {
        "title": "Электрика и слаботочные системы в частном доме | КРЕПОСТЬ",
        "description": "Что важно учесть в проекте электрики и слаботочных систем: нагрузки, безопасность, резервы и эксплуатация.",
        "h1": "Электрика и слаботочка",
        "page_type": "guide_pillar",
        "cluster": "Инженерия",
        "intent": "Informational",
        "primary_cta": "Получить проект инженерных сетей",
    },
    "/guides/inzheneriya/stoimost-proekta-setey/": {
        "title": "Сколько стоит проект инженерных сетей для частного дома | КРЕПОСТЬ",
        "description": "Факторы стоимости проекта инженерных сетей: состав разделов, сложность объекта, сроки и глубина проработки.",
        "h1": "Стоимость проекта инженерных сетей",
        "page_type": "guide_pillar",
        "cluster": "Инженерия",
        "intent": "Informational",
        "primary_cta": "Получить консультацию инженера",
    },
    "/guides/otdelka/etapy-i-sroki/": {
        "title": "Этапы и сроки отделочных работ в Махачкале | КРЕПОСТЬ",
        "description": "Пошаговый план отделочных работ: черновой и чистовой этапы, контроль качества, сроки и точки согласования.",
        "h1": "Этапы и сроки отделочных работ",
        "page_type": "guide_pillar",
        "cluster": "Отделочные работы",
        "intent": "Informational",
        "primary_cta": "Рассчитать стоимость отделки",
    },
    "/tseny/stroitelstvo-domov-v-dagestane/": {
        "title": "Цены на строительство домов в Дагестане | КРЕПОСТЬ",
        "description": "Актуальные сценарии стоимости строительства дома в Дагестане: факторы бюджета, этапы и что влияет на итоговую цену.",
        "h1": "Цены на строительство домов в Дагестане",
        "page_type": "prices",
        "cluster": "Строительство",
        "intent": "Commercial",
        "primary_cta": "Получить расчет строительства",
    },
    "/tseny/otdelochnye-raboty-mahachkala/": {
        "title": "Цены на отделочные работы в Махачкале | КРЕПОСТЬ",
        "description": "Сколько стоят отделочные работы в Махачкале: черновая и чистовая отделка, факторы цены и сценарии бюджета.",
        "h1": "Цены на отделочные работы в Махачкале",
        "page_type": "prices",
        "cluster": "Отделка",
        "intent": "Commercial",
        "primary_cta": "Получить расчет отделки",
    },
    "/guides/proektirovanie/chto-vhodit-v-proekt/": {
        "title": "Что входит в проект дома: состав и структура | КРЕПОСТЬ",
        "description": "Разбираем состав проекта дома: архитектурные, конструктивные и инженерные разделы, сроки подготовки и контроль качества.",
        "h1": "Что входит в проект дома",
        "page_type": "guide_pillar",
        "cluster": "Проектирование",
        "intent": "Informational",
        "primary_cta": "Заказать проект дома",
    },
    "/guides/inzheneriya/vodosnabzhenie-i-kanalizaciya/": {
        "title": "Водоснабжение и канализация частного дома: что важно учесть | КРЕПОСТЬ",
        "description": "Практический гайд по проектированию водоснабжения и канализации: состав решений, типичные ошибки и контрольные точки.",
        "h1": "Водоснабжение и канализация частного дома",
        "page_type": "guide_pillar",
        "cluster": "Инженерия",
        "intent": "Informational",
        "primary_cta": "Получить консультацию по инженерии",
    },
    "/guides/otdelka/chernovaya-vs-chistovaya/": {
        "title": "Черновая и чистовая отделка: отличия и бюджет | КРЕПОСТЬ",
        "description": "Сравнение черновой и чистовой отделки: этапы, сроки, контроль качества и влияние на бюджет проекта.",
        "h1": "Черновая и чистовая отделка: в чем разница",
        "page_type": "guide_pillar",
        "cluster": "Отделка",
        "intent": "Informational",
        "primary_cta": "Рассчитать стоимость отделки",
    },
}

GUIDE_BASE_FAQ = [
    ("Зачем нужен этот материал перед стартом проекта?", "Чтобы быстрее принять решение и избежать типовых ошибок по бюджету, срокам и составу работ."),
    ("Можно ли получить персональные рекомендации по объекту?", "Да, после короткого брифа подскажем релевантный сценарий под ваш участок и задачу."),
    ("Где посмотреть примеры реализованных проектов?", "Реальные кейсы собраны на странице /raboty/ с разбором задач, решений и результатов."),
]


def read_csv_semicolon(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


def ensure_dirs():
    (ROOT / "assets/css").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets/js").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets/img").mkdir(parents=True, exist_ok=True)


def extract_assets_from_index(index_text: str):
    style_m = re.search(r"\n  <style>\n(.*?)\n  </style>\n", index_text, flags=re.S)
    script_m = re.search(r"\n  <!-- СКРИПТЫ -->\n  <script>\n(.*?)\n  </script>\n", index_text, flags=re.S)
    if not style_m or not script_m:
        raise RuntimeError("Не удалось извлечь style/script из index.html")

    css = style_m.group(1).rstrip() + "\n"
    css += "\n/* ==========================================================================\n   GENERIC INNER PAGES\n   ========================================================================== */\n"
    css += ".page-intro{padding:56px var(--pad);display:grid;gap:16px;background:var(--bg-white);}\n"
    css += ".page-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;}\n"
    css += ".page-card{padding:34px;border-right:1px solid var(--border);border-bottom:1px solid var(--border);background:var(--bg-white);}\n"
    css += ".page-grid .page-card:nth-child(3n){border-right:none;}\n"
    css += ".page-card h3{margin-bottom:10px;}\n"
    css += ".page-links{display:grid;gap:10px;margin-top:14px;}\n"
    css += ".page-links a{text-decoration:underline;text-underline-offset:3px;color:var(--text-muted);}\n"
    css += ".article-table{width:100%;border-collapse:collapse;background:var(--bg-white);}\n"
    css += ".article-table th,.article-table td{padding:14px var(--pad);border-bottom:1px solid var(--border);text-align:left;vertical-align:top;}\n"
    css += ".cta-strip{padding:28px var(--pad);display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;background:var(--bg-white);border-top:1px solid var(--border);}\n"
    css += ".cta-actions{display:flex;gap:10px;flex-wrap:wrap;}\n"
    css += ".guide-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));}\n"
    css += ".guide-item{padding:24px;border-right:1px solid var(--border);border-bottom:1px solid var(--border);background:var(--bg-white);}\n"
    css += ".guide-item:nth-child(2n){border-right:none;}\n"
    css += ".breadcrumbs{padding:12px var(--pad);border-bottom:1px solid var(--border);display:flex;flex-wrap:wrap;gap:8px;background:var(--bg-white);}\n"
    css += ".breadcrumbs a{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--text-muted);}\n"
    css += ".breadcrumbs span{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--text);}\n"
    css += "@media (max-width:1024px){.page-grid{grid-template-columns:1fr 1fr;}.page-grid .page-card:nth-child(2n){border-right:none;}.guide-list{grid-template-columns:1fr;}.guide-item{border-right:none;}.cta-strip{flex-direction:column;align-items:flex-start;}}\n"
    css += "@media (max-width:768px){.page-grid{grid-template-columns:1fr;}.page-card{border-right:none;}.article-table th{display:none;}.article-table td{display:block;padding:10px var(--pad);}.article-table tr{display:block;border-bottom:1px solid var(--border);padding:16px 0;}}\n"

    js = script_m.group(1).rstrip() + "\n"
    js = js.replace(
        "const follower = document.querySelector('.hover-img-follower');\n      const svcTriggers = document.querySelectorAll('.svc-hover-trigger');\n      const followerImgs = follower.querySelectorAll('img');\n\n      if (window.innerWidth > 1024) {",
        "const follower = document.querySelector('.hover-img-follower');\n      const svcTriggers = document.querySelectorAll('.svc-hover-trigger');\n      const followerImgs = follower ? follower.querySelectorAll('img') : [];\n\n      if (window.innerWidth > 1024 && follower && svcTriggers.length) {",
    )

    (ROOT / "assets/css/main.css").write_text(css, encoding="utf-8")
    (ROOT / "assets/js/main.js").write_text(js, encoding="utf-8")


def write_config_js():
    config_js = f"""window.SITE_CONFIG = {{
  brand: \"КРЕПОСТЬ\",
  domain: \"{DOMAIN}\",
  phone: \"{PHONE_RAW}\",
  email: \"{EMAIL}\",
  geo: [\"Махачкала\", \"Республика Дагестан\"]
}};

window.ANALYTICS_CONFIG = {{
  ga4MeasurementId: \"\",
  yandexMetrikaId: \"\"
}};
"""
    (ROOT / "assets/js/config.js").write_text(config_js, encoding="utf-8")


def write_analytics_js():
    analytics = r"""(function () {
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
"""
    (ROOT / "assets/js/analytics.js").write_text(analytics, encoding="utf-8")


def write_graphics_and_manifest():
    favicon_svg = """<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 64 64\"><rect width=\"64\" height=\"64\" rx=\"10\" fill=\"#111111\"/><text x=\"32\" y=\"42\" text-anchor=\"middle\" font-family=\"Manrope, Arial, sans-serif\" font-size=\"34\" font-weight=\"700\" fill=\"#ffffff\">K</text></svg>\n"""
    og_svg = """<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1200\" height=\"630\" viewBox=\"0 0 1200 630\"><defs><linearGradient id=\"g\" x1=\"0\" x2=\"1\"><stop offset=\"0\" stop-color=\"#111111\"/><stop offset=\"1\" stop-color=\"#333333\"/></linearGradient></defs><rect width=\"1200\" height=\"630\" fill=\"url(#g)\"/><text x=\"80\" y=\"230\" fill=\"#ffffff\" font-family=\"Manrope, Arial, sans-serif\" font-size=\"64\" font-weight=\"700\">КРЕПОСТЬ</text><text x=\"80\" y=\"320\" fill=\"#ffffff\" font-family=\"Manrope, Arial, sans-serif\" font-size=\"40\">Строительство домов в Махачкале и Дагестане</text><text x=\"80\" y=\"390\" fill=\"#d0d0d0\" font-family=\"Manrope, Arial, sans-serif\" font-size=\"30\">Проектирование • Инженерия • Отделка</text></svg>\n"""
    webmanifest = {
        "name": "КРЕПОСТЬ",
        "short_name": "КРЕПОСТЬ",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#f4f4f4",
        "theme_color": "#111111",
        "icons": [
            {
                "src": "/assets/img/favicon.svg",
                "sizes": "64x64",
                "type": "image/svg+xml",
            }
        ],
    }

    (ROOT / "assets/img/favicon.svg").write_text(favicon_svg, encoding="utf-8")
    (ROOT / "assets/img/og-default.svg").write_text(og_svg, encoding="utf-8")
    (ROOT / "site.webmanifest").write_text(json.dumps(webmanifest, ensure_ascii=False, indent=2), encoding="utf-8")


def clean_index_and_switch_assets(index_text: str):
    index_text = re.sub(
        r"\n  <style>\n.*?\n  </style>\n",
        "\n  <link rel=\"stylesheet\" href=\"/assets/css/main.css\" />\n",
        index_text,
        flags=re.S,
    )

    script_include = """
  <!-- СКРИПТЫ -->
  <script src="/assets/js/config.js"></script>
  <script src="/assets/js/main.js"></script>
  <script src="/assets/js/analytics.js"></script>
"""
    index_text = re.sub(
        r"\n  <!-- СКРИПТЫ -->\n  <script>\n.*?\n  </script>\n",
        "\n" + script_include,
        index_text,
        flags=re.S,
    )

    if "<link rel=\"canonical\"" not in index_text:
        index_text = index_text.replace(
            '<meta name="description" content="Строительство домов в Махачкале и Дагестане: проектирование, инженерные сети, отделочные работы. Прозрачная смета, этапы, кейсы, отзывы, FAQ." />',
            '<meta name="description" content="Строительство домов в Махачкале и Дагестане: проектирование, инженерные сети, отделочные работы. Прозрачная смета, этапы, кейсы, отзывы, FAQ." />\n  <link rel="canonical" href="https://krepostdom.ru/" />',
        )

    if 'property="og:image"' not in index_text:
        index_text = index_text.replace(
            '<meta property="og:locale" content="ru_RU" />',
            '<meta property="og:locale" content="ru_RU" />\n  <meta property="og:image" content="https://krepostdom.ru/assets/img/og-default.svg" />\n  <meta name="twitter:card" content="summary_large_image" />',
        )

    if 'rel="icon" href="/assets/img/favicon.svg"' not in index_text:
        index_text = index_text.replace(
            '<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700&display=swap" rel="stylesheet" />',
            '<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700&display=swap" rel="stylesheet" />\n  <link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml" />\n  <link rel="manifest" href="/site.webmanifest" />',
        )

    index_text = index_text.replace("<body>", '<body data-page-type="home" data-service="all">')
    index_text = index_text.replace("Адрес офиса (Махачкала): <strong>TBD</strong>", "Адрес офиса: уточняем при обращении")
    index_text = index_text.replace("Режим работы: <strong>TBD</strong>", "Режим работы: ежедневно, по согласованию времени")
    index_text = index_text.replace(
        "Юридический блок перед продакшном: политика ПД, реквизиты, договор и гарантийные условия помечены как <strong>TBD</strong> в отчете.",
        "Политика обработки персональных данных, договор и гарантийные условия предоставляются перед подписанием документов.",
    )

    return index_text


def load_meta_sources():
    seo_rows = read_csv_semicolon(SEO_TABLE)
    seo_map = {row["URL"]: row for row in seo_rows}

    aeo_rows = read_csv_semicolon(AEO_TABLE)
    aeo_map = {}
    for row in aeo_rows:
        target = row["Target URL"].strip()
        aeo_map.setdefault(target, []).append((row["Question"].strip(), row["Short Answer (1-3 sentences)"].strip()))
    return seo_map, aeo_map


def breadcrumb_name(url: str):
    mapping = {
        "/": "Главная",
        "/services/": "Услуги",
        "/tseny/": "Цены",
        "/raboty/": "Кейсы",
        "/otzyvy/": "Отзывы",
        "/faq/": "FAQ",
        "/guides/": "Гайды",
        "/guides/stroitelstvo/": "Строительство",
        "/guides/proektirovanie/": "Проектирование",
        "/guides/inzheneriya/": "Инженерия",
        "/guides/otdelka/": "Отделка",
        "/o-kompanii/": "О компании",
        "/kontakty/": "Контакты",
        "/tseny/stroitelstvo-domov-v-dagestane/": "Строительство домов в Дагестане",
        "/tseny/otdelochnye-raboty-mahachkala/": "Отделочные работы в Махачкале",
        "/guides/proektirovanie/chto-vhodit-v-proekt/": "Что входит в проект дома",
        "/guides/inzheneriya/vodosnabzhenie-i-kanalizaciya/": "Водоснабжение и канализация",
        "/guides/otdelka/chernovaya-vs-chistovaya/": "Черновая vs чистовая отделка",
        "/guides/stroitelstvo/oshibki-pri-vybore-podryadchika/": "Ошибки при выборе подрядчика",
        "/guides/stroitelstvo/kak-vybrat-tehnologiyu-doma/": "Как выбрать технологию дома",
        "/guides/proektirovanie/kak-sostavit-tz/": "Как составить ТЗ",
        "/guides/proektirovanie/tipovoy-vs-individualnyy-proekt/": "Типовой vs индивидуальный проект",
        "/guides/inzheneriya/elektrika-i-slabotochka/": "Электрика и слаботочка",
        "/guides/inzheneriya/stoimost-proekta-setey/": "Стоимость проекта инженерных сетей",
        "/guides/otdelka/etapy-i-sroki/": "Этапы и сроки отделки",
    }
    if url in mapping:
        return mapping[url]
    slug = url.strip("/").split("/")[-1]
    return slug.replace("-", " ").capitalize()


def build_breadcrumb_list(url: str):
    parts = [p for p in url.strip("/").split("/") if p]
    items = [{"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{DOMAIN}/"}]
    if not parts:
        return items

    current = ""
    pos = 2
    for part in parts:
        current += f"/{part}"
        item_url = f"{DOMAIN}{current}/"
        items.append({"@type": "ListItem", "position": pos, "name": breadcrumb_name(f"{current}/"), "item": item_url})
        pos += 1
    return items


def base_local_business():
    return {
        "@type": "LocalBusiness",
        "name": "КРЕПОСТЬ",
        "url": f"{DOMAIN}/",
        "telephone": PHONE_RAW,
        "email": EMAIL,
        "areaServed": ["Махачкала", "Республика Дагестан"],
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Махачкала",
            "addressRegion": "Республика Дагестан",
            "addressCountry": "RU",
        },
    }


def page_kind_from_url(url: str, seo_map):
    if url in PAGE_META_DEFAULTS:
        return PAGE_META_DEFAULTS[url]["page_type"]
    if url in seo_map:
        return seo_map[url]["Page Type"]
    if url.startswith("/guides/"):
        return "guide_pillar"
    return "webpage"


def normalize_page_type(url: str, raw_page_type: str):
    pt = (raw_page_type or "").strip().lower()
    if pt and pt not in {"webpage", "web_page", "page", "landing_page"}:
        return raw_page_type
    if url == "/services/":
        return "service_category"
    if url.startswith("/services/"):
        return "service_landing"
    if url.startswith("/tseny/"):
        return "prices"
    if url == "/faq/":
        return "faq_hub"
    if url == "/guides/":
        return "guides_hub"
    if url.startswith("/guides/"):
        return "guide_pillar"
    if url == "/raboty/":
        return "cases_hub"
    if url == "/otzyvy/":
        return "reviews_hub"
    if url in {"/o-kompanii/", "/kontakty/"}:
        return "trust_page"
    return "webpage"


def cluster_from_url(url: str):
    if "stroitelstvo" in url:
        return "Строительство"
    if "proektirovanie" in url:
        return "Проектирование"
    if "inzhener" in url:
        return "Инженерия"
    if "otdel" in url:
        return "Отделка"
    if url.startswith("/guides/"):
        return "Гайды"
    if url.startswith("/tseny/"):
        return "Цены"
    return "Все направления"


def build_meta(url: str, seo_map):
    if url in PAGE_META_DEFAULTS:
        return PAGE_META_DEFAULTS[url].copy()

    if url in seo_map:
        row = seo_map[url]
        page_type = normalize_page_type(url, row["Page Type"])
        primary_cta = "Получить смету"
        if "service" in page_type:
            primary_cta = "Получить консультацию"
        if "faq" in page_type:
            primary_cta = "Перейти к услугам"
        if "guide" in page_type:
            primary_cta = "Получить консультацию"
        return {
            "title": row["Title"],
            "description": row["Meta Description"],
            "h1": row["H1"],
            "page_type": page_type,
            "cluster": cluster_from_url(url),
            "intent": "Commercial" if page_type not in {"guide_pillar", "faq_hub"} else "Informational",
            "primary_cta": primary_cta,
        }

    slug = url.strip("/").split("/")[-1]
    text = slug.replace("-", " ")
    return {
        "title": f"{text.capitalize()} | КРЕПОСТЬ",
        "description": f"{text.capitalize()} в Махачкале и Дагестане. Этапы, цены, кейсы, FAQ и консультация.",
        "h1": text.capitalize(),
        "page_type": normalize_page_type(url, page_kind_from_url(url, seo_map)),
        "cluster": cluster_from_url(url),
        "intent": "Informational" if "guide" in url else "Commercial",
        "primary_cta": "Получить консультацию",
    }


def faq_html(faq_items):
    if not faq_items:
        faq_items = [
            ("Сколько стоит услуга?", "Стоимость зависит от объема и состава работ. Предварительный диапазон даем после короткого брифа."),
            ("Какие сроки реализации?", "Срок зависит от площади, технологии и сезонности. Фиксируем этапы в договоре."),
            ("Можно ли начать с консультации?", "Да, начнем с брифа и подберем формат работ под вашу задачу."),
        ]
    rows = []
    for i, (q, a) in enumerate(faq_items, 1):
        rows.append(
            f'''        <div class="faq-item hover-target">\n          <div class="faq-head h-md" data-faq-id="faq_{i}" style="font-size: 22px;">{q}</div>\n          <div class="faq-body"><p class="t-body" style="padding-top: 20px;">{a}</p></div>\n        </div>'''
        )
    return "\n".join(rows)


def related_links_block(url):
    common = [
        ("/services/", "Все услуги"),
        ("/tseny/", "Цены по направлениям"),
        ("/raboty/", "Реальные кейсы"),
        ("/otzyvy/", "Отзывы клиентов"),
        ("/faq/", "Ответы на вопросы"),
        ("/kontakty/", "Контакты и зоны обслуживания"),
    ]
    links = [x for x in common if x[0] != url][:4]
    links_html = "\n".join([f'          <a href="{href}" class="hover-target">{label}</a>' for href, label in links])
    return f'''\n    <section class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">Полезные<br>Ссылки.</h2>\n        <p class="t-body reveal">Быстрый переход к ключевым коммерческим и информационным разделам сайта.</p>\n      </div>\n      <div class="page-intro">\n        <div class="page-links">\n{links_html}\n        </div>\n      </div>\n    </section>\n'''


def cta_strip(text, cta_text, cta_href, secondary_text="Позвонить", secondary_href=f"tel:{PHONE_RAW}"):
    return f'''\n    <section class="border-b">\n      <div class="cta-strip">\n        <p class="t-body" style="font-size: 15px;">{text}</p>\n        <div class="cta-actions">\n          <a href="{secondary_href}" class="btn btn-outline hover-target" data-event="call_click" data-cta-id="cta_secondary">{secondary_text}</a>\n          <a href="{cta_href}" class="btn hover-target" data-event="cta_click_primary" data-cta-id="cta_primary">{cta_text}</a>\n        </div>\n      </div>\n    </section>\n'''


def service_cards_block():
    items = [
        ("/services/stroitelstvo-domov-pod-klyuch-mahachkala/", "Строительство домов под ключ", "Проект + стройка + инженерия + отделка в одном контуре."),
        ("/services/proektirovanie-domov-mahachkala/", "Проектирование домов", "АР/КР и состав проекта с понятными сроками и этапами."),
        ("/services/proekt-inzhenernyh-setey-mahachkala/", "Проект инженерных сетей", "Электрика, водоснабжение, канализация, отопление и вентиляция."),
        ("/services/otdelochnye-raboty-mahachkala/", "Отделочные работы", "Черновая и чистовая отделка с прозрачной сметой."),
    ]
    cards = []
    for href, title, desc in items:
        cards.append(
            f'''        <article class="page-card reveal">\n          <h3 class="h-md" style="font-size: 24px;">{title}</h3>\n          <p class="t-body" style="font-size: 15px;">{desc}</p>\n          <a href="{href}" class="proof-link hover-target" data-event="cta_click_primary" data-cta-id="service_card">Перейти к услуге</a>\n        </article>'''
        )
    return "\n".join(cards)


def build_content(url, meta, faq_items):
    h1 = meta["h1"]
    lead = meta["description"]
    cta = meta["primary_cta"]
    page_type = meta["page_type"]
    cluster = meta["cluster"]

    hero = f'''\n    <section class="hero border-b">\n      <div class="hero-text-box border-r">\n        <div>\n          <div class="t-mono reveal">Махачкала + Республика Дагестан</div>\n          <h1 class="h-huge reveal" style="margin: 20px 0;">{h1}</h1>\n          <p class="t-body reveal" style="max-width: 560px;">{lead}</p>\n        </div>\n        <div class="reveal">\n          <div class="hero-tags">\n            <span>Кластер: {cluster}</span>\n            <span>Интент: {meta["intent"]}</span>\n            <span>Локальное SEO: Махачкала + РД</span>\n          </div>\n          <div class="hero-cta-row">\n            <a href="#contact" class="btn hover-target" data-event="cta_click_primary" data-cta-id="hero_primary">{cta}</a>\n            <a href="tel:{PHONE_RAW}" class="btn btn-outline hover-target" data-event="call_click" data-cta-id="hero_call">Позвонить {PHONE_DISPLAY}</a>\n          </div>\n        </div>\n      </div>\n      <div class="hero-img-box">\n        <img src="https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1600&q=90" alt="{h1}" class="parallax-img hero-img" loading="lazy">\n      </div>\n    </section>\n'''

    if page_type == "service_category":
        return (
            hero
            + '''\n    <section class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">Все<br>Направления.</h2>\n        <p class="t-body reveal">Выберите нужный формат работ: от проектирования до реализации под ключ.</p>\n      </div>\n      <div class="page-grid">\n'''
            + service_cards_block()
            + "\n      </div>\n    </section>\n"
            + cta_strip("Подберем оптимальный формат работ и заранее согласуем бюджет/этапы.", "Получить смету", "#contact")
            + f'''\n    <section id="faq" class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">FAQ.</h2>\n        <p class="t-body reveal">Короткие ответы перед выбором направления.</p>\n      </div>\n      <div>\n{faq_html(faq_items)}\n      </div>\n    </section>\n'''
            + related_links_block(url)
        )

    if page_type in {"service_landing", "service_template"}:
        rows = [
            ("Базовый", "Ключевой объем работ", "Подходит для старта и оценки бюджета"),
            ("Стандарт", "Оптимальный набор этапов", "Баланс сроков и стоимости"),
            ("Расширенный", "Максимальный контроль результата", "Под ключ по согласованному маршруту"),
        ]
        price_rows = "\n".join([f"        <tr><td class=\"h-md\" style=\"font-size:24px\">{a}</td><td class=\"t-body\">{b}</td><td class=\"t-body\" style=\"font-size:14px\">{c}</td></tr>" for a, b, c in rows])
        return (
            hero
            + '''\n    <section id="prices" class="border-b" data-track-price="service_price_block">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">Стоимость<br>И Варианты.</h2>\n        <p class="t-body reveal">Даем сценарии стоимости и фиксируем условия до старта работ.</p>\n      </div>\n      <table class="price-table reveal">\n        <thead><tr class="t-mono"><th>Сценарий</th><th>Что входит</th><th>Когда подходит</th></tr></thead>\n        <tbody>\n'''
            + price_rows
            + '''\n        </tbody>\n      </table>\n    </section>\n'''
            + '''\n    <section id="process" class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">Этапы<br>Работы.</h2>\n        <p class="t-body reveal">Маршрут от брифа до сдачи с контрольными точками по срокам и бюджету.</p>\n      </div>\n      <div class="process-grid">\n        <div class="process-card reveal"><span class="process-num">01 / Бриф</span><p class="t-body" style="font-size:15px;">Собираем вводные и ограничения проекта.</p></div>\n        <div class="process-card reveal"><span class="process-num">02 / Смета</span><p class="t-body" style="font-size:15px;">Формируем предварительный расчет.</p></div>\n        <div class="process-card reveal"><span class="process-num">03 / Договор</span><p class="t-body" style="font-size:15px;">Фиксируем этапы и условия.</p></div>\n        <div class="process-card reveal"><span class="process-num">04 / Подготовка</span><p class="t-body" style="font-size:15px;">Согласование решений перед стартом.</p></div>\n        <div class="process-card reveal"><span class="process-num">05 / Реализация</span><p class="t-body" style="font-size:15px;">Выполнение работ по этапам.</p></div>\n        <div class="process-card reveal"><span class="process-num">06 / Сдача</span><p class="t-body" style="font-size:15px;">Финальная проверка и передача.</p></div>\n      </div>\n    </section>\n'''
            + '''\n    <section class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">Кейсы И<br>Отзывы.</h2>\n        <p class="t-body reveal">Реальные примеры помогают оценить подход и уровень контроля на объекте.</p>\n      </div>\n      <div class="page-grid">\n        <article class="page-card reveal"><h3 class="h-md" style="font-size:24px;">Кейсы</h3><p class="t-body" style="font-size:15px;">Показываем задачи, решения и результаты на реальных объектах.</p><a href="/raboty/" class="proof-link hover-target" data-event="case_view" data-case-id="hub">Смотреть кейсы</a></article>\n        <article class="page-card reveal"><h3 class="h-md" style="font-size:24px;">Отзывы</h3><p class="t-body" style="font-size:15px;">Публикуем отзывы с внешних площадок и подтверждением источников.</p><a href="/otzyvy/" class="proof-link hover-target">Читать отзывы</a></article>\n        <article class="page-card reveal"><h3 class="h-md" style="font-size:24px;">FAQ</h3><p class="t-body" style="font-size:15px;">Короткие ответы по стоимости, срокам и составу работ.</p><a href="/faq/" class="proof-link hover-target">Перейти в FAQ</a></article>\n      </div>\n    </section>\n'''
            + f'''\n    <section id="faq" class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">FAQ.</h2>\n        <p class="t-body reveal">Ответы на частые вопросы по услуге.</p>\n      </div>\n      <div>\n{faq_html(faq_items)}\n      </div>\n    </section>\n'''
            + cta_strip("Готовы обсудить задачу и показать сценарии по стоимости и этапам.", cta, "#contact")
            + related_links_block(url)
        )

    if page_type in {"prices", "prices_hub", "prices_template"}:
        rows = [
            ("Площадь объекта", "Чем выше площадь, тем больше объем материалов и времени"),
            ("Состав работ", "Проект, инженерия, отделка и дополнительные этапы"),
            ("Технология", "Выбор конструктивной схемы влияет на бюджет и сроки"),
            ("Условия участка", "Геометрия и логистика влияют на организацию работ"),
        ]
        table_rows = "\n".join([f"        <tr><td class=\"h-md\" style=\"font-size:24px\">{a}</td><td class=\"t-body\">{b}</td></tr>" for a, b in rows])
        links = '''        <article class="page-card reveal"><h3 class="h-md" style="font-size:24px;">Цены на строительство</h3><p class="t-body" style="font-size:15px;">Детальный сценарий стоимости по этапам строительства.</p><a href="/tseny/stroitelstvo-domov-v-dagestane/" class="proof-link hover-target">Открыть страницу</a></article>\n        <article class="page-card reveal"><h3 class="h-md" style="font-size:24px;">Цены на отделку</h3><p class="t-body" style="font-size:15px;">Разбивка по видам отделочных работ и факторам стоимости.</p><a href="/tseny/otdelochnye-raboty-mahachkala/" class="proof-link hover-target">Открыть страницу</a></article>\n        <article class="page-card reveal"><h3 class="h-md" style="font-size:24px;">Услуги</h3><p class="t-body" style="font-size:15px;">Выберите направление работ и получите консультацию по бюджету.</p><a href="/services/" class="proof-link hover-target">Перейти к услугам</a></article>'''

        return (
            hero
            + '''\n    <section class="border-b" data-track-price="prices_main_block">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">Что Влияет<br>На Стоимость.</h2>\n        <p class="t-body reveal">Коротко фиксируем факторы расчета, чтобы диапазон цены был понятен еще до детальной сметы.</p>\n      </div>\n      <table class="article-table reveal">\n        <thead><tr class="t-mono"><th>Фактор</th><th>Влияние</th></tr></thead>\n        <tbody>\n'''
            + table_rows
            + '''\n        </tbody>\n      </table>\n    </section>\n'''
            + '''\n    <section class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">Разделы<br>Цен.</h2>\n        <p class="t-body reveal">Переходы на детальные страницы по направлениям.</p>\n      </div>\n      <div class="page-grid">\n'''
            + links
            + "\n      </div>\n    </section>\n"
            + f'''\n    <section id="faq" class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">FAQ.</h2>\n        <p class="t-body reveal">Ответы по стоимости и расчету.</p>\n      </div>\n      <div>\n{faq_html(faq_items)}\n      </div>\n    </section>\n'''
            + cta_strip("Отправьте вводные по объекту и получите предварительный расчет в 2-3 сценариях.", "Получить смету", "#contact")
            + related_links_block(url)
        )

    if page_type == "cases_hub":
        cards = []
        for idx, (title, desc, cluster) in enumerate([
            ("Строительство дома под ключ", "Полный цикл от брифа до сдачи с фиксированными этапами и бюджетом.", "строительство"),
            ("Проект дома с инженерией", "АР/КР и инженерные решения без коллизий на реализации.", "проектирование"),
            ("Отделка под смету", "Черновая и чистовая отделка с контролем сроков.", "отделка"),
            ("Реконструкция и доработка", "Оптимизация решений на существующих объектах.", "инженерия"),
            ("Сложный участок", "Сценарий реализации с учетом геометрии и логистики.", "строительство"),
            ("Инженерные узлы", "Проектирование критичных систем для частного дома.", "инженерия"),
        ], 1):
            cards.append(f'''        <article class="page-card reveal">\n          <h3 class="h-md" style="font-size:24px;">{title}</h3>\n          <p class="t-body" style="font-size:15px;">{desc}</p>\n          <span class="t-mono">Кластер: {cluster}</span>\n          <a href="#contact" class="proof-link hover-target" data-event="case_view" data-case-id="case_{idx}">Запросить похожий кейс</a>\n        </article>''')
        return (
            hero
            + '''\n    <section class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">Подборка<br>Кейсов.</h2>\n        <p class="t-body reveal">Показываем задачу, решение, этапность и итог по каждому типу работ.</p>\n      </div>\n      <div class="page-grid">\n'''
            + "\n".join(cards)
            + "\n      </div>\n    </section>\n"
            + f'''\n    <section id="faq" class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">FAQ.</h2>\n        <p class="t-body reveal">Ответы по выбору исполнителя и разбору реализованных кейсов.</p>\n      </div>\n      <div>\n{faq_html(faq_items)}\n      </div>\n    </section>\n'''
            + cta_strip("Расскажите параметры объекта, и мы подберем релевантные кейсы под вашу задачу.", "Подобрать кейс", "#contact")
            + related_links_block(url)
        )

    if page_type == "reviews_hub":
        return (
            hero
            + '''\n    <section class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">Контур<br>Репутации.</h2>\n        <p class="t-body reveal">Синхронизируем отзывы на сайте и внешних площадках с прозрачным SLA ответа.</p>\n      </div>\n      <div class="reviews-grid">\n        <article class="review-card reveal"><h3 class="h-md" style="font-size:24px;">Yandex</h3><p class="t-body" style="font-size:15px;">Запрос отзыва после завершения этапа. SLA ответа: до 48 часов.</p><p class="t-mono review-meta">KPI: рост числа отзывов</p></article>\n        <article class="review-card reveal"><h3 class="h-md" style="font-size:24px;">Google</h3><p class="t-body" style="font-size:15px;">Ответ на новый отзыв. SLA: до 24 часов.</p><p class="t-mono review-meta">KPI: response rate >= 95%</p></article>\n        <article class="review-card reveal"><h3 class="h-md" style="font-size:24px;">2GIS + Сайт</h3><p class="t-body" style="font-size:15px;">Сбор отзывов и публикация в /otzyvy/ с источниками.</p><p class="t-mono review-meta">KPI: Trust CTR / стабильность рейтинга</p></article>\n      </div>\n    </section>\n'''
            + f'''\n    <section id="faq" class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">FAQ.</h2>\n        <p class="t-body reveal">Ответы по репутации и проверке отзывов.</p>\n      </div>\n      <div>\n{faq_html(faq_items)}\n      </div>\n    </section>\n'''
            + cta_strip("Хотите увидеть отзывы по релевантным объектам? Подберем и покажем источники.", "Получить консультацию", "#contact")
            + related_links_block(url)
        )

    if page_type in {"faq_hub", "faq_template"}:
        return (
            hero
            + f'''\n    <section id="faq" class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">Вопросы<br>И Ответы.</h2>\n        <p class="t-body reveal">AEO-блок с короткими ответами по стоимости, срокам и составу работ.</p>\n      </div>\n      <div>\n{faq_html(faq_items)}\n      </div>\n    </section>\n'''
            + cta_strip("Если вопрос специфичный, разберем его на коротком звонке и подскажем следующий шаг.", "Перейти к услугам", "/services/")
            + related_links_block(url)
        )

    if page_type in {"guides_hub", "guide_template"}:
        guides = [
            ("/guides/stroitelstvo/oshibki-pri-vybore-podryadchika/", "Ошибки при выборе подрядчика", "Строительство"),
            ("/guides/stroitelstvo/kak-vybrat-tehnologiyu-doma/", "Как выбрать технологию дома", "Строительство"),
            ("/guides/proektirovanie/chto-vhodit-v-proekt/", "Что входит в проект дома", "Проектирование"),
            ("/guides/proektirovanie/kak-sostavit-tz/", "Как составить ТЗ", "Проектирование"),
            ("/guides/proektirovanie/tipovoy-vs-individualnyy-proekt/", "Типовой vs индивидуальный проект", "Проектирование"),
            ("/guides/inzheneriya/vodosnabzhenie-i-kanalizaciya/", "Водоснабжение и канализация", "Инженерия"),
            ("/guides/inzheneriya/elektrika-i-slabotochka/", "Электрика и слаботочка", "Инженерия"),
            ("/guides/inzheneriya/stoimost-proekta-setey/", "Стоимость проекта сетей", "Инженерия"),
            ("/guides/otdelka/chernovaya-vs-chistovaya/", "Черновая vs чистовая отделка", "Отделка"),
            ("/guides/otdelka/etapy-i-sroki/", "Этапы и сроки отделки", "Отделка"),
        ]
        rows = []
        for href, title, cluster_name in guides:
            rows.append(f'''        <article class="guide-item reveal">\n          <div class="t-mono">{cluster_name}</div>\n          <h3 class="h-md" style="font-size:24px; margin-top: 8px;">{title}</h3>\n          <a href="{href}" class="proof-link hover-target" style="margin-top: 10px;">Открыть гайд</a>\n        </article>''')
        return (
            hero
            + '''\n    <section class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">База<br>Материалов.</h2>\n        <p class="t-body reveal">Гайды по ключевым кластерам спроса: строительство, проектирование, инженерия и отделка.</p>\n      </div>\n      <div class="guide-list">\n'''
            + "\n".join(rows)
            + "\n      </div>\n    </section>\n"
            + cta_strip("Нужен персональный разбор? Свяжитесь с нами и подберем материал под ваш сценарий.", "Получить консультацию", "#contact")
            + related_links_block(url)
        )

    if page_type == "guide_pillar":
        qa = faq_items if faq_items else GUIDE_BASE_FAQ
        checklist_rows = [
            ("Договор", "Этапы, сроки, стоимость, ответственность сторон"),
            ("Смета", "Состав работ и прозрачная структура бюджета"),
            ("Доказательства", "Кейсы, отзывы, внешние источники"),
            ("Инженерия", "Наличие профильных решений по системам"),
        ]
        table_rows = "\n".join([f"        <tr><td class=\"h-md\" style=\"font-size:22px\">{a}</td><td class=\"t-body\">{b}</td></tr>" for a, b in checklist_rows])
        return (
            hero
            + '''\n    <section class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">Короткий<br>Ответ.</h2>\n        <p class="t-body reveal">Сначала даем суть, затем чек-лист и практические шаги.</p>\n      </div>\n      <div class="page-intro">\n        <p class="t-body" style="font-size: 16px; color: var(--text);">'''
            + (qa[0][1] if qa else "Решение принимается на базе договора, сметы, этапов и подтвержденных кейсов.")
            + "</p>\n      </div>\n    </section>\n"
            + '''\n    <section class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">Чек-Лист<br>Проверки.</h2>\n        <p class="t-body reveal">Ключевые критерии для принятия решения без лишних рисков.</p>\n      </div>\n      <table class="article-table reveal">\n        <thead><tr class="t-mono"><th>Критерий</th><th>Что проверить</th></tr></thead>\n        <tbody>\n'''
            + table_rows
            + '''\n        </tbody>\n      </table>\n    </section>\n'''
            + f'''\n    <section id="faq" class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">FAQ.</h2>\n        <p class="t-body reveal">Ответы по теме материала.</p>\n      </div>\n      <div>\n{faq_html(qa)}\n      </div>\n    </section>\n'''
            + cta_strip("Если хотите применить чек-лист к вашему объекту, разберем задачу на консультации.", meta["primary_cta"], "#contact")
            + related_links_block(url)
        )

    if url == "/o-kompanii/":
        return (
            hero
            + '''\n    <section class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">Кто Мы<br>И Как Работаем.</h2>\n        <p class="t-body reveal">Команда полного цикла: проектирование, инженерия, строительство и отделка в едином маршруте реализации.</p>\n      </div>\n      <div class="page-grid">\n        <article class="page-card reveal"><h3 class="h-md" style="font-size:24px;">Единая ответственность</h3><p class="t-body" style="font-size:15px;">Один подрядчик на весь объем работ, без разрывов между этапами.</p></article>\n        <article class="page-card reveal"><h3 class="h-md" style="font-size:24px;">Прозрачная смета</h3><p class="t-body" style="font-size:15px;">Фиксируем состав работ и правила изменения бюджета.</p></article>\n        <article class="page-card reveal"><h3 class="h-md" style="font-size:24px;">Контроль сроков</h3><p class="t-body" style="font-size:15px;">Этапность и контрольные точки фиксируются в договоре.</p></article>\n      </div>\n    </section>\n'''
            + cta_strip("Расскажите задачу, и мы предложим оптимальный сценарий реализации под ваш объект.", "Получить смету", "#contact")
            + related_links_block(url)
        )

    if url == "/kontakty/":
        return (
            hero
            + '''\n    <section class="border-b">\n      <div class="sec-header border-b">\n        <h2 class="h-lg reveal">Контакты<br>И Гео.</h2>\n        <p class="t-body reveal">Работаем по Махачкале и Республике Дагестан. Уточняем адрес встречи и график под ваш формат коммуникации.</p>\n      </div>\n      <div class="geo-grid">\n        <article class="geo-card reveal">\n          <h3 class="h-md" style="font-size: 24px;">Как связаться</h3>\n          <ul class="geo-list" style="margin-top: 16px;">\n            <li>Телефон: <a class="link-inline hover-target" href="tel:+79035262526" data-event="call_click">+7 (903) 526-25-26</a></li>\n            <li>Email: <a class="link-inline hover-target" href="mailto:info@krepostdom.ru">info@krepostdom.ru</a></li>\n            <li>Сайт: <a class="link-inline hover-target" href="https://krepostdom.ru/">krepostdom.ru</a></li>\n            <li>Зона работ: Махачкала + Республика Дагестан</li>\n          </ul>\n        </article>\n        <article class="geo-card reveal">\n          <h3 class="h-md" style="font-size: 24px;">Локальные профили</h3>\n          <ul class="geo-list" style="margin-top: 16px;">\n            <li>Yandex Business: категории, услуги, NAP</li>\n            <li>Google Business Profile: услуги, FAQ, посты</li>\n            <li>2GIS: синхронизация NAP и услуг</li>\n            <li>Сайт: единый NAP в шапке, футере и контактах</li>\n          </ul>\n        </article>\n      </div>\n    </section>\n'''
            + cta_strip("Выберите удобный канал связи, и мы быстро вернемся с планом следующего шага.", "Оставить заявку", "#contact")
            + related_links_block(url)
        )

    # fallback
    return hero + cta_strip("Готовы обсудить задачу?", cta, "#contact") + related_links_block(url)


def page_contact_section(page_type: str, service_slug: str):
    return f'''\n    <section id="contact" class="contact-sec">\n      <div class="c-info">\n        <h2 class="h-huge reveal">Обсудим<br>Ваш Проект.</h2>\n        <div class="c-meta reveal">\n          <div class="t-mono">Контакты</div>\n          <a href="tel:{PHONE_RAW}" class="c-phone hover-target" data-event="call_click">{PHONE_DISPLAY}</a>\n          <a href="mailto:{EMAIL}" class="c-mail hover-target">{EMAIL}</a>\n          <div class="c-chips">\n            <span>звонок</span><span>WhatsApp</span><span>Telegram</span><span>бриф в день обращения</span>\n          </div>\n          <p class="c-note">После заявки проводим короткий бриф и отправляем предварительный расчет со сроками по этапам.</p>\n          <div class="c-actions">\n            <a href="tel:{PHONE_RAW}" class="btn btn-outline hover-target" data-event="call_click" data-cta-id="contact_call">Позвонить сейчас</a>\n            <a href="#contact-form" class="btn hover-target" data-event="cta_click_primary" data-cta-id="contact_form">Заполнить форму</a>\n          </div>\n        </div>\n      </div>\n      <div class="c-form-box">\n        <div class="t-mono reveal" style="margin-bottom: 40px;">Получите предварительную смету и план этапов</div>\n        <form id="contact-form" class="reveal" data-form-id="lead_main" data-page-type="{page_type}" data-service="{service_slug}" onsubmit="event.preventDefault(); alert('Спасибо! Мы свяжемся с вами.');">\n          <input type="text" name="name" class="form-input" placeholder="Ваше имя" required>\n          <input type="tel" name="phone" class="form-input" placeholder="Телефон" required>\n          <select name="service" class="form-input" required style="color: var(--text-muted);">\n            <option value="" disabled selected>Интересующее направление</option>\n            <option style="color: var(--text);">Строительство под ключ</option>\n            <option style="color: var(--text);">Проектирование домов</option>\n            <option style="color: var(--text);">Инженерные сети</option>\n            <option style="color: var(--text);">Отделочные работы</option>\n          </select>\n          <input type="text" name="details" class="form-input" placeholder="Площадь/участок/сроки (опционально)">\n          <button type="submit" class="btn hover-target" data-event="cta_click_primary" data-cta-id="form_submit_btn" style="width: 100%; margin-top: 20px;">Отправить заявку</button>\n          <p class="t-body" style="font-size: 13px; margin-top: 16px;">Политика обработки персональных данных и договорные условия предоставляются перед подписанием документов.</p>\n        </form>\n      </div>\n    </section>\n'''


def header_block():
    return f"""
  <div class="topbar t-mono">
    <span>Махачкала & РД</span>
    <span>Строительство / Проектирование / Инженерия / Отделка</span>
  </div>

  <header>
    <a href="/" class="logo hover-target" aria-label="Крепость - главная">
      <span class="logo-mark" aria-hidden="true">
        <svg viewBox="0 0 64 64" role="img" aria-hidden="true">
          <path d="M8 14 32 5l24 9v15c0 15-9 25-24 30C17 54 8 44 8 29V14Zm8 5v10h9v-7h14v7h9V19L32 13 16 19Zm0 18c2 6 7 11 16 15 9-4 14-9 16-15H16Z" fill="currentColor"></path>
        </svg>
      </span>
      <span class="logo-text">Крепость</span>
    </a>
    <nav class="nav" aria-label="Основная навигация">
      <a href="/services/" class="hover-target">Услуги</a>
      <a href="/tseny/" class="hover-target">Цены</a>
      <a href="/raboty/" class="hover-target">Построенные дома</a>
      <a href="/otzyvy/" class="hover-target">Отзывы</a>
      <a href="/kontakty/" class="hover-target">Контакты</a>
      <div class="nav-mega-wrap">
        <button class="nav-mega-trigger hover-target" type="button" aria-expanded="false" aria-controls="mega-menu">Все разделы</button>
        <div class="mega-menu" id="mega-menu" aria-label="Полная структура сайта">
          <div class="mega-top">
            <div>
              <h4>Выберите формат работ и перейдите на нужную страницу</h4>
              <p>Хабы и посадочные по услугам, ценам, кейсам, отзывам и FAQ для быстрого принятия решения.</p>
            </div>
            <div class="mega-chips">
              <span class="mega-chip">коммерческие страницы</span>
              <span class="mega-chip">локальное SEO</span>
              <span class="mega-chip">прямые CTA</span>
            </div>
          </div>

          <div class="mega-quick-grid">
            <a href="/services/" class="mega-quick-link hover-target">
              <b>Подобрать услугу</b>
              <span>Сразу перейти к направлениям работ</span>
            </a>
            <a href="/tseny/" class="mega-quick-link hover-target">
              <b>Понять бюджет</b>
              <span>Сценарии стоимости и факторы цены</span>
            </a>
            <a href="/raboty/" class="mega-quick-link hover-target">
              <b>Посмотреть кейсы</b>
              <span>Реальные объекты и решения по этапам</span>
            </a>
          </div>

          <div class="mega-grid">
            <div class="mega-col">
              <div class="mega-title">Услуги</div>
              <a href="/services/" class="mega-link hover-target"><b>Все услуги</b><span>Хаб коммерческих страниц</span></a>
              <a href="/services/stroitelstvo-domov-pod-klyuch-mahachkala/" class="mega-link hover-target"><b>Строительство под ключ</b><span>Полный цикл в одном контуре</span></a>
              <a href="/services/proektirovanie-domov-mahachkala/" class="mega-link hover-target"><b>Проектирование домов</b><span>АР/КР и подготовка к стройке</span></a>
              <a href="/services/proekt-inzhenernyh-setey-mahachkala/" class="mega-link hover-target"><b>Инженерные сети</b><span>Электрика, вода, канализация, отопление</span></a>
              <a href="/services/otdelochnye-raboty-mahachkala/" class="mega-link hover-target"><b>Отделочные работы</b><span>Черновая и чистовая отделка</span></a>
            </div>
            <div class="mega-col">
              <div class="mega-title">Цены</div>
              <a href="/tseny/" class="mega-link hover-target"><b>Цены по направлениям</b><span>Главный ценовой хаб</span></a>
              <a href="/tseny/stroitelstvo-domov-v-dagestane/" class="mega-link hover-target"><b>Цена строительства дома</b><span>Сценарии стоимости по Дагестану</span></a>
              <a href="/tseny/otdelochnye-raboty-mahachkala/" class="mega-link hover-target"><b>Цена отделочных работ</b><span>Прайс по Махачкале</span></a>
            </div>
            <div class="mega-col">
              <div class="mega-title">Доверие</div>
              <a href="/raboty/" class="mega-link hover-target"><b>Кейсы и объекты</b><span>Реальные проекты и результаты</span></a>
              <a href="/otzyvy/" class="mega-link hover-target"><b>Отзывы клиентов</b><span>Публичные trust-сигналы</span></a>
              <a href="/o-kompanii/" class="mega-link hover-target"><b>О компании</b><span>Команда и подход к работе</span></a>
              <a href="/kontakty/" class="mega-link hover-target"><b>Контакты</b><span>Махачкала и Республика Дагестан</span></a>
            </div>
            <div class="mega-col">
              <div class="mega-title">FAQ и Гайды</div>
              <a href="/faq/" class="mega-link hover-target"><b>FAQ</b><span>Короткие ответы по цене и срокам</span></a>
              <a href="/guides/" class="mega-link hover-target"><b>Все гайды</b><span>Инфо-контент по кластерам</span></a>
              <a href="/guides/stroitelstvo/oshibki-pri-vybore-podryadchika/" class="mega-link hover-target"><b>Как выбрать подрядчика</b><span>Чек-лист перед стартом</span></a>
              <a href="/guides/proektirovanie/chto-vhodit-v-proekt/" class="mega-link hover-target"><b>Состав проекта дома</b><span>Что входит и зачем нужно</span></a>
              <a href="/guides/inzheneriya/vodosnabzhenie-i-kanalizaciya/" class="mega-link hover-target"><b>Инженерия: вода и канализация</b><span>Базовые решения для дома</span></a>
              <a href="/guides/otdelka/chernovaya-vs-chistovaya/" class="mega-link hover-target"><b>Черновая vs чистовая отделка</b><span>Разница по этапам и бюджету</span></a>
            </div>
          </div>

          <div class="mega-cta">
            <p class="mega-cta-note">
              <b>Нужен быстрый маршрут по сайту?</b>
              Напишите в WhatsApp/Telegram или получите смету по вашей задаче.
            </p>
            <div class="mega-cta-actions">
              <a href="https://wa.me/79035262526?text=Здравствуйте!%20Нужна%20предварительная%20смета%20по%20дому." target="_blank" rel="noopener" class="btn btn-outline hover-target" data-event="cta_click_primary" data-cta-id="mega_whatsapp">WhatsApp</a>
              <a href="#contact" class="btn hover-target" data-event="cta_click_primary" data-cta-id="mega_estimate">Получить смету</a>
            </div>
          </div>
        </div>
      </div>
    </nav>
    <div class="header-actions">
      <a href="tel:{PHONE_RAW}" class="header-phone-chip hover-target" data-event="call_click" data-cta-id="header_phone">
        <span class="header-phone-icon" aria-hidden="true">☎</span>
        <span class="header-phone-meta">
          <b>8 903 526-25-26</b>
          <small>Махачкала и РД</small>
        </span>
      </a>
      <a href="https://t.me/share/url?url=https://krepostdom.ru&text=Здравствуйте!%20Интересует%20строительство%20дома." target="_blank" rel="noopener" class="msg-btn msg-btn-tg hover-target" data-event="cta_click_primary" data-cta-id="header_telegram">Telegram</a>
      <a href="https://wa.me/79035262526?text=Здравствуйте!%20Нужна%20предварительная%20смета%20по%20дому." target="_blank" rel="noopener" class="msg-btn msg-btn-wa hover-target" data-event="cta_click_primary" data-cta-id="header_whatsapp">WhatsApp</a>
      <button class="menu-toggle hover-target" type="button" aria-expanded="false" aria-controls="mobile-nav" aria-label="Открыть меню">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>

  <div class="mobile-nav-overlay"></div>
  <aside class="mobile-nav" id="mobile-nav" aria-label="Боковое меню">
    <div class="mobile-nav-top">
      <div class="t-mono">Разделы сайта</div>
      <button class="mobile-close hover-target" type="button" aria-label="Закрыть меню">Закрыть</button>
    </div>
    <nav class="mobile-nav-links">
      <a href="/" class="hover-target">Главная</a>
      <a href="/services/" class="hover-target">Услуги</a>
      <a href="/tseny/" class="hover-target">Цены</a>
      <a href="/raboty/" class="hover-target">Кейсы</a>
      <a href="/otzyvy/" class="hover-target">Отзывы</a>
      <a href="/faq/" class="hover-target">FAQ</a>
      <a href="/guides/" class="hover-target">Гайды</a>
      <a href="/o-kompanii/" class="hover-target">О компании</a>
      <a href="/kontakty/" class="hover-target">Контакты</a>
    </nav>
    <div class="mobile-nav-secondary t-mono">
      <a href="/services/stroitelstvo-domov-pod-klyuch-mahachkala/" class="hover-target">Строительство</a>
      <a href="/services/proektirovanie-domov-mahachkala/" class="hover-target">Проектирование</a>
      <a href="/services/proekt-inzhenernyh-setey-mahachkala/" class="hover-target">Инженерия</a>
      <a href="/services/otdelochnye-raboty-mahachkala/" class="hover-target">Отделка</a>
    </div>
    <div class="mobile-nav-cta">
      <a href="https://wa.me/79035262526?text=Здравствуйте!%20Нужна%20предварительная%20смета%20по%20дому." target="_blank" rel="noopener" class="btn hover-target" data-event="cta_click_primary" data-cta-id="mobile_whatsapp">Написать в WhatsApp</a>
      <a href="https://t.me/share/url?url=https://krepostdom.ru&text=Здравствуйте!%20Интересует%20строительство%20дома." target="_blank" rel="noopener" class="btn btn-outline hover-target" data-event="cta_click_primary" data-cta-id="mobile_telegram">Написать в Telegram</a>
      <a href="#contact" class="btn btn-outline hover-target" data-event="cta_click_primary" data-cta-id="mobile_estimate">Получить смету</a>
    </div>
  </aside>
"""


def footer_block():
    return f'''\n  <footer class="site-footer">\n    <div class="footer-main">\n      <div class="footer-col footer-col-main">\n        <a href="/" class="footer-logo hover-target">КРЕПОСТЬ</a>\n        <p class="footer-note">Строительство домов, проектирование, инженерные сети и отделочные работы в Махачкале и Республике Дагестан.</p>\n        <div class="footer-offer">\n          <p class="footer-offer-title">Получите предварительный сценарий по стоимости и этапам</p>\n          <p class="footer-offer-note">После короткого брифа покажем, какой формат работ подойдет именно вашему объекту.</p>\n          <div class="footer-scenarios">\n            <a href="/tseny/" class="hover-target">Хочу понять бюджет по направлениям</a>\n            <a href="/raboty/" class="hover-target">Хочу посмотреть релевантные кейсы</a>\n            <a href="/services/proekt-inzhenernyh-setey-mahachkala/" class="hover-target">Нужна консультация по инженерии</a>\n          </div>\n        </div>\n        <div class="footer-contact">\n          <a href="tel:{PHONE_RAW}" class="hover-target" data-event="call_click">{PHONE_DISPLAY}</a>\n          <a href="https://krepostdom.ru/" class="hover-target">krepostdom.ru</a>\n          <a href="#contact" class="hover-target">Оставить заявку на расчет</a>\n        </div>\n        <div class="footer-actions">\n          <a href="#contact" class="btn hover-target" data-event="cta_click_primary" data-cta-id="footer_primary">Получить смету и этапы</a>\n          <a href="tel:{PHONE_RAW}" class="btn btn-outline hover-target" data-event="call_click">Позвонить сейчас</a>\n        </div>\n      </div>\n\n      <div class="footer-col">\n        <div class="t-mono">Услуги</div>\n        <div class="footer-links">\n          <a href="/services/stroitelstvo-domov-pod-klyuch-mahachkala/" class="hover-target">Строительство домов под ключ</a>\n          <a href="/services/proektirovanie-domov-mahachkala/" class="hover-target">Проектирование домов</a>\n          <a href="/services/proekt-inzhenernyh-setey-mahachkala/" class="hover-target">Проект инженерных сетей</a>\n          <a href="/services/otdelochnye-raboty-mahachkala/" class="hover-target">Отделочные работы</a>\n        </div>\n      </div>\n\n      <div class="footer-col">\n        <div class="t-mono">Ключевые Страницы</div>\n        <div class="footer-links">\n          <a href="/tseny/" class="hover-target">Цены по направлениям</a>\n          <a href="/raboty/" class="hover-target">Кейсы и портфолио</a>\n          <a href="/otzyvy/" class="hover-target">Отзывы клиентов</a>\n          <a href="/faq/" class="hover-target">FAQ</a>\n          <a href="/kontakty/" class="hover-target">Контакты и зоны обслуживания</a>\n          <a href="/o-kompanii/" class="hover-target">О компании</a>\n        </div>\n      </div>\n\n      <div class="footer-col">\n        <div class="t-mono">Гайды И Локальное SEO</div>\n        <div class="footer-links">\n          <a href="/guides/" class="hover-target">Хаб гайдов</a>\n          <a href="/guides/stroitelstvo/oshibki-pri-vybore-podryadchika/" class="hover-target">Как выбрать подрядчика</a>\n          <a href="/guides/proektirovanie/chto-vhodit-v-proekt/" class="hover-target">Что входит в проект дома</a>\n          <a href="/guides/inzheneriya/vodosnabzhenie-i-kanalizaciya/" class="hover-target">Инженерные сети: вода и канализация</a>\n          <a href="/guides/otdelka/chernovaya-vs-chistovaya/" class="hover-target">Черновая vs чистовая отделка</a>\n        </div>\n        <p class="footer-mini">Локальные профили по плану: Yandex Business, Google Business Profile и 2GIS. NAP синхронизирован в шапке, футере и контактах.</p>\n      </div>\n    </div>\n\n    <div class="footer-bottom">\n      <div class="t-mono">© 2026 <strong>КРЕПОСТЬ</strong> · Махачкала / Республика Дагестан</div>\n      <div class="t-mono">Структура: /services/ · /tseny/ · /raboty/ · /otzyvy/ · /faq/ · /guides/ · /kontakty/</div>\n    </div>\n  </footer>\n'''


def breadcrumb_html(url: str):
    parts = [p for p in url.strip("/").split("/") if p]
    crumbs = ['<a href="/" class="hover-target">Главная</a>']
    if not parts:
        crumbs.append("<span>/</span>")
    else:
        running = ""
        for i, part in enumerate(parts):
            running = f"{running.rstrip('/')}/{part}"
            href = f"{running}/"
            name = breadcrumb_name(href)
            if i == len(parts) - 1:
                crumbs.append(f"<span>{name}</span>")
            else:
                if href in EXISTING_ROUTES:
                    crumbs.append(f'<a href="{href}" class="hover-target">{name}</a>')
                else:
                    crumbs.append(f"<span>{name}</span>")
    return "<div class=\"breadcrumbs t-mono\">" + "<span>•</span>".join(crumbs) + "</div>"


def build_schema(url: str, meta: dict, faq_items):
    graph = [base_local_business()]

    abs_url = f"{DOMAIN}{url}"
    graph.append(
        {
            "@type": "WebPage",
            "name": meta["h1"],
            "url": abs_url,
            "description": meta["description"],
            "inLanguage": "ru-RU",
        }
    )

    graph.append(
        {
            "@type": "BreadcrumbList",
            "itemListElement": build_breadcrumb_list(url),
        }
    )

    page_type = meta["page_type"]
    if page_type in {"service_landing", "service_template"}:
        graph.append(
            {
                "@type": "Service",
                "name": meta["h1"],
                "url": abs_url,
                "areaServed": "Махачкала",
                "provider": {"@type": "LocalBusiness", "name": "КРЕПОСТЬ"},
            }
        )

    if page_type in {"guide_pillar", "guide_template"}:
        graph.append(
            {
                "@type": "Article",
                "headline": meta["h1"],
                "mainEntityOfPage": abs_url,
                "author": {"@type": "Organization", "name": "КРЕПОСТЬ"},
            }
        )

    if faq_items:
        graph.append(
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a},
                    }
                    for q, a in faq_items[:8]
                ],
            }
        )

    return {"@context": "https://schema.org", "@graph": graph}


def render_page(url: str, meta: dict, faq_items):
    abs_url = f"{DOMAIN}{url}"
    service_slug = "all"
    for s in ["stroitelstvo", "proektirovanie", "inzheneriya", "otdelka"]:
        if s in url:
            service_slug = s
            break

    schema = build_schema(url, meta, faq_items)
    content = build_content(url, meta, faq_items)

    html = f'''<!doctype html>
<html lang="ru" class="lenis">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>{meta["title"]}</title>
  <meta name="description" content="{meta["description"]}" />
  <meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1" />
  <link rel="canonical" href="{abs_url}" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="{meta["h1"]}" />
  <meta property="og:description" content="{meta["description"]}" />
  <meta property="og:url" content="{abs_url}" />
  <meta property="og:locale" content="ru_RU" />
  <meta property="og:image" content="{DOMAIN}/assets/img/og-default.svg" />
  <meta name="twitter:card" content="summary_large_image" />

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml" />
  <link rel="manifest" href="/site.webmanifest" />

  <script src="https://cdn.jsdelivr.net/gh/studio-freight/lenis@1.0.19/bundled/lenis.min.js"></script>
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
  <link rel="stylesheet" href="/assets/css/main.css" />
</head>
<body data-page-type="{meta["page_type"]}" data-service="{service_slug}">
  <div class="cursor"><span class="cursor-text">View</span></div>
{header_block()}
  <main class="grid-wrap">
{breadcrumb_html(url)}
{content}
{page_contact_section(meta["page_type"], service_slug)}
  </main>
{footer_block()}
  <script src="/assets/js/config.js"></script>
  <script src="/assets/js/main.js"></script>
  <script src="/assets/js/analytics.js"></script>
</body>
</html>
'''
    return html


def write_pages(seo_map, aeo_map):
    for url in URLS:
        meta = build_meta(url, seo_map)
        faq_items = aeo_map.get(url, [])
        if not faq_items and meta["page_type"] in {"guide_pillar", "guide_template"}:
            faq_items = GUIDE_BASE_FAQ

        html = render_page(url, meta, faq_items)

        rel = url.strip("/")
        out_dir = ROOT / rel
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(html, encoding="utf-8")


def write_robots_and_sitemap():
    robots = """User-agent: *
Allow: /

Sitemap: https://krepostdom.ru/sitemap.xml
"""
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")

    today = date.today().isoformat()
    all_urls = ["/"] + URLS
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in all_urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{DOMAIN}{url}</loc>")
        lines.append(f"    <lastmod>{today}</lastmod>")
        lines.append("    <changefreq>weekly</changefreq>")
        lines.append("    <priority>0.8</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_404_page():
    schema_404 = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "name": "Страница не найдена",
                "url": f"{DOMAIN}/404.html",
                "description": "Страница не найдена. Перейдите в ключевые разделы сайта КРЕПОСТЬ.",
                "inLanguage": "ru-RU",
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{DOMAIN}/"},
                    {"@type": "ListItem", "position": 2, "name": "404", "item": f"{DOMAIN}/404.html"},
                ],
            },
        ],
    }

    html = f'''<!doctype html>
<html lang="ru" class="lenis">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Страница не найдена | КРЕПОСТЬ</title>
  <meta name="description" content="Страница не найдена. Перейдите в услуги, цены, кейсы или контакты КРЕПОСТЬ." />
  <meta name="robots" content="noindex,follow" />
  <link rel="canonical" href="{DOMAIN}/404.html" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="Страница не найдена | КРЕПОСТЬ" />
  <meta property="og:description" content="Перейдите в ключевые разделы сайта КРЕПОСТЬ." />
  <meta property="og:url" content="{DOMAIN}/404.html" />
  <meta property="og:locale" content="ru_RU" />
  <meta property="og:image" content="{DOMAIN}/assets/img/og-default.svg" />
  <meta name="twitter:card" content="summary_large_image" />

  <link rel="stylesheet" href="/assets/css/main.css" />
  <link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml" />
  <link rel="manifest" href="/site.webmanifest" />
  <script type="application/ld+json">{json.dumps(schema_404, ensure_ascii=False)}</script>
</head>
<body data-page-type="404" data-service="all">
  <div class="topbar t-mono"><span>Махачкала & РД</span><span>КРЕПОСТЬ</span></div>
  <main class="grid-wrap">
    <section class="hero border-b">
      <div class="hero-text-box border-r">
        <div>
          <div class="t-mono">Ошибка 404</div>
          <h1 class="h-huge" style="margin:20px 0;">Страница<br>Не Найдена.</h1>
          <p class="t-body" style="max-width:560px;">Возможно, ссылка устарела или адрес введен с ошибкой. Перейдите в ключевые разделы сайта.</p>
        </div>
        <div class="hero-cta-row">
          <a href="/" class="btn hover-target">На главную</a>
          <a href="/services/" class="btn btn-outline hover-target">К услугам</a>
        </div>
      </div>
      <div class="hero-img-box">
        <img src="https://images.unsplash.com/photo-1600566753051-f0b10f6f3f67?auto=format&fit=crop&w=1400&q=80" alt="404" class="hero-img" loading="lazy">
      </div>
    </section>
  </main>
  <script src="/assets/js/config.js"></script>
  <script src="/assets/js/analytics.js"></script>
</body>
</html>
'''
    (ROOT / "404.html").write_text(html, encoding="utf-8")


def main():
    ensure_dirs()

    index_text = INDEX_PATH.read_text(encoding="utf-8")
    has_inline_assets = bool(
        re.search(r"\n  <style>\n.*?\n  </style>\n", index_text, flags=re.S)
        and re.search(r"\n  <!-- СКРИПТЫ -->\n  <script>\n.*?\n  </script>\n", index_text, flags=re.S)
    )
    if has_inline_assets:
        extract_assets_from_index(index_text)
    else:
        if not (ROOT / "assets/css/main.css").exists() or not (ROOT / "assets/js/main.js").exists():
            raise RuntimeError("Не найдены assets/css/main.css или assets/js/main.js для повторной генерации.")

    write_config_js()
    write_analytics_js()
    write_graphics_and_manifest()

    cleaned = clean_index_and_switch_assets(index_text)
    INDEX_PATH.write_text(cleaned, encoding="utf-8")

    seo_map, aeo_map = load_meta_sources()
    write_pages(seo_map, aeo_map)
    write_robots_and_sitemap()
    write_404_page()


if __name__ == "__main__":
    main()
