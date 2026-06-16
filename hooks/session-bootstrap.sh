#!/usr/bin/env bash
# session-bootstrap.sh — SessionStart. Богатое приветствие: новичка сразу ведём в тур+setup.
set -euo pipefail
cat >/dev/null 2>&1 || true
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CFG="$ROOT/.corevia/config.json"
na=$(ls "$ROOT"/agents/*.md 2>/dev/null | wc -l | tr -d ' ')
ns=$(ls -d "$ROOT"/skills/*/ 2>/dev/null | wc -l | tr -d ' ')
if [ -f "$CFG" ]; then
  name=$(grep -o '"user_name"[^,]*' "$CFG" 2>/dev/null | cut -d'"' -f4)
  ctx="Corevia Flow Office: ${na} агентов + ${ns} скиллов готовы. Привет, ${name:-владелец}! Пиши задачу словами — нужный отдел сделает. Не знаешь кого звать — /tour или «кто у меня есть». Команды — docs/COMMANDS.md, ключи — /doctor."
else
  ctx="Это Corevia Flow Office — AI-команда в коробке (${na} агентов + ${ns} скиллов). НОВИЧОК: проведи его сразу — предложи (1) /tour (объяснить простыми словами как всё работает + схемы из docs/GUIDE.md), затем (2) /setup (подключить ключи под цель). Пиши задачи обычными словами; не знает кого звать — пусть спросит «как это работает» или «кто у меня есть». Кода знать НЕ нужно."
fi
esc="${ctx//\"/\\\"}"
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$esc"
exit 0
