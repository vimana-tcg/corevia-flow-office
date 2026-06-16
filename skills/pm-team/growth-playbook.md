# Growth Playbook — actionable tactics

Версия: 2026-05. Поддерживается `pm-research` (ежедневные обновления) +
ручные правки PM-команды. Каждое добавление помечается датой и источником.

**Источники паттернов:** First Round Review, Lenny's Newsletter, Andrew Chen,
GrowthHackers community, Reforge, Indie Hackers founder stories, собственная
conversation-intel из ваших ботов.

---

## Принципы (применяй ко ВСЕМУ)

1. **Loops > funnels.** Funnels leaky, loops compound. Каждое усилие проектируй
   как inputs для следующей итерации.
2. **One bottleneck at a time.** AAARRR не балансируется — самое узкое место
   определяет throughput. Фокус.
3. **Experiments > opinions.** Decisions без hypothesis + success criteria = «попробуем».
4. **Talk to users weekly.** Conversation insights бьют дашборды на early-stage.
5. **Compound > spike.** Один работающий канал на 3 года > 5 каналов на месяц.

---

## AARRR tactics

### A1. Awareness — пользователи знают что мы существуем

**Что работает:**
- **SEO-first programmatic content** — масштабно если ниша имеет много queries.
  *Пример:* N ниш × M тем = 1000s posts (программатик-контент).
- **Public success stories** — case studies с реальными цифрами.
  *Tactic:* Каждый платящий клиент = candidate для story после 30 дней.
- **Founder content на Linkedin/Twitter** — для B2B особенно. Personal brand → company brand.
- **Free tool/resource как трафиковый магнит** — калькулятор, шаблон, чек-лист.
  *Пример идеи:* «Калькулятор окупаемости» на сайте.
- **Podcast appearance** — таргетный B2B аудитория слушает.

**Что НЕ работает (опровергнуто):**
- Generic content marketing «о тенденциях» — никто не читает, не ранкуется
- Press releases — никто не читает
- Reddit/HN-стелс маркетинг — палится, банит сообщество

### A2. Acquisition — приходят на сайт / в продукт

**Working channels (по убыванию ROI для B2B SaaS):**
1. **Organic search** — самый высокий LTV/CAC ratio долгосрочно. Долгий time-to-result (3-6 мес).
2. **Direct word-of-mouth** — нужен NPS ≥40 и активная community.
3. **Paid Search (Google Ads)** — bottom-funnel queries только («купить X», «X review»).
   Не TOFU — слив бюджета.
4. **Meta / LinkedIn Ads** — для visual или high-intent verticals. ROI volatile.
5. **Partnerships / integrations** — co-marketing, cross-promotion.
6. **Affiliate / Influencer** — нишевые с реальной аудиторией ≥10k.
7. **Outreach (cold email / LinkedIn DM)** — работает для high-LTV clients (>$5k LTV).
   *Применимо у нас:* если outreach machine уже есть.

**Эксперимент-патерны:**
- **Targeted landing per channel** — utm-aware landings конвертят лучше generic.
- **Geo-targeted ads** — для marketplaces. UA-only ads → UA-specific landing.
- **Retargeting сегментирован по depth** — visited pricing но не checkout = одна аудитория, visited checkout но не paid = другая.

### A3. Activation — первое полезное действие

**Activation events** для разных моделей:
- **SaaS:** signup → first project created → invite teammate.
- **Marketplace:** visited niche page → opened consultation widget → submitted lead.
- **API/dev tool:** signed up → first successful API call → integrated.

**Что работает:**
- **Reduce signup friction** — Google/Apple sign-in, minimal form fields, email-only (не «name + company + role»).
- **Time-to-value <5 min** — пользователь должен получить «aha» в первые 5 минут.
- **Guided onboarding** — checklist «complete to unlock value».
- **Use-case templates** — стартовые шаблоны для разных JTBD.
- **Demo data** — пре-загруженный example, чтоб увидеть результат сразу.

**Activation для marketplace (пример):**
- Открытая консультация через бота — типичный activation event
- Можно тестировать: «Попробовать бота в чате 5 минут» — interactive demo before commit
- Тестировать: «Скачать sample-deal-report по своей нише» (free → contact info → email follow-up)

### A4. Retention — возвращаются

**Habit-формирующие механики:**
- **Hooks (Eyal):** Trigger → Action → Variable reward → Investment.
- **Lifecycle emails:** post-onboarding серия 7-30 дней. Содержит useful tips не promo.
- **In-app notifications** — для recurring use-cases.
- **Status emails** — weekly digest «вот что произошло за неделю».

**Для SaaS marketplace:**
- После первой покупки: 24h «welcome» с onboarding-видео
- Day 3: «вот как другие клиенты в вашей нише настроили бота» (success story)
- Day 14: «бот собрал X лидов за 2 недели» (proof of value)
- Day 30: NPS survey + offer upgrade to higher tier

**Что НЕ работает:**
- Spammy emails (>3/неделя) → unsubscribe
- Push без personalization
- «We miss you» серия — выглядит desperate

### A5. Revenue — платят и платят больше

