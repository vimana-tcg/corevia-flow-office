#!/usr/bin/env python3
"""keyword_bank.py — управляет «банком ключей» проекта (keywords/<тема>.json).

Детерминированный, без сети, stdlib. Банк хранит ключевые слова + МИНУС-слова
(negatives — то, что не сработало). Агенты пополняют/читают через этот скрипт.

Команды:
  init      --bank keywords/topic.json --topic "тема" --locale ru
  add       --bank ... --keywords-json '[{"keyword":"...","source":"autocomplete","intent":"commercial","cluster":"..."}]'
  negative  --bank ... --keyword "..." --reason "0 конверсий за 30 дней"
  list      --bank ... [--status new|active|winner|loser]
  stats     --bank ...

Статусы ключа: new → active → winner | loser. loser можно перевести в negatives.
"""
import argparse, json, os, sys, datetime


def load(path):
    if not os.path.exists(path):
        sys.exit(f"❌ банк не найден: {path} (сначала init)")
    return json.load(open(path, encoding="utf-8"))


def save(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    data["updated_at"] = _now()
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def _now():
    # дата передаётся снаружи если нужно; здесь — UTC-дата без времени
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")


def cmd_init(a):
    if os.path.exists(a.bank):
        sys.exit(f"⚠️ банк уже есть: {a.bank}")
    save(a.bank, {"topic": a.topic, "locale": a.locale, "keywords": [], "negatives": []})
    print(f"✅ банк создан: {a.bank} (тема: {a.topic}, локаль: {a.locale})")


def cmd_add(a):
    data = load(a.bank)
    existing = {k["keyword"].lower() for k in data["keywords"]}
    neg = {n["keyword"].lower() for n in data["negatives"]}
    incoming = json.loads(a.keywords_json)
    added = 0
    for item in incoming:
        kw = item["keyword"].strip()
        low = kw.lower()
        if not kw or low in existing or low in neg:
            continue  # дубль или уже в минус-словах — пропускаем
        data["keywords"].append({
            "keyword": kw,
            "source": item.get("source", "manual"),
            "intent": item.get("intent", ""),
            "cluster": item.get("cluster", ""),
            "volume": item.get("volume"),
            "status": "new",
            "metrics": {"impressions": 0, "clicks": 0, "conversions": 0, "spend": 0.0},
            "first_seen": _now(), "last_updated": _now(), "notes": "",
        })
        existing.add(low); added += 1
    save(a.bank, data)
    print(f"✅ добавлено новых ключей: {added} (пропущено дублей/минус-слов: {len(incoming) - added})")


def cmd_negative(a):
    data = load(a.bank)
    data["keywords"] = [k for k in data["keywords"] if k["keyword"].lower() != a.keyword.lower()]
    if not any(n["keyword"].lower() == a.keyword.lower() for n in data["negatives"]):
        data["negatives"].append({"keyword": a.keyword, "reason": a.reason, "date": _now()})
    save(a.bank, data)
    print(f"🚫 в минус-слова: «{a.keyword}» — {a.reason}")


def cmd_list(a):
    data = load(a.bank)
    rows = [k for k in data["keywords"] if not a.status or k["status"] == a.status]
    for k in rows:
        m = k["metrics"]
        print(f"  [{k['status']:7}] {k['keyword']}  vol={k.get('volume')} conv={m['conversions']} clk={m['clicks']} imp={m['impressions']} ({k['cluster']})")
    print(f"— всего: {len(rows)} | минус-слов: {len(data['negatives'])}")


def cmd_stats(a):
    data = load(a.bank)
    by = {}
    for k in data["keywords"]:
        by[k["status"]] = by.get(k["status"], 0) + 1
    print(f"📊 банк «{data['topic']}» ({data['locale']}), обновлён {data['updated_at']}")
    print(f"   ключей: {len(data['keywords'])} | по статусам: {by}")
    print(f"   минус-слов: {len(data['negatives'])}")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    pi = sub.add_parser("init"); pi.add_argument("--bank", required=True); pi.add_argument("--topic", required=True); pi.add_argument("--locale", default="en"); pi.set_defaults(fn=cmd_init)
    pa = sub.add_parser("add"); pa.add_argument("--bank", required=True); pa.add_argument("--keywords-json", required=True); pa.set_defaults(fn=cmd_add)
    pn = sub.add_parser("negative"); pn.add_argument("--bank", required=True); pn.add_argument("--keyword", required=True); pn.add_argument("--reason", default=""); pn.set_defaults(fn=cmd_negative)
    pl = sub.add_parser("list"); pl.add_argument("--bank", required=True); pl.add_argument("--status", default=""); pl.set_defaults(fn=cmd_list)
    ps = sub.add_parser("stats"); ps.add_argument("--bank", required=True); ps.set_defaults(fn=cmd_stats)
    a = p.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
