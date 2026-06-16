#!/usr/bin/env bash
# doctor.sh — показывает, какие ключи подключены (из .env), без раскрытия значений.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV="$ROOT/.env"
[ -f "$ENV" ] || { echo "Нет .env. Запустите /setup или: cp .env.example .env"; exit 0; }

check() { # $1=имя переменной  $2=человеческое имя
  v=$(grep -E "^$1=" "$ENV" 2>/dev/null | cut -d= -f2- | tr -d ' "')
  if [ -n "$v" ]; then echo "  ✅ $2"; else echo "  ⬜ $2 — не подключено"; fi
}
echo "🩺 Состояние подключений Corevia Flow Office:"
echo "Мозг (LLM):"
check ANTHROPIC_API_KEY "Anthropic (Claude)"; check OPENAI_API_KEY "OpenAI"
echo "Медиа:"
check REPLICATE_API_TOKEN "Replicate"; check PEXELS_API_KEY "Pexels"; check GEMINI_API_KEY "Gemini"; check ELEVENLABS_API_KEY "ElevenLabs"
echo "Соцсети/реклама:"
check META_ACCESS_TOKEN "Meta (FB/IG)"; check YOUTUBE_REFRESH_TOKEN "YouTube"; check TIKTOK_CLIENT_KEY "TikTok"
echo ""
echo "ℹ️ Canva подключается как MCP (не ключом) — см. skills/setup/references/api-setup.md"
echo "Чего не хватает под вашу задачу — добавьте через /setup."
