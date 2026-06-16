#!/usr/bin/env python3
"""Гибрид-рендер: фон (сток/ИИ) + текст/CTA кодом (Montserrat, Cyrillic).

Вход — JSON-конфиг (см. references/brief-to-config.md). Поддержка палитры
(accent_color) для A/B-вариаций и двух стилей (clean / mrbeast).
  python3 overlay.py creatives.json
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(SKILL, "assets/fonts/Montserrat.ttf")
GOLD = (240, 178, 35)
WHITE = (255, 255, 255)
GREY = (203, 205, 210)
BLACK = (10, 10, 12)

# Пресет-палитры для A/B (accent_color)
PALETTES = {
    "gold": (240, 178, 35),
    "blue": (56, 132, 255),
    "emerald": (32, 201, 151),
    "crimson": (235, 64, 78),
    "mono": (245, 245, 245),
}


def f(size, weight="Regular"):
    fnt = ImageFont.truetype(FONT, size)
    try:
        fnt.set_variation_by_name(weight)
    except Exception:
        pass
    return fnt


def cover(img, size):
    W, H = size; iw, ih = img.size
    s = max(W / iw, H / ih)
    img = img.resize((int(iw * s) + 1, int(ih * s) + 1)); iw, ih = img.size
    return img.crop(((iw - W) // 2, (ih - H) // 2, (iw - W) // 2 + W, (ih - H) // 2 + H))


def wrap(d, t, fnt, mw):
    words, lines, cur = t.split(), [], ""
    for w in words:
        tt = (cur + " " + w).strip()
        if d.textlength(tt, font=fnt) <= mw:
            cur = tt
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def scrim(img, strength=1.0):
    W, H = img.size
    g = Image.new("L", (1, H), 0)
    for y in range(H):
        g.putpixel((0, y), min(255, int((60 + 225 * max(0, (y - H * 0.36) / (H * 0.64))) * strength)))
    layer = Image.new("RGBA", (W, H), (5, 6, 9, 255)); layer.putalpha(g.resize((W, H)))
    img.alpha_composite(layer)


def spaced(d, xy, text, fnt, fill, sp, stroke=0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=BLACK)
        x += d.textlength(ch, font=fnt) + sp


def draw_headline(d, m, y, lines, fnt, lh, color, accent_word, accent_color, stroke):
    for ln in lines:
        if accent_word and accent_word in ln:
            x = m
            for i, part in enumerate(ln.split(accent_word)):
                if i > 0:
                    d.text((x, y), accent_word, font=fnt, fill=accent_color, stroke_width=stroke, stroke_fill=BLACK)
                    x += d.textlength(accent_word, font=fnt)
                if part:
                    d.text((x, y), part, font=fnt, fill=color, stroke_width=stroke, stroke_fill=BLACK)
                    x += d.textlength(part, font=fnt)
        else:
            d.text((m, y), ln, font=fnt, fill=color, stroke_width=stroke, stroke_fill=BLACK)
        y += lh
    return y


def cta(d, x, y, text, fnt, color, pad=28):
    tw = d.textlength(text, font=fnt)
    d.rounded_rectangle([x, y, x + tw + pad * 2, y + fnt.size + pad], radius=12, fill=color)
    d.text((x + pad, y + pad // 2 - 1), text, font=fnt, fill=(17, 17, 19))


def make(c, out_dir):
    W, H = c["size"]; m = int(W * 0.072)
    acc = c.get("accent_color")
    if isinstance(acc, str):
        acc = PALETTES.get(acc, GOLD)
    acc = tuple(acc) if acc else GOLD
    img = cover(Image.open(c["bg"]).convert("RGBA"), (W, H))
    mb = c.get("style") == "mrbeast"
    scrim(img, strength=0.7 if mb else 1.0)
    # MrBeast-слой: вырезанное лицо (PNG с альфой от любого rembg-инструмента, см. SKILL.md шаг 3.5)
    if c.get("face") and os.path.exists(c["face"]):
        fimg = Image.open(c["face"]).convert("RGBA")
        fh_px = int(H * c.get("face_scale", 0.92))
        s = fh_px / fimg.height
        fimg = fimg.resize((int(fimg.width * s), fh_px))
        side = c.get("face_side", "right")
        fx = (W - fimg.width + int(W * 0.04)) if side == "right" else int(-W * 0.04)
        fy = H - fimg.height
        sil = Image.new("RGBA", fimg.size, (0, 0, 0, 0))
        sil.putalpha(fimg.split()[3].point(lambda a: int(a * 0.55)))
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        shadow.paste(sil, (fx - 16, fy + 12), sil)
        img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(20)))
        img.alpha_composite(fimg, (fx, fy))
    d = ImageDraw.Draw(img)
    spaced(d, (m, m), c.get("brand", "BRAND"), f(int(W * 0.032), "Bold"), WHITE, 7)
    hsize, ssize = c.get("hsize", 88), c.get("ssize", 36)
    stroke = max(4, int(hsize * 0.07)) if mb else 0
    fh = f(hsize, "Black"); fa = f(int(hsize * 0.72), "ExtraBold")
    fe = f(int(ssize * 0.74), "SemiBold"); fs = f(ssize, "Medium"); fc = f(ssize, "SemiBold")
    lh = int(hsize * 1.08)            # межстрочный заголовка (больше воздуха)
    slh = ssize + 14                  # межстрочный подписи
    hl = wrap(d, c["headline"], fh, W - 2 * m)
    accent = c.get("accent", "")
    sub_lines = wrap(d, c["sub"], fs, W - 2 * m) if c.get("sub") else []
    # точный расчёт высоты блока (учитывает реальное число строк → ничего не наезжает)
    eb_h = (int(ssize * 0.74) + 12 + 4 + 24) if c.get("eyebrow") else 0
    acc_h = (6 + int(hsize * 0.72) + 18) if accent else 0
    sub_h = (20 + len(sub_lines) * slh) if sub_lines else 0
    cta_h = (28 + ssize + 28) if c.get("cta") else 0
    bh = eb_h + len(hl) * lh + acc_h + sub_h + cta_h
    y = H - m - bh
    if c.get("eyebrow"):
        spaced(d, (m, y), c["eyebrow"], fe, acc, 4); y += int(ssize * 0.74) + 12
        d.rectangle([m, y, m + 70, y + 4], fill=acc); y += 24
    y = draw_headline(d, m, y, hl, fh, lh, WHITE, c.get("accent_word"), acc, stroke)
    if accent:
        y += 6
        d.text((m, y), accent, font=fa, fill=acc, stroke_width=stroke, stroke_fill=BLACK)
        y += int(hsize * 0.72) + 18
    if sub_lines:
        y += 20
        for ln in sub_lines:
            d.text((m, y), ln, font=fs, fill=GREY); y += slh
    if c.get("cta"):
        y += 28
        cta(d, m, y, c["cta"], fc, acc)
    out = os.path.join(out_dir, f"final_{c['id']}.png")
    img.convert("RGB").save(out, quality=95)
    print(f"  {out} {W}x{H} [{c.get('style','clean')}/{c.get('accent_color','gold')}]")


def main():
    cfg = json.load(open(sys.argv[1]))
    out_dir = cfg.get("out_dir", os.path.dirname(os.path.abspath(sys.argv[1])))
    os.makedirs(out_dir, exist_ok=True)
    for c in cfg["creatives"]:
        c.setdefault("brand", cfg.get("brand", "BRAND"))
        c.setdefault("style", cfg.get("style", "clean"))
        make(c, out_dir)
    print("done")


if __name__ == "__main__":
    main()
