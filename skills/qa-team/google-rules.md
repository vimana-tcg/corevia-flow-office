# Google Search rules — actionable reference for qa-team

Версия: 2026-05 (Helpful Content стал core ranking в марте 2024, INP заменил FID
в марте 2024, Site Reputation Abuse policy запущена в мае 2024, Core Updates
ежемесячные).

**Источники:** developers.google.com/search/docs, web.dev, Google Search Status
Dashboard, Search Quality Evaluator Guidelines 2024, Google Search Central blog.

Этот файл — НЕ теория. Каждое правило — что Google требует/штрафует + что
конкретно чекать + как фиксить.

---

## 1. Indexability

### robots.txt
- **Правило:** Должен быть доступен по `/robots.txt`, статус 200. Если 5xx — Google прекращает crawl всего сайта.
- **Чекать:** `curl -I https://site.com/robots.txt` → 200. Содержимое валидно.
- **Не делать:** `User-agent: *\nDisallow: /` на проде. `Disallow:` без слэша = блок ничего, но путаница.
- **Sitemap:** должен быть указан в robots.txt: `Sitemap: https://site.com/sitemap.xml`.
- **2024 нюанс:** `noindex` в robots.txt **не работает** (был deprecated в 2019). Используй `<meta robots="noindex">` или HTTP header.

### Canonical
- **Правило:** Каждая страница должна иметь `<link rel="canonical">`. Self-canonical ОК. Cross-canonical (на другую страницу) — Google может проигнорировать.
- **Чекать:** Каждая URL → canonical → должен быть **absolute HTTPS URL**, без trailing-slash-mismatch с реальным URL.
- **Чекать:** Canonical с одной страницы НЕ должен указывать на 404 / redirect / noindex-страницу.
- **Не делать:** `canonical="http://"` (HTTP в HTTPS-проекте). `canonical="/"` на не-главной (relative path рискован).

### Noindex
- **Правило:** `<meta name="robots" content="noindex">` или HTTP `X-Robots-Tag: noindex`. Удаляет из индекса.
- **Грабли:** Если noindex-страница ТАКЖЕ заблокирована в robots.txt — Google не сможет прочитать noindex и страница останется в индексе.
- **Чекать:** Прод-страницы НЕ имеют случайного noindex (часто остаётся со staging).

### Redirect chains
- **Правило:** Максимум 1-2 редиректа. Google перестаёт следовать после 5+.
- **Чекать:** `curl -IL <url>` — сколько 301/302 в цепочке.
- **Особенно:** Внутренние ссылки через redirect → теряется crawl budget + small ranking signal. Линкуй на конечный URL.

### Crawl budget
- **Правило:** Релевантен только для крупных сайтов (>10k URL). Google priorityet важные.
- **Чекать:** Бесполезные URL в индексе (filter combinations, tracking params, session IDs). Используй robots.txt для disallow.

---

## 2. Sitemaps

### Формат XML
- **Правило:** Каждый sitemap ≤ 50 000 URL и ≤ 50 MB uncompressed. Если больше — split + sitemap index.
- **Правило:** Только canonical URLs. НЕ должно быть редиректов / 404 / noindex / параметризованных URL.
- **Правило:** `<lastmod>` — реальная дата изменения содержимого. ISO 8601 (`2026-05-26` или `2026-05-26T17:30:00+03:00`). НЕ менять lastmod на каждый билд без реальных изменений — Google расценит как «не доверять датам этого сайта».
- **Не делать:** Включать URL других доменов (sitemap only для своего origin).

### Hreflang в sitemap
- Альтернатива HTML `<link rel="alternate">`. В `<url>` добавляй `<xhtml:link rel="alternate" hreflang="X" href="Y">` для всех языков + self + x-default.

### Sitemap index
- Если >1 sitemap → один `sitemap_index.xml` со списком всех sitemap'ов.

---

## 3. Mobile-First Indexing

**С 2023 Mobile-First Indexing полностью развёрнут — Google индексирует мобильную версию.**

- **Правило:** Контент на mobile и desktop должен быть равноценным. Если мобильная версия урезана — теряются ранкинги.
- **Правило:** Структурированные данные (schema) должны быть на обеих версиях.
- **Правило:** Внутренние ссылки и hreflang — на обеих версиях.
- **Правило:** `<meta name="viewport" content="width=device-width,initial-scale=1">` обязательно.
- **Не делать:** `user-scalable=no` (Google штрафует UX-метрику + Lighthouse + a11y).
- **Не делать:** Контент `display:none` на мобиле — Google всё равно индексирует его на mobile-first.

