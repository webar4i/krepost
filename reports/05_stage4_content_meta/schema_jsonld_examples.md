# JSON-LD Examples (адаптировано под проект)

## Organization (TBD-поля)
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "TBD",
  "url": "TBD",
  "logo": "TBD",
  "sameAs": ["TBD"]
}
```

## LocalBusiness
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "TBD",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Махачкала",
    "addressRegion": "Республика Дагестан",
    "addressCountry": "RU",
    "streetAddress": "TBD"
  },
  "telephone": "TBD",
  "areaServed": ["Махачкала", "Республика Дагестан"],
  "url": "TBD"
}
```

## Service
```json
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "Строительство домов под ключ",
  "areaServed": "Махачкала",
  "provider": {
    "@type": "LocalBusiness",
    "name": "TBD"
  }
}
```

## FAQPage
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Сколько стоит построить дом в Дагестане?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Стоимость зависит от площади, материалов и инженерных решений; точная смета рассчитывается по ТЗ."
      }
    }
  ]
}
```
