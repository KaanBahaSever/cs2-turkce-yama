#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates the placeholder Paradox Mods thumbnail (Properties/Thumbnail.png, 512x512).

    python tools/make_thumbnail.py [version]

The version defaults to the one in mod.json. Requires Pillow (pip install pillow).
"""
import io
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ROOT, "Properties", "Thumbnail.png")
SIZE = 512
BG_TOP, BG_BOTTOM = (30, 40, 58), (20, 27, 40)      # around #1a2230
ACCENT = (64, 186, 213)                              # CS2-like cyan
RED = (227, 10, 23)                                  # Turkish flag red
WHITE, MUTED = (240, 244, 250), (150, 164, 184)

FONT_DIRS = [r"C:\Windows\Fonts", "/usr/share/fonts/truetype/dejavu", "/Library/Fonts", "/System/Library/Fonts"]
BOLD = ["bahnschrift.ttf", "segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf", "Arial Bold.ttf"]
REGULAR = ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf", "Arial.ttf"]


def font(candidates, size):
    for folder in FONT_DIRS:
        for name in candidates:
            path = os.path.join(folder, name)
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def fit(draw, text, candidates, max_width, start, spacing=0):
    """Largest font size (<= start) at which the text fits the width."""
    size = start
    while size > 10:
        f = font(candidates, size)
        if text_width(draw, text, f, spacing) <= max_width:
            return f
        size -= 1
    return font(candidates, size)


def text_width(draw, text, f, spacing=0):
    return sum(draw.textlength(ch, font=f) for ch in text) + spacing * (len(text) - 1)


def centered(draw, y, text, f, fill, spacing=0):
    x = (SIZE - text_width(draw, text, f, spacing)) / 2
    for ch in text:                                   # manual tracking for a cleaner title look
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + spacing


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else json.load(io.open(os.path.join(ROOT, "mod.json"), encoding="utf-8"))["Version"]

    img = Image.new("RGB", (SIZE, SIZE), BG_BOTTOM)
    px = img.load()
    for y in range(SIZE):                             # vertical gradient
        t = y / (SIZE - 1)
        row = tuple(int(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOTTOM))
        for x in range(SIZE):
            px[x, y] = row

    # soft glow behind the title
    glow = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
    ImageDraw.Draw(glow).ellipse((96, 120, 416, 360), fill=(26, 58, 78))
    img = Image.blend(img, Image.composite(glow.filter(ImageFilter.GaussianBlur(70)), img, glow.convert("L").filter(ImageFilter.GaussianBlur(70))), 0.55)
    d = ImageDraw.Draw(img)

    # faint skyline along the bottom
    heights = [38, 62, 46, 88, 54, 110, 70, 96, 48, 128, 66, 84, 52, 104, 60, 76, 44, 92, 58, 40]
    w = SIZE / len(heights)
    for i, h in enumerate(heights):
        d.rectangle((i * w + 2, SIZE - 24 - h * 0.62, (i + 1) * w - 2, SIZE - 24), fill=(34, 46, 66))

    # subtle double border
    d.rounded_rectangle((10, 10, SIZE - 11, SIZE - 11), radius=18, outline=(52, 66, 90), width=2)
    d.rounded_rectangle((18, 18, SIZE - 19, SIZE - 19), radius=13, outline=(38, 50, 70), width=1)

    inner = SIZE - 96
    f1 = fit(d, "CITIES: SKYLINES II", BOLD, inner, 38, spacing=3)
    centered(d, 150, "CITIES: SKYLINES II", f1, ACCENT, spacing=3)

    d.rectangle((SIZE / 2 - 46, 206, SIZE / 2 + 46, 209), fill=RED)

    f2 = fit(d, "TÜRKÇE YERELLEŞTİRME", BOLD, inner, 40, spacing=1)
    centered(d, 232, "TÜRKÇE YERELLEŞTİRME", f2, WHITE, spacing=1)

    f3 = font(REGULAR, 24)
    label = "v%s Standalone" % version
    tw = text_width(d, label, f3)
    d.rounded_rectangle(((SIZE - tw) / 2 - 18, 300, (SIZE + tw) / 2 + 18, 342), radius=21, fill=(28, 38, 56), outline=(60, 78, 106), width=1)
    centered(d, 306, label, f3, MUTED)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print("wrote %s  %dx%d  %d bytes" % (os.path.relpath(OUT, ROOT), img.width, img.height, os.path.getsize(OUT)))


if __name__ == "__main__":
    main()
