#!/usr/bin/env bash
# install-git-hooks.sh — ставит pre-commit, который запускает секрет-страж.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK="$ROOT/.git/hooks/pre-commit"
[ -d "$ROOT/.git" ] || { echo "не git-репо, пропускаю"; exit 0; }
cat > "$HOOK" <<'EOF'
#!/usr/bin/env bash
ROOT="$(git rev-parse --show-toplevel)"
bash "$ROOT/scripts/scan-secrets.sh" || {
  echo "🛑 Коммит отменён секрет-стражем (см. выше)."; exit 1; }
EOF
chmod +x "$HOOK"
echo "✅ pre-commit секрет-страж установлен."
