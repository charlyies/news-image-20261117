#!/usr/bin/env python3
"""Draw the 17 November 2026 front page: 'THE WORLD TODAY'.

A newspaper front page summarising the day's world news in one image.
Everything is drawn in code with Pillow and real Noto fonts, so every
word is spelled correctly and legible. The build is fully deterministic:
fixed palette, fixed layout, fixed fonts, no timestamps, no randomness.

Run:  python3 compose.py        -> writes entry.png next to this file.
"""

from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/usr/share/fonts/truetype/noto"

SERIF_BLACK = FONT_DIR + "/NotoSerifDisplay-Black.ttf"
SERIF_REGULAR = FONT_DIR + "/NotoSerifDisplay-Regular.ttf"
SANS_BLACK = FONT_DIR + "/NotoSans-Black.ttf"
SANS_BOLD = FONT_DIR + "/NotoSans-Bold.ttf"
SANS_REGULAR = FONT_DIR + "/NotoSans-Regular.ttf"

W, H = 1024, 1024
MARGIN = 36
CONTENT_W = W - 2 * MARGIN          # 952
CX = W // 2                         # 512

PAPER = (250, 246, 236)
INK = (17, 17, 17)
RED = (178, 24, 24)
WHITE = (255, 255, 255)

SCENE_Y = 268
SCENE_H = 240                       # scene runs 268..508
SCENE_W = CONTENT_W


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(path, text, max_width, start):
    """Largest font size (<= start) whose text fits max_width."""
    size = start
    while size > 8:
        f = font(path, size)
        if f.getlength(text) <= max_width:
            return f
        size -= 1
    return font(path, 8)


def wrap(draw, text, f, max_width):
    """Greedy word wrap; returns a list of lines."""
    lines, current = [], ""
    for word in text.split(" "):
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=f) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


# ---------------------------------------------------------------- scene ---

def teardrop_points(cx, base_y, width, height, lean=0.0):
    """Outline of a flame tongue: pointed tip, fat belly, round base.

    lean shifts the tip sideways so the flame bends in the wind.
    """
    import math
    steps = 24
    left, right = [], []
    for i in range(steps + 1):
        s = i / steps                    # 0 = base, 1 = tip
        y = base_y - s * height
        # belly peaks about a third of the way up, tip pinches to a point
        half = width * (abs(math.sin(math.pi * (s ** 0.75))) ** 0.85)
        half *= 1.0 - 0.30 * s
        x_off = lean * s * s
        left.append((cx - half + x_off, y))
        right.append((cx + half + x_off, y))
    return left + right[::-1]


def flame_tongue(layer, cx, base_y, width, height, lean=0.0):
    """One layered flame: red outside, orange middle, yellow core."""
    draw = ImageDraw.Draw(layer)
    draw.polygon(teardrop_points(cx, base_y, width, height, lean),
                 fill=(198, 38, 16, 235))
    draw.polygon(teardrop_points(cx + 2, base_y, width * 0.70, height * 0.74, lean),
                 fill=(238, 108, 18, 240))
    draw.polygon(teardrop_points(cx + 3, base_y, width * 0.44, height * 0.50, lean),
                 fill=(250, 196, 58, 245))
    draw.polygon(teardrop_points(cx + 3, base_y, width * 0.20, height * 0.28, lean),
                 fill=(255, 240, 170, 250))


def cloud(layer, x, y, scale, base, light):
    """A layered cloud: overlapping ellipses, paler on top."""
    draw = ImageDraw.Draw(layer)
    puffs = [(-46, 6, 52, 26), (-18, -8, 60, 30), (16, 2, 56, 28),
             (42, 8, 40, 20), (-2, 10, 70, 22)]
    for dx, dy, w, h in puffs:
        draw.ellipse([x + dx * scale - w * scale / 2, y + dy * scale - h * scale / 2,
                      x + dx * scale + w * scale / 2, y + dy * scale + h * scale / 2],
                     fill=base)
    for dx, dy, w, h in [(-18, -12, 46, 20), (14, -10, 40, 18), (-40, 0, 30, 14)]:
        draw.ellipse([x + dx * scale - w * scale / 2, y + dy * scale - h * scale / 2,
                      x + dx * scale + w * scale / 2, y + dy * scale + h * scale / 2],
                     fill=light)


