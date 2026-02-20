# Launch Gate Checklist

## Deployment Fact (2026-02-20)
- `main` pushed: `998c30d`.
- `gh-pages` branch pushed from current `main`.
- Candidate live URL: `https://webar4i.github.io/krepost_doma/`.
- External check result: currently returns `404` (GitHub Pages site not active yet for repo settings).

## GO only if (status)
- [x] Все ключевые URL отдают `200` локально (25/25).
- [x] Нет критичных ошибок schema/metadata (валидация по всем страницам пройдена).
- [x] Формы и клики по контактам отправляют события в аналитику (`form_submit`, `call_click`, `cta_click_primary`, `faq_expand`, `case_view`).
- [ ] Proof Matrix закрыта по всем обещаниям Hero/CTA.
  - Блокер: в `reports/05_stage4_content_meta/proof_matrix.csv` остаются `TBD` для стоимости/гарантий/сроков.
- [ ] Публикация в sitemap и отправка в вебмастера выполнены.
  - `sitemap.xml` готов и актуален.
  - Отправка в Яндекс Вебмастер / Google Search Console не выполнена на момент этой проверки.
- [ ] Публичный деплой доступен по live URL.
  - Блокер: GitHub Pages не активирован в настройках репозитория.

## STOP conditions (status)
- [x] Нет рабочих форм на mobile. (не обнаружено)
- [x] Важные страницы закрыты robots/noindex. (не обнаружено)
- [ ] Нет подтверждения по юридически значимым обещаниям (цены/гарантии).
  - Стоп-фактор активен до закрытия `TBD` в Proof Matrix.

## Final Pre-Launch Actions
1. Активировать GitHub Pages для репозитория (`Deploy from branch: gh-pages / root`) и дождаться `200` по `https://webar4i.github.io/krepost_doma/`.
2. Подтвердить юридические обещания и убрать `TBD` из proof-артефактов.
3. Отправить `https://krepostdom.ru/sitemap.xml` в Яндекс Вебмастер и Google Search Console после переключения на прод-домен.
