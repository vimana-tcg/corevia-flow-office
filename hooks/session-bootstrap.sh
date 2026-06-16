#!/usr/bin/env bash
# session-bootstrap.sh — SessionStart. Если профиль не настроен → мягко зовём /setup.
# Контракт: читает stdin (игнор), всегда exit 0, печатает hookSpecificOutput.
set -euo pipefail
cat >/dev/null 2>&1 || true
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CFG="$ROOT/.corevia/config.json"
if [ -f "$CFG" ]; then
  name=$(grep -o '"user_name"[^,]*' "$CFG" 2>/dev/null | cut -d'"' -f4)
  ctx="Corevia Flow Office готов. Профиль: ${name:-есть}. Команды — docs/COMMANDS.md, проверка ключей — /doctor, примеры — /cases."
else
  ctx="Первый запуск Corevia Flow Office. Профиль не настроен → предложи пользователю команду /setup (мастер проведёт простыми словами: имя, бизнес, город, цель, подключение ключей API). Без /setup команды работать будут, но без ключей часть откажет."
fi
esc="${ctx//\"/\\\"}"
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$esc"
exit 0
