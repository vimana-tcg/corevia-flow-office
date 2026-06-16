#!/usr/bin/env bash
# check-update.sh — тихая проверка обновлений (раз в сутки). Если локальная версия
# отстала от GitHub — печатает короткое уведомление. Без телеметрии: только git к origin.
# Всегда exit 0, ничего не ломает, сеть ограничена по времени.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[ -d "$ROOT/.git" ] || exit 0
mkdir -p "$ROOT/.corevia"
STAMP="$ROOT/.corevia/.update_check"
now=$(date +%s 2>/dev/null || echo 0)
last=$(cat "$STAMP" 2>/dev/null || echo 0)
# троттлинг: проверяем не чаще раза в 24ч (чтобы не тормозить старт)
[ $((now - last)) -lt 86400 ] && exit 0
echo "$now" > "$STAMP" 2>/dev/null || true

# быстрый сетевой запрос с ограничением по времени (без полного fetch)
git -C "$ROOT" config --local http.lowSpeedLimit 1000 >/dev/null 2>&1 || true
git -C "$ROOT" config --local http.lowSpeedTime 6 >/dev/null 2>&1 || true
remote=$(git -C "$ROOT" ls-remote origin -h refs/heads/main 2>/dev/null | awk '{print $1}')
local=$(git -C "$ROOT" rev-parse HEAD 2>/dev/null)

if [ -n "$remote" ] && [ -n "$local" ] && [ "$remote" != "$local" ]; then
  echo "🔔 Доступно обновление Corevia Flow Office. Обнови: bash scripts/update.sh (потом перезапусти сессию)"
fi
exit 0
