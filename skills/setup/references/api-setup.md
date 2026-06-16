# Карточки подключения API (официальные ссылки, проверены)

Для каждого сервиса: где взять ключ → в какую строку `.env` вставить. Веди по одному.

## 🧠 Anthropic (Claude) — рекомендуем
- Ссылка: https://console.anthropic.com/settings/keys
- Создай ключ → вставь в `.env`: `ANTHROPIC_API_KEY=`
- Платно по факту использования.

## 🧠 OpenAI (GPT, Whisper, картинки)
- Ссылка: https://platform.openai.com/api-keys
- `.env`: `OPENAI_API_KEY=`

## 🎨 Replicate (Ideogram / Flux / удаление фона)
- Ссылка: https://replicate.com/account/api-tokens
- `.env`: `REPLICATE_API_TOKEN=`  (ключи начинаются с `r8_`)
- Оплата по факту (~$0.03 за картинку Ideogram turbo).

## 📷 Pexels (бесплатные стоковые фото)
- Ссылка: https://www.pexels.com/api/  → «Get Started» → ключ
- `.env`: `PEXELS_API_KEY=`  (бесплатно)
- ⚠️ Фото с узнаваемыми людьми НЕЛЬЗЯ в платную рекламу (нет model-release).

## 🖌️ Canva (дизайн) — через MCP, не ключом
- Подключается как MCP-сервер Claude. Инструкция: https://www.canva.com/developers/
- В Claude Code добавь Canva MCP (см. docs.claude.com → MCP). Ключ в `.env` не нужен.

## 🟦 Google Gemini (nano-banana, картинки с текстом)
- Ссылка: https://aistudio.google.com/apikey
- `.env`: `GEMINI_API_KEY=`  (ключи `AIza...`). Для генерации картинок нужен биллинг.

## 🔊 ElevenLabs (озвучка / клон голоса) — опц.
- Ссылка: https://elevenlabs.io/app/settings/api-keys
- `.env`: `ELEVENLABS_API_KEY=`

## 📘 Meta — Facebook / Instagram (публикация + реклама)
- Ссылка: https://developers.facebook.com/ → создать App → Graph API
- Нужен Business/Creator IG-аккаунт + связанная FB-страница + App Review.
- `.env`: `META_ACCESS_TOKEN=`, `META_AD_ACCOUNT_ID=` (формат `act_...`)
- Реклама: подключи пиксель / Conversions API.

## ▶️ YouTube (загрузка видео)
- Ссылка: https://console.cloud.google.com/ → включить «YouTube Data API v3» → OAuth
- `.env`: `YOUTUBE_CLIENT_ID=`, `YOUTUBE_CLIENT_SECRET=`, `YOUTUBE_REFRESH_TOKEN=`

## 🎵 TikTok (Content Posting API)
- Ссылка: https://developers.tiktok.com/ → создать App → Content Posting API
- ⚠️ Для публичных постов нужен аудит приложения; без него — только приватные.
- `.env`: `TIKTOK_CLIENT_KEY=`, `TIKTOK_CLIENT_SECRET=`

---
Правило: ключи только в `.env` (он в .gitignore). Никогда не вставляй ключ в чат, код
или коммит. Проверка подключений — `scripts/doctor.sh`.
