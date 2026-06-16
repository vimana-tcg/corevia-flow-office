#!/usr/bin/env bash
# scan-secrets.sh — секрет-страж. Падает (exit 1), если в репо найдены ключи,
# приватные данные или упоминания внутренних бизнесов/инфраструктуры.
# Запускается вручную ПЕРЕД пушем и как pre-commit хук (scripts/install-git-hooks.sh).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Файлы под контролем: tracked + новые, но БЕЗ .gitignored (.env) и без самого сканера
FILES=$(git ls-files -co --exclude-standard 2>/dev/null | grep -v 'scripts/scan-secrets.sh' || find . -type f -not -path './.git/*' -not -name 'scan-secrets.sh')

# Паттерны секретов и приватных данных
declare -a PATTERNS=(
  'r8_[A-Za-z0-9]{20,}'                       # Replicate
  'sk-[A-Za-z0-9]{20,}'                       # OpenAI
  'sk-ant-[A-Za-z0-9-]{20,}'                  # Anthropic
  'AIza[0-9A-Za-z_-]{30,}'                    # Google
  'xi-api[-_]?key'                            # ElevenLabs (header)
  'EAA[A-Za-z0-9]{20,}'                       # Meta long-lived token
  'ghp_[A-Za-z0-9]{30,}'                      # GitHub PAT
  'xoxb-[A-Za-z0-9-]{10,}'                    # Slack
  'AKIA[0-9A-Z]{16}'                          # AWS
  '-----BEGIN [A-Z ]*PRIVATE KEY-----'        # private keys
  '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b'           # any IPv4 (наши VPS)
)
# Упоминания НАШИХ бизнесов/инфраструктуры (не должны попасть в публичный набор)
declare -a FORBIDDEN_WORDS=(
  'gemalli' 'gemalliclaw' 'osktrade' 'osktrade' 'bulldozer\.uno' 'oсктрейд'
  'kwom' 'sl-claw' 'sl_claw' 'vimanaltd' 'luxpromo' 'coreviaflow\.space'
  'corevia-vps' 'contabo_corevia' 'agent-marketolog-montazher' 'token-platform'
  '/opt/' 'korogodskyi' 'm\.korogodskyi'
)

fail=0
echo "🔎 scan-secrets: проверяю $(echo "$FILES" | wc -l | tr -d ' ') файлов…"
for pat in "${PATTERNS[@]}"; do
  hits=$(echo "$FILES" | xargs grep -nEI "$pat" 2>/dev/null | grep -v '\.env\.example' || true)
  if [ -n "$hits" ]; then echo "❌ СЕКРЕТ/IP [$pat]:"; echo "$hits" | head -5; fail=1; fi
done
for w in "${FORBIDDEN_WORDS[@]}"; do
  hits=$(echo "$FILES" | xargs grep -niEI "$w" 2>/dev/null || true)
  if [ -n "$hits" ]; then echo "❌ УПОМИНАНИЕ БИЗНЕСА/ИНФРЫ [$w]:"; echo "$hits" | head -5; fail=1; fi
done

if [ "$fail" -eq 0 ]; then
  echo "✅ Чисто: секретов и упоминаний внутренних бизнесов не найдено."
else
  echo ""
  echo "🛑 НЕ ПУШИТЬ. Удалите найденное выше, затем повторите scan."
fi
exit $fail
