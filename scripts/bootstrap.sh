#!/usr/bin/env bash
# bootstrap.sh — установка «в одну команду»: клонирует репо и подключает ВСЁ
# (всех агентов + все скиллы) к вашему Claude Code. Для новичков.
#
# Запуск одной строкой:
#   curl -fsSL https://raw.githubusercontent.com/vimana-tcg/corevia-flow-office/main/scripts/bootstrap.sh | bash
set -euo pipefail
REPO="https://github.com/vimana-tcg/corevia-flow-office.git"
DIR="${COREVIA_DIR:-$HOME/corevia-flow-office}"

echo "🏢 Corevia Flow Office — установка вашей AI-команды"
if [ -d "$DIR/.git" ]; then
  echo "↻ Уже скачано — обновляю ($DIR)…"; git -C "$DIR" pull --ff-only origin main || true
else
  echo "⬇️  Скачиваю в $DIR…"; git clone --depth 1 "$REPO" "$DIR"
fi
bash "$DIR/scripts/install.sh"
echo ""
echo "👉 Дальше: открой Claude Code в папке $DIR (или в любом своём проекте) и напиши:  /setup"