**Pricing патерны:**
- **3 tiers** > 2 или 4 (decoy effect делает middle anchor).
- **Annual discount** (если SaaS): 15-20% типичный, поднимает LTV.
- **Mid-tier sweet spot** — обычно среднее «Most popular» с buyback features.
- **Per-seat vs flat pricing** — per-seat scales с компанией, flat — predictable для buyer.

**ARPU growth tactics:**
- **Usage-based add-ons** (для B2B): N сообщений в месяц, X интеграций.
- **Premium support** SLA — для enterprise tier.
- **Customization** — индивидуальные tweaks как paid add-on.

**Пример для marketplace:**
- Текущая структура (пример): $249/$449/$499 (Pro со скидкой).
- Test: добавить «Setup-with-experts +$200» — guided onboarding как up-sell
- Test: «Дополнительная позиция +$149» — для клиентов с multi-сегмент бизнесом
- Test: annual prepayment с 20% дисконтом для long-tail клиентов

### A6. Referral — приводят других

**Виральный коэффициент k = invites_per_user × conversion_rate**

Для B2B realistic k = 0.3-0.5 (не expential, но meaningful supplement).

**Что работает:**
- **Both-side rewards** («Give $50, Get $50») — лучше one-side
- **Frictionless invite** — pre-filled email, shareable URL
- **Public success metrics** в продукте — стимулирует sharing
- **Affiliate program** — 20% recurring commission для professional аффилиатов

**Пример:**
- Скидка $50 для рефералера + $50 для referee — простой start
- White-label опция для агентств — они переупаковывают продукт клиентам (revenue share)
- Public «hall of customers» с opt-in — социальное доказательство + ego boost

---

## Growth Loops (готовые patterns)

### Content Loop
```
SEO статья →  organic traffic → email capture →
лиды → продажи → success story →
новые SEO-tема + social → больше traffic
```
*Применимо у нас прямо сейчас:* посты блога → лиды → success stories → новые посты.

### Product Loop
```
клиент покупает бота → бот пишет в CRM → клиент видит результат →
показывает коллегам / партнёрам → они спрашивают → продажа
```
*Активировать:* добавить «share my results» в дашборд после первого месяца.

### Outreach Loop
```
cold email → reply → персональная демо → продажа →
case study →  данные для следующих cold emails (proof) →
лучшая conversion на cold
```

### Marketplace Loop
```
больше ниш → больше organic SEO traffic →
больше leads → больше клиентов в разных нишах →
больше success stories → авторитет в индустрии →
выше ranking → больше traffic
```

---

## Frameworks

### North Star Metric (NSM)
Одна метрика отражает ценность продукта для пользователя.

**Хорошая NSM:** 
- Корелирует с долгосрочной выручкой
- Отражает delivered value
- Усилия команды двигают её

**Пример NSM:** Active paying clients × ARPU × Retention rate (proxy: MRR)

### RICE / ICE для приоритизации
Описаны в `pm-product-manager.md`. Использовать ВСЕГДА для сравнения инициатив.

### Sean Ellis PMF test
«How would you feel if you could no longer use this product?» — если ≥40% «very disappointed», у нас PMF.

### Jobs to Be Done (JTBD)
Формулируй features как «when [situation], i want [motivation], so that [outcome]».

### AARRR (covered в основной секции)

---

## Anti-patterns (что НЕ делать)

- **Feature factory** — катить фичи без data/research-обоснования
- **Vanity metrics** — pageviews / signups без conversion / retention
- **Premature optimization** — стартап ≠ Google scale, не нужны kubernetes на 100 пользователей
- **Dark patterns** — fake scarcity, fake countdowns, hidden costs. Краткосрочный лифт, долгосрочный убыток
- **AI-generated mass content** — нарушает Helpful Content + Scaled Content Abuse (Google 2024 policy)
- **Stealth marketing на форумах** — банит сообщество, токсично

---

## Industry-specific (AI sales agents / programmatic SEO marketplace)

### Что работает в этом сегменте (наблюдения 2025-2026):
- **Готовый product** > custom build — клиенты хотят turnkey, не «build with us»
- **Per-niche personalization** — generic AI бот не продаёт, нишевая экспертиза продаёт
- **Lokal-language fluency** — українська/російська/польська для CEE стран критична
- **Bot voice (TTS+STT)** — повышает trust и conversion vs text-only в некоторых нишах (e.g., колл-центр replacement)
- **CRM integration first** — без HubSpot/Pipedrive/Bitrix/SalesDrive бот «сирота»

### Что НЕ работает:
- **Generic «AI for everyone» messaging** — конверсия низкая, бренд размыт
- **High-stakes verticals** без compliance (медицина, юр.услуги, инвестиции) — отказы + reputation risk
- **Слишком сложный onboarding** (>1 час) для marketplace SKU — клиент уйдёт обратно к менеджеру

---

## Versioning / changelog

<!-- pm-research добавляет deltas сюда (один-два раза в неделю компактует выше в секции) -->

### 2026-05-26
- Initial playbook v1.0 — base patterns from PM/growth canonical sources.
