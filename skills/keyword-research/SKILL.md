---
name: keyword-research
description: >
  Подбор и ведение «банка ключевых слов» проекта с самоулучшением. Находит ключи
  (Google Autocomplete / People-Also-Ask / related / запросы Search Console / кластеризация
  по выдаче), сохраняет в файл проекта `keywords/<тема>.json` вместе с МИНУС-словами,
  дедуплицирует и НЕ предлагает то, что уже помечено как не сработавшее. Раз в неделю
  анализатор размечает ключи по реальным данным рекламы/SEO (winner/loser) и пополняет
  минус-слова. Подходит под запуск по расписанию (cron / /schedule).
  Use PROACTIVELY: «подбери ключевые слова», «keyword research», «семантика», «ключи под
  тему», «минус-слова», «банк ключей», «какие слова работают», «обнови ключи», «KWords».
user-invokable: true
---

# Keyword Research — банк ключей с ежедневным сбором и недельным вердиктом

Закрывает полный цикл: **найти → сохранить в файл проекта → разметить по результатам →
исключить мусор (минус-слова) → расти вокруг работающего**. Подробные правила (включая
поведение при запуске по таймеру) — `references/operating-rules.md`.

## Шаг 0 — найти/создать банк
Банк живёт в `keywords/<тема>.json` в корне проекта. Если нет — создай:
```bash
python3 scripts/keyword_bank.py init --bank keywords/<тема>.json --topic "<тема>" --locale <ru|uk|en>
```
Загрузи активные ключи + **минус-слова** (`negatives`). Минус-слова НИКОГДА не предлагать.

## Сбор ключей (ежедневно — дёшево)
1. Возьми seed (тема + текущие winner-ключи из банка).
2. Расширь: Google Autocomplete, «People Also Ask», related searches (WebSearch/WebFetch),
   новые запросы из Search Console (если подключён GSC), кластеризация — через `@seo-cluster`.
   Точные объёмы/сложность — через `@seo-dataforseo` (если есть DataForSEO).
3. Запиши новые (дедуп + отсев минус-слов делает скрипт):
```bash
python3 scripts/keyword_bank.py add --bank keywords/<тема>.json \
  --keywords-json '[{"keyword":"...","source":"autocomplete","intent":"commercial","cluster":"..."}]'
```

## Вердикт (раз в неделю — нужна статзначимость) → агент `@keyword-performance-analyzer`
Собери метрики по ключам (Meta Ads таргет-термы + GSC impressions/clicks/conversions) в
`metrics.json`, затем:
```bash
python3 scripts/mark_performance.py --bank keywords/<тема>.json --metrics metrics.json --auto-negative
```
→ размечает 🏆winner / 🚫loser / ⏳active; явные loser'ы уходят в минус-слова.

## Использование результата
- winner-ключи → брифы `@seo-content-brief` / статьи `content-article` + новые seed.
- минус-слова → `@paid-ads-manager` исключает их из кампаний; контент по ним не делаем.
- статус банка: `python3 scripts/keyword_bank.py stats --bank keywords/<тема>.json`.

## Запуск по расписанию
Поставь два задания (см. operating-rules.md):
- ЕЖЕДНЕВНО: сбор новых кандидатов (этот скилл).
- ЕЖЕНЕДЕЛЬНО: вердикт (`@keyword-performance-analyzer`).
Заводится через `/schedule` (облачный агент) или cron. Минус: дневной вердикт = шум, не делать.

## Что НЕ делать
- ❌ Не предлагать/не добавлять ключи из `negatives`.
- ❌ Не выносить вердикт по дневным данным (мало сигнала).
- ❌ Не хардкодить ключи API — GSC/DataForSEO/Meta берутся из `.env`/конфига проекта.

## Связи
`@seo-cluster` (расширение), `@seo-dataforseo` (метрики), `@keyword-performance-analyzer`
(вердикт), `@seo-content-brief`/`content-article` (применение), `@paid-ads-manager`/`@pm-analytics` (данные).
