"""Share images (1200x630) for links on X, LinkedIn, iMessage, etc."""
from pathlib import Path

W, H = 1200, 630
BG, INK, MUTED, ACCENT, LIGHT = "#f7f8f6", "#1b2126", "#5d6870", "#1f6f5c", "#f7f8f6"
FONTS = Path(__file__).parent / "fonts"

try:
    from PIL import Image, ImageDraw, ImageFont
    OK = True
except Exception:  # Pillow missing: pages still build, just without images
    OK = False


def _font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def _wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def _mark(draw, x, y, s):
    draw.rounded_rectangle([x, y, x + s, y + s], radius=int(s * .22), fill=ACCENT)
    c, r, w = (x + s / 2, y + s / 2), s * .28, max(3, int(s * .08))
    draw.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=LIGHT, width=w)
    draw.line([c, (c[0], c[1] - r * .62)], fill=LIGHT, width=w)
    draw.line([c, (c[0] + r * .45, c[1] + r * .33)], fill=LIGHT, width=w)


def card(out_path, title, eyebrow="", footer="geteveryhour.lol  ·  by Tineessa Nelson"):
    if not OK:
        return False
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, H - 14, W, H], fill=ACCENT)
    _mark(d, 72, 64, 64)
    d.text((152, 70), "EveryHour", font=_font("display-700.woff", 44), fill=INK)
    if eyebrow:
        d.text((72, 178), eyebrow.upper(), font=_font("display-700.woff", 26), fill=ACCENT)
    size = 76
    while True:
        f = _font("display-700.woff", size)
        lines = _wrap(d, title, f, W - 144)
        if len(lines) <= 3 or size <= 48:
            break
        size -= 6
    lines = lines[:4]
    y = 228
    for ln in lines:
        d.text((72, y), ln, font=f, fill=INK)
        y += int(size * 1.12)
    d.text((72, H - 84), footer, font=_font("body-400.woff", 28), fill=MUTED)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    return True
