#!/usr/bin/env python3
"""
build_thumbnail.py — собирает MrBeast-обложку из конфига (детерминированно, 0 токенов).

Слои (фиксированный рецепт, см. SKILL.md):
  реальный скриншот-фон -> затемнение+градиент -> вырезанное лицо с тенью -> текст с обводкой -> акценты(овал/бейдж)

Usage:
  build_thumbnail.py config.json
Конфиг — JSON, см. tools/example_config.json. Все координаты в пикселях холста.

Палитра (имена цветов в конфиге): yellow cyan green red white black  (или "#RRGGBB").
Шрифт: бандл assets/fonts/Montserrat.ttf (относительно скилла). Переопределяется "font" в конфиге.
"""
import sys, json, os, shutil, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PALETTE = {
    "yellow": (255, 210, 0), "cyan": (150, 240, 255), "green": (43, 227, 77),
    "red": (237, 28, 36), "white": (255, 255, 255), "black": (0, 0, 0),
}
# Bundled font ships with this skill (Cyrillic-ready). Falls back to system bolds.
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_CANDIDATES = [
    os.path.join(SKILL_DIR, "assets", "fonts", "Montserrat.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]

def col(c):
    if isinstance(c, (list, tuple)): return tuple(c)
    if isinstance(c, str) and c.startswith("#"):
        h = c[1:]; return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return PALETTE.get(c, (255, 255, 255))

def find_font(cfg):
    f = cfg.get("font")
    if f and os.path.exists(f): src = f
    else:
        src = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
        if not src: raise SystemExit("No bold font found; set 'font' in config")
    # копируем в путь без пробелов (ffmpeg/PIL дружелюбнее)
    dst = os.path.join(tempfile.gettempdir(), "thumb_font" + os.path.splitext(src)[1])
    if not os.path.exists(dst): shutil.copy(src, dst)
    return dst

def cover(path, W, H):
    im = Image.open(path).convert("RGB")
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r), int(im.height * r)))
    x = (im.width - W) // 2; y = (im.height - H) // 2
    return im.crop((x, y, x + W, y + H)).convert("RGBA")

def vgrad(img, W, H, color, top_a, bot_a):
    g = Image.new("L", (1, H))
    for y in range(H): g.putpixel((0, y), int(top_a + (bot_a - top_a) * y / H))
    ov = Image.new("RGBA", (W, H), tuple(color) + (0,)); ov.putalpha(g.resize((W, H)))
    return Image.alpha_composite(img, ov)

def place_face(cv, W, H, face, h, dx=0, dy=0, shadow=True):
    fw = int(face.width * h / face.height); f = face.resize((fw, h))
    x = W - fw + dx; y = H - h + dy
    if shadow:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); a = f.split()[3]
        sil = Image.new("RGBA", (fw, h), (0, 0, 0, 170)); sil.putalpha(a)
        sh.paste(sil, (x + 16, y + 14), sil)
        cv.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    cv.alpha_composite(f, (x, y))

def main():
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    W, H = cfg.get("size", [1080, 1920])
    FONT = find_font(cfg)
    def F(s): return ImageFont.truetype(FONT, s)

    # 1) фон — реальный скриншот (доверие)
    cv = cover(cfg["background"], W, H)
    # 2) затемнение + градиент под текст
    if cfg.get("bg_darken"):
        cv = Image.alpha_composite(cv, Image.new("RGBA", (W, H), (0, 0, 0, cfg["bg_darken"])))
    g = cfg.get("gradient")
    if g: cv = vgrad(cv, W, H, col(g.get("color", "black")), g.get("top", 190), g.get("bottom", 50))
    # 3) вырезанное лицо
    if cfg.get("face"):
        face = Image.open(cfg["face"]).convert("RGBA")
        place_face(cv, W, H, face, cfg.get("face_height", 1600),
                   cfg.get("face_dx", 250), cfg.get("face_dy", 0), cfg.get("face_shadow", True))
    d = ImageDraw.Draw(cv)
    # 4) акцент-плашки (рисуем ПОД текстом)
    for box in cfg.get("boxes", []):
        d.rounded_rectangle(box["xy"], box.get("radius", 16), fill=tuple(col(box.get("color", "black"))) + (box.get("alpha", 160),))
    # 5) текст с толстой обводкой
    for t in cfg.get("texts", []):
        d.text(tuple(t["xy"]), t["text"], font=F(t["size"]), fill=col(t.get("color", "white")),
               stroke_width=t.get("stroke", 0), stroke_fill=col(t.get("stroke_color", "black")),
               anchor=t.get("anchor", "la"))
    # 6) «маркерные» овалы (эмоц. акцент, как от руки)
    for el in cfg.get("ellipses", []):
        c = col(el.get("color", "red")); w = el.get("width", 9); b = el["xy"]
        d.ellipse(b, outline=c, width=w)
        d.ellipse([b[0]+3, b[1]+3, b[2]+3, b[3]+3], outline=c, width=max(1, w-1))

    out = cfg["output"]
    cv.convert("RGB").save(out, quality=cfg.get("quality", 92))
    print("saved:", out)

if __name__ == "__main__":
    main()
