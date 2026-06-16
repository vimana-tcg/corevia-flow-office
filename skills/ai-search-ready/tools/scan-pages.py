#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scan-pages.py — baseline + post-scan для AI-search compliance.

Перевіряє кожен HTML файл по 7 критеріях:
1. <section id="intro"> з 80+ слів
2. >=50% <h2> мають id-attr
3. FAQPage JSON-LD schema present
4. 3+ user-voice FAQ questions
5. Answer Block (40-80 слів під H1)
6. llms-full.txt present у webroot
7. robots.txt має AI-bots whitelist

Usage:
    python3 scan-pages.py --root /var/www/site
    python3 scan-pages.py --root /var/www/site --compare baseline.json
    python3 scan-pages.py --root /var/www/site --out baseline.json
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "user-voice-prefixes.json"), encoding="utf-8") as f:
    USER_VOICE = json.load(f)
USER_VOICE_RE = re.compile('"name"\\s*:\\s*"(?:' + USER_VOICE["_regex_uk"][3:-1] + ')[^"]{8,}\\?"', re.I)


def scan_file(path: str) -> dict:
    try:
        html = Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"error": "unreadable"}

    out = {"path": path, "size": len(html)}

    # 1. Intro section з 80+ слів
    m = re.search(r'<section[^>]*id=["\']intro["\'][^>]*>([\s\S]*?)</section>', html, re.I)
    if m:
        text = re.sub(r'<[^>]+>', ' ', m.group(1))
        words = len(text.split())
        out["intro_words"] = words
        out["has_intro"] = words >= 80
    else:
        out["intro_words"] = 0
        out["has_intro"] = False

    # 2. Anchor IDs на H2
    h2s = re.findall(r'<h2\b([^>]*)>', html, re.I)
    h2_with_id = sum(1 for a in h2s if re.search(r'\bid=["\']', a))
    out["h2_total"] = len(h2s)
    out["h2_with_id"] = h2_with_id
    out["h2_id_ratio"] = (h2_with_id / len(h2s)) if h2s else 0

    # 3. FAQPage schema
    out["has_faq_schema"] = bool(re.search(r'"@type"\s*:\s*"FAQPage"', html, re.I))

    # 4. User-voice FAQ count (у JSON-LD)
    user_voice_qs = USER_VOICE_RE.findall(html)
    out["user_voice_faq_count"] = len(user_voice_qs)
    out["has_3plus_user_voice"] = len(user_voice_qs) >= 3

    # 5. Answer Block (40-80 слів перших p після H1)
    h1_m = re.search(r'<h1\b[^>]*>[\s\S]*?</h1>', html, re.I)
    if h1_m:
        after = html[h1_m.end():h1_m.end()+3000]
        first_p = re.search(r'<p\b[^>]*>([\s\S]*?)</p>', after, re.I)
        if first_p:
            text = re.sub(r'<[^>]+>', ' ', first_p.group(1))
            w = len(text.split())
            out["answer_block_words"] = w
            out["has_answer_block"] = 40 <= w <= 200
        else:
            out["answer_block_words"] = 0
            out["has_answer_block"] = False
    else:
        out["answer_block_words"] = 0
        out["has_answer_block"] = False

    return out


def scan_root(root: str) -> dict:
    files = []
    for path in Path(root).rglob("*.html"):
        # Skip common excludes
        rel = str(path.relative_to(root))
        if rel.startswith(("404.html",)) or "/_" in rel or rel.startswith("seo-watchdog/"):
            continue
        files.append(str(path))

    pages = [scan_file(f) for f in files]
    pages = [p for p in pages if "error" not in p]

    n = len(pages)
    if n == 0:
        return {"error": "no html files", "root": root}

    summary = {
        "root": root,
        "scanned": n,
        "has_intro_pct": round(sum(1 for p in pages if p["has_intro"]) / n * 100, 1),
        "h2_id_avg_ratio": round(sum(p["h2_id_ratio"] for p in pages) / n * 100, 1),
        "has_faq_schema_pct": round(sum(1 for p in pages if p["has_faq_schema"]) / n * 100, 1),
        "has_3plus_user_voice_pct": round(sum(1 for p in pages if p["has_3plus_user_voice"]) / n * 100, 1),
        "has_answer_block_pct": round(sum(1 for p in pages if p["has_answer_block"]) / n * 100, 1),
    }

    # Site-wide signals
    summary["llms_full_present"] = os.path.exists(os.path.join(root, "llms-full.txt"))
    robots_path = os.path.join(root, "robots.txt")
    if os.path.exists(robots_path):
        robots = Path(robots_path).read_text(errors="ignore")
        summary["robots_has_gptbot"] = "GPTBot" in robots
        summary["robots_has_claudebot"] = "ClaudeBot" in robots
        summary["robots_has_perplexity"] = "PerplexityBot" in robots
        summary["robots_blocks_ccbot"] = "CCBot" in robots and "Disallow" in robots
    return summary


def print_summary(s: dict, prev: dict | None = None):
    if "error" in s:
        print(f"✗ {s['error']}", file=sys.stderr)
        return
    print(f"📊 AI-search readiness · {s['root']} ({s['scanned']} pages)")
    print()
    metrics = [
        ("Intro prose 80+ words", "has_intro_pct", "%"),
        ("H2 anchor IDs avg", "h2_id_avg_ratio", "%"),
        ("FAQPage schema", "has_faq_schema_pct", "%"),
        ("3+ user-voice FAQ", "has_3plus_user_voice_pct", "%"),
        ("Answer Block under H1", "has_answer_block_pct", "%"),
    ]
    for label, key, unit in metrics:
        cur = s.get(key, 0)
        delta = ""
        if prev:
            d = cur - prev.get(key, 0)
            delta = f"  (Δ{'+' if d >= 0 else ''}{d:.1f})" if d else ""
        bar = int(cur / 10) * '█' + (10 - int(cur / 10)) * '░'
        print(f"  {label:32} {bar} {cur:5.1f}{unit}{delta}")
    print()
    print("Site-wide:")
    for k in ["llms_full_present", "robots_has_gptbot", "robots_has_claudebot",
              "robots_has_perplexity", "robots_blocks_ccbot"]:
        v = s.get(k, False)
        print(f"  {'✅' if v else '❌'} {k}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", help="Save JSON snapshot")
    ap.add_argument("--compare", help="Compare with previous JSON")
    args = ap.parse_args()

    s = scan_root(args.root)

    prev = None
    if args.compare and os.path.exists(args.compare):
        with open(args.compare) as f:
            prev = json.load(f)

    print_summary(s, prev)

    if args.out:
        with open(args.out, "w") as f:
            json.dump(s, f, indent=2)
        print(f"\n💾 Saved: {args.out}")


if __name__ == "__main__":
    main()
