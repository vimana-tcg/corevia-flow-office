# PM Team — Product Management команда

**7 субагентов** (6 специалистов + 1 research) + skill-оркестратор. В отличие
от `qa-team` (фиксит баги), `pm-team` отвечает на вопрос **«ЧТО строить и
почему»** — приоритеты, эксперименты, новые ниши, контент-планы.

## Запуск

```
/pm-team               ← Full strategic brief (все 6 + research)
/pm-team daily         ← Только pm-research → дип-сёрч мира → playbook updates
/pm-team weekly        ← Tactical adjustments (analytics + conv-intel)
/pm-team growth        ← Эксперименты (growth + analytics)
/pm-team niches        ← Новые ниши (niche-scout + conv-intel)
/pm-team content       ← SEO/content план (content-strategist + analytics)
/pm-team voice         ← Голос клиента (только conversation-intel)
```

Натуральные триггеры: «стратегия», «куда двигаем продукт», «что катить»,
«growth review», «новые ниши», «контент-план», «PM review».

## Команда

| Agent | Профиль | Tools |
|---|---|---|
| 🧠 **pm-product-manager** | Главный — roadmap, OKR, RICE/ICE, PRD, координация | Agent · Read · Edit · Write · AskUser |
| 📊 **pm-analytics** | GA4, GSC, Pixel, CRM, server-logs, payments | Read · Bash · WebFetch · Write |
| 💬 **pm-conversation-intel** | Анализ диалогов Дарины / sales-bots / CRM | Read · Bash · Grep · Write |
| 🚀 **pm-growth** | A/B-эксперименты, AARRR, growth loops, ICE | Read · Bash · Write · WebFetch |
| 🌍 **pm-niche-scout** | Новые ниши: demand + competition + fit + revenue | Read · WebSearch · WebFetch · Write |
| ✍️ **pm-content-strategist** | Topic clusters, internal linking, content calendar | Read · Bash · WebFetch · Write |
| 🔬 **pm-research** | Ежедневный дип-сёрч мира + auto-update playbooks | WebSearch · WebFetch · Read · Edit · Write |

## База знаний

- **`growth-playbook.md`** — actionable AARRR-тактики, growth loops, frameworks
- **`../qa-team/google-rules.md`** — Google rules (shared с qa-team)
- **`../../projects/<proj>/memory/team-knowledge/`** — долгосрочная межсессионная память

## Самоулучшающийся ежедневный цикл

```
Каждое утро:
  pm-research → дип-сёрч GitHub/Lenny's/HN/Indie Hackers →
  фильтр «применимо нам» → 2-3 находки →
  Edit growth-playbook.md / google-rules.md (с датой и источником) →
  Write team-knowledge/today-learned-YYYY-MM-DD.md

Раз в неделю:
  pm-research компактует daily → weekly-digest-YYYY-WW.md →
  старое чистится

После каждого крупного pm-team прохода:
  Write team-knowledge/latest-pm-brief.md →
  qa-team увидит на следующем прогоне (фокус на priority surfaces)

После каждого крупного qa-team прохода:
  Write team-knowledge/latest-qa-findings.md →
  pm-team увидит при следующем strategic review (учёт системных issues)
```

**Через `/schedule create` можно запустить ежедневный auto-run:**
```
/schedule create
  cron: 0 9 * * *
  prompt: /pm-team daily
```

## Файлы команды

```
~/.claude/skills/pm-team/
  ├ SKILL.md         ← оркестратор-промпт
  ├ README.md        ← этот файл
  └ growth-playbook.md  ← actionable тактики, обновляются pm-research

~/.claude/agents/
  ├ pm-product-manager.md
  ├ pm-analytics.md
  ├ pm-conversation-intel.md
  ├ pm-growth.md
  ├ pm-niche-scout.md
  ├ pm-content-strategist.md
  └ pm-research.md
```

## Открытые паттерны на которые опираемся

- **MetaGPT** (geekan/MetaGPT) — Product Manager роль с PRD-генерацией
- **CrewAI** (joaomdmoura/crewAI) — role-based multi-agent teams
- **AutoGen** (microsoft/autogen) — agent conversation framework
- **gpt-researcher** (assafelovic/gpt-researcher) — autonomous research patterns
- **mem0** (mem0ai/mem0) — долгосрочная память для агентов
- **Anthropic Cookbook** — agent skill examples

## Связка с qa-team

| Цикл | Команда | Когда |
|---|---|---|
| После большого коммита | qa-team | Auto-prompt из вашего project CLAUDE.md |
| Ежедневно (утро) | pm-research | Cron-job через `/schedule` (опционально) |
| Еженедельно | pm-team subset (analytics + conv-intel) | Понедельник или конец недели |
| Ежемесячно | pm-team full + qa-team comprehensive | Конец месяца → planning next |

Обе команды читают/пишут **shared memory** в `team-knowledge/` — учатся друг у друга.

## Похожие skill'ы (чем отличаемся)

- `/qa-team` — quality / bug-hunting (12 профилей) → ЧТО сломано
- `/pm-team` — strategy / growth / analysis (7 профилей) → **ЧТО строить и почему**
- `/seo-audit`, `/seo-technical` — точечный SEO-анализ → один аспект глубоко
- `/codex review` — second opinion на код → review одного diff'а
- `/office-hours` — brainstorm идеи перед кодом → форсирующие вопросы
- `/autoplan` — review плана → принять/изменить план

Когда что:
- Есть код → хочу qa → `/qa-team`
- Есть метрики, хочу понять что улучшить → `/pm-team`
- Есть идея, не знаю стоит ли делать → `/office-hours`
- Есть план, нужен review → `/autoplan`
