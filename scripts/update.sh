#!/usr/bin/env bash
# update.sh — подтягивает свежую версию набора (обновления команд/скиллов).
# Работает и для форка (upstream), и для прямого клона (origin).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

UPSTREAM_URL="https://github.com/Corevia-Flow/corevia-flow-office.git"

# Если форк — добавим upstream один раз
if ! git remote | grep -q '^upstream$'; then
  if [ "$(git remote get-url origin 2>/dev/null)" != "$UPSTREAM_URL" ]; then
    git remote add upstream "$UPSTREAM_URL" 2>/dev/null || true
  fi
fi

REMOTE=upstream; git remote | grep -q '^upstream$' || REMOTE=origin
echo "⬇️  Тяну обновления из $REMOTE/main…"
git fetch "$REMOTE" --tags -q
git merge --ff-only "$REMOTE/main" 2>/dev/null || {
  echo "⚠️ Есть локальные правки — делаю rebase…"; git rebase "$REMOTE/main" || {
    echo "❌ Конфликт. Решите вручную или сделайте 'git stash' и повторите."; exit 1; }
}
echo "🔗 Переподключаю (на случай новых агентов/скиллов)…"
bash "$ROOT/scripts/install.sh" >/dev/null
echo "✅ Обновлено до $(git describe --tags --always 2>/dev/null). Список изменений — CHANGELOG.md"
