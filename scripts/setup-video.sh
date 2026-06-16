#!/usr/bin/env bash
# setup-video.sh — мастер установки софта для видео-монтажа (простыми словами).
# Проверяет ffmpeg/ffprobe/python, подсказывает как поставить, проверяет шрифт.
# Ничего НЕ ставит сам без спроса — показывает команду и ждёт.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

say() { printf '%s\n' "$1"; }
have() { command -v "$1" >/dev/null 2>&1; }

say "🎬 Проверка софта для видео-монтажа"
say "────────────────────────────────────"

# --- ffmpeg / ffprobe (обязательно) ---
os=$(uname -s)
if have ffmpeg && have ffprobe; then
  say "  ✅ ffmpeg: $(ffmpeg -version 2>/dev/null | head -1 | cut -d' ' -f1-3)"
else
  say "  ⬜ ffmpeg НЕ найден — это главный движок монтажа. Установите:"
  case "$os" in
    Darwin) say "       brew install ffmpeg        # macOS (нужен Homebrew: brew.sh)";;
    Linux)  say "       sudo apt install ffmpeg    # Debian/Ubuntu";;
    *)      say "       скачайте с https://ffmpeg.org/download.html";;
  esac
  say "       (или статический бинарник в \$PATH). Потом запустите этот скрипт снова."
fi

# --- Python ---
if have python3; then say "  ✅ python3: $(python3 --version 2>&1 | cut -d' ' -f2)";
else say "  ⬜ python3 НЕ найден — нужен 3.10+. python.org/downloads"; fi

# --- Pillow (для обложек) ---
if python3 -c "import PIL" 2>/dev/null; then say "  ✅ Pillow (обложки)";
else say "  ⬜ Pillow — для обложек: pip3 install Pillow"; fi

# --- шрифт (идёт в комплекте) ---
if [ -f "$ROOT/skills/video-render-vertical/assets/fonts/Montserrat.ttf" ]; then
  say "  ✅ Шрифт Montserrat (в комплекте, кириллица)"
else
  say "  ⬜ Шрифт не найден в комплекте (странно) — положите .ttf в assets/fonts/"
fi

# --- опциональные ключи ---
say ""
say "Опционально (для озвучки/липсинка — НЕ нужно для базового монтажа):"
ENV="$ROOT/.env"
key() { [ -f "$ENV" ] && grep -qE "^$1=." "$ENV" 2>/dev/null && say "  ✅ $2" || say "  ⬜ $2 (по желанию)"; }
key REPLICATE_API_TOKEN "Replicate — вырезка фона у лица (обложки)"
key ELEVENLABS_API_KEY "ElevenLabs — озвучка голосом"
key OPENAI_API_KEY "OpenAI — транскрипция (Whisper)"

say ""
say "Готово к монтажу, если выше ffmpeg + python3 + Pillow = ✅."
say "Команды: «нарежь видео», «сделай вертикальный ролик», «обложка». См. docs/COMMANDS.md."
