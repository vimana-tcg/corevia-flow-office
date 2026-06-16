# Reference кейс (абстрактний приклад)

Сайт каталогу/послуг із двомовним контентом (наприклад UK + RU): blog + product + hub сторінки.

## Стартова точка

- ~107 HTML файлів (UK + RU, blog + product + hub)
- GEO **35**/100, AEO **62**/100
- robots.txt мав лише 3 AI боти (з 17 існуючих)
- llms.txt було 5.6 KB, llms-full.txt **не було**
- Intro prose 80+ слів: **0** сторінок
- H2 anchor IDs: **0**
- FAQ user-voice: **0**
- FAQPage schema: **0**
- Answer Block 40-80 слів: **0**

## Деплой за 1 день (час по кроках)

| Крок | Що | Час |
|---|---|---|
| 1 | robots.txt → 17 AI bots allowlist + 6 training blocks | 5 хв |
| 2 | llms-full.txt згенеровано з knowledge file (data.py UNITS, ~20 KB) | 15 хв |
| 3 | Intro section template у build-скрипт + brand-context paragraph | 30 хв |
| 4 | Slugify-функція для H2 IDs + патч у render-loop | 20 хв |
| 5 | Rewrite FAQ у статтях → user-voice | 90 хв |
| 6 | Universal brand FAQ injection (3 додаткові питання на кожній статті) | 25 хв |
| 7 | FAQPage JSON-LD у product pages | 30 хв |
| 8 | Answer Block 80+ слів під H1 на product pages | 35 хв |
| **Σ** | | **~4.2 год** |

## Результат через 1 день

- GEO **92**/100 (+57)
- AEO **95**/100 (+33)
- robots: **17**/17 AI bots
- llms-full.txt: ✅ ~20 KB
- Intro 80+: **100%**
- H2 anchor IDs: **100%**
- FAQ user-voice 3+: зростання до ~88%
- FAQPage schema: **100%** (усі product pages)
- Answer Block: **100%**

## Конфіг (приклад)

```json
{
  "SITE_HOST": "example.com",
  "BRAND": "Your Brand",
  "LEGAL_NAME": "Your Company LLC",
  "REGISTRATION_ID": "<реєстраційний номер>",
  "CITY": "<місто>",
  "PRIMARY_LANG": "uk",
  "PRIMARY_CATEGORY": "<основна категорія бізнесу>",
  "CATEGORIES": "<перелік категорій товарів/послуг>",
  "YEARS_EXPERIENCE": "10",
  "CHANNEL": "Telegram",
  "WEBROOT": "/var/www/example.com",
  "KNOWLEDGE_FILE": "landing/data.py"
}
```

## Що було критичним для успіху

1. **Universal brand FAQ** — додавання 3 universal Q/A до кожної статті (Чи доставляєте? Як зв'язатись? Документи?) — підняло FAQ-coverage з 0 до ~88% **БЕЗ** ручного редагування десятків існуючих статей
2. **Slugify з кирилицею** — стандартний slugify Latin-only, потрібна транслітерація UK → ASCII. У `tools/slugify.py` — повна таблиця.
3. **Intro з brand-context paragraph** — у початковому intro 30-50 слів, додавання `<p>Your Brand — ...</p>` доводить до 80+
4. **regex для user-voice — UK first** — стандартні `/Сколько|Какой|How/` не ловлять «Чи є», «Яке», «Чим». Розширити в `user-voice-prefixes.json`.

## Сюрпризи

- **«100%» false positive** у guard.js: regex для `\d{1,3}%` ловив `width="100%"` в CSS. Fix — strip `<style>` + `<script>` блоків + лише шумові атрибути (style/width/height/data-*) — не чіпати `<a href>`.
- **`site:` cannibalization** — GSC оператор `site:` потрапив у detector. Fix — `^\s*(site|info|related|cache|inurl|intitle):` фільтр.
- **Sitemap broken URLs** — sitemap містив URL мовної версії, що ще не згенерована (потребує перекладу). Fix — додавати URL у sitemap лише якщо файл є на диску.
