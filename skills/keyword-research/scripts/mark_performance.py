#!/usr/bin/env python3
"""mark_performance.py — анализатор: размечает ключи в банке по реальным данным
рекламы/SEO (что СРАБОТАЛО, что НЕТ). Запускается раз в неделю (статзначимость).

Вход — метрики по ключам (из Meta Ads / Google Search Console), JSON-массив:
  [{"keyword":"...","impressions":1200,"clicks":18,"conversions":2,"spend":40.0}, ...]

Логика разметки (пороги настраиваare флагами):
  • winner  — есть конверсии (conversions >= 1) ИЛИ CTR выше порога.
  • loser   — набрал показы (>= min_impressions), но 0 конверсий и низкий CTR.
  • active  — данных пока мало (не трогаем).
  loser'ы при --auto-negative автоматически уходят в МИНУС-СЛОВА (с причиной).

Использование:
  python3 mark_performance.py --bank keywords/topic.json --metrics metrics.json \
      [--min-impressions 500] [--ctr-floor 0.005] [--auto-negative] [--date 2026-06-16]
"""
import argparse, json, os, sys


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bank", required=True)
    p.add_argument("--metrics", required=True, help="JSON-файл с метриками по ключам")
    p.add_argument("--min-impressions", type=int, default=500)
    p.add_argument("--ctr-floor", type=float, default=0.005)  # 0.5%
    p.add_argument("--auto-negative", action="store_true")
    p.add_argument("--date", default="")
    a = p.parse_args()

    if not os.path.exists(a.bank):
        sys.exit(f"❌ банк не найден: {a.bank}")
    data = json.load(open(a.bank, encoding="utf-8"))
    metrics = {m["keyword"].lower(): m for m in json.load(open(a.metrics, encoding="utf-8"))}
    date = a.date or data.get("updated_at", "")

    win = lose = active = 0
    kept = []
    for k in data["keywords"]:
        m = metrics.get(k["keyword"].lower())
        if m:
            k["metrics"] = {
                "impressions": int(m.get("impressions", 0)),
                "clicks": int(m.get("clicks", 0)),
                "conversions": int(m.get("conversions", 0)),
                "spend": float(m.get("spend", 0.0)),
            }
            k["last_updated"] = date
            imp = k["metrics"]["impressions"]; clk = k["metrics"]["clicks"]; conv = k["metrics"]["conversions"]
            ctr = (clk / imp) if imp else 0.0
            if conv >= 1 or (imp >= a.min_impressions and ctr >= a.ctr_floor * 3):
                k["status"] = "winner"; win += 1
            elif imp >= a.min_impressions and conv == 0 and ctr < a.ctr_floor:
                k["status"] = "loser"; lose += 1
                if a.auto_negative:
                    data["negatives"].append({
                        "keyword": k["keyword"],
                        "reason": f"loser: {imp} показов, 0 конв., CTR {ctr:.2%} (< {a.ctr_floor:.2%})",
                        "date": date,
                    })
                    continue  # убираем из активных ключей
            else:
                k["status"] = "active"; active += 1
        kept.append(k)

    data["keywords"] = kept
    data["updated_at"] = date
    json.dump(data, open(a.bank, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"📊 размечено: 🏆 winner={win}  🚫 loser={lose}  ⏳ active={active}")
    if a.auto_negative and lose:
        print(f"   {lose} проигравших → минус-слова (исключаются из будущих кампаний/контента)")
    print("   winner'ы используй как новые seed для расширения; минус-слова НЕ предлагать.")


if __name__ == "__main__":
    main()
