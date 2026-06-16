---
name: video-render-vertical
description: |
  Движок монтажа вертикальных 9:16 шорт-видео для TikTok / Instagram Reels /
  YouTube Shorts. На вход — TTS mp3 + Whisper транскрипт + cut plan (визуальные
  моменты на фразу). На выход — готовый 1080×1920 mp4 с phrase-sync субтитрами,
  freeze frames для статики + live segments для money shots, blur-фоном по краям,
  студийным аудио (-16 LUFS).
  Use when user says: "собери шорт", "смонтируй 9:16", "vertical render",
  "phrase-sync субтитры", "video render", "монтаж из mp3 и видео".
allowed-tools:
  - Read
  - Bash
  - Edit
  - Write
---

# Video Render Vertical

Финальный монтаж 9:16 шорта из (TTS аудио + screencast + транскрипт + cut plan).

## Когда брать

Когда уже есть:
- mp3 с голосом (любой TTS или ручной)
- Whisper word-level транскрипт этого mp3
- Source видео (screencast .mov)
- Cut plan: для каждой фразы — `(video_id, timestamp, mode='freeze'|'live')`

## Калибровка

| Параметр | Значение |
|---|---|
| Resolution | **1080×1920** (9:16) |
| FPS | 30 |
| Codec | h264 crf=20 preset=medium |
| Шрифт | бандл `assets/fonts/Montserrat.ttf` (относительно скилла) |
| Цвет сабов | `#F9A825` (золотой) + чёрная обводка 3px |
| Позиция сабов | y ≈ 1320 (выше social UI 270-330px) |
| Размер шрифта | 68px дефолт, авто-shrink до 54px |
| Перенос | до 3 строк, авто-wrap по chars |
| Loudness | -16 LUFS broadcast |

ffmpeg/ffprobe берутся из `PATH` (переопределяются `FFMPEG_BIN` / `FFPROBE_BIN`).

## Структура проекта (workdir)

```
output/<тема>/
  source/            <video_id>.mov          (исходники)
  tts/               <reel_id>.mp3           (озвучка)
  transcripts/tts/   <reel_id>.json          (Whisper word-level)
  scripts/cut_plan.json                      (cut plan, см. ниже)
  final/             (сырой рендер)
  final_polished/    (после polish_audio.py)
```

## Использование

```bash
# 1. транскрибировать озвучку (OPENAI_API_KEY из env или .env)
python3 tools/transcribe_tts.py --workdir output/my_video

# 2. собрать ролик(и)
python3 tools/montage.py --workdir output/my_video r1_short

# 3. отполировать звук
python3 tools/polish_audio.py --workdir output/my_video r1_short
```

## Cut plan структура

В `<workdir>/scripts/cut_plan.json`:
```json
{
  "r1_short": {
    "phrase_sync": true,
    "visuals": [
      ["v1", 10, "freeze"],
      ["v1", 148, "freeze"],
      ["v1", 502, "live"]
    ]
  }
}
```

Количество элементов = количество Whisper segments. Альтернативный legacy-формат —
список `["video_id", start_sec, end_sec, "subtitle text"]` в поле `segments`.

## Режимы visual'а

### `freeze` — для статики
- Один кадр (PNG) с timestamp ts
- Loop'нут на phrase_dur
- Без speedup → не мельтешит, всё видно
- Идеально для: коротких фраз, таблиц, скриншотов кода

### `live` — для money shots
- Реальный кусок видео `[ts : ts+phrase_dur]`
- 1.0x скорость (no speedup)
- Идеально для: появления цифры/результата, скролла, любого действия

## Sync фикс (КРИТИЧНО)

Каждый segment длится **до начала следующей фразы** в TTS (не до конца текущей):
```python
seg_dur = whisper_segments[i+1].start - whisper_segments[i].start  # включая паузу после
# для последнего:
seg_dur = audio_total - whisper_segments[i].start
```

Иначе TTS длиннее видео → конец обрезается.

## Audio polish

После сырого .mp4 → ffmpeg chain:
```
afftdn=nr=12:nf=-25,
highpass=f=85,
acompressor=threshold=-20dB:ratio=3:attack=8:release=80:knee=2:makeup=2,
equalizer=f=4500:t=q:w=2:g=-3,
loudnorm=I=-16:LRA=11:TP=-1.5
```
Video stream-copy (не перекодировать), audio aac 192kbps. Результат в `final_polished/`.

## Tools

В `tools/`:
- `transcribe_tts.py` — Whisper word-level транскрипция (OpenAI, ключ из env/.env)
- `montage.py` — основной движок (phrase-sync + freeze/live)
- `polish_audio.py` — пост-обработка аудио

## Конфигурация
Бренд-дефолты (цвет сабов, шрифт, голос для TTS) читаются из `.corevia/config.json`
в корне проекта. Если файла нет — запусти `/setup`, либо передай параметры/env явно
(`ELEVENLABS_VOICE_ID`, `OPENAI_API_KEY`).

## Антипаттерны

- ❌ ffmpeg `subtitles=` filter — кириллица silent-fail на macOS. Только `drawtext`
- ❌ Speedup > 1.0x — мельтешит. Используй freeze для статики
- ❌ Игнорировать паузы между фразами — рассинхрон в конце
- ❌ Position y > 1500 — заходит под social UI overlay
- ❌ Толстая обводка >5px — выглядит "дёшево"
