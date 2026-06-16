---
name: ai-search-ready
description: "Робить будь-який сайт AI-search ready за 1 deploy. 7 компонентів: (1) robots.txt з 17 AI-ботами whitelist + 6 training scrapers blocked, (2) llms-full.txt згенерований з каталогу/UNITS, (3) intro prose 80+ слів під H1 для GEO passage citation, (4) anchor IDs (slug) на всіх <h2>, (5) FAQ в user-query voice (Скільки/Який/Чи є/Чи можна…), (6) FAQPage JSON-LD schema, (7) Answer Block 40-80 слів під H1 (AEO). У реальному кейсі підняло GEO 35→92, AEO 62→95 за 30 хв. Use коли: 'AI search optimization', 'ChatGPT search', 'Perplexity', 'Google AIO', 'AI Overviews', 'llms.txt', 'GEO optimize', 'AEO optimize', 'зробити сайт під AI пошук'."
user-invokable: true
argument-hint: "[path-to-site-source]"
license: MIT
metadata:
  version: "1.0.0"
  category: seo
  prerequisites: "Python build pipeline (data.py UNITS + build.py + build_articles.py) АБО будь-який framework з editable templates"
---

# AI Search Ready — оптимізація сайту під GEO/AEO

## Що дає

7 структурних змін, кожна підтверджена реальним lift на проді:

| Компонент | Що | GEO/AEO lift |
|---|---|---|
| 1. **robots.txt** | 17 AI-ботів allowlist (GPTBot, ClaudeBot, OAI-SearchBot, Perplexity, Apple, Bing, Google-Extended) + 6 training scrapers block (CCBot, Bytespider, ImagesiftBot) | AI crawlers access: 3/7 → **7/7** ✅ |
| 2. **llms-full.txt** | ~20-30 KB структурованого контексту: компанія, каталог, FAQ, sitemaps, контакти | GEO score: ~+15 балів |
| 3. **Intro prose** | `<section id="intro">` з 80+ слів prose під H1 (з brand-context) | GEO passage citation 0% → 100% |
| 4. **Anchor IDs** | Всі `<h2 id="slugify(title)">` через транслітерацію кирилиці | Passage-level citation 0% → 100% |
| 5. **FAQ user-voice** | Питання типу «Скільки коштує…?», «Чи є в наявності…?», «Як перевірити…?» (не «Цены», «Гарантия») | FAQ detection 0/138 → 50/57 |
| 6. **FAQPage schema** | JSON-LD з 3+ user-voice Question/Answer | AEO citation eligibility +18 балів |
| 7. **Answer Block** | 40-80 слів безпосередньо під H1 — прямий direct answer на головний user-query | AEO snippet 0% → 100% |

## Коли НЕ брати

- Сайт на закритій платформі без access до template (Squarespace, Wix без code injection)
- WordPress із readonly theme — спочатку відкрити child theme
- React/SPA без SSR — google не побачить — спочатку перевести на SSG/SSR

## Передумови

1. **Edit access** до template файлів сайту
2. **Knowledge base** для llms-full.txt: каталог продуктів / послуг / units в Python-форматі (як `data.py` UNITS) АБО Markdown файлах
3. **Python 3.8+** для render тулзів (тимчасово, скрипти однопустотні)
4. Сайт має **canonical URL** (HTTPS + одна версія www чи без)

## Workflow (10 кроків)

### Передзйомка (5 хв)

1. **Питаю 6 параметрів:**
   - `SITE_HOST` (домен)
   - `BRAND` (назва бренду для intro контексту)
   - `PRIMARY_LANG` (uk/ru/en — для user-voice patterns)
   - `WEBROOT` (де лежать HTML файли)
   - `KNOWLEDGE_FILE` (data.py UNITS / yaml / markdown — звідки тягнути для llms-full)
   - `TEMPLATE_LANG` (python/jinja/handlebars/react)

2. **Baseline scan:**
   ```bash
   python3 tools/scan-pages.py --root <WEBROOT>
   # → Поточний stan: % intro, % anchor IDs, FAQ schema, robots.txt
   ```

### Деплой компонентів (25 хв)

3. **robots.txt** — генерую через `tools/robots-builder.py` → deploy на VPS / git push

4. **llms-full.txt** — генерую через `tools/llms-full-builder.py` з knowledge file → deploy

5. **Intro prose template** — патч у template файлі (`build_articles.py` для нашого Python pipeline, `_layouts/post.html` для Jekyll, `pages/[slug].tsx` для Next.js). Tools/intro-block.tpl містить готовий блок.

6. **Anchor IDs на H2** — патч render-функції щоб slugify+транслітерувати UK/RU H2 → `id` attribute. Tools/slugify.py готовий.

7. **FAQ user-voice rewrite** — `tools/faq-rewriter.py` бере existing FAQ → перевіряє чи user-voice → пропонує rewrite. Якщо існуюча FAQ генерується кодом — патч у writer.

8. **FAQPage JSON-LD** — додати в `<head>` template `<script type="application/ld+json">{ "@type": "FAQPage", ...}</script>` з 3+ Q/A. Tools/faq-schema.tpl.

9. **Answer Block** — 40-80 слів прямо під H1, відповідь на головний user-query сторінки. Tools/answer-block.tpl + builder.

### Перевірка (5 хв)

10. **Re-scan:**
    ```bash
    python3 tools/scan-pages.py --root <WEBROOT> --compare baseline.json
    # → +N% intro / +M% anchor / +K% FAQ
    ```

## Файли у `tools/`

| Файл | Призначення |
|---|---|
| `scan-pages.py` | Baseline + post-scan: % intro / anchor / FAQ / schema |
| `robots-builder.py` | Генерує robots.txt з 17 AI bots + 6 training blocks |
| `llms-full-builder.py` | З knowledge file → llms-full.txt (20+ KB структурований) |
| `slugify.py` | UK/RU/EN транслітерація кирилиці → ASCII slug |
| `intro-block.tpl` | Template intro section з brand-context (80+ слів) |
| `answer-block.tpl` | Template Answer Block 40-80 слів |
| `faq-rewriter.py` | Перевіряє existing FAQ + пропонує user-voice |
| `faq-schema.tpl` | JSON-LD FAQPage template |
| `ai-bots-list.json` | Канонічний список 17 AI-ботів + категоризація |
| `user-voice-prefixes.json` | UK/RU/EN регекс паттерни для FAQ детекту |

## Приклади

- `examples/example.md` — приклад кейсу (GEO 35→92, AEO 62→95)

## Композиція з іншими скілами

- `/seo-autopilot` — повний autopilot (включає `/ai-search-ready` як частину)
- `/seo-audit` — баз knowledge для перевірки що змінилось
- `/seo-cluster` — для FAQ-питань на основі реального GSC данных
- `/seo-page` — деталь на одну сторінку

## Анти-патерни

- ❌ **Не додавати** AI-bot allowlist для сайтів **з paid content** — він стане безкоштовно в AI-відповідях
- ❌ **Не генерувати llms-full.txt** автоматично — це public документ, перевіряй цифри/контакти ВРУЧНУ
- ❌ **Не fake-генерувати FAQ** — питання мають бути на реальних user queries (з GSC або conversation history)
- ❌ Answer Block НЕ дублює body — це ВИКЛЮЧЕНО summary, не reword

## Версії

- **1.0.0** — перший реліз