def draw_scene():
    """The lead illustration: Kerch Bridge span down in the strait, at night.

    Drawn on its own RGBA layer the size of the scene box, so nothing can
    spill outside the frame. Sky gradient + fire glow, bridge with railings,
    cables and towers, a tilted fallen span, layered flames, drifting
    smoke, a dark sea with a column of firelight reflected in it.
    """
    import math
    layer = Image.new("RGBA", (SCENE_W, SCENE_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    water_y = 168          # horizon / waterline inside the scene
    fire_x, fire_y = 482, 152

    # --- sky: deep navy at the top, violet in the middle, warm near the sea
    stops = [(0.0, (9, 17, 40)), (0.45, (30, 28, 66)),
             (0.70, (88, 46, 70)), (1.0, (122, 58, 52))]
    for y in range(water_y):
        t = y / water_y
        col = stops[-1][1]
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                col = lerp(c0, c1, (t - t0) / (t1 - t0))
                break
        draw.line([(0, y), (SCENE_W - 1, y)], fill=col + (255,))

    # --- stars, fixed positions
    for sx, sy, r, a in [(60, 26, 2, 220), (150, 48, 1, 160), (240, 22, 2, 200),
                         (330, 40, 1, 150), (620, 30, 2, 210), (700, 52, 1, 160),
                         (830, 24, 2, 200), (905, 44, 1, 170), (90, 78, 1, 140),
                         (880, 84, 1, 140), (270, 66, 1, 130), (660, 78, 1, 130)]:
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(235, 238, 250, a))

    # --- fire glow: soft concentric ellipses hugging the flames, warm orange.
    # Drawn on a separate overlay and alpha-composited, so the faint rings
    # truly blend into the sky instead of letting the paper show through.
    glow = Image.new("RGBA", (SCENE_W, SCENE_H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    for rx, ry, alpha in [(200, 88, 22), (160, 66, 34), (120, 50, 48),
                          (85, 36, 70), (55, 24, 100)]:
        gdraw.ellipse([fire_x - rx, fire_y - 10 - ry, fire_x + rx, fire_y - 10 + ry],
                      fill=(255, 88, 18, alpha))
    layer = Image.alpha_composite(layer, glow)
    draw = ImageDraw.Draw(layer)

    # --- clouds, kept clear of the fire column
    cloud(layer, 150, 46, 1.0, (88, 98, 132, 235), (146, 154, 180, 235))
    cloud(layer, 800, 40, 0.85, (82, 92, 128, 235), (138, 148, 176, 235))
    cloud(layer, 330, 26, 0.55, (76, 86, 122, 220), (130, 140, 168, 220))

    # --- sea: dark navy, lighter toward the glow
    for y in range(water_y, SCENE_H):
        t = (y - water_y) / (SCENE_H - water_y)
        col = lerp((16, 30, 58), (8, 18, 40), t)
        draw.line([(0, y), (SCENE_W - 1, y)], fill=col + (255,))

    # --- reflection column + wave dashes: faint marks on the water, drawn
    # on their own overlay and composited so they blend with the sea.
    water_fx = Image.new("RGBA", (SCENE_W, SCENE_H), (0, 0, 0, 0))
    wdraw = ImageDraw.Draw(water_fx)
    for sx, wdt, col, top_a in [(438, 5, (255, 150, 40), 150),
                                (456, 7, (255, 180, 60), 170),
                                (474, 6, (250, 120, 30), 160),
                                (492, 8, (255, 200, 80), 180),
                                (510, 5, (255, 150, 40), 150),
                                (528, 4, (240, 110, 30), 120)]:
        for seg, a in enumerate([top_a, int(top_a * 0.6), int(top_a * 0.3)]):
            y0 = water_y + 3 + seg * 13
            wdraw.rectangle([sx, y0, sx + wdt, y0 + 11], fill=col + (a,))
    for wy, x0, length, a in [(178, 40, 46, 120), (178, 640, 52, 120),
                              (192, 120, 60, 100), (192, 760, 44, 100),
                              (204, 30, 40, 80), (204, 580, 58, 80),
                              (206, 860, 50, 80), (188, 340, 34, 90)]:
        wdraw.line([(x0, wy), (x0 + length, wy)], fill=(96, 128, 175, a), width=2)
    layer = Image.alpha_composite(layer, water_fx)
    draw = ImageDraw.Draw(layer)

    # --- bridge towers: twin legs, cross beams, X bracing, above the deck
    def tower(tx):
        leg = (104, 112, 126, 255)
        beam = (88, 96, 112, 255)
        draw.rectangle([tx - 16, 52, tx - 7, water_y], fill=leg)
        draw.rectangle([tx + 7, 52, tx + 16, water_y], fill=leg)
        for by in (66, 92):
            draw.rectangle([tx - 16, by, tx + 16, by + 6], fill=beam)
        draw.line([(tx - 16, 72), (tx + 16, 92)], fill=beam, width=4)
        draw.line([(tx + 16, 72), (tx - 16, 92)], fill=beam, width=4)
        draw.rectangle([tx - 19, 48, tx + 19, 54], fill=(126, 134, 148, 255))

    tower(150)
    tower(802)

    # --- suspension cables: shallow sagging curves from tower to tower
    def cable(x0, y0, x1, y1, sag):
        pts = []
        for i in range(21):
            t = i / 20
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)
            pts.append((x, y))
        draw.line(pts, fill=(150, 158, 170, 255), width=3)

    cable(0, 84, 392, 108, 10)
    cable(560, 108, SCENE_W, 84, 10)

    # --- deck segments left and right of the gap, with railings
    def deck(x0, x1, broken_left=False, broken_right=False):
        top, mid, bot = 112, 124, 130
        draw.rectangle([x0, top, x1, top + 4], fill=(152, 160, 170, 255))
        draw.rectangle([x0, top + 4, x1, mid], fill=(112, 120, 132, 255))
        draw.rectangle([x0, mid, x1, bot], fill=(70, 78, 90, 255))
        # railing: posts + two horizontal rails
        for px in range(x0 + 6, x1, 28):
            draw.rectangle([px, top - 16, px + 2, top], fill=(130, 138, 150, 255))
        draw.line([(x0, top - 16), (x1, top - 16)], fill=(140, 148, 160, 255), width=2)
        draw.line([(x0, top - 8), (x1, top - 8)], fill=(140, 148, 160, 255), width=2)
        # suspender cables from the main cable down to the deck
        for px in range(x0 + 20, x1, 40):
            draw.line([(px, top - 26), (px, top)], fill=(150, 158, 170, 255), width=2)
        # jagged broken edge: a row of small triangles
        if broken_right:
            for ty in [top, top + 5, top + 10]:
                draw.polygon([(x1, ty), (x1 + 12, ty + 3), (x1, ty + 6)],
                             fill=(96, 104, 116, 255))
        if broken_left:
            for ty in [top, top + 5, top + 10]:
                draw.polygon([(x0, ty), (x0 - 12, ty + 3), (x0, ty + 6)],
                             fill=(96, 104, 116, 255))

    deck(0, 392, broken_right=True)
    deck(560, SCENE_W, broken_left=True)

    # --- fallen span: tilted ~20 degrees, half sunk, jagged break, bent rebar
    span = [(402, 108), (560, 172), (548, 200), (390, 136)]
    draw.polygon(span, fill=(88, 96, 110, 255))
    draw.line([(402, 108), (560, 172)], fill=(140, 148, 160, 255), width=4)
    draw.line([(390, 136), (548, 200)], fill=(60, 68, 82, 255), width=3)
    for tx, ty in [(402, 108), (396, 122), (390, 136)]:
        draw.polygon([(tx, ty), (tx - 12, ty + 4), (tx, ty + 8)],
                     fill=(72, 80, 94, 255))
    # bent steel rods sticking out of the broken end
    for (rx0, ry0, rx1, ry1) in [(398, 118, 372, 108), (394, 128, 366, 126),
                                 (392, 136, 370, 144)]:
        draw.line([(rx0, ry0), ((rx0 + rx1) // 2, (ry0 + ry1) // 2 - 4), (rx1, ry1)],
                  fill=(60, 66, 78, 255), width=2)
    # snapped railing stubs on the fallen span
    draw.line([(430, 122), (520, 158)], fill=(130, 138, 150, 255), width=2)
    for px, py in [(445, 128), (475, 140), (505, 152)]:
        draw.line([(px, py), (px, py - 10)], fill=(130, 138, 150, 255), width=2)

    # --- flames: a tall central tongue, two shorter ones, one low by the water
    flame_tongue(layer, 478, 168, 34, 92, lean=10)
    flame_tongue(layer, 512, 176, 24, 62, lean=14)
    flame_tongue(layer, 448, 164, 20, 52, lean=6)
    flame_tongue(layer, 536, 196, 16, 34, lean=8)

    # --- embers drifting up from the fire
    for ex, ey, r, col in [(470, 66, 2, (255, 180, 60, 240)),
                           (492, 52, 2, (255, 140, 40, 230)),
                           (508, 70, 1, (255, 200, 90, 230)),
                           (456, 84, 1, (240, 120, 30, 220)),
                           (524, 58, 2, (255, 160, 50, 230)),
                           (486, 40, 1, (255, 190, 80, 220))]:
        draw.ellipse([ex - r, ey - r, ex + r, ey + r], fill=col)

    # --- smoke: three grey tones, leaning right with the wind, rising clear
    # of the flame tips so the fire reads first
    smoke = [(478, 96, 24, (44, 44, 52, 245)),
             (500, 78, 28, (86, 88, 98, 245)),
             (524, 60, 26, (126, 128, 138, 245)),
             (546, 44, 22, (150, 152, 160, 245)),
             (564, 30, 16, (168, 170, 178, 245)),
             (456, 86, 18, (70, 72, 82, 245)),
             (534, 76, 16, (104, 106, 116, 245))]
    for sx, sy, r, col in smoke:
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=col)
    # thin wisps curling off the main column
    draw.arc([540, 18, 620, 66], start=200, end=330, fill=(170, 172, 180, 200), width=3)
    draw.arc([420, 60, 470, 104], start=180, end=300, fill=(120, 122, 132, 200), width=3)

    # --- floating debris near the fallen span
    for (dx, dy, w, h, ang) in [(586, 198, 22, 6, 12), (612, 206, 16, 5, -8),
                                (420, 206, 18, 5, 6), (566, 210, 12, 4, 20)]:
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        corners = []
        for ox, oy in [(-w / 2, -h / 2), (w / 2, -h / 2),
                       (w / 2, h / 2), (-w / 2, h / 2)]:
            corners.append((dx + ox * ca - oy * sa, dy + ox * sa + oy * ca))
        draw.polygon(corners, fill=(28, 30, 36, 255))
        draw.line([corners[0], corners[1]], fill=(90, 96, 108, 255), width=1)

    # --- caption strip pinned to the bottom of the scene
    draw.rectangle([0, SCENE_H - 26, SCENE_W, SCENE_H], fill=(0, 0, 0, 255))
    cap = "THE KERCH BRIDGE, CRIMEA  —  ROAD SPAN IN THE STRAIT"
    cap_font = fit(SANS_BOLD, cap, SCENE_W - 24, 20)
    draw.text((SCENE_W // 2, SCENE_H - 13), cap, font=cap_font,
              fill=WHITE + (255,), anchor="mm")
    return layer


# ----------------------------------------------------------------- page ---

STORIES = [
    ("MIDDLE EAST", "MINES HIT TANKERS IN HORMUZ",
     "Two oil tankers ablaze; Iran drones fired at a Bahrain base."),
    ("ASIA SUMMIT", "TRUMP LANDS IN MANILA",
     "Xi–Trump–Putin talks set for Thursday in Shenzhen."),
    ("MARKETS", "CHASE BLAMES A SOFTWARE BUG",
     "Banking outage hits online accounts and Zelle."),
    ("TECH", "NVIDIA REPORTS TONIGHT",
     "First results since Huang stepped down."),
]


def build():
    page = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(page)

    # --- masthead, fitted to the content width
    mast = fit(SERIF_BLACK, "THE WORLD TODAY", CONTENT_W, 118)
    draw.text((CX, 26), "THE WORLD TODAY", font=mast, fill=INK, anchor="ma")

    # --- double rule under the masthead
    draw.rectangle([MARGIN, 138, W - MARGIN, 141], fill=INK)
    draw.rectangle([MARGIN, 146, W - MARGIN, 146], fill=INK)

    # --- red date bar
    draw.rectangle([MARGIN, 158, W - MARGIN, 216], fill=RED)
    date_font = fit(SANS_BLACK, "TUESDAY, 17 NOVEMBER 2026", CONTENT_W - 40, 46)
    draw.text((CX, 187), "TUESDAY, 17 NOVEMBER 2026",
              font=date_font, fill=WHITE, anchor="mm")

    # --- kicker above the lead scene
    draw.text((MARGIN, 232), "LEAD STORY  •  UKRAINE WAR",
              font=font(SANS_BLACK, 24), fill=RED, anchor="la")

    # --- lead scene (drawn once, pasted once)
    scene = draw_scene()
    page.paste(scene, (MARGIN, SCENE_Y), scene)

    # --- headline under the scene (kept compact so the deck clears the rule)
    head_y = SCENE_Y + SCENE_H + 10
    head = fit(SERIF_BLACK, "KERCH BRIDGE FALLS", CONTENT_W, 80)
    draw.text((CX, head_y), "KERCH BRIDGE FALLS", font=head, fill=INK, anchor="ma")
    head_bottom = head_y + head.getbbox("KERCH BRIDGE FALLS")[3]

    # --- deck, centred, wrapped to two lines
    deck_font = font(SERIF_REGULAR, 29)
    deck_text = ("Ukraine strike drops a road span into the strait in a second "
                 "night of attacks — the Kremlin vows to rebuild.")
    deck_lines = wrap(draw, deck_text, deck_font, CONTENT_W)
    deck_y = head_bottom + 8
    for i, line in enumerate(deck_lines):
        draw.text((CX, deck_y + i * 36), line, font=deck_font,
                  fill=INK, anchor="ma")

    # --- rule + ALSO TODAY
    draw.rectangle([MARGIN, 690, W - MARGIN, 691], fill=INK)
    draw.text((MARGIN, 702), "ALSO TODAY", font=font(SANS_BLACK, 26),
              fill=RED, anchor="la")

    # --- 2x2 grid of secondary stories
    grid_y, cell_w, cell_h = 740, 462, 104
    col_gap, row_gap = 28, 14
    # thin divider between the two columns
    draw.line([(CX, grid_y), (CX, grid_y + 2 * cell_h + row_gap)],
              fill=(205, 196, 186), width=1)
    for idx, (section, title, body) in enumerate(STORIES):
        col, row = idx % 2, idx // 2
        x = MARGIN + col * (cell_w + col_gap)
        y = grid_y + row * (cell_h + row_gap)
        draw.text((x, y), section, font=font(SANS_BLACK, 18), fill=RED, anchor="la")
        title_font = fit(SERIF_BLACK, title, cell_w, 29)
        draw.text((x, y + 24), title, font=title_font, fill=INK, anchor="la")
        body_font = font(SANS_REGULAR, 20)
        for j, line in enumerate(wrap(draw, body, body_font, cell_w)):
            draw.text((x, y + 60 + j * 22), line, font=body_font,
                      fill=INK, anchor="la")

    # --- footer strip
    draw.rectangle([MARGIN, 962, W - MARGIN, 1000], fill=INK)
    foot = fit(SANS_BOLD, "KERCH BRIDGE  •  HORMUZ  •  MANILA  •  CHASE  •  NVIDIA",
               CONTENT_W - 40, 20)
    draw.text((CX, 981), "KERCH BRIDGE  •  HORMUZ  •  MANILA  •  CHASE  •  NVIDIA",
              font=foot, fill=WHITE, anchor="mm")

    page.save("entry.png", format="PNG")
    print("wrote entry.png", page.size)


if __name__ == "__main__":
    build()
