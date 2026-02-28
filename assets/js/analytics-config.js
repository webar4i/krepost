// Конфигурация аналитики
// ЗАПОЛНИТЬ: реальные ID счетчиков

window.ANALYTICS_CONFIG = {
  // Google Analytics 4 Measurement ID (формат: G-XXXXXXXXXX)
  googleAnalyticsId: 'G-XXXXXXXXXX',
  
  // Яндекс.Метрика counter ID (число)
  yandexMetrikaId: 123456789,
  
  // Включить дебаг-режим (выводит события в консоль)
  debug: false
};

// Инициализация Google Analytics 4
(function() {
  const cfg = window.ANALYTICS_CONFIG;
  
  // Google Analytics
  if (cfg.googleAnalyticsId && cfg.googleAnalyticsId !== 'G-XXXXXXXXXX') {
    const gaScript = document.createElement('script');
    gaScript.async = true;
    gaScript.src = `https://www.googletagmanager.com/gtag/js?id=${cfg.googleAnalyticsId}`;
    document.head.appendChild(gaScript);
    
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', cfg.googleAnalyticsId, {
      'send_page_view': true,
      'cookie_flags': 'SameSite=None;Secure'
    });
  }
  
  // Яндекс.Метрика
  if (cfg.yandexMetrikaId && cfg.yandexMetrikaId !== 123456789) {
    (function(m,e,t,r,i,k,a){
      m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
      m[i].l=1*new Date();
      k=e.createElement(t),a=e.getElementsByTagName(t)[0];
      k.async=1;k.src=r;a.parentNode.insertBefore(k,a);
    })(window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");
    
    window.ym(cfg.yandexMetrikaId, "init", {
      clickmap: true,
      trackLinks: true,
      accurateTrackBounce: true,
      webvisor: true,
      trackHash: true
    });
  }
})();
