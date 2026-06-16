#!/usr/bin/env bash
# cutout_face.sh — удаляет фон у портрета через Replicate (rembg), отдаёт PNG с альфой.
# Токен Replicate берётся из переменной окружения REPLICATE_API_TOKEN или из локального .env.
#
# Usage: cutout_face.sh <input-photo> <output-png>
#   <input-photo>  любое фото (jpg/png/heic — heic конвертится через sips, если есть)
#   <output-png>   куда сохранить вырез (PNG с прозрачным фоном)
set -euo pipefail
IN="${1:?usage: cutout_face.sh <input> <output.png>}"
OUT="${2:?need output.png}"
[ -f "$IN" ] || { echo "ERR: not found: $IN" >&2; exit 1; }

# Resolve token: env first, then ./.env, then ~/.env
if [ -z "${REPLICATE_API_TOKEN:-}" ]; then
  for envf in ".env" "$HOME/.env"; do
    if [ -f "$envf" ]; then
      val="$(grep -E '^REPLICATE_API_TOKEN=' "$envf" | head -n1 | cut -d= -f2- | tr -d '"'"'"'' )"
      if [ -n "$val" ]; then export REPLICATE_API_TOKEN="$val"; break; fi
    fi
  done
fi
if [ -z "${REPLICATE_API_TOKEN:-}" ]; then
  echo "ERR: нужен REPLICATE_API_TOKEN — задай переменную окружения или добавь в .env" >&2
  echo "     export REPLICATE_API_TOKEN=... (ключ на replicate.com/account)" >&2
  exit 2
fi

TMP="$(mktemp -t _cf_XXXX).png"
trap 'rm -f "$TMP"' EXIT
# normalize + downscale to <=1200px (HEIC -> png via macOS sips when available)
if command -v sips >/dev/null 2>&1; then
  sips -s format png "$IN" --out "$TMP" >/dev/null 2>&1 || cp "$IN" "$TMP"
else
  cp "$IN" "$TMP"
fi
python3 - "$TMP" <<'PY'
import sys
from PIL import Image
p = sys.argv[1]
im = Image.open(p).convert('RGB')
im.thumbnail((1200, 1200))
im.save(p)
PY

echo ">> rembg on Replicate" >&2
python3 - "$TMP" "$OUT" <<'PY'
import base64, json, os, sys, time, urllib.request, urllib.error

tok = os.environ.get("REPLICATE_API_TOKEN")
if not tok:
    sys.exit("ERR: нужен REPLICATE_API_TOKEN")
in_path, out_path = sys.argv[1], sys.argv[2]
# A User-Agent header avoids Cloudflare error code 1010.
UA = "Mozilla/5.0 (compatible; thumb/1.0)"


def api(url, data=None, method="GET"):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode() if data else None,
        method=method,
        headers={
            "Authorization": f"Bearer {tok}",
            "Content-Type": "application/json",
            "User-Agent": UA,
        },
    )
    try:
        return urllib.request.urlopen(req).read()
    except urllib.error.HTTPError as e:
        return e.read()


ver = json.loads(api("https://api.replicate.com/v1/models/cjwbw/rembg"))["latest_version"]["id"]
img = "data:image/png;base64," + base64.b64encode(open(in_path, "rb").read()).decode()
pred = json.loads(api(
    "https://api.replicate.com/v1/predictions",
    {"version": ver, "input": {"image": img}},
    "POST",
))
url = pred["urls"]["get"]
p = pred
for _ in range(90):
    p = json.loads(api(url))
    if p["status"] in ("succeeded", "failed", "canceled"):
        break
    time.sleep(2)
out = p.get("output")
out = out if isinstance(out, str) else (out[0] if out else "")
if p["status"] == "succeeded" and out:
    req = urllib.request.Request(out, headers={"User-Agent": UA})
    open(out_path, "wb").write(urllib.request.urlopen(req).read())
    print("OK")
else:
    sys.exit(f"ERR rembg failed: status={p.get('status')} error={p.get('error')}")
PY

echo ">> saved cutout: $OUT" >&2
