(function () {
  function safeText(value) {
    return value == null ? '' : String(value);
  }

  function setText(selector, value) {
    const node = document.querySelector(selector);
    if (node) node.textContent = safeText(value);
  }

  function setHref(selector, href) {
    const node = document.querySelector(selector);
    if (node && href) node.setAttribute('href', href);
  }

  function renderRelatedCases(currentCase, allCases) {
    const relatedRoot = document.querySelector('[data-case-related]');
    if (!relatedRoot) return;

    const related = allCases
      .filter((item) => item.id !== currentCase.id)
      .sort((a, b) => {
        const scoreA = a.category === currentCase.category ? 1 : 0;
        const scoreB = b.category === currentCase.category ? 1 : 0;
        if (scoreA !== scoreB) return scoreB - scoreA;
        return String(b.year).localeCompare(String(a.year), 'ru');
      })
      .slice(0, 3);

    relatedRoot.innerHTML = related.map((item) => {
      return `
        <article class="case-related-card">
          <a class="hover-target" href="/raboty/${item.slug}/">
            <span class="meta">${safeText(item.categoryLabel || '')} • ${safeText(item.year || '')}</span>
            <b>${safeText(item.title)}</b>
            <span class="case-link">Открыть кейс</span>
          </a>
        </article>
      `;
    }).join('');
  }

  document.addEventListener('DOMContentLoaded', function () {
    const root = document.querySelector('[data-case-detail]');
    const data = Array.isArray(window.CASES_DATA) ? window.CASES_DATA : [];

    if (!root || !data.length) return;

    const slug = root.dataset.caseSlug;
    const item = data.find((entry) => entry.slug === slug);

    if (!item) {
      setText('[data-case-title]', 'Кейс не найден');
      setText('[data-case-description]', 'Кейс отсутствует в каталоге. Вернитесь на страницу каталога работ.');
      return;
    }

    document.body.dataset.service = item.category || 'all';

    setText('[data-case-breadcrumb]', item.title);
    setText('[data-case-location]', item.location);
    setText('[data-case-title]', item.title);
    setText('[data-case-description]', item.description);
    setText('[data-case-area]', item.stats && item.stats.area ? item.stats.area : '—');
    setText('[data-case-duration]', item.stats && item.stats.duration ? item.stats.duration : '—');
    setText('[data-case-budget]', item.stats && item.stats.budget ? item.stats.budget : '—');
    setText('[data-case-task]', item.task);
    setText('[data-case-solution]', item.solution);
    setText('[data-case-result]', item.result);
    setText('[data-case-testimonial-text]', item.testimonial && item.testimonial.text ? item.testimonial.text : '');
    setText('[data-case-testimonial-author]', item.testimonial && item.testimonial.author ? `— ${item.testimonial.author}` : '');
    setText('[data-case-category-label]', item.categoryLabel || 'Кейс');

    const metaRoot = document.querySelector('[data-case-meta]');
    if (metaRoot) {
      const chips = [item.categoryLabel || 'Кейс', item.city || '', item.year || ''].filter(Boolean);
      metaRoot.innerHTML = chips.map((value) => `<span>${safeText(value)}</span>`).join('');
    }

    const stagesRoot = document.querySelector('[data-case-stages]');
    if (stagesRoot) {
      const stages = Array.isArray(item.stages) ? item.stages : [];
      stagesRoot.innerHTML = stages.map((stage) => `<li>${safeText(stage)}</li>`).join('');
    }

    const featuresRoot = document.querySelector('[data-case-features]');
    if (featuresRoot) {
      const features = Array.isArray(item.features) ? item.features : [];
      featuresRoot.innerHTML = features.map((feature) => `<span>${safeText(feature)}</span>`).join('');
    }

    const coverNode = document.querySelector('[data-case-cover]');
    if (coverNode && item.cover) {
      coverNode.classList.add(item.cover);
    }

    const img = document.querySelector('[data-case-image]');
    if (img) {
      img.src = item.image || '';
      img.alt = item.alt || item.title || 'Кейс';
    }

    setHref('[data-case-service-link]', item.serviceUrl || '/services/');
    setHref('[data-case-price-link]', item.priceUrl || '/tseny/');

    renderRelatedCases(item, data);
  });
})();
