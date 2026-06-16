#!/usr/bin/env python3
"""apply-model-tiers.py — проставляет model: в frontmatter агентов по политике.

Политика (без потери качества):
  • opus   — оркестрация, ресёрч, анализ, дорогие решения (юр/фин/безопасность/память).
  • haiku  — механические генераторы (детерминированный вывод, мало рассуждения).
  • sonnet — всё остальное (исполнители-специалисты): дефолт.

Запуск: python3 scripts/apply-model-tiers.py [--dir agents]
"""
import argparse, os, re, sys

OPUS = {
    # оркестраторы
    "brand-director", "smm-orchestrator", "pm-product-manager", "sales-head",
    "tech-director", "office-director", "fin-director", "agent-mentor",
    # ресёрч / анализ
    "pm-research", "pm-conversation-intel", "pm-growth", "pm-niche-scout",
    "pm-analytics", "content-researcher", "oss-vetter", "keyword-performance-analyzer",
    "seo-cluster", "seo-sxo", "paid-ads-manager",
    # дорогие решения / стратегия
    "fin-cfo", "legal-counsel", "founder-coach", "memory-keeper",
}
HAIKU = {
    # механические генераторы (детерминированный вывод)
    "seo-schema", "seo-sitemap", "seo-image-gen",
}


def tier(name):
    if name in OPUS:
        return "opus"
    if name in HAIKU:
        return "haiku"
    return "sonnet"


def process(path):
    name = os.path.basename(path)[:-3]
    want = tier(name)
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---"):
        return None  # нет frontmatter
    end = text.index("\n---", 3)
    fm, body = text[:end], text[end:]
    if re.search(r'(?m)^model:\s*', fm):
        fm2 = re.sub(r'(?m)^model:.*$', f"model: {want}", fm)
    else:
        fm2 = fm.rstrip() + f"\nmodel: {want}"
    if fm2 != fm:
        open(path, "w", encoding="utf-8").write(fm2 + body)
        return want
    return want  # уже верный


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents"))
    a = ap.parse_args()
    counts = {"opus": 0, "sonnet": 0, "haiku": 0, "skip": 0}
    for f in sorted(os.listdir(a.dir)):
        if not f.endswith(".md"):
            continue
        r = process(os.path.join(a.dir, f))
        counts[r if r else "skip"] += 1
    print(f"model-tiers применены: opus={counts['opus']} sonnet={counts['sonnet']} haiku={counts['haiku']} skip={counts['skip']}")


if __name__ == "__main__":
    main()
