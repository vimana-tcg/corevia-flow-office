#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""robots-builder.py — генерує robots.txt з canonical AI-bots списком.

Usage:
    python3 robots-builder.py --host example.com [--out robots.txt]
                              [--block-training | --allow-all]
"""
from __future__ import annotations
import argparse
import json
import os
import sys


def build(host: str, block_training: bool = True) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "ai-bots-list.json"), encoding="utf-8") as f:
        bots = json.load(f)

    lines = ["User-agent: *", "Allow: /", ""]
    lines.append("# ── AI-search crawlers (allowed: Google AIO / ChatGPT / Perplexity / Claude / Bing Copilot) ──")
    for b in bots["allow_ai_search"]:
        lines += [f"User-agent: {b['ua']}", "Allow: /", ""]
    if block_training:
        lines.append("# ── Training scrapers (blocked — used for LLM training only, not search) ──")
        for b in bots["block_training_scrapers"]:
            lines += [f"User-agent: {b['ua']}", "Disallow: /", ""]
    lines += [f"Sitemap: https://{host}/sitemap.xml"]
    # Поширений pattern — також sitemap-blog.xml
    lines.append(f"Sitemap: https://{host}/sitemap-blog.xml")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True)
    ap.add_argument("--out", default="-")
    ap.add_argument("--no-block-training", action="store_true",
                    help="Allow training scrapers (default: block CCBot etc.)")
    args = ap.parse_args()

    content = build(args.host, block_training=not args.no_block_training)
    if args.out == "-":
        sys.stdout.write(content)
    else:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ written: {args.out} ({len(content)} bytes)")


if __name__ == "__main__":
    main()
