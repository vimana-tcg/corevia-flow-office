#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""llms-full-builder.py — генерує llms-full.txt з knowledge file.

Knowledge file може бути:
- Python data.py з UNITS = [...]
- JSON структурований
- Markdown із Front Matter

Usage:
    python3 llms-full-builder.py --knowledge data.py --host example.com \\
                                  --brand "Your Brand" --out llms-full.txt
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path


def load_knowledge(path: str) -> dict:
    """Гнучко завантажуємо knowledge — підтримуємо .py / .json / .md."""
    if path.endswith(".py"):
        spec = importlib.util.spec_from_file_location("kw", path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return {
            "CONFIG": getattr(m, "CONFIG", {}),
            "UNITS": getattr(m, "UNITS", []),
            "INTERNET_PRICE_EUR": getattr(m, "INTERNET_PRICE_EUR", {}),
        }
    if path.endswith(".json"):
        return json.loads(Path(path).read_text(encoding="utf-8"))
    raise SystemExit(f"Unsupported knowledge format: {path}")


def build_llms_full(data: dict, host: str, brand: str, faqs: list | None = None) -> str:
    """Будуємо llms-full.txt у проробленому форматі."""
    C = data.get("CONFIG", {})
    UNITS = data.get("UNITS", [])
    PRICES = data.get("INTERNET_PRICE_EUR", {})

    parts = []
    parts.append(f"# {C.get('company', brand)} — {C.get('brand', brand)}")
    parts.append("")
    intro = (C.get("description") or
             f"Каталог і послуги {brand}. Структуровані дані для AI-search "
             f"(ChatGPT / Perplexity / Claude / Google AIO).")
    parts.append(f"> {intro}")
    parts.append("")
    parts.append("## Про компанію")
    parts.append("")
    for k, label in [
        ("company", "Юридична назва"), ("edrpou", "ЄДРПОУ"),
        ("address", "Адреса"), ("phone", "Телефон"),
        ("chat_url", "Telegram-бот"), ("group_url", "Спільнота"),
        ("domain", "Сайт"),
    ]:
        if C.get(k):
            parts.append(f"- **{label}:** {C[k]}")
    parts.append("")

    # Каталог
    if UNITS:
        parts.append("## Каталог (повний)")
        parts.append("")
        for u in UNITS:
            slug = u.get("slug", "")
            parts.append(f"### {u.get('title', slug)}")
            parts.append("")
            if slug:
                parts.append(f"**URL:** https://{host}/{slug}.html")
            for k in ("brand", "model", "year", "category", "badge"):
                if u.get(k):
                    parts.append(f"**{k.title()}:** {u[k]}")
            if PRICES.get(slug):
                parts.append(f"**Ціна:** €{PRICES[slug]:,}".replace(",", " "))
            if u.get("highlight"):
                parts.append(f"**Ключове:** {u['highlight']}")
            if u.get("specs"):
                parts.append("")
                parts.append("**Характеристики:**")
                for k, v in u["specs"].items():
                    parts.append(f"- {k}: {v}")
            parts.append("")

    # FAQ
    if faqs:
        parts.append("## Часті запитання (FAQ)")
        parts.append("")
        for q, a in faqs:
            parts.append(f"### {q}")
            parts.append("")
            parts.append(a)
            parts.append("")

    # Sitemaps + контакти
    parts.append("## Sitemaps")
    parts.append("")
    parts.append(f"- {host}/sitemap.xml")
    parts.append(f"- {host}/sitemap-blog.xml")
    parts.append("")

    parts.append("## Канали зв'язку")
    parts.append("")
    if C.get("chat_url"):
        parts.append(f"- Telegram-бот: {C['chat_url']}")
    if C.get("group_url"):
        parts.append(f"- Telegram-спільнота: {C['group_url']}")
    if C.get("phone"):
        parts.append(f"- Телефон: {C['phone']}")
    parts.append("")

    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--knowledge", required=True, help="data.py / .json / .md")
    ap.add_argument("--host", required=True)
    ap.add_argument("--brand", required=True)
    ap.add_argument("--out", default="-")
    args = ap.parse_args()

    data = load_knowledge(args.knowledge)
    content = build_llms_full(data, args.host, args.brand)

    if args.out == "-":
        sys.stdout.write(content)
    else:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ written: {args.out} ({len(content):,} bytes, {len(content)//1024} KB)")


if __name__ == "__main__":
    main()