### Адаптивность
- Текст ≥16px на mobile (иначе iOS Safari зумит инпуты).
- Tap targets ≥48dp (Material) / 44px (Apple HIG). Google Lighthouse чекает.
- Никаких горизонтальных скроллов (overflow-x).

---

## 4. Core Web Vitals (CWV) — Page Experience signal

**С марта 2024 INP заменил FID.** Текущие пороги:

| Метрика | Good | Needs work | Poor |
|---|---|---|---|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | 2.5-4s | > 4s |
| **INP** (Interaction to Next Paint) | ≤ 200ms | 200-500ms | > 500ms |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | 0.1-0.25 | > 0.25 |

Дополнительные (не core, но в Search Console):
- **FCP** (First Contentful Paint) ≤ 1.8s
- **TTFB** (Time to First Byte) ≤ 800ms
- **TBT** (Total Blocking Time) ≤ 200ms (lab-only)

### Источники данных
- **Field data** (real users): CrUX dataset, доступен через PageSpeed Insights API или CrUX API. **Это то, что использует Google для ранкинга.**
- **Lab data** (Lighthouse): эмуляция, не для ранкинга, но удобно для разработки.
- **Search Console** → Core Web Vitals report.

### Типичные причины fail и фиксы
- **LCP fail:** большая картинка без `preload`, без `loading="eager"` для hero, без `srcset`, render-blocking CSS/JS, медленный TTFB. Фикс: `<link rel="preload" as="image">` для LCP-картинки, lazy всё below-fold, defer не-critical JS.
- **INP fail:** тяжёлый JS на main thread, long tasks >50ms, неоптимизированный React hydration. Фикс: code-splitting, `requestIdleCallback`, web-workers для тяжёлого.
- **CLS fail:** картинки без `width/height`, embed (YouTube/iframes) без зарезервированного места, динамически вставляемый контент (banners, ads), `font-display: block` (FOIT). Фикс: всегда указывай dimensions, `font-display: swap`, не вставляй контент над existing.

### Не делать
- Полагаться только на Lighthouse score. Google ранкает по field data (CrUX).
- Считать что 1 страница с good CWV даёт буст всему сайту — оценка per-URL.

---

## 5. Page Experience signals (полный список)

Google официально: «we look at signals like Core Web Vitals + HTTPS + no intrusive interstitials».

- **HTTPS обязательно.** Mixed content — minus signal.
- **No intrusive interstitials** на mobile. Большие модалки/попапы, перекрывающие основной контент при загрузке → minus signal. Исключения: GDPR/cookie banners (если не агрессивны), age verification, login walls для премиум-контента.
- **Safe Browsing** — сайт не помечен как malware/phishing.
- **CWV** — см. раздел 4.

---

## 6. Helpful Content System (core ranking signal с 2024)

**Self-assessment вопросы из Google docs** (отвечаешь «нет» — content unhelpful):

### People-first (хороший)
- Есть ли существующая или предполагаемая аудитория, которой контент полезен?
- Демонстрирует ли контент first-hand expertise (Experience)?
- Если выложить такое в социалках, поделятся ли коллеги?
- Получит ли пользователь то, что искал?
- Уходит ли пользователь с ощущением, что узнал достаточно?

### Search-engine-first (плохой)
- Контент создан в основном для ранжирования?
- Делаешь ли контент по широкому спектру тем в надежде что какой-то взлетит?
- Используешь ли автоматизацию для production контента по многим темам?
- Суммируешь ли чужой контент без значимой добавочной ценности?
- Описываешь ли «тренды» без эксперт-понимания?
- Контент обещает что-то, чего не отвечает (clickbait)?
- Контент о new tech, который ты не пробовал сам?
- Контент с непопулярным результатом, потому что «надо что-то опубликовать»?

### Действия Google
Helpful Content классификатор — site-wide signal. Если значимая часть сайта unhelpful — **весь сайт** просядет. Восстановление — месяцы (требует major content reduction or quality improvement).

### Что чекать в QA
- Тонкие страницы (<300 слов), не дающие ответа на запрос.
- Дубль-контент в разных страницах с минимальной вариацией (программатик-SEO часто этим грешит).
- Author info / about page присутствует. Реальные люди, не «AI Writer».
- Date published / updated видим.
- Контент глубокий — раскрывает тему, а не суммирует чужое.

---

## 7. E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness)

Из Search Quality Evaluator Guidelines — Google использует это как сигнал. **Особенно жёстко для YMYL (Your Money or Your Life)** — финансы, медицина, юридическое, безопасность.

