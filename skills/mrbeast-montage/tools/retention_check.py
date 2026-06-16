#!/usr/bin/env python3
"""
retention_check.py — оценивает cut-план по правилам удержания MrBeast.
Даёт балл 0-100 + чек-лист с конкретными «что починить».

Usage:
  python3 retention_check.py cutplan.json
  python3 shotlist_gen.py tx.json --target 35 | python3 retention_check.py -
"""
import json
import sys

MAX_SHOT = 3.5
AVG_LO, AVG_HI = 1.5, 3.0
SFX_PER_SEC = 1 / 6.0      # ≥1 звук на 6 сек
REHOOK_MIN_TOTAL = 25


def load(path):
    raw = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    return json.loads(raw)


def check(plan):
    scenes = plan.get("scenes", [])
    if not scenes:
        return 0, [("FAIL", "Нет сцен", "Сгенерируй cut-план через shotlist_gen.py")]
    durs = [s.get("duration", 0) for s in scenes]
    total = sum(durs)
    avg = total / len(scenes)
    results = []
    score = 0

    def add(ok, w, label, fix):
        nonlocal score
        score += w if ok else 0
        results.append(("PASS" if ok else "FAIL", label, "" if ok else fix))

    # 1. Крючок ≤3с (20)
    hook = scenes[0]
    ok = hook.get("type") == "hook" and hook.get("duration", 9) <= 3.0
    add(ok, 20, f"Крючок 0-3с (сейчас {hook.get('duration')}с, тип {hook.get('type')})",
        "Первая сцена должна быть hook ≤3с с цифрой/результатом. См. hook-bank.md")

    # 2. Средняя длина кадра 1.5-3.0 (20)
    ok = AVG_LO <= avg <= AVG_HI
    add(ok, 20, f"Средняя длина кадра {avg:.2f}с (цель {AVG_LO}-{AVG_HI})",
        "Слишком длинные кадры — дроби фразы. shotlist_gen уже режет, проверь источник.")

    # 3. Нет кадров >3.5с (15)
    longs = [s["idx"] for s in scenes if s.get("duration", 0) > MAX_SHOT]
    add(not longs, 15, f"Длинных кадров >{MAX_SHOT}с: {len(longs)} {longs[:5]}",
        "Разбей эти сцены или добавь зум/врезку внутри них.")

    # 4. Плотность звуков ≥1/6с (15)
    sfx_n = sum(1 for s in scenes if s.get("sfx") not in (None, "none"))
    need = total * SFX_PER_SEC
    ok = sfx_n >= need
    add(ok, 15, f"Звуков {sfx_n} (нужно ≥{need:.0f} на {total:.0f}с)",
        "Добавь whoosh на резах, ding на цифрах, boom на итоге.")

    # 5. Зум-удары на цифрах (10)
    num_scenes = [s for s in scenes if any(c.isdigit() for c in s.get("text", ""))]
    zoomed = [s for s in num_scenes if s.get("zoom") == "punch"]
    ok = not num_scenes or len(zoomed) >= len(num_scenes) * 0.7
    add(ok, 10, f"Зум на цифрах: {len(zoomed)}/{len(num_scenes)}",
        "Каждая цифра/акцент → zoom=punch.")

    # 6. Ре-крючок в середине для длинных (10)
    if total >= REHOOK_MIN_TOTAL:
        ok = any(s.get("type") == "rehook" for s in scenes)
        add(ok, 10, "Ре-крючок на 30-50%", "Вставь сцену type=rehook («но дальше интереснее»).")
    else:
        score += 10
        results.append(("PASS", "Ре-крючок не нужен (ролик короткий)", ""))

    # 7. CTA ровно 1, в конце (10)
    ctas = [s for s in scenes if s.get("type") == "cta"]
    ok = len(ctas) == 1 and scenes[-1].get("type") == "cta"
    add(ok, 10, f"CTA в конце: {len(ctas)} шт",
        "Должен быть ровно 1 CTA — последняя сцена. См. hook-bank.md → CTA-банк.")

    return min(score, 100), results


def main():
    if len(sys.argv) < 2:
        print("usage: retention_check.py <cutplan.json|->", file=sys.stderr)
        sys.exit(1)
    plan = load(sys.argv[1])
    score, results = check(plan)
    print(f"\n🎬 RETENTION SCORE: {score}/100\n")
    for status, label, fix in results:
        icon = "✅" if status == "PASS" else "❌"
        print(f"{icon} {label}")
        if fix:
            print(f"   → {fix}")
    verdict = ("🔥 Готов к рендеру" if score >= 80 else
               "🟡 Доработать" if score >= 60 else "🔴 Переделать")
    print(f"\n{verdict} ({score}/100)\n")


if __name__ == "__main__":
    main()
