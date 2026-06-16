#!/usr/bin/env bash
# install.sh — подключает ВСЕХ агентов + ВСЕ скиллы набора к вашему Claude Code.
# Симлинки в ~/.claude (не копии — чтобы update.sh сразу обновлял). Идемпотентно.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE="$HOME/.claude"
mkdir -p "$CLAUDE/agents" "$CLAUDE/skills"

a=0; s=0
echo "🔗 Подключаю агентов…"
for f in "$ROOT"/agents/*.md; do [ -e "$f" ] && ln -sf "$f" "$CLAUDE/agents/$(basename "$f")" && a=$((a+1)); done
echo "🔗 Подключаю скиллы…"
for d in "$ROOT"/skills/*/; do [ -e "$d" ] && ln -sf "${d%/}" "$CLAUDE/skills/$(basename "$d")" && s=$((s+1)); done

# .env из примера, если нет
[ -f "$ROOT/.env" ] || { cp "$ROOT/.env.example" "$ROOT/.env"; echo "📄 Создан .env (заполните ключи или запустите /setup)"; }
# git-хук секрет-стража (если это git-репо)
bash "$ROOT/scripts/install-git-hooks.sh" 2>/dev/null || true

echo ""
echo "✅ Установлено: $a агентов + $s скиллов → ~/.claude/"
echo "────────────────────────────────────────────────────────"
echo "ВАЖНО: чтобы Claude «увидел» новых агентов — ПЕРЕЗАПУСТИ сессию"
echo "(агенты загружаются при старте). Скиллы доступны сразу."
echo ""
echo "👉 Первый шаг (мастер для новичка, простыми словами):  /setup"
echo "👉 Обзор и схемы «как всё работает»:                    /tour  (или docs/GUIDE.md)"
echo "👉 Что подключено из ключей:                            /doctor"
echo "👉 Какими словами что звать:                            docs/COMMANDS.md"
echo "👉 Обновления потом:                                    bash scripts/update.sh"