### Experience (новое — 2022, добавлено к старому E-A-T)
- Автор лично использовал продукт / сервис / тему?
- First-hand photos, screenshots, ownership statements.

### Expertise
- Автор имеет квалификацию обсуждать тему?
- Бэк-линки от експертов / индустриальных ресурсов.

### Authoritativeness
- Узнаваем ли сайт как авторитет в нише?
- Brand mentions в индустрии.

### Trustworthiness (самое важное)
- Точный, безопасный, надёжный контент.
- HTTPS, корректные контакты, **прозрачное owner-info**.
- Для e-commerce: refund policy, customer service contact, secure checkout.
- Для медицины/финансов: автор-квалификация явна.

### Что чекать в QA
- Контакты, физический адрес (если применимо), real names of authors.
- Privacy policy, terms of service.
- No misleading claims, no fake testimonials.
- Numbers + sources, не утверждения без основания.
- Customer reviews — реальные (можно проверить кросс-ссылки на третьи стороны).

---

## 8. AI-generated content (политика 2024)

**Краткая позиция Google (Feb 2023 + обновления):**

> «Using automation — including AI — to generate content with the primary purpose of manipulating ranking in search results is a violation of our spam policies.»

### Что разрешено
- AI-content **если он помогает пользователю** — OK.
- AI как ассистент написания, переводов, summary — OK.
- Disclosure (что AI генерировал) не **обязательна**, но Google рекомендует прозрачность для тем где автор важен (медицина, финансы).

### Что НЕ разрешено
- **Scaled content abuse** (2024 policy): массовое создание AI-content без added value — манипуляция ранкингом. **Жёстко штрафуется**.
- AI-сгенерённое + автопостинг + минимальная вычитка = риск Spam Penalty.

### Что чекать в QA для программатик-SEO
- Каждая страница даёт unique value, не просто шаблон с подставленным slug.
- Boilerplate <50% от страницы.
- E-E-A-T: реальная экспертиза, не AI hallucinations.
- Source attribution для статистик / цитат — реальные.

---

## 9. Spam Policies (2024 — полный список нарушений)

Из spam.google.com/spam-policies (последнее обновление 2024-05):

1. **Cloaking** — показывать разное Google и пользователю.
2. **Doorway pages** — много почти одинаковых страниц под мини-вариации запросов.
3. **Expired domain abuse** — купить мёртвый домен с истории + залить мусор.
4. **Hidden text/links** — `display:none`, `color: transparent`, текст за пределами viewport, тонкий шрифт.
5. **Keyword stuffing** — >2-3% плотности одного ключа.
6. **Link spam** — купленные ссылки, link-схемы, тонкие гостевые-posts массами.
7. **Machine-generated traffic** — automated queries, scraping search results.
8. **Malware / malicious behavior** — drive-by-download, обманчивые downloads.
9. **Misleading functionality** — фейковые кнопки/линки.
10. **Scaled content abuse** (NEW 2024) — массовая публикация низкокачественного контента, часто AI.
11. **Scraped content** — копии чужого без значимой добавки.
12. **Sneaky redirects** — пользователю одно, боту другое.
13. **Site reputation abuse** (NEW May 2024 — «Parasite SEO») — публикация third-party content на trusted-сайте для рангирования. Целятся: news-сайты, медиа, академические домены, продававшие свой авторитет.
14. **Thin affiliate** — страницы с минимальной добавочной ценностью к product feed.
15. **User-generated spam** — комменты-spam, profile-spam без модерации.

### Penalty последствия
- **Manual action** — appears в Search Console. Site/section deindexed до фикса.
- **Algorithmic** — нет уведомления, ранкинг просел. Восстановление — недели/месяцы после устранения причин.

---

## 10. Rich Results / Schema.org для Google

**Поддерживаемые типы (developers.google.com/search/docs/appearance/structured-data):**

| Type | Status | Ключевое |
|---|---|---|
| Article / BlogPosting / NewsArticle | ✅ | headline, datePublished, author, image |
| Product | ✅ | name, image, offers, brand, aggregateRating(если реальный), review |
| Product Snippets (для shopping) | ✅ | Дополнительно: gtin, mpn, sku |
| Recipe | ✅ | image, totalTime, recipeIngredient |
| FAQPage | ⚠️ ОГРАНИЧЕНО (Aug 2023) — Rich Result только для авторитетных gov/health sites | Q+A видимые на странице |
| HowTo | ⚠️ Deprecated для English desktop (Sep 2023) | — |
| Event | ✅ | name, startDate, location |
| LocalBusiness | ✅ | name, address, telephone, openingHoursSpecification |
| Organization | ✅ | name, url, logo, sameAs (social profiles), contactPoint |
| BreadcrumbList | ✅ | itemListElement (position, name, item) |
| Review | ✅ | itemReviewed, reviewRating, author. **Self-reviews запрещены — должны быть из independent reviewers** |
| VideoObject | ✅ | name, thumbnailUrl, uploadDate, duration |
| Course / LearningResource | ✅ | name, provider, courseInstance |
| JobPosting | ✅ | title, description, hiringOrganization |
| Dataset | ✅ | name, description, license |
| SoftwareApplication | ✅ | name, applicationCategory, operatingSystem, offers |

