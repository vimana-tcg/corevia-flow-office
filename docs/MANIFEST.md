# Манифест состава (что включаем в публичный набор)

Принцип: только **горизонтальные** (универсальные) команды. Всё бизнес-специфичное и
персональные данные — ИСКЛЮЧАЕМ. Каждый включённый агент перед коммитом проходит
генерикизацию (убрать упоминания конкретных бизнесов/инфраструктуры) + секрет-страж.

## ✅ ВКЛЮЧАЕМ (горизонтальные, после генерикизации)
**Продукт:** pm-product-manager, pm-analytics, pm-conversation-intel, pm-growth,
pm-niche-scout, pm-content-strategist, pm-research
**Маркетинг/SMM:** brand-director, content-strategist-personal, smm-orchestrator,
paid-ads-manager, marketing-email, publishing-automation, engagement-manager
**Контент:** content-writer-social, content-writer-longform, content-researcher,
carousel-designer, video-creator-shorts
**Дизайн:** web-designer, motion-designer  (+ скилл ui-ux-pro-max, frontend-design)
**SEO:** все seo-* (technical, content, geo, schema, sitemap, backlinks, local, cluster…)
**Финансы:** fin-cfo, fin-director, fin-bookkeeper, fin-runway, fin-saas-metrics
**Безопасность:** oss-vetter  (+ скилл security-review)
**QA:** все qa-* (functional, edge, security, performance, a11y, i18n, content, data…)
**Продажи (универс.):** sales-head, office-sales, office-account-manager,
office-onboarding, office-buyer-intel, office-director
**Инфра (универс.):** infra-dns, infra-email-deliverability  (server-admin — генерикизировать VPS)
**Поддержка/право:** customer-support, legal-counsel
**Мета:** agent-mentor, memory-keeper (генерикизировать), prompt-curator, tech-director, founder-coach
**Ключевые скиллы:** setup, doctor (наши), ad-creative-studio, content-article,
qa-team, pm-team, seo-audit, и сопутствующие.

## ❌ ИСКЛЮЧАЕМ (бизнес-специфика / персональное / рискованное)
- Любые **вертикально-нишевые** агенты/скиллы конкретного бизнеса (напр. отраслевые
  инженеры-диагносты, агенты под конкретный маркетплейс/площадку объявлений, онбординг
  страниц конкретного продукта) — они бесполезны вне своего бизнеса.
- Любые **именные sales-боты** конкретных проектов и их персональные настройки.
- **Менторы-«реальные-личности»** — заменить на обобщённые роли
  («marketing-mentor / sales-mentor / strategy-mentor») БЕЗ имён реальных людей, либо исключить.
- Любые файлы памяти проектов, внутренний «Хаб», facts/CLAUDE/global-memory владельца,
  настройки продавцов, любые `.env`, ключи, IP-адреса, абсолютные серверные пути.

> Конкретные имена наших внутренних бизнесов здесь НЕ перечисляются намеренно — секрет-страж
> блокирует их попадание в публичный набор. Правило простое: **если агент знает про
> конкретный наш бизнес — он не едет в публичный набор.**

## Процесс генерикизации (на каждый включаемый файл)
1. Убрать упоминания брендов/доменов/городов наших бизнесов.
2. Заменить «Холдинг», конкретные проекты → нейтральное «ваш бизнес / проект».
3. Убрать абсолютные пути VPS, IP, ssh-алиасы, имена людей.
4. Ссылки на память Холдинга → на локальный профиль `.corevia/config.json` и `/setup`.
5. Прогнать `scripts/scan-secrets.sh` — должно быть чисто.
