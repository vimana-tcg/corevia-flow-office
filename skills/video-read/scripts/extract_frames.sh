#!/usr/bin/env bash
# extract_frames.sh — РАСКАДРОВКА: вытаскивает кадры из видео, чтобы Claude мог их
# «прочитать» (посмотреть через Read) и понять, что на видео. Опц. контактный лист
# (все кадры в одной картинке-сетке) для быстрого обзора.
#
# Использование:
#   extract_frames.sh --video in.mp4 --out output/frames [--count 12] [--contact]
#   extract_frames.sh --video in.mp4 --out output/frames --every 5      # кадр каждые 5 сек
#
# ffmpeg берётся из $FFMPEG, иначе из PATH. Нет ffmpeg → подсказка про setup-video.sh.
set -euo pipefail
FFMPEG="${FFMPEG:-$(command -v ffmpeg || true)}"
FFPROBE="${FFPROBE:-$(command -v ffprobe || true)}"
VIDEO=""; OUT="output/frames"; COUNT=12; EVERY=""; CONTACT=0
while [ $# -gt 0 ]; do case "$1" in
  --video) VIDEO="$2"; shift 2;; --out) OUT="$2"; shift 2;;
  --count) COUNT="$2"; shift 2;; --every) EVERY="$2"; shift 2;;
  --contact) CONTACT=1; shift;; *) echo "неизвестный флаг: $1" >&2; exit 1;; esac; done

[ -n "$FFMPEG" ] || { echo "❌ ffmpeg не найден. Установите: bash scripts/setup-video.sh (или brew install ffmpeg)"; exit 2; }
[ -n "$VIDEO" ] && [ -f "$VIDEO" ] || { echo "❌ нет видео: $VIDEO"; exit 1; }
mkdir -p "$OUT"

if [ -n "$EVERY" ]; then
  # кадр каждые EVERY секунд
  "$FFMPEG" -hide_banner -loglevel error -i "$VIDEO" -vf "fps=1/$EVERY,scale=640:-1" "$OUT/frame_%03d.jpg"
else
  # COUNT равномерно распределённых кадров
  dur=$("$FFPROBE" -v error -show_entries format=duration -of default=nk=1:nw=1 "$VIDEO" 2>/dev/null | cut -d. -f1)
  dur=${dur:-0}
  if [ "$dur" -le 0 ]; then
    "$FFMPEG" -hide_banner -loglevel error -i "$VIDEO" -vf "fps=1,scale=640:-1" "$OUT/frame_%03d.jpg"
  else
    i=0
    while [ "$i" -lt "$COUNT" ]; do
      t=$(awk "BEGIN{printf \"%.2f\", $dur*($i+0.5)/$COUNT}")
      n=$(printf "%03d" "$i")
      "$FFMPEG" -hide_banner -loglevel error -ss "$t" -i "$VIDEO" -frames:v 1 -vf "scale=640:-1" "$OUT/frame_$n.jpg"
      i=$((i+1))
    done
  fi
fi

frames=$(ls "$OUT"/frame_*.jpg 2>/dev/null | wc -l | tr -d ' ')
echo "✅ кадров извлечено: $frames → $OUT/frame_*.jpg"

if [ "$CONTACT" -eq 1 ] && [ "$frames" -gt 0 ]; then
  cols=4; rows=$(( (frames + cols - 1) / cols ))
  "$FFMPEG" -hide_banner -loglevel error -pattern_type glob -i "$OUT/frame_*.jpg" \
    -filter_complex "tile=${cols}x${rows}" -frames:v 1 "$OUT/contact_sheet.jpg" 2>/dev/null \
    && echo "🗂  контактный лист: $OUT/contact_sheet.jpg (открой/Read его — обзор всего видео одной картинкой)"
fi
echo "👉 Чтобы «прочитать» видео: открой кадры ($OUT/frame_*.jpg) инструментом Read — Claude увидит, что на видео."