### Универсальные правила schema
- **Контент в schema должен быть видим на странице.** Google проверяет. Несоответствие = warning в Search Console.
- **FAQPage:** все вопросы из schema **обязаны** быть видимы пользователю в `<details>` / `<dl>` / `<h>`-секциях.
- **Review schema на самом сайте:** только real, third-party reviews. Self-reviews → manual action.
- **JSON-LD предпочтительнее** microdata / RDFa.

### Чекать
- Google Rich Results Test (`search.google.com/test/rich-results`) — лучший валидатор.
- Schema.org Validator (`validator.schema.org`) — общая валидация.
- В Search Console → Enhancement report.

---

## 11. Hreflang rules

**Формат:** `<link rel="alternate" hreflang="LANG-REGION" href="URL">`

- **LANG:** ISO 639-1 (2 буквы): `en`, `ru`, `uk`, `de`, `fr`.
- **REGION** (опционально): ISO 3166-1 alpha-2 (2 буквы): `US`, `UA`, `DE`, `GB`. **С дефисом, не подчёркиванием.**
- **x-default:** для дефолтного fallback ("когда не знаем какой регион — отправляй сюда").

### Правила
1. **Reciprocal:** если A ссылается на B как alternate, B должен ссылаться на A.
2. **Self-referencing:** каждая страница должна иметь hreflang на саму себя.
3. **Absolute URLs:** не относительные.
4. **Один canonical на cluster:** все hreflang-варианты делят canonical между собой (canonical = self).
5. **Хорошие пары:**
   - `en` (просто язык, любой регион) — самый широкий.
   - `en-US` (английский для США) — конкретный регион.
   - `en-GB` — английский UK.
   - **`ru-UA`** (русский в Украине) и **`uk-UA`** (украинский в Украине) — типичный кейс UA-проектов.

### Не делать
- `ua` как код языка — это страна, не язык. **uk** = украинский язык.
- `uk_UA` (подчёркивание) — Google требует дефис.
- Hreflang на 404 / noindex / redirect-страницы.
- Hreflang только на одной стороне (без реципрокции).

### Имплементация
- **HTML head:** `<link rel="alternate">` на каждой странице (стандарт).
- **HTTP header:** `Link: <URL>; rel="alternate"; hreflang="X"` (для non-HTML — PDF, изображения).
- **XML sitemap:** `<xhtml:link>` внутри `<url>` (масштабируется, но валидация сложнее).

Только одна имплементация — не дублировать в трёх местах.

---

## 12. JavaScript SEO

Google рендерит JS через Web Rendering Service (WRS), сейчас на базе Chromium 100+.

### Что работает
- Client-side rendering (CSR) — Google рендерит, но **с задержкой** (renders happen после initial crawl).
- Dynamic content via JS — индексируется.
- React, Vue, Angular SPA — поддерживаются.

### Что НЕ работает / плохо
- **Soft 404:** SPA возвращает 200 для несуществующего URL с «Not Found» текстом. Google индексирует как тонкую страницу.
  - Фикс: возвращай 404 HTTP-статус для несуществующего, либо `<meta name="robots" content="noindex">` для not-found views.
- **Lazy-rendered content внутри `<details closed>` или больших скроллах** — Google всё равно индексирует (mobile-first crawler видит весь DOM).
- **Контент за JS-event (нужен click)** — может не быть проиндексирован. Используй SSR для критичного контента.
- **Бесконечный скролл без pagination URL** — Google не доскроллит. Используй infinite scroll + paginated URLs (`?page=2`).

### Best practice
- **SSR/SSG** для SEO-критичных страниц (главная, лендинги, ниши, статьи).
- **Hydration** для интерактивности после initial render.
- **Pre-rendering** через services типа Prerender.io как fallback.

---

## 13. Site reputation abuse — Parasite SEO (May 2024 policy)

