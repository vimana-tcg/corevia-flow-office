#!/usr/bin/env python3
"""
shotlist_gen.py — МОЗГ монтажа в стиле MrBeast.

Берёт транскрипт (Whisper JSON: segments[] и/или words[]) и выдаёт cut-план
(editing_schema.json): сцены hook→stakes→proof→loop→cta с таймингом ≤3с,
зум-ударами, звуками и подсказками b-roll.

Детерминированный (stdlib-only, без API-ключей).

Структура сцен: hook→stakes→proof→loop→cta.
Правила удержания: references/retention-dna.md.

Usage:
  python3 shotlist_gen.py transcript.json --target 35 --platform reels > cutplan.json
  python3 shotlist_gen.py transcript.json --target 35 --pretty
"""
import argparse
import json
import re
import sys

# --- Правила удержания (из retention-dna.md) ---
MAX_SHOT = 3.2          # макс длина одного кадра, сек
TARGET_SHOT = 2.4       # к чему стремимся
MIN_REHOOK_TOTAL = 25   # ролики длиннее → вставляем ре-крючок

NUM_RE = re.compile(r"\d")
# слова-акценты → зум + звук (RU/UK)
EMPHASIS = re.compile(
    r"(беспл|безкошт|секунд|минут|часов|годин|ноль|нуль|сам|авто|"
    r"клиент|продаж|результат|прибыл|прибут|вырос|зросл|"
    r"тысяч|миллион|млн|процент|%|раз\b|х\d|x\d)",
    re.IGNORECASE,
)
# слова-раскрытия → тишина перед + boom
REVEAL = re.compile(r"(вот|итог|результат|смотри|оказал|выясн|секрет|главн|вышло)", re.IGNORECASE)
# абстрактные слова → подсказать b-roll вместо говорящей головы
ABSTRACT = re.compile(r"(будущ|стратег|идея|концеп|рынок|тренд|масштаб|систем|процесс)", re.IGNORECASE)


def load_chunks(tx: dict):
    """Возвращает список (text, start, end). Дробит длинные сегменты по словам."""
    chunks = []
    segs = tx.get("segments") or []
    for s in segs:
        text = (s.get("text") or "").strip()
        start = float(s.get("start", 0.0))
        end = float(s.get("end", start))
        if not text:
            continue
        dur = end - start
        words = s.get("words") or []
        # длинный сегмент + есть слова → дробим на куски ≤MAX_SHOT
        if dur > MAX_SHOT and words:
            cur, cstart = [], None
            for w in words:
                wt = (w.get("word") or w.get("text") or "").strip()
                ws = float(w.get("start", start))
                we = float(w.get("end", ws))
                if cstart is None:
                    cstart = ws
                cur.append(wt)
                if we - cstart >= TARGET_SHOT:
                    chunks.append((" ".join(cur).strip(), cstart, we))
                    cur, cstart = [], None
            if cur:
                chunks.append((" ".join(cur).strip(), cstart, end))
        elif dur > MAX_SHOT:
            # нет слов — рубим по словам текста пропорционально времени
            ws = text.split()
            n = max(1, round(dur / TARGET_SHOT))
            per = len(ws) / n
            for i in range(n):
                a = int(i * per)
                b = int((i + 1) * per) if i < n - 1 else len(ws)
                t0 = start + (end - start) * (i / n)
                t1 = start + (end - start) * ((i + 1) / n)
                piece = " ".join(ws[a:b]).strip()
                if piece:
                    chunks.append((piece, t0, t1))
        else:
            chunks.append((text, start, end))
    return chunks


def pick_focus(text: str):
    """Слово-акцент для подсветки субтитра: число > emphasis-слово > самое длинное."""
    m = re.search(r"\d[\d\s.,%]*\S*", text)
    if m:
        return m.group(0).strip(" .,")
    m = EMPHASIS.search(text)
    if m:
        # вернуть слово целиком вокруг матча
        for w in text.split():
            if EMPHASIS.search(w):
                return w.strip(" .,!?")
    words = [w.strip(" .,!?") for w in text.split() if len(w) > 4]
    return max(words, key=len) if words else None


def scene_type(idx: int, total: int, text: str, rehook_at: int):
    if idx == 0:
        return "hook"
    if idx == total - 1:
        return "cta"
    if idx == rehook_at:
        return "rehook"
    if NUM_RE.search(text) or REVEAL.search(text):
        return "proof"
    if idx <= 1:
        return "stakes"
    return "explanation"


def build(tx: dict, target: float, platform: str):
    chunks = load_chunks(tx)
    if not chunks:
        raise SystemExit("Пустой транскрипт: нет segments[] с текстом.")
    total = len(chunks)
    total_dur = chunks[-1][2] - chunks[0][1]
    rehook_at = round(total * 0.4) if total_dur >= MIN_REHOOK_TOTAL and total >= 5 else -1

    scenes = []
    for idx, (text, start, end) in enumerate(chunks):
        dur = round(min(max(end - start, 0.8), MAX_SHOT), 2)
        stype = scene_type(idx, total, text, rehook_at)
        focus = pick_focus(text)
        has_num = bool(NUM_RE.search(text))
        emph = bool(EMPHASIS.search(text))

        # zoom
        if stype in ("hook", "rehook") or has_num or emph:
            zoom = "punch"
        elif stype == "proof":
            zoom = "kenburns"
        else:
            zoom = "none"

        # sfx
        if REVEAL.search(text):
            sfx = "silence"   # тишина ПЕРЕД раскрытием
        elif stype == "cta":
            sfx = "boom"
        elif has_num:
            sfx = "ding"
        elif stype in ("hook", "rehook"):
            sfx = "whoosh"
        else:
            sfx = "whoosh" if idx % 2 == 0 else "none"

        # visual mode
        if stype == "proof":
            visual = {"mode": "live", "source_ts": round(start, 2), "broll_query": None}
        elif ABSTRACT.search(text):
            kw = ABSTRACT.search(text).group(0)
            visual = {"mode": "broll", "source_ts": None, "broll_query": _broll_query(text, kw)}
        elif dur <= 1.6:
            visual = {"mode": "freeze", "source_ts": round(start, 2), "broll_query": None}
        else:
            visual = {"mode": "live", "source_ts": round(start, 2), "broll_query": None}

        scenes.append({
            "idx": idx, "type": stype, "text": text,
            "start": round(start, 2), "end": round(end, 2), "duration": dur,
            "visual": visual, "zoom": zoom, "sfx": sfx, "caption_focus": focus,
        })
    return {"target_duration": target, "platform": platform, "scenes": scenes}


def _broll_query(text: str, kw: str):
    base = {
        "будущ": "futuristic technology abstract",
        "стратег": "business strategy meeting",
        "рынок": "stock market data screen",
        "тренд": "growth chart trending up",
        "масштаб": "scaling growth network",
        "систем": "automation system flow",
        "процесс": "workflow automation",
    }
    for k, q in base.items():
        if k in kw.lower():
            return q
    return "business technology b-roll"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("transcript", help="Whisper JSON (segments[]/words[])")
    ap.add_argument("--target", type=float, default=35.0)
    ap.add_argument("--platform", default="reels",
                    choices=["reels", "tiktok", "shorts", "youtube_long"])
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()

    with open(args.transcript, encoding="utf-8") as f:
        tx = json.load(f)
    plan = build(tx, args.target, args.platform)
    indent = 2 if args.pretty else None
    json.dump(plan, sys.stdout, ensure_ascii=False, indent=indent)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
