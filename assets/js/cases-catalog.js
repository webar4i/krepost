(function () {
  const BASE_PATH = '/krepost';
  const CATEGORY_META = {
    all: 'Все работы',
    stroitelstvo: 'Строительство',
    proektirovanie: 'Проектирование',
    inzheneriya: 'Инженерия',
    otdelka: 'Отделка'
  };

  function escapeHtml(value) {
    return String(value || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function getCtx() {
    const ds = (document.body && document.body.dataset) || {};
    return {
      page_type: ds.pageType || 'unknown',
      service: ds.service || 'all'
    };
  }

  function sendFilterEvent(state, resultsCount) {
    const cfg = window.ANALYTICS_CONFIG || {};
    const ctx = getCtx();
    const payload = {
      event: 'catalog_filter_change',
      page_type: ctx.page_type,
      service: ctx.service,
      category: state.category,
      city: state.city,
      year: state.year,
      results_count: resultsCount
    };

    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(payload);

    if (typeof window.gtag === 'function') {
      window.gtag('event', 'catalog_filter_change', payload);
    }

    if (typeof window.ym === 'function' && cfg.yandexMetrikaId) {
      try {
        window.ym(Number(cfg.yandexMetrikaId), 'reachGoal', 'catalog_filter_change', payload);
      } catch (e) {
        // no-op
      }
    }
  }

  function buildCard(item) {
    const detailUrl = `${BASE_PATH}/raboty/${item.slug}/`;
    const metaChips = [
      item.categoryLabel || CATEGORY_META[item.category] || 'Кейс',
      item.city || '',
      item.year || ''
    ].filter(Boolean);

    const features = (item.features || []).slice(0, 3);

    return `
      <article class="case-card catalog-case-card" data-case-id="${escapeHtml(item.id)}" data-case-category="${escapeHtml(item.category)}">
        <a class="catalog-card-link hover-target" href="${escapeHtml(detailUrl)}" aria-label="${escapeHtml(item.title)}">
          <div class="catalog-cover ${escapeHtml(item.cover || 'cover-default')}">
            <img src="${escapeHtml(item.image || '')}" alt="${escapeHtml(item.alt || item.title || 'Кейс')}" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.classList.add('is-broken');this.closest('.catalog-cover').classList.add('is-fallback');">
            <span class="catalog-cover-badge">${escapeHtml(item.categoryLabel || CATEGORY_META[item.category] || 'Кейс')}</span>
          </div>
          <div class="catalog-card-body">
            <div class="catalog-card-meta t-mono">${metaChips.map(escapeHtml).join(' • ')}</div>
            <h3 class="h-md catalog-card-title">${escapeHtml(item.title)}</h3>
            <p class="catalog-card-description">${escapeHtml(item.description)}</p>
            <div class="catalog-card-stats">
              <span><b>${escapeHtml(item.stats && item.stats.area ? item.stats.area : '—')}</b><small>Площадь</small></span>
              <span><b>${escapeHtml(item.stats && item.stats.duration ? item.stats.duration : '—')}</b><small>Срок</small></span>
              <span><b>${escapeHtml(item.stats && item.stats.budget ? item.stats.budget : '—')}</b><small>Бюджет</small></span>
            </div>
            <div class="catalog-card-points">
              ${features.map((feature) => `<span>${escapeHtml(feature)}</span>`).join('')}
            </div>
            <span class="catalog-card-cta">Открыть кейс</span>
          </div>
        </a>
      </article>
    `;
  }

  document.addEventListener('DOMContentLoaded', function () {
    const root = document.querySelector('[data-cases-catalog]');
    const data = Array.isArray(window.CASES_DATA) ? window.CASES_DATA : [];

    if (!root || !data.length) return;

    const cases = data.filter((item) => item && item.status === 'realized');
    const grid = root.querySelector('[data-catalog-grid]');
    const countNode = root.querySelector('[data-catalog-count]');
    const emptyNode = root.querySelector('[data-catalog-empty]');
    const citySelect = root.querySelector('[data-filter-city]');
    const yearSelect = root.querySelector('[data-filter-year]');
    const resetButtons = Array.from(root.querySelectorAll('[data-filter-reset]'));
    const categoryButtons = Array.from(root.querySelectorAll('[data-filter-category]'));

    const state = {
      category: 'all',
      city: 'all',
      year: 'all'
    };

    const cities = Array.from(new Set(cases.map((item) => item.city).filter(Boolean))).sort((a, b) => a.localeCompare(b, 'ru'));
    const years = Array.from(new Set(cases.map((item) => item.year).filter(Boolean))).sort((a, b) => String(b).localeCompare(String(a), 'ru'));

    cities.forEach((city) => {
      const option = document.createElement('option');
      option.value = city;
      option.textContent = city;
      citySelect.appendChild(option);
    });

    years.forEach((year) => {
      const option = document.createElement('option');
      option.value = year;
      option.textContent = year;
      yearSelect.appendChild(option);
    });

    function applyStateToControls() {
      categoryButtons.forEach((button) => {
        const isActive = button.dataset.filterCategory === state.category;
        button.classList.toggle('is-active', isActive);
        button.setAttribute('aria-pressed', String(isActive));
      });

      citySelect.value = state.city;
      yearSelect.value = state.year;
    }

    function filterCases() {
      return cases
        .filter((item) => (state.category === 'all' ? true : item.category === state.category))
        .filter((item) => (state.city === 'all' ? true : item.city === state.city))
        .filter((item) => (state.year === 'all' ? true : String(item.year) === String(state.year)))
        .sort((a, b) => {
          const byYear = String(b.year).localeCompare(String(a.year), 'ru');
          if (byYear !== 0) return byYear;
          return String(a.title).localeCompare(String(b.title), 'ru');
        });
    }

    function render() {
      const filtered = filterCases();
      grid.innerHTML = filtered.map(buildCard).join('');
      countNode.textContent = String(filtered.length);
      const isEmpty = filtered.length === 0;
      emptyNode.hidden = !isEmpty;
      grid.hidden = isEmpty;
    }

    function setState(nextState, shouldTrack) {
      state.category = nextState.category;
      state.city = nextState.city;
      state.year = nextState.year;

      applyStateToControls();
      render();

      if (shouldTrack) {
        sendFilterEvent(state, filterCases().length);
      }
    }

    categoryButtons.forEach((button) => {
      button.addEventListener('click', function () {
        setState({
          category: button.dataset.filterCategory || 'all',
          city: state.city,
          year: state.year
        }, true);
      });
    });

    citySelect.addEventListener('change', function () {
      setState({
        category: state.category,
        city: citySelect.value || 'all',
        year: state.year
      }, true);
    });

    yearSelect.addEventListener('change', function () {
      setState({
        category: state.category,
        city: state.city,
        year: yearSelect.value || 'all'
      }, true);
    });

    resetButtons.forEach((button) => {
      button.addEventListener('click', function () {
        setState({ category: 'all', city: 'all', year: 'all' }, true);
      });
    });

    /* --- Mirror count sync --- */
    const mirrorCountNode = root.querySelector('[data-catalog-count-mirror]');

    const originalRender = render;
    render = function () {
      originalRender();
      if (mirrorCountNode) {
        mirrorCountNode.textContent = countNode.textContent;
      }
    };

    /* --- Mobile filter toggle --- */
    const mobileToggle = root.querySelector('[data-mobile-filter-toggle]');
    const sidebar = root.querySelector('.catalog-sidebar');

    if (mobileToggle && sidebar) {
      mobileToggle.addEventListener('click', function () {
        sidebar.classList.toggle('is-open');
        const isOpen = sidebar.classList.contains('is-open');
        mobileToggle.setAttribute('aria-expanded', String(isOpen));
      });
    }

    setState(state, false);
  });
})();
