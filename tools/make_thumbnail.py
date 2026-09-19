#!/usr/bin/env python3
"""Thumbnail generator for the Cities: Skylines II Turkish localization mod.

Usage:  python make_thumbnail.py [output.png]
Default output: <repo root>/Properties/Thumbnail.png  (repo root = parent of this script's folder)

Pure Pillow geometry (rectangles, polygons, ellipses, gradients). Everything is drawn on a
4x supersampled canvas and downscaled with LANCZOS, so every edge ends up anti-aliased.
All layout numbers below are in final 512px units.
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- canvas
SIZE = 512            # final image size
SS = 4                # supersampling factor
SEED = 29             # deterministic skyline / stars

# ---------------------------------------------------------------- palette
BG_TOP, BG_BOTTOM = "#0f172a", "#1e293b"
WHITE = "#ffffff"
CYAN = "#22d3ee"
SUBTITLE_COLOR = "#67e8f9"
FLAG_RED = "#E30A17"
RING_COLOR = "#f1f5f9"
GLOW_COLOR = "#dbeafe"
STAR_COLOR = "#cbd5e1"
WINDOW_LIT = ["#fbbf24", "#fbbf24", "#fde68a", "#f59e0b"]

# ---------------------------------------------------------------- layout
CX = SIZE // 2
SUBTITLE, SUB_SIZE, SUB_TRACK, SUB_BASELINE = "CITIES: SKYLINES II", 27, 5.5, 64
TITLE, TITLE_WIDTH, TITLE_TRACK, TITLE_BASELINE = "TÜRKÇE YAMA", 456, 2, 156
BADGE_Y, BADGE_R, RING_W = 258, 60, 3.5          # the "moon"
GLOW_R, GLOW_ALPHA = 150, 46                      # soft radial glow (alpha 0-255) - kept faint: flat look
HALO_R, HALO_ALPHA = 78, 16                       # flat, barely visible halo disc
FLAG_G = BADGE_R * 2.2                            # virtual flag height driving the emblem size
ROOF_LIMIT = BADGE_Y + BADGE_R + 34               # nothing of the city may rise above this (clear sky under the moon)
ANTENNA_SPACING = 150                             # min distance between antennas within a layer
STAR_COUNT = 24
EDGE_OVERSCAN = 40                                # towers are laid out a bit past both edges

# Skyline layers, far -> near. base/bump/jitter: tower heights (bump = extra height under the
# moon, spread = how wide that bump is); gaps: possible spacing between towers; roofs: roof styles
# to pick from; win: window cell (w, h, gap_x, gap_y); lit: lit-ratio range per tower; dim: how
# much lit windows are blended into the wall colour; peak: centre the tallest tower under the moon.
LAYERS = [
    dict(color="#3a5182", base=98, bump=64, spread=80, jitter=13, width=(22, 32), gaps=(3, 5, 8),
         roofs=("flat", "flat", "step", "step", "antenna"), win=None, lit=None, dim=0.0, peak=True),
    dict(color="#263659", base=78, bump=40, spread=120, jitter=15, width=(32, 48), gaps=(0, 0, 4),
         roofs=("flat", "line", "step", "slant"),
         win=(4, 5, 5, 6), lit=(0.2, 0.45), dim=0.38, peak=False),
    dict(color="#0a1020", base=58, bump=24, spread=150, jitter=20, width=(46, 72), gaps=(0,),
         roofs=("flat", "line", "line", "step", "antenna"),
         win=(5, 7, 5, 6), lit=(0.35, 0.7), dim=0.0, peak=False),
]

FONT_CANDIDATES = [  # (path, is_variable) - first one that loads wins
    ("C:/Windows/Fonts/bahnschrift.ttf", True),
    ("C:/Windows/Fonts/seguisb.ttf", False),
    ("C:/Windows/Fonts/segoeuib.ttf", False),
    ("C:/Windows/Fonts/arialbd.ttf", False),
    ("DejaVuSans-Bold.ttf", False),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", False),
    ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", False),
    ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", False),
    ("/Library/Fonts/Arial Bold.ttf", False),
]


# ---------------------------------------------------------------- helpers
def px(v):
    """512px units -> supersampled pixels."""
    return int(round(v * SS))


def rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(c1, c2, t):
    a, b = rgb(c1), rgb(c2)
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def rect(d, x0, y0, x1, y1, fill):
    d.rectangle([px(x0), px(y0), px(x1) - 1, px(y1) - 1], fill=fill)


def disc(d, cx, cy, r, fill):
    d.ellipse([px(cx - r), px(cy - r), px(cx + r), px(cy + r)], fill=fill)


def load_font(size, weight="Bold"):
    """First usable font of the chain at `size` (512px units); never raises."""
    for path, variable in FONT_CANDIDATES:
        try:
            font = ImageFont.truetype(path, px(size))
            if variable:
                try:
                    font.set_variation_by_name(weight)
                except Exception:
                    pass
            return font
        except Exception:
            continue
    try:
        return ImageFont.load_default(px(size))
    except Exception:
        return ImageFont.load_default()


# ---------------------------------------------------------------- text
def advances(font, text, tracking):
    """Per-character advances (kerning aware) plus manual letter-spacing, in supersampled px."""
    out = []
    for i, ch in enumerate(text):
        nxt = text[i + 1:i + 2]
        adv = font.getlength(ch + nxt) - font.getlength(nxt) if nxt else font.getlength(ch)
        out.append(adv + (px(tracking) if nxt else 0))
    return out


def draw_tracked(d, font, text, baseline, tracking, fill):
    """Draw horizontally centred, letter-spaced text char by char on a baseline."""
    adv = advances(font, text, tracking)
    x = px(CX) - sum(adv) / 2
    for ch, a in zip(text, adv):
        d.text((x, px(baseline)), ch, font=font, fill=fill, anchor="ls")
        x += a


def fit_font(text, width, tracking, start=96):
    """Largest font whose tracked text fits into `width`."""
    for size in range(start, 20, -1):
        font = load_font(size)
        if sum(advances(font, text, tracking)) <= px(width):
            return font
    return load_font(20)


# ---------------------------------------------------------------- scene parts
def background():
    img = Image.new("RGB", (px(SIZE), px(SIZE)))
    d = ImageDraw.Draw(img)
    for y in range(px(SIZE)):
        d.line([(0, y), (px(SIZE), y)], fill=mix(BG_TOP, BG_BOTTOM, y / (px(SIZE) - 1)))
    return img


def draw_glow(img):
    """Soft radial glow behind the badge, built as an exact alpha mask from concentric discs."""
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    steps = 160
    for i in range(steps):
        t = i / (steps - 1)                                   # 0 = outer edge, 1 = badge rim
        r = GLOW_R - (GLOW_R - BADGE_R) * t
        disc(md, CX, BADGE_Y, r, round(GLOW_ALPHA * t ** 2.2))
    img.paste(rgb(GLOW_COLOR), (0, 0), mask)
    ImageDraw.Draw(img, "RGBA").ellipse(
        [px(CX - HALO_R), px(BADGE_Y - HALO_R), px(CX + HALO_R), px(BADGE_Y + HALO_R)],
        fill=rgb(GLOW_COLOR) + (HALO_ALPHA,))


def draw_stars(d, rng):
    """A few tiny stars, balanced left/right, kept clear of the text block and the moon."""
    placed = 0
    while placed < STAR_COUNT:
        x = rng.uniform(8, CX) + (placed % 2) * (CX - 8)          # alternate halves
        y = rng.uniform(8, 335)
        in_text = 30 < x < SIZE - 30 and 34 < y < 182
        near_moon = math.hypot(x - CX, y - BADGE_Y) < HALO_R + 14
        if in_text or near_moon:
            continue
        r = rng.choice([0.9, 0.9, 1.2, 1.6])
        disc(d, x, y, r, rgb(STAR_COLOR) + (rng.choice([110, 160, 220]),))
        placed += 1


def draw_badge(d):
    """Red disc with a thin ring and a geometrically correct crescent and star."""
    disc(d, CX, BADGE_Y, BADGE_R + RING_W, RING_COLOR)
    disc(d, CX, BADGE_Y, BADGE_R, FLAG_RED)
    g = FLAG_G
    star_r, star_dx = 0.125 * g, 0.30 * g
    # Emblem spans from the crescent's left edge to the star's right tips; centre that box.
    left, right = -0.25 * g, star_dx + star_r * math.cos(math.radians(36))
    ox = CX - (left + right) / 2                      # centre of the outer crescent circle
    disc(d, ox, BADGE_Y, 0.25 * g, WHITE)             # outer circle (white)
    disc(d, ox + 0.0625 * g, BADGE_Y, 0.20 * g, FLAG_RED)   # inner circle, shifted to the fly
    pts = []
    for k in range(10):                               # star: first point faces LEFT (180 deg)
        r = star_r if k % 2 == 0 else star_r * 0.381966
        a = math.radians(180 + 36 * k)
        pts.append((px(ox + star_dx + r * math.cos(a)), px(BADGE_Y + r * math.sin(a))))
    d.polygon(pts, fill=WHITE)


def plan_layer(rng, spec):
    """Lay out one depth layer as (x, width, height, roof) towers, tallest under the moon."""
    towers, prev_h, last_mast = [], 0, -999
    x = -EDGE_OVERSCAN - rng.randint(0, 20)
    while x < SIZE + EDGE_OVERSCAN:
        w = rng.randint(*spec["width"])
        bump = math.exp(-((x + w / 2 - CX) / spec["spread"]) ** 2)
        h = prev_h
        while abs(h - prev_h) < 10:                   # neighbours never share a roof height
            h = spec["base"] + spec["bump"] * bump + rng.randint(-spec["jitter"], spec["jitter"])
        prev_h = h
        roof = rng.choice(spec["roofs"])
        if roof == "antenna":
            if x - last_mast < ANTENNA_SPACING:
                roof = "step"                         # keep antennas sparse
            else:
                last_mast = x
        towers.append([x, w, round(h), roof])
        x += w + rng.choice(spec["gaps"])
    if spec["peak"]:                                  # slide the layer so its peak is under the moon
        hero = max(towers, key=lambda t: t[2])
        hero[3] = "step"
        shift = round(CX - (hero[0] + hero[1] / 2))
        for t in towers:
            t[0] += shift
    return towers


def draw_layer(d, rng, spec):
    body = spec["color"]
    for x, w, h, roof in plan_layer(rng, spec):
        # Roof extras first, so the whole tower (incl. antenna) can be kept below the moon.
        cap = rng.randint(7, 11) if roof in ("step", "antenna") else 0       # top block height
        mast = rng.randint(12, 18) if roof == "antenna" else 0              # antenna height
        rise = rng.randint(8, 12) if roof == "slant" else 0                 # sloped roof rise
        top = max(SIZE - h, ROOF_LIMIT + cap + mast + rise)
        rect(d, x, top, x + w, SIZE, body)

        if roof == "slant":
            lo, hi = (x, x + w) if rng.random() < 0.5 else (x + w, x)
            d.polygon([(px(lo), px(top)), (px(hi), px(top)), (px(hi), px(top - rise))], fill=body)
        elif cap:
            cw = round(w * rng.choice([0.4, 0.5, 0.6]))
            cx0 = x + (w - cw) // 2
            rect(d, cx0, top - cap, cx0 + cw, top, body)
            if mast:
                ax, ay = cx0 + cw / 2, top - cap - mast
                rect(d, ax - 1, ay, ax + 1, top - cap, body)
                disc(d, ax, ay, 5, rgb(CYAN) + (45,))                        # tip halo
                disc(d, ax, ay, 2.3, CYAN)                                   # tip light
            else:
                rect(d, cx0, top - cap, cx0 + cw, top - cap + 1.5, CYAN)     # neon cap line
        elif roof == "line":
            rect(d, x, top, x + w, top + 1.5, CYAN)                          # neon roof line

        if spec["win"]:
            ww, wh, gx, gy = spec["win"]
            cols = (w - 10 + gx) // (ww + gx)
            x0 = x + (w - (cols * (ww + gx) - gx)) // 2
            unlit = mix(body, "#94a3b8", 0.09)
            lit_ratio = rng.uniform(*spec["lit"])
            for wy in range(top + 9, SIZE - wh, wh + gy):
                for c in range(cols):
                    lit = rng.random() < lit_ratio
                    color = mix(rng.choice(WINDOW_LIT), body, spec["dim"]) if lit else unlit
                    wx = x0 + c * (ww + gx)
                    rect(d, wx, wy, wx + ww, wy + wh, color)


# ---------------------------------------------------------------- main
def render():
    star_rng, city_rng = random.Random(SEED), random.Random(SEED + 1)
    img = background()
    draw_glow(img)
    d = ImageDraw.Draw(img, "RGBA")                   # "RGBA" mode blends translucent fills
    draw_stars(d, star_rng)
    for spec in LAYERS:
        draw_layer(d, city_rng, spec)
    draw_badge(d)
    draw_tracked(d, load_font(SUB_SIZE, "SemiBold"), SUBTITLE, SUB_BASELINE, SUB_TRACK, SUBTITLE_COLOR)
    draw_tracked(d, fit_font(TITLE, TITLE_WIDTH, TITLE_TRACK), TITLE, TITLE_BASELINE, TITLE_TRACK, WHITE)
    return img.resize((SIZE, SIZE), Image.LANCZOS)


def main():
    default = Path(__file__).resolve().parent.parent / "Properties" / "Thumbnail.png"
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    out.parent.mkdir(parents=True, exist_ok=True)
    render().save(out, "PNG", optimize=True)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
