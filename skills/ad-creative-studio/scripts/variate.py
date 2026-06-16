#!/usr/bin/env python3
"""A/B-вариатор: 1 базовый креатив + список «углов» → N разных вариантов.

Усиливает креативность: вместо 1 решения на бриф — 5 РАЗНЫХ заходов для теста
(разные психо-углы/хуки/палитры/CTA). Анти-дубляж: углы берутся из таксономии
(references/angles.md), палитры разные → варианты не схлопываются в перефраз.

Вход — base.json:
{
  "base": {"size":[1080,1080], "bg":"output/bg.jpg", "sub":"...", "hsize":92, "ssize":36},
  "out_dir": "output/variants",
  "variants": [
    {"id":"v1_pain",    "eyebrow":"БОЛЬ",        "headline":"...", "accent":"...", "cta":"...", "accent_color":"crimson"},
    {"id":"v2_proof",   "eyebrow":"ДОКАЗ",       "headline":"...", "cta":"...", "accent_color":"emerald"},
    ...
  ]
}
→ пишет creatives.json и зовёт overlay.py.
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    cfg = json.load(open(sys.argv[1]))
    base = cfg.get("base", {})
    out_dir = cfg.get("out_dir", "output/ad-variants")
    creatives = []
    for v in cfg["variants"]:
        c = dict(base)        # общий фон/размер/sub
        c.update(v)           # переопределения варианта
        creatives.append(c)
    merged = {"brand": cfg.get("brand", "BRAND"), "out_dir": out_dir, "creatives": creatives}
    cpath = os.path.join(out_dir, "creatives.json")
    os.makedirs(out_dir, exist_ok=True)
    json.dump(merged, open(cpath, "w"), ensure_ascii=False, indent=2)
    print(f"creatives.json -> {cpath} ({len(creatives)} вариантов)")
    subprocess.run([sys.executable, os.path.join(HERE, "overlay.py"), cpath], check=True)


if __name__ == "__main__":
    main()
