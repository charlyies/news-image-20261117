#!/usr/bin/env python3
"""Compose the news-image-20261117 entry: a newspaper front page
summarising Tuesday 17 November 2026, drawn with PIL and real Noto fonts.
Deterministic: no timestamps, no randomness, fixed palette and layout.
Run: python3 compose.py  ->  writes entry.png (1024x1024) in this directory.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CONTENT_W = W - 2 * MARGIN

PAPER = (250, 246, 236)
INK = (17, 17, 17)
RED = (178, 24, 24)
NAVY = (24, 48, 76)
SEA = (16, 38, 62)
STEEL = (148, 158, 168)
STEEL_DARK = (96, 106, 116)
FIRE = (232, 116, 28)
FIRE_YELLOW = (250, 196, 64)
SMOKE = (120, 122, 124)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/noto"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_BLACK = "NotoSerifDisplay-Black.ttf"
SERIF_BOLD = "NotoSerifDisplay-Bold.ttf"
SERIF = "NotoSerifDisplay-Regular.ttf"
SANS_BLACK = "NotoSans-Black.ttf"
SANS_BOLD = "NotoSans-Bold.ttf"
SANS = "NotoSans-Regular.ttf"


def text_width(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def fit_font(draw, text, name, start_size, max_width):
    """Largest font size (down from start_size) at which text fits max_width."""
    size = start_size
    while size > 10:
        fnt = font(name, size)
        if draw.textlength(text, font=fnt) <= max_width:
            return fnt
        size -= 2
    return font(name, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def centered(draw, y, text, fnt, fill=INK):
    draw.text((W / 2, y), text, font=fnt, fill=fill, anchor="ma")


def draw_bridge_scene(img, x0, y0, x1, y1):
    """Stylised Kerch Bridge scene: dusk sky, sea, a bridge deck with a
    collapsed span in the middle, smoke and fire at the gap. Drawn on a
    separate layer so nothing can spill outside the scene rectangle."""
    w, h = x1 - x0, y1 - y0
    layer = Image.new("RGB", (w, h), NAVY)
    draw = ImageDraw.Draw(layer)
    # Sky: horizontal bands, dusk blue darkening upward.
    bands = 12
    for i in range(bands):
        t = i / bands
        r = int(38 + (16 - 38) * t)
        g = int(66 + (34 - 66) * t)
        b = int(102 + (58 - 102) * t)
        draw.rectangle([0, h * 0.55 * i / bands, w, h * 0.55 * (i + 1) / bands],
                       fill=(r, g, b))
    horizon = int(h * 0.55)
    # A few fixed stars in the upper sky.
    for sx, sy in ((60, 18), (150, 40), (830, 22), (880, 48), (740, 14),
                   (250, 14), (420, 30)):
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(220, 228, 238))
    # Sea.
    draw.rectangle([0, horizon, w, h], fill=SEA)
    cx = w // 2
    # Smoke plume rising from the gap, kept inside the scene.
    smoke_circles = [
        (cx - 46, horizon - 72, 24), (cx - 14, horizon - 88, 30),
        (cx + 20, horizon - 76, 25), (cx + 48, horizon - 58, 19),
        (cx - 4, horizon - 108, 20),
    ]
    for sx, sy, sr in smoke_circles:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=SMOKE)
        draw.ellipse([sx - sr + 6, sy - sr + 6, sx + sr - 4, sy + sr - 4],
                     fill=(138, 140, 142))
    # Bridge deck: left segment and right segment, gap in the middle.
    deck_y = horizon - 34
    deck_h = 16
    gap = 150
    draw.rectangle([0, deck_y, cx - gap // 2, deck_y + deck_h], fill=STEEL)
    draw.rectangle([cx + gap // 2, deck_y, w, deck_y + deck_h], fill=STEEL)
    # Deck edge highlight.
    draw.rectangle([0, deck_y + deck_h - 4, cx - gap // 2, deck_y + deck_h],
                   fill=STEEL_DARK)
    draw.rectangle([cx + gap // 2, deck_y + deck_h - 4, w, deck_y + deck_h],
                   fill=STEEL_DARK)
    # Support pillars under each deck segment.
    for px in (70, 250, w - 250, w - 70):
        draw.rectangle([px - 9, deck_y + deck_h, px + 9, h - 26], fill=STEEL_DARK)
    # The fallen span: tilted slab sinking into the water at the gap.
    draw.polygon([
        (cx - gap // 2 + 6, deck_y + 4), (cx + gap // 2 - 14, deck_y + 30),
        (cx + gap // 2 - 40, horizon + 66), (cx - gap // 2 - 22, horizon + 44),
    ], fill=STEEL_DARK)
    draw.polygon([
        (cx - gap // 2 + 6, deck_y + 4), (cx + gap // 2 - 14, deck_y + 30),
        (cx + gap // 2 - 26, deck_y + 44), (cx - gap // 2 - 4, deck_y + 18),
    ], fill=STEEL)
    # Fire at the gap, on the waterline.
    for fx, fy, fr, col in (
            (cx - 26, horizon + 8, 22, FIRE), (cx + 8, horizon + 14, 25, FIRE),
            (cx - 8, horizon + 2, 15, FIRE_YELLOW), (cx + 30, horizon + 10, 12, FIRE_YELLOW)):
        draw.ellipse([fx - fr, fy - fr, fx + fr, fy + fr], fill=col)
    # Waves: short white strokes across the sea.
    for wx in range(24, w - 24, 74):
        wy = horizon + 52 + ((wx * 7) % 3) * 14
        draw.arc([wx, wy, wx + 52, wy + 12], start=200, end=340,
                 fill=(200, 214, 226), width=3)
    # Caption strip along the bottom of the scene.
    draw.rectangle([0, h - 34, w, h], fill=(10, 10, 10))
    cap = font(SANS_BOLD, 20)
    draw.text((14, h - 30), "THE KERCH BRIDGE, CRIMEA  —  ROAD SPAN IN THE STRAIT",
              font=cap, fill=WHITE)
    img.paste(layer, (x0, y0))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # ---- Masthead -------------------------------------------------------
    mast = fit_font(draw, "THE WORLD TODAY", SERIF_BLACK, 100, CONTENT_W)
    draw.text((W / 2, 26), "THE WORLD TODAY", font=mast, fill=INK, anchor="ma")
    # Double rule under the masthead.
    draw.line([(MARGIN, 138), (W - MARGIN, 138)], fill=INK, width=4)
    draw.line([(MARGIN, 146), (W - MARGIN, 146)], fill=INK, width=1)

    # ---- Date bar -------------------------------------------------------
    draw.rectangle([MARGIN, 158, W - MARGIN, 216], fill=RED)
    date_font = fit_font(draw, "TUESDAY, 17 NOVEMBER 2026", SANS_BLACK, 44,
                         CONTENT_W - 24)
    draw.text((W / 2, 187), "TUESDAY, 17 NOVEMBER 2026", font=date_font,
              fill=WHITE, anchor="mm")

    # ---- Lead kicker ----------------------------------------------------
    kicker = font(SANS_BLACK, 24)
    draw.text((MARGIN, 232), "LEAD STORY  •  UKRAINE WAR", font=kicker, fill=RED)

    # ---- Lead visual ----------------------------------------------------
    draw_bridge_scene(img, MARGIN, 268, W - MARGIN, 500)

    # ---- Lead headline --------------------------------------------------
    head = fit_font(draw, "KERCH BRIDGE FALLS", SERIF_BLACK, 88, CONTENT_W)
    draw.text((W / 2, 512), "KERCH BRIDGE FALLS", font=head, fill=INK, anchor="ma")
    deck_font = font(SERIF, 31)
    deck_lines = wrap(
        draw,
        "Ukraine strike drops a road span into the strait in a second night "
        "of attacks — the Kremlin vows to rebuild.",
        deck_font, CONTENT_W)
    y = 596
    for line in deck_lines:
        centered(draw, y, line, deck_font)
        y += 38

    # ---- Rule + "Also today" --------------------------------------------
    draw.line([(MARGIN, 690), (W - MARGIN, 690)], fill=INK, width=2)
    also = font(SANS_BLACK, 24)
    draw.text((MARGIN, 702), "ALSO TODAY", font=also, fill=RED)

    # ---- Secondary stories, 2 x 2 grid ----------------------------------
    stories = [
        ("MIDDLE EAST",
         "MINES HIT TANKERS IN HORMUZ",
         "Two oil tankers ablaze; Iran drones fired at a Bahrain base."),
        ("ASIA SUMMIT",
         "TRUMP LANDS IN MANILA",
         "Xi–Trump–Putin talks set for Thursday in Shenzhen."),
        ("MARKETS",
         "CHASE BLAMES A SOFTWARE BUG",
         "Banking outage hits online accounts and Zelle."),
        ("TECH",
         "NVIDIA REPORTS TONIGHT",
         "First results since Huang stepped down."),
    ]
    cell_w = (CONTENT_W - 28) // 2
    cell_h = 104
    grid_y = 740
    for i, (kicker_text, headline, deck) in enumerate(stories):
        col = i % 2
        row = i // 2
        cx0 = MARGIN + col * (cell_w + 28)
        cy0 = grid_y + row * (cell_h + 14)
        if col == 1:
            draw.line([(MARGIN + cell_w + 14, cy0 + 4),
                       (MARGIN + cell_w + 14, cy0 + cell_h - 4)],
                      fill=(190, 184, 170), width=1)
        kf = font(SANS_BLACK, 19)
        draw.text((cx0, cy0), kicker_text, font=kf, fill=RED)
        hf = fit_font(draw, headline, SERIF_BOLD, 31, cell_w)
        draw.text((cx0, cy0 + 26), headline, font=hf, fill=INK)
        df = font(SANS, 21)
        deck_lines = wrap(draw, deck, df, cell_w)
        dy = cy0 + 62
        for line in deck_lines[:2]:
            draw.text((cx0, dy), line, font=df, fill=(52, 52, 52))
            dy += 26

    # ---- Footer ---------------------------------------------------------
    draw.rectangle([MARGIN, 962, W - MARGIN, 1000], fill=INK)
    foot = font(SANS_BOLD, 20)
    draw.text((W / 2, 981),
              "KERCH BRIDGE  •  HORMUZ  •  MANILA  •  CHASE  •  NVIDIA",
              font=foot, fill=WHITE, anchor="mm")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, img.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
