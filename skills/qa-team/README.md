# QA Team — multi-profile orchestrated testing

Команда из 8 специалист-субагентов + skill-оркестратор. Запускается в параллель,
каждый специалист тестирует со своим углом зрения, оркестратор собирает находки в
один отчёт, применяет безопасные правки и предлагает остальное.

## Использование

```
/qa-team                              ← общий запуск, спросит target
/qa-team shop/n/restaurant-delivery   ← на конкретную папку
/qa-team https://example.com/         ← на живой URL
/qa-team security only                ← только один профиль
/qa-team last PR                      ← на текущий PR
```

Естественно-языковые триггеры (без слэша):
- «запусти команду тестировщиков»
- «найди баги»
- «команда qa проверь shop/»
- «test everything in this dir»

## Профили

| Профиль | Что ищет |
|---|---|
| 🎯 **qa-functional** | Соответствие фичи спеке: happy path, business logic, API-контракты, кнопки ведут куда обещают |
| 🧪 **qa-edge** | Null/empty/overflow/off-by-one/race/error-paths — ломаем happy path намеренно |
| 🔒 **qa-security** | OWASP Top-10: injection, broken auth, секреты в репо, CSRF, CVE, headers, cookie flags |
| ⚡ **qa-performance** | N+1, Big-O cliffs, blocking I/O, bundle size, Core Web Vitals (LCP/INP/CLS), кэш |
| ♿ **qa-a11y** | WCAG 2.2 AA, ARIA, клавиатура, контраст, alt, focus, мобильный zoom, reduced-motion |
| 📱 **qa-mobile** | Touch ≥44px, viewport, шрифт ≥16px, inputmode, safe-area, hover-only states |
| 🌍 **qa-i18n** | Полнота переводов, утечки языков (ru в uk), даты/числа/валюты, hreflang, lang-атрибуты |
| ✍️ **qa-content** | Опечатки, тон, битые ссылки, alt-качество, микрокопия, дубли, метаданные, шаблонные leak |
| 🔎 **qa-seo** | SEO-harm: кросс-страничные дубли, противоречия, ложные источники, stale dates, cannibalization, schema-vs-DOM, spam-паттерны |
| 📊 **qa-data** | Schema validation, типы, JSON/YAML парсинг, санитайз, миграции, целостность |
| 🔁 **qa-regression** | Что сломалось от недавних правок (git-diff aware): побочный ущерб, API-контракт, snapshot drift |
| 📦 **qa-deps** | Outdated/CVE/abandoned пакеты, lockfile sync, unused deps, лицензии, supply-chain |
| 💳 **qa-payments** | Stripe/LiqPay/Mono/Apple Pay: webhook signature+idempotency, currency minor units, 3DS/SCA, refunds, PCI hygiene, test-vs-live keys |
| 🚀 **qa-conversion** | **CRO-голос команды:** value-prop, CTA копия/видимость, trust-сигналы, checkout friction, social proof, scarcity-честность, противоречия между лендингом и реальностью продукта. Главный профиль для публичных страниц. |

## База знаний Google rules

`~/.claude/skills/qa-team/google-rules.md` — actionable reference (16 секций):
indexability, sitemaps, mobile-first, **Core Web Vitals 2026 (LCP≤2.5s · INP≤200ms · CLS≤0.1)**, page experience, **Helpful Content System** (core ranking signal с 2024), E-E-A-T (Experience/Expertise/Authoritativeness/Trustworthiness), **AI content policy** (включая Scaled Content Abuse 2024), **Spam Policies 2024** (включая Site Reputation Abuse / Parasite SEO), Rich Results / Schema, hreflang, JavaScript SEO, URL structure, Search Console signals, **AI Overviews readiness**.

7 агентов (seo, content, performance, mobile, i18n, a11y, conversion) обязаны прочитать релевантные секции перед работой — это прописано в их промптах. Обновление одного `google-rules.md` обновляет поведение всех 7.

## Дефолтные наборы по типу проекта

| Тип | Кого запускать |
|---|---|
| Web-лендинг / маркетинг | **conversion** · seo · content · a11y · mobile · i18n |
| Программатик-SEO / блог | seo · content · **conversion** · i18n · a11y |
| E-commerce / SaaS с биллингом | **conversion** · payments · functional · security · content · mobile |
| Pricing / checkout страница | **conversion** · payments · functional · a11y · mobile |
| Backend API / сервис | functional · edge · security · performance · data |
| CLI / библиотека | functional · edge · content · deps |
| Bugfix PR | regression · functional · edge (+security/payments при касании auth/денег) |
| Целевая проверка одного аспекта | один профиль |

**Правило:** для **публичных страниц** (любых, ради которых идёт трафик) `qa-conversion` обязателен — без него команда найдёт баги, но не то, что реально двигает деньги. На backend/CLI он не нужен.

Оркестратор сам выбирает набор. Можно переопределить: `/qa-team security only`.

## Что команда делает с находкой

- **Тривиальный безопасный фикс** (1-2 строки, очевидный) → агент сам применяет через `Edit`, помечает «applied»
- **Рискованный / большой** → агент предлагает, **не применяет**, выносит как «proposed»
- **Critical** (утечка секрета, упавший прод, security-дыра) → красным флагом наверху отчёта

## Severity

🔴 critical · 🟠 high · 🟡 medium · 🟢 low

## Файлы

- `~/.claude/skills/qa-team/SKILL.md` — оркестратор-промпт
- `~/.claude/agents/qa-{functional,edge,security,performance,a11y,i18n,content,data}.md` — 8 специалистов

## Расширение

Чтобы добавить ещё профиль (например, `qa-mobile` или `qa-regression`):
1. Создай `~/.claude/agents/qa-<name>.md` с frontmatter (`name`, `description`, `tools`, `model`)
2. Допиши его в раздел «Доступные профили» в `SKILL.md`
3. Опиши, когда оркестратор должен его подключать

## Похожие skill'ы (чем отличаются)

- `/qa` — линейный QA-проход с фиксами и коммитами, **один тестировщик**, делает всё сам
- `/qa-only` — то же что `/qa`, но без фиксов (report only)
- `/cso` — security audit (1 профиль глубже)
- `/design-review` — визуальный QA
- **`/qa-team` — параллельная команда с разными углами зрения, агрегацией и выборочным применением фиксов**

Используй `/qa-team`, когда хочешь быстрый широкий охват от 8 разных углов. Используй
`/qa` для линейной exhaustive проверки одного аспекта.

## Open-source inspiration

Команда собрана из публичных паттернов:
- Anthropic Cookbook subagent examples ([anthropics/anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook))
- OWASP Testing Guide 2024 для qa-security профиля
- WCAG 2.2 AA checklist для qa-a11y
- web.dev Core Web Vitals + Performance Patterns для qa-performance
- Patterns of multi-agent QA orchestration из community claude-code-templates
