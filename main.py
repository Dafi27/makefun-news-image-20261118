#!/usr/bin/env python3
"""World news of Wednesday 18 November 2026, summed up in one image.

Draws a newspaper front page: a masthead naming the day, then five
stories first reported on 18 November 2026, each with a drawn picture,
a headline and a one-line caption:

  1. Trump lands in Manila for Quad talks, ahead of a China visit.
  2. Ukraine hits the Crimean bridge for a second day; Russia pounds Kyiv.
  3. Iran drones hit a US radar site in Bahrain; Kuwait reports drones too.
  4. Nvidia sales jump 103% in the quarter; its chief faces a spy probe.
  5. Cyclone Akvan bears down on the Bay of Bengal, set to turn severe.

Pure standard library. No network, no randomness, no assets: every pixel
is drawn by this file, so two runs write byte-identical output.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 234)
INK = (22, 22, 26)
NAVY = (20, 38, 74)
NAVY_DARK = (13, 26, 52)
RED = (178, 34, 34)
GOLD = (242, 193, 78)
GREY = (90, 90, 96)
LIGHT_GREY = (210, 208, 200)
WHITE = (255, 255, 255)
SKY = (168, 204, 224)
SEA = (46, 107, 158)

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows; bit 4 is the leftmost pixel.
# ---------------------------------------------------------------------------
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    "-": (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "%": (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "=": (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '"': (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
}


def text_width(text, scale):
    return len(text) * (6 * scale) - scale


def wrap_text(text, max_chars):
    """Greedy word wrap; returns at most the lines that fit the width."""
    lines = []
    for piece in text.split("\n"):
        words = piece.split(" ")
        line = ""
        for word in words:
            trial = word if not line else line + " " + word
            if len(trial) <= max_chars:
                line = trial
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


# ---------------------------------------------------------------------------
# Canvas: an RGB buffer with small drawing primitives.
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(bg) * (w * h))

    def set(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = col[0]
            self.buf[i + 1] = col[1]
            self.buf[i + 2] = col[2]

    def rect(self, x, y, w, h, col):
        x0 = max(x, 0)
        y0 = max(y, 0)
        x1 = min(x + w, self.w)
        y1 = min(y + h, self.h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(col) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def line(self, x0, y0, x1, y1, col):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, col)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def thick_line(self, x0, y0, x1, y1, t, col):
        self.line(x0, y0, x1, y1, col)
        half = t // 2
        for k in range(-half, half + 1):
            self.line(x0 + k, y0, x1 + k, y1, col)
            self.line(x0, y0 + k, x1, y1 + k, col)

    def disc(self, cx, cy, r, col):
        for y in range(cy - r, cy + r + 1):
            dy = y - cy
            rest = r * r - dy * dy
            if rest < 0:
                continue
            dx = int(rest ** 0.5)
            self.rect(cx - dx, y, 2 * dx + 1, 1, col)

    def fill_triangle(self, x0, y0, x1, y1, x2, y2, col):
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts

        def edge_x(xa, ya, xb, yb, y):
            if yb == ya:
                return float(xa)
            return xa + (xb - xa) * (y - ya) / (yb - ya)

        for y in range(max(ay, 0), min(cy, self.h - 1) + 1):
            if y < by:
                xl = edge_x(ax, ay, bx, by, y)
                xr = edge_x(ax, ay, cx, cy, y)
            else:
                xl = edge_x(bx, by, cx, cy, y)
                xr = edge_x(ax, ay, cx, cy, y)
            if xl > xr:
                xl, xr = xr, xl
            self.rect(int(xl), y, int(xr) - int(xl) + 1, 1, col)

    def fill_poly(self, pts, col):
        ys = [p[1] for p in pts]
        n = len(pts)
        for y in range(max(min(ys), 0), min(max(ys), self.h - 1) + 1):
            xs = []
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, int(xs[i + 1]) - int(xs[i]) + 1, 1, col)

    def text(self, x, y, s, scale, col):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for bit in range(5):
                    if bits & (1 << (4 - bit)):
                        self.rect(cx + bit * scale, y + row * scale,
                                  scale, scale, col)
            cx += 6 * scale

    def text_center(self, cx, y, s, scale, col):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, col)


# ---------------------------------------------------------------------------
# Pictures: one small drawn scene per story.
# ---------------------------------------------------------------------------
def pic_manila(c, x, y, w, h):
    # Sky in three bands, sun, skyline, and a plane on approach.
    c.rect(x, y, w, h // 3, (168, 204, 224))
    c.rect(x, y + h // 3, w, h // 3, (191, 217, 232))
    c.rect(x, y + 2 * h // 3, w, h - 2 * h // 3, (214, 230, 240))
    c.disc(x + w - 88, y + 30, 24, GOLD)
    c.disc(x + w - 88, y + 30, 18, (250, 214, 110))
    ground = y + h - 16
    # Skyline silhouettes with lit windows.
    specs = [(0, 62, 66), (68, 44, 96), (118, 52, 80), (176, 40, 116),
             (222, 64, 88), (292, 48, 126), (346, 56, 72), (408, 44, 104),
             (458, 60, 84), (524, 48, 120), (578, 52, 76), (636, 44, 92),
             (686, 58, 66), (748, 46, 108), (800, 54, 82), (860, 44, 96),
             (910, 34, 60)]
    for i, (bx, bw, bh) in enumerate(specs):
        c.rect(x + bx, ground - bh, bw, bh, NAVY_DARK)
        for wy in range(ground - bh + 8, ground - 10, 16):
            for wx in range(x + bx + 8, x + bx + bw - 6, 14):
                if (wx // 14 + wy // 16 + i) % 3 != 0:
                    c.rect(wx, wy, 5, 7, GOLD)
    c.rect(x, ground, w, 16, (30, 30, 36))
    # Plane flying right, with a contrail.
    px, py = x + 300, y + 34
    c.line(px - 150, py + 4, px - 6, py + 4, WHITE)
    c.line(px - 150, py + 10, px - 6, py + 10, WHITE)
    c.rect(px, py, 150, 15, WHITE)
    c.rect(px, py, 150, 15, WHITE)
    c.fill_triangle(px + 150, py, px + 176, py + 7, px + 150, py + 15, WHITE)
    c.fill_triangle(px + 96, py + 15, px + 128, py + 15, px + 108, py + 38,
                    WHITE)
    c.fill_triangle(px + 96, py, px + 128, py, px + 108, py - 22, WHITE)
    c.fill_triangle(px + 8, py, px + 30, py, px + 14, py - 26, WHITE)
    c.rect(px + 18, py + 5, 96, 4, NAVY)
    for wx in range(px + 24, px + 108, 16):
        c.rect(wx, py + 5, 6, 4, NAVY)


def pic_crimea(c, x, y, w, h):
    # Dusk sky, sea, a cable-stayed bridge, and a blast on its deck.
    c.rect(x, y, w, h * 2 // 5, (199, 211, 224))
    c.rect(x, y + h * 2 // 5, w, h - h * 2 // 5, SEA)
    deck = y + h * 2 // 5
    # Sea shimmer.
    for k in range(6):
        c.rect(x + 20 + k * 72, deck + 18 + (k % 3) * 12, 44, 3, (120, 170, 205))
    # Towers and cables.
    for tx in (x + 96, x + w - 110):
        c.rect(tx, y + 8, 10, deck - y - 8, (90, 96, 104))
        for dx in (-70, -35, 35, 70):
            c.line(tx + 5, y + 12, tx + 5 + dx, deck, (140, 146, 154))
    # Deck and pillars.
    c.rect(x, deck, w, 10, (107, 114, 128))
    for px in (x + 40, x + 180, x + 320):
        c.rect(px, deck + 10, 12, h - (deck - y) - 10, (90, 96, 104))
    # Explosion starburst on the deck.
    ex, ey = x + w // 2, deck - 2
    outer = []
    inner = []
    for k in range(14):
        ang = 3.14159 * k / 7.0
        r = 30 if k % 2 == 0 else 13
        outer.append((ex + int(r * 2.2 * math.cos(ang)),
                      ey - int(r * math.sin(ang))))
        r2 = 15 if k % 2 == 0 else 7
        inner.append((ex + int(r2 * 2.2 * math.cos(ang)),
                      ey - int(r2 * math.sin(ang))))
    c.fill_poly(outer, (242, 140, 40))
    c.fill_poly(inner, (250, 214, 60))
    # Smoke puffs.
    c.disc(ex - 26, ey - 34, 12, (120, 120, 126))
    c.disc(ex + 6, ey - 46, 15, (140, 140, 146))
    c.disc(ex + 30, ey - 30, 10, (120, 120, 126))


def pic_gulf(c, x, y, w, h):
    # Night sky, stars, a radar dish sweeping, and two drones.
    c.rect(x, y, w, h, (16, 30, 51))
    stars = [(18, 14), (70, 30), (130, 10), (200, 26), (260, 12),
             (330, 30), (400, 16), (40, 52), (300, 52), (370, 62)]
    for sx, sy in stars:
        c.rect(x + sx, y + sy, 3, 3, WHITE)
    # Sea at the bottom.
    c.rect(x, y + h - 18, w, 18, (22, 50, 74))
    c.line(x + 20, y + h - 10, x + 90, y + h - 10, (90, 140, 180))
    c.line(x + 300, y + h - 10, x + 380, y + h - 10, (90, 140, 180))
    # Radar: base, mast, dish, sweeping beam.
    bx, by = x + w // 2 - 40, y + h - 34
    c.rect(bx, by + 16, 80, 16, (150, 156, 164))
    c.rect(bx + 36, by - 6, 8, 22, (150, 156, 164))
    cx, cy = bx + 40, by - 6
    for k in range(41):
        ang = 3.14159 * (200 + k * 3.5) / 180.0
        px = cx + int(34 * math.cos(ang))
        py = cy + int(20 * math.sin(ang))
        c.rect(px - 1, py - 1, 3, 3, (220, 226, 232))
    c.line(cx, cy, cx + 44, cy - 34, (127, 179, 213))
    c.line(cx, cy, cx + 40, cy - 30, (127, 179, 213))
    # Drones: body, rotors, red lights.
    for dx, dy in ((x + 56, y + 26), (x + w - 130, y + 40)):
        c.rect(dx, dy + 8, 22, 8, (200, 200, 206))
        c.line(dx - 8, dy, dx + 30, dy, (200, 200, 206))
        c.line(dx - 8, dy + 20, dx + 30, dy + 20, (200, 200, 206))
        c.disc(dx - 8, dy, 3, RED)
        c.disc(dx + 30, dy, 3, RED)
        c.disc(dx + 11, dy + 12, 3, RED)


def pic_nvidia(c, x, y, w, h):
    # Dark green board, an NVDA chip, and rising sales bars.
    c.rect(x, y, w, h, (14, 43, 26))
    # Chip with gold pins.
    cx, cy, s = x + 34, y + h // 2 - 48, 96
    for k in range(5):
        off = 12 + k * 16
        c.rect(cx + off, cy - 10, 8, 10, GOLD)
        c.rect(cx + off, cy + s, 8, 10, GOLD)
        c.rect(cx - 10, cy + off, 10, 8, GOLD)
        c.rect(cx + s, cy + off, 10, 8, GOLD)
    c.rect(cx, cy, s, s, (30, 122, 60))
    c.rect(cx + 4, cy + 4, s - 8, s - 8, (21, 94, 46))
    c.text_center(cx + s // 2, cy + s // 2 - 10, "NVDA", 3, WHITE)
    # Rising bars and an arrow over them.
    base = y + h - 22
    heights = [22, 36, 50, 64, 80]
    bx = x + 180
    for k, bh in enumerate(heights):
        c.rect(bx + k * 44, base - bh, 28, bh, (47, 168, 92))
    c.thick_line(bx - 6, base - 26, bx + 4 * 44 + 34, base - 92, 3,
                 (124, 242, 154))
    ax, ay = bx + 4 * 44 + 34, base - 92
    c.fill_triangle(ax, ay, ax - 22, ay + 2, ax - 2, ay + 20, (124, 242, 154))


def pic_cyclone(c, x, y, w, h):
    # Pale sky, a spiral storm, rain, and waves below.
    c.rect(x, y, w, h, (220, 230, 238))
    cx, cy = x + w // 2, y + h // 2 - 8
    # Two Archimedean spiral arms, kept inside the picture.
    for arm, col in ((0.0, WHITE), (3.14159, (74, 123, 166))):
        prev = None
        for k in range(160):
            t = arm + k * 0.06
            r = 5 + (t - arm) * 4.6
            px = cx + int(r * math.cos(t))
            py = cy + int(r * 0.85 * math.sin(t))
            if prev is not None:
                c.thick_line(prev[0], prev[1], px, py, 3, col)
            prev = (px, py)
    c.disc(cx, cy, 8, (74, 123, 166))
    # Rain streaks.
    for rx, ry in [(30, 20), (90, 44), (390, 26), (330, 52), (60, 84),
                   (380, 88), (150, 16), (250, 70)]:
        c.line(x + rx, y + ry, x + rx - 6, y + ry + 16, (122, 155, 181))
    # Waves.
    c.rect(x, y + h - 26, w, 26, SEA)
    for wy in (y + h - 16, y + h - 8):
        for wx in range(x + 8, x + w - 8, 26):
            c.disc(wx, wy, 4, WHITE)


# ---------------------------------------------------------------------------
# Page layout.
# ---------------------------------------------------------------------------
def story_panel(c, x, y, w, h, pic_h, pic_fn, headline, caption, accent):
    c.rect(x, y, w, h, WHITE)
    c.rect(x, y, w, 6, accent)
    # Thin frame.
    c.rect(x, y, w, 2, LIGHT_GREY)
    c.rect(x, y + h - 2, w, 2, LIGHT_GREY)
    c.rect(x, y, 2, h, LIGHT_GREY)
    c.rect(x + w - 2, y, 2, h, LIGHT_GREY)
    pic_fn(c, x + 14, y + 16, w - 28, pic_h)
    # Headline, centred, at most two lines.
    max_h = (w - 40) // 24
    lines = wrap_text(headline, max_h)[:2]
    hy = y + 16 + pic_h + 10
    for line in lines:
        c.text_center(x + w // 2, hy, line, 4, INK)
        hy += 32
    # Caption, centred, at most two lines.
    max_c = (w - 40) // 18
    clines = wrap_text(caption, max_c)[:2]
    cy = hy + 6
    for line in clines:
        c.text_center(x + w // 2, cy, line, 3, (64, 64, 70))
        cy += 24


def build_image():
    c = Canvas(W, H, PAPER)
    # Masthead.
    c.rect(0, 0, W, 118, NAVY)
    c.text_center(W // 2, 16, "WORLD NEWS", 6, WHITE)
    c.text_center(W // 2, 68, "WEDNESDAY 18 NOVEMBER 2026", 4, GOLD)
    c.rect(0, 118, W, 8, RED)

    # Lead story: Trump in Manila.
    story_panel(c, 24, 140, 976, 290, 148, pic_manila,
                "TRUMP LANDS IN MANILA FOR QUAD TALKS",
                "US president opens his Asia tour as Quad leaders meet, "
                "ahead of his visit to China.",
                NAVY)

    # Second row: Crimea and the Gulf.
    story_panel(c, 24, 446, 476, 254, 118, pic_crimea,
                "UKRAINE HITS THE CRIMEAN BRIDGE",
                "Second day of strikes; Russia pounds Kyiv.",
                RED)
    story_panel(c, 524, 446, 476, 254, 118, pic_gulf,
                "IRAN DRONES HIT US RADAR IN BAHRAIN",
                "Kuwait reports drones; region on alert.",
                (120, 60, 30))

    # Third row: Nvidia and Cyclone Akvan.
    story_panel(c, 24, 716, 476, 284, 140, pic_nvidia,
                "NVIDIA SALES JUMP 103%",
                "Record quarter, but chief faces spy probe.",
                (30, 122, 60))
    story_panel(c, 524, 716, 476, 284, 140, pic_cyclone,
                "CYCLONE AKVAN HEADS FOR INDIA",
                "Bay of Bengal storm set to turn severe Thursday.",
                SEA)
    return c


def write_png(path, w, h, buf):
    raw = bytearray()
    stride = w * 3
    for yy in range(h):
        raw.append(0)
        raw += buf[yy * stride:(yy + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
    for i in range(0, len(comp), 65536):
        data += chunk(b"IDAT", comp[i:i + 65536])
    data += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(data)
    return len(data)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    canvas = build_image()
    size = write_png(os.path.join(out_dir, "entry.png"), W, H, canvas.buf)
    print("wrote entry.png: %d bytes, %dx%d" % (size, W, H))


if __name__ == "__main__":
    main()
