// Данные компании для использования на всех страницах
// ЗАПОЛНИТЬ: реальные данные компании

const COMPANY_DATA = {
  // Основная информация
  name: 'ООО «КРЕПОСТЬ»',
  shortName: 'КРЕПОСТЬ',
  slogan: 'Строим дома, которые служат поколениям',
  
  // Юридические реквизиты
  legal: {
    inn: '[ИНН - 10 цифр]',
    ogrn: '[ОГРН - 13 цифр]',
    kpp: '[КПП - 9 цифр]',
    legalAddress: '[ЮРИДИЧЕСКИЙ АДРЕС С ИНДЕКСОМ]',
    actualAddress: '[ФАКТИЧЕСКИЙ АДРЕС ОФИСА]',
    bankAccount: '[Р/С]',
    bank: '[БАНК]',
    bik: '[БИК]',
    corrAccount: '[К/С]'
  },
  
  // Контакты
  contacts: {
    phone: '+7-XXX-XXX-XX-XX',
    phoneDisplay: '+7 (XXX) XXX-XX-XX',
    email: 'info@krepostdom.ru',
    whatsapp: '+7-XXX-XXX-XX-XX',
    telegram: '@krepostdom',
    
    // Часы работы
    workingHours: {
      weekdays: '09:00 - 18:00',
      saturday: '10:00 - 15:00',
      sunday: 'Выходной'
    }
  },
  
  // Адрес с геокоординатами
  address: {
    street: '[УЛИЦА, ДОМ]',
    city: 'Махачкала',
    region: 'Республика Дагестан',
    zip: '[ИНДЕКС]',
    country: 'RU',
    lat: '[ШИРОТА]',
    lng: '[ДОЛГОТА]'
  },
  
  // Социальные сети и профили
  social: {
    vk: '[ССЫЛКА VK]',
    instagram: '[ССЫЛКА INSTAGRAM]',
    youtube: '[ССЫЛКА YOUTUBE]',
    telegram: '[ССЫЛКА TELEGRAM КАНАЛ]'
  },
  
  // Профили на картах и агрегаторах
  profiles: {
    yandexMaps: '[ССЫЛКА ЯНДЕКС.КАРТЫ]',
    googleMaps: '[ССЫЛКА GOOGLE MAPS]',
    gis2: '[ССЫЛКА 2GIS]',
    yandexBusiness: '[ССЫЛКА ЯНДЕКС.БИЗНЕС]',
    googleBusiness: '[ССЫЛКА GOOGLE BUSINESS]'
  },
  
  // О компании
  about: {
    founded: '[ГОД ОСНОВАНИЯ]',
    experience: '[X] лет',
    teamSize: '[X] человек',
    projectsCount: '[X]+',
    description: 'Строительная компания полного цикла в Махачкале. Специализируемся на строительстве частных домов под ключ: от проектирования до чистовой отделки.'
  },
  
  // Лицензии и сертификаты
  licenses: [
    {
      name: 'СРО на строительство',
      number: '[НОМЕР]',
      date: '[ДАТА]'
    }
  ]
};

// Экспорт для использования в других скриптах
if (typeof module !== 'undefined' && module.exports) {
  module.exports = COMPANY_DATA;
}
