#!/usr/bin/env bash
# install.sh — подключает агентов/скиллы/хуки набора к вашему Claude Code.
# Делает симлинки в ~/.claude (не копии — чтобы update.sh сразу обновлял).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE="$HOME/.claude"
mkdir -p "$CLAUDE/agents" "$CLAUDE/skills"

echo "🔗 Подключаю агентов…"
for f in "$ROOT"/agents/*.md; do [ -e "$f" ] && ln -sf "$f" "$CLAUDE/agents/$(basename "$f")"; done

echo "🔗 Подключаю скиллы…"
for d in "$ROOT"/skills/*/; do [ -e "$d" ] && ln -sf "${d%/}" "$CLAUDE/skills/$(basename "$d")"; done

# .env из примера, если нет
[ -f "$ROOT/.env" ] || { cp "$ROOT/.env.example" "$ROOT/.env"; echo "📄 Создан .env (заполните ключи или запустите /setup)"; }

# git-хук секрет-стража
bash "$ROOT/scripts/install-git-hooks.sh" 2>/dev/null || true

echo ""
echo "✅ Готово. Откройте Claude Code в этой папке и напишите:  /setup"
echo "   Проверить подключения:  /doctor    Команды:  docs/COMMANDS.md"