**Новое в 2024:** Если на trusted-домене публикуется third-party контент, который ранкуется на back of домена, но не имеет отношения к основному назначению сайта — это **abuse**.

Примеры:
- Финансовое медиа разрешает третьим лицам публиковать «лучшие казино 2024» под /coupons/.
- Образовательный сайт продаёт раздел /reviews/ маркетологам.

### Что чекать в QA
- Если сайт имеет user-contributed sections (gostevye posts, comments, marketplace listings) — модерируются?
- /coupons/, /reviews/, /partners/ sub-sections — релевантны основной теме сайта?
- Footer-link sells, sidebar widget с unrelated affiliate links — risk.

---

## 14. URL structure / canonicalization

### Best practices
- **Descriptive URLs:** `/products/blue-shoes` лучше `/p?id=12345`.
- **Hyphens not underscores:** `blue-shoes` лучше `blue_shoes` (Google parsing).
- **Lowercase preferred:** избегает дубль-URL `Page` vs `page`.
- **Stable URLs:** не меняй без 301-редиректа.
- **Avoid deep nesting:** `/a/b/c/d/e/page` тяжело для crawl. Max 4-5 уровней.

### Canonical edge cases
- **Pagination:** `rel=next/prev` **deprecated в 2019**. Сейчас Google handles automatically. Каждая страница пагинации имеет self-canonical.
- **Filters / sorts:** `?color=blue&sort=price` — canonical обычно указывает на parameterless version, OR используй `noindex` для фильтр-комбинаций.
- **Trailing slash:** будь консистентен. `/page/` и `/page` — для Google разные URL (потенциально).
- **www vs non-www, http vs https:** один canonical форма, остальные → 301 редирект.

---

## 15. Search Console signals

### Coverage report
- **Indexed:** ОК.
- **Indexed, not submitted in sitemap:** Google нашёл сам — добавь в sitemap.
- **Submitted, not indexed:** Google решил не индексировать. Reasons: thin, duplicate, low quality, soft 404. Каждую категорию надо разбирать.
- **Excluded (Crawled — currently not indexed):** Google знает страницу, но не считает достойной индексации. Часто = quality issue.
- **Discovered — currently not indexed:** Crawl budget — Google знает URL но не зашёл. Wait or improve internal linking.

### Manual actions
- **Most common:** Unnatural links, Thin content, Pure spam, User-generated spam.
- **Recovery:** Fix issue, submit Reconsideration Request.

### Page experience report
- Pass/Fail per URL based on Core Web Vitals + HTTPS + Mobile-Friendly + Safe Browsing + No Intrusive Interstitials.

---

## 16. AI Overviews / SGE / AI Search readiness (2024+)

### Что Google использует для AI Overview
- **Authoritative content** (высокий E-E-A-T).
- **Structured data** (FAQPage, Article).
- **Clear passage-level content** — короткие, само-достаточные абзацы.
- **Trusted citations** — реальные источники с линками.

### Optimization
- **Conversational structure:** Q+A формат, Что/Как/Когда заголовки.
- **Direct answers первые 50-100 слов абзаца.**
- **Skimmable formatting:** короткие параграфы, списки, табы.
- **llms.txt** (новый стандарт 2024) — даёт AI краулерам структурированный гид.
- **Open access:** позволь GPTBot, ClaudeBot, PerplexityBot в robots.txt (если хочешь AI-цитирования).

---

## Quick checklist для qa-* агентов

При проверке любой публичной страницы — пробежись по этим высокоприоритетным правилам:

- [ ] robots.txt → 200, Sitemap указан
- [ ] Self-canonical, абсолютный HTTPS URL
- [ ] viewport meta, без user-scalable=no
- [ ] `<html lang>` соответствует контенту
- [ ] Hreflang: self + alt + x-default, реципрокно, формат `lang-REGION` с дефисом
- [ ] CWV target: LCP ≤2.5s, INP ≤200ms, CLS ≤0.1
- [ ] HTTPS, mixed content отсутствует
- [ ] Schema совпадает с visible content
- [ ] FAQPage Q+A видимы на странице
- [ ] Title 50-60 chars, unique, без keyword stuffing
- [ ] Meta description 70-160 chars, unique
- [ ] H1 ровно один на странице
- [ ] Картинки с width/height (CLS) + alt
- [ ] Внутренние ссылки на final URLs (не через redirect)
- [ ] Sitemap содержит только canonical, indexable URLs
- [ ] Нет hidden text / cloaking / doorway patterns
- [ ] Helpful Content: страница даёт unique value, не просто шаблон
- [ ] E-E-A-T: автор/owner info, контакты, дата published/modified
