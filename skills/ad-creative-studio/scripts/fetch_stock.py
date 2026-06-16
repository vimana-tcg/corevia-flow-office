#!/usr/bin/env python3
"""Тянет бесплатное стоковое фото с Pexels (commercial-free) под концепт.

Использование:
  PEXELS_API_KEY=... python3 fetch_stock.py --query "modern office bright" \
      --orientation square --index 0 --out path/bg.jpg

Ключ: PEXELS_API_KEY берётся из переменной окружения / .env проекта
(не хардкодить в коде).
"""
import argparse, json, os, subprocess, sys

KEY = os.environ.get("PEXELS_API_KEY", "").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--orientation", default="square", choices=["square", "portrait", "landscape"])
    ap.add_argument("--index", type=int, default=0, help="какое из найденных фото взять")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if not KEY:
        sys.exit("❌ PEXELS_API_KEY не задан (env). См. docstring.")
    url = (f"https://api.pexels.com/v1/search?query={a.query.replace(' ', '+')}"
           f"&orientation={a.orientation}&per_page=12")
    raw = subprocess.run(["curl", "-s", "-H", f"Authorization: {KEY}", url],
                         capture_output=True, text=True, timeout=60).stdout
    photos = json.loads(raw).get("photos", [])
    if not photos:
        sys.exit(f"❌ нет фото для '{a.query}'")
    p = photos[min(a.index, len(photos) - 1)]
    src = p["src"].get("large2x") or p["src"]["large"]
    subprocess.run(["curl", "-s", src, "-o", a.out], timeout=60)
    print(f"OK {a.out} <- Pexels/{p.get('photographer', '?')} (id {p.get('id')})")


if __name__ == "__main__":
    main()
