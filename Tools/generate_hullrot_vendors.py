"""Generates the Hullrot faction vendor RSIs.

Two chassis, drawn from scratch rather than reskinned from the RMC ColMarTech racks:
  armory -- heavy armoured cabinet: bolted side pillars, crest plate, weapon rack window, dispensing hatch.
  supply -- slimmer requisitions rack: lit emblem sign, glass front with folded stock on shelves, tray.

Every faction gets both chassis. Beyond the colours, each faction varies the silhouette of the cap, the
emblem, the trim pattern on the header and the pillar dressing, so two vendors read apart even in greyscale.
Adding a faction = one FACTIONS entry (and an EMBLEMS glyph if it needs a new one).

States (all the vendor visualizers use): off, broken, panel, normal-unshaded, deny-unshaded, eject-unshaded.
CMAutomatedVendor racks have no visualizer, so they show off + normal-unshaded statically.

Also palette-swaps the shipyard console screen (shipyard_console.rsi, left untouched as the neutral one) into
ShipyardScreens/<faction>.rsi; consoles opt in with the ShipyardScreen component.

Usage: python Tools/generate_hullrot_vendors.py [repo] [--preview out.png]   (needs Pillow; overwrites
Resources/Textures/_Crescent/Structures/Machines/Vendors in place)
"""
import json
import math
import os
import sys
from PIL import Image

argv = sys.argv[1:]
PREVIEW = None
if "--preview" in argv:
    i = argv.index("--preview")
    PREVIEW = argv[i + 1]
    del argv[i:i + 2]
REPO = argv[0] if argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(REPO, "Resources/Textures/_Crescent/Structures/Machines/Vendors")

S = 32
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GLASS_TOP = (34, 46, 56)
GLASS_BOT = (16, 21, 27)
GLASS_HI = (86, 108, 124)
SCREEN_OFF = (12, 16, 18)
PLATE = (20, 22, 26)
METAL = (132, 138, 144)
METAL_DK = (70, 74, 80)
STOCK = (74, 58, 44)
LED_GO = (120, 232, 120)
LED_GO_DIM = (48, 100, 52)
DENY = (236, 66, 54)
WIRES = [(206, 62, 52), (226, 196, 64), (84, 186, 96), (74, 126, 214)]


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def scale(c, k):
    return tuple(max(0, min(255, int(round(v * k)))) for v in c)


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


# cap:    silhouette above the body (see cap_height)
# emblem: glyph on the crest plate / sign (EMBLEMS)
# trim:   pattern on the header band (trim_color)
# pillar: side dressing -- bolts, a gilded stripe, or a rivet column
FACTIONS = {
    "neutral": dict(chassis="#4A525B", accent="#8FB8C8", cap="flat", emblem="square", trim="solid", pillar="bolts"),
    "dsm": dict(chassis="#48425A", accent="#9D7BE6", cap="crown", emblem="sun", trim="double", pillar="stripe"),
    "ncwl": dict(chassis="#51533F", accent="#D9962B", cap="vents", emblem="star", trim="hazard", pillar="bolts"),
    "shi": dict(chassis="#7F888C", accent="#6FB0A6", cap="dome", emblem="s", trim="solid", pillar="stripe"),
    "tfsc": dict(chassis="#56453F", accent="#D0463F", cap="chamfer", emblem="diamonds", trim="dash", pillar="bolts"),
    "tap": dict(chassis="#766650", accent="#5DBB5A", cap="stepped", emblem="crescent", trim="chevron", pillar="rivets"),
    "srm": dict(chassis="#302C2A", accent="#B8A97A", cap="arch", emblem="cross", trim="double", pillar="stripe"),
    "ath": dict(chassis="#9E998C", accent="#E0CF8A", cap="spire", emblem="crown", trim="double", pillar="stripe"),
    "tsp": dict(chassis="#3A4658", accent="#4E8FD6", cap="badge", emblem="shield", trim="solid", pillar="rivets"),
}

EMBLEMS = {
    "square": [".......", ".#####.", ".#...#.", ".#.#.#.", ".#...#.", ".#####.", "......."],
    "sun": ["#..#..#", ".#####.", ".##.##.", "###.###", ".##.##.", ".#####.", "#..#..#"],
    "star": ["...#...", "...#...", "#######", ".#####.", "..###..", ".##.##.", ".#...#."],
    "s": [".#####.", "##...##", "##.....", ".#####.", ".....##", "##...##", ".#####."],
    "diamonds": [".#...#.", "###.###", ".#...#.", ".......", ".#...#.", "###.###", ".#...#."],
    "crescent": ["..###..", ".##....", "##.....", "##...#.", "##.....", ".##....", "..###.."],
    "cross": ["..###..", "...#...", "#..#..#", "#######", "#..#..#", "...#...", "..###.."],
    "crown": ["#..#..#", "#..#..#", "##.#.##", "#######", "#######", ".......", "#######"],
    "shield": ["#######", "#.....#", "#..#..#", "#.###.#", "#..#..#", ".#...#.", "..###.."],
}


def palette(fac):
    base = rgb(fac["chassis"])
    acc = rgb(fac["accent"])
    return dict(
        out=scale(base, 0.3), dk=scale(base, 0.7), md=base,
        lt=mix(base, WHITE, 0.16), hi=mix(base, WHITE, 0.32), seam=scale(base, 0.5),
        acc=acc, acc_lt=mix(acc, WHITE, 0.45), acc_dk=scale(acc, 0.58), acc_dim=scale(acc, 0.4),
    )


def cap_height(shape, u, n):
    """Rows of cap above the body at column u of an n-wide body (n odd)."""
    mid = (n - 1) // 2
    d = abs(u - mid)
    e = min(u, n - 1 - u)
    edge = 1 if e == 0 else 2
    if shape == "flat":
        return edge
    if shape == "vents":  # industrial lip with two exhaust stacks
        return 5 if e in (3, 4) else (2 if e == 0 else 3)
    if shape == "crown":  # three points, studs between
        if d <= 1:
            return 5
        if e in (2, 3):
            return 4
        return 3 if d == mid // 2 else edge
    if shape == "dome":  # smooth corporate crown
        return 1 + int(round(2.6 * math.sqrt(max(0.0, 1 - (d / (mid + 1)) ** 2))))
    if shape == "chamfer":  # angular shoulders, notched centre
        return 2 if d <= 2 else min(3, e + 1)
    if shape == "stepped":  # caravan ziggurat
        return 1 if e < 3 else (5 if d <= 3 else 3)
    if shape == "arch":  # pointed gothic arch
        return max(1, 5 - int(d / 2.6))
    if shape == "spire":  # central spire, finials at the shoulders
        if d <= 3:
            return max(2, 5 - d)
        return 4 if e == 2 else edge
    if shape == "badge":  # flat, raised badge mount in the middle
        return 4 if d <= 2 else edge
    raise ValueError(shape)


def trim_color(pat, x, y, y0, y1, p):
    ymid = (y0 + y1) // 2
    if pat == "solid":
        return p["acc"] if y == y0 else (scale(p["acc"], 0.35) if y == y1 else p["acc_dk"])
    if pat == "double":
        return p["acc"] if y in (y0, y1) else p["dk"]
    if pat == "hazard":
        return p["acc"] if ((x + y) // 2) % 2 == 0 else (22, 22, 22)
    if pat == "dash":
        return p["acc"] if (y == ymid and x % 3 != 2) else p["acc_dk"]
    if pat == "chevron":
        return p["acc"] if (x + abs(y - ymid)) % 4 == 0 else p["acc_dk"]
    raise ValueError(pat)


class Canvas:
    def __init__(self):
        self.im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        self.px = self.im.load()

    def put(self, x, y, c, a=255):
        if 0 <= x < S and 0 <= y < S:
            self.px[x, y] = tuple(c[:3]) + (a,)

    def rect(self, x0, y0, x1, y1, c, a=255):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.put(x, y, c, a)

    def frame(self, x0, y0, x1, y1, c):
        for x in range(x0, x1 + 1):
            self.put(x, y0, c)
            self.put(x, y1, c)
        for y in range(y0, y1 + 1):
            self.put(x0, y, c)
            self.put(x1, y, c)

    def glyph(self, rows, x0, y0, c):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch == "#":
                    self.put(x0 + i, y0 + j, c)


# Geometry. Bodies are odd-width so the emblem centres on a pixel column.
GEO = {
    "armory": dict(
        bx0=2, bx1=28, bt=6,
        plate=(11, 7, 19, 15), band=(7, 9, 23, 12),
        glass=(8, 18, 16, 25), glass_frame=(7, 17, 17, 26),
        screen=(20, 18, 22, 20), screen_frame=(19, 17, 23, 21),
        keys=(20, 23, 22, 24), led=(23, 23), slot=(20, 26, 22, 26),
        hatch=(9, 28, 21, 28), console=(19, 17, 23, 26),
    ),
    "supply": dict(
        bx0=4, bx1=26, bt=6,
        sign=(7, 7, 23, 15), plate=(11, 7, 19, 15),
        glass=(8, 18, 18, 26), glass_frame=(7, 17, 19, 27),
        screen=(21, 18, 22, 20), screen_frame=(20, 17, 23, 21),
        keys=(21, 23, 22, 24), led=(23, 23), slot=(21, 26, 22, 26),
        hatch=(9, 29, 21, 29), console=(20, 17, 23, 27),
    ),
}

RIFLES = (9, 12, 15)
STOCK_COLORS = [(92, 98, 76), (124, 124, 128), (188, 180, 158), (62, 72, 98), (106, 76, 62)]


def rifle_pixels():
    px = {}
    for x in RIFLES:
        for y in (18, 19, 20):
            px[(x, y)] = METAL_DK
        for y in (21, 22, 23):
            px[(x, y)] = METAL
            px[(x + 1, y)] = METAL_DK
        px[(x + 1, 24)] = METAL_DK  # magazine
        px[(x, 24)] = STOCK
        px[(x, 25)] = STOCK
    return px


def shelf_items(p):
    """(x, y) -> colour for the folded stock behind the supply glass."""
    px = {}
    cols = [p["acc_dk"]] + STOCK_COLORS
    k = 0
    for top in (18, 21, 24):
        for x0 in (8, 12, 16):
            c = cols[k % len(cols)]
            k += 2 if k % 3 == 0 else 1
            for x in range(x0, x0 + 3):
                if x > 18:
                    continue
                px[(x, top)] = mix(c, WHITE, 0.22)
                px[(x, top + 1)] = c
    return px


def draw_body(kind, fac, p):
    g = GEO[kind]
    c = Canvas()
    bx0, bx1, bt = g["bx0"], g["bx1"], g["bt"]
    n = bx1 - bx0 + 1

    # Silhouette mask: cap heightmap + body + plinth, then shade, then outline its border.
    mask = {}
    for u in range(n):
        x = bx0 + u
        h = cap_height(fac["cap"], u, n)
        for k in range(1, h + 1):
            mask[(x, bt - k)] = p["acc"] if k >= 3 else (p["hi"] if k == h - 1 else p["lt"])
        for y in range(bt, 31):
            t = (y - bt) / (30 - bt)
            col = mix(p["md"], p["dk"], t * 0.4)
            if y == bt:
                col = p["seam"]
            elif u == 1:
                col = p["lt"]
            elif u == n - 2:
                col = p["dk"]
            mask[(x, y)] = col
    for x in range(bx0 + 1, bx1):
        mask[(x, 31)] = p["out"]
    for (x, y), col in mask.items():
        c.put(x, y, col)
    for (x, y) in mask:
        if any((x + dx, y + dy) not in mask for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            c.put(x, y, p["out"])

    if kind == "armory":
        draw_armory(c, g, fac, p)
    else:
        draw_supply(c, g, fac, p)
    return c


def draw_pillar(c, x0, y0, y1, fac, p, mirrored):
    lo, mid, hi = (p["dk"], p["md"], p["lt"]) if mirrored else (p["lt"], p["md"], p["dk"])
    for y in range(y0, y1 + 1):
        c.put(x0, y, lo)
        c.put(x0 + 1, y, mid)
        c.put(x0 + 2, y, hi)
    cx = x0 + 1
    if fac["pillar"] == "bolts":
        for y in (y0 + 2, (y0 + y1) // 2, y1 - 2):
            c.put(cx, y, p["hi"])
            c.put(cx, y + 1, p["out"])
    elif fac["pillar"] == "stripe":
        for y in range(y0 + 1, y1):
            c.put(cx, y, p["acc_dk"])
        c.put(cx, y0 + 1, p["acc_lt"])
        c.put(cx, y1 - 1, p["acc"])
    elif fac["pillar"] == "rivets":
        for y in range(y0 + 1, y1, 3):
            c.put(cx, y, p["hi"])


def draw_plate(c, g, fac, p, glyph_col):
    x0, y0, x1, y1 = g["plate"]
    c.rect(x0, y0, x1, y1, PLATE)
    c.frame(x0, y0, x1, y1, p["out"])
    c.put(x0 + 1, y1 - 1, PLATE)
    c.glyph(EMBLEMS[fac["emblem"]], x0 + 1, y0 + 1, glyph_col)


def draw_console(c, g, p):
    c.frame(*g["screen_frame"], p["out"])
    c.rect(*g["screen"], SCREEN_OFF)
    kx0, ky0, kx1, ky1 = g["keys"]
    for y in range(ky0, ky1 + 1):
        for x in range(kx0, kx1 + 1):
            c.put(x, y, p["hi"] if (x + y) % 2 == 0 else p["dk"])
    c.put(*g["led"], LED_GO_DIM)
    sx0, sy, sx1, _ = g["slot"]
    for x in range(sx0, sx1 + 1):
        c.put(x, sy, p["out"])
    c.put(sx1, sy, p["hi"])


def draw_glass(c, g, p):
    fx0, fy0, fx1, fy1 = g["glass_frame"]
    c.frame(fx0, fy0, fx1, fy1, p["out"])
    x0, y0, x1, y1 = g["glass"]
    for y in range(y0, y1 + 1):
        col = mix(GLASS_TOP, GLASS_BOT, (y - y0) / max(1, y1 - y0))
        for x in range(x0, x1 + 1):
            c.put(x, y, col)


def draw_armory(c, g, fac, p):
    draw_pillar(c, 3, g["bt"] + 1, 29, fac, p, False)
    draw_pillar(c, 25, g["bt"] + 1, 29, fac, p, True)
    for y in range(g["bt"] + 1, 30):
        c.put(6, y, p["seam"])
        c.put(24, y, p["seam"])

    x0, y0, x1, y1 = g["band"]
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c.put(x, y, trim_color(fac["trim"], x, y, y0, y1, p))
    draw_plate(c, g, fac, p, p["acc_dim"])
    for x in range(7, 24):
        c.put(x, 16, p["seam"])

    draw_glass(c, g, p)
    gx0, gy0, _, _ = g["glass"]
    for (x, y) in ((gx0 + 1, gy0 + 1), (gx0, gy0 + 2), (gx0 + 2, gy0)):
        c.put(x, y, GLASS_HI)
    for (x, y), col in rifle_pixels().items():
        c.put(x, y, col)

    draw_console(c, g, p)

    hx0, hy, hx1, _ = g["hatch"]
    for x in range(hx0 - 1, hx1 + 2):
        c.put(x, hy - 1, p["lt"])
        c.put(x, hy, p["out"])
        c.put(x, hy + 1, p["dk"])
    for x in range(hx0 - 1, hx1 + 2):
        if x in (hx0 - 1, hx1 + 1):
            c.put(x, hy, p["seam"])


def draw_supply(c, g, fac, p):
    bt = g["bt"]
    for y in range(bt + 1, 30):
        c.put(5, y, p["lt"])
        c.put(6, y, p["seam"])
        c.put(24, y, p["seam"])
        c.put(25, y, p["dk"])
    cx = 5
    if fac["pillar"] == "stripe":
        for y in range(bt + 2, 29):
            c.put(cx, y, p["acc_dk"])
            c.put(25, y, scale(p["acc_dk"], 0.8))
    elif fac["pillar"] == "rivets":
        for y in range(bt + 2, 29, 3):
            c.put(cx, y, p["hi"])
            c.put(25, y, p["lt"])
    else:
        for y in (bt + 3, 18, 27):
            c.put(cx, y, p["hi"])
            c.put(25, y, p["hi"])

    sx0, sy0, sx1, sy1 = g["sign"]
    c.frame(sx0, sy0, sx1, sy1, p["out"])
    for y in range(sy0 + 1, sy1):
        for x in range(sx0 + 1, sx1):
            c.put(x, y, trim_color(fac["trim"], x, y, sy0 + 2, sy1 - 2, p) if (y > sy0 + 1 and y < sy1 - 1) else p["acc_dim"])
    draw_plate(c, g, fac, p, p["acc_dim"])
    for x in range(7, 24):
        c.put(x, 16, p["seam"])

    draw_glass(c, g, p)
    for (x, y), col in shelf_items(p).items():
        c.put(x, y, col)
    for y in (20, 23, 26):
        for x in range(g["glass"][0], g["glass"][2] + 1):
            c.put(x, y, METAL_DK)
    c.put(g["glass"][0], g["glass"][1], GLASS_HI)
    c.put(g["glass"][0] + 1, g["glass"][1], GLASS_HI)

    draw_console(c, g, p)

    hx0, hy, hx1, _ = g["hatch"]
    for x in range(hx0 - 1, hx1 + 2):
        c.put(x, hy - 1, p["out"])
        c.put(x, hy, p["lt"])


# ---------------------------------------------------------------- lights (unshaded overlays)

SCREEN_TEXT = [["##.", ".#.", "###"], ["#.#", "##.", ".##"], [".##", "#.#", "##."], ["###", ".#.", "#.."]]
DENY_X = ["#.#", ".#.", "#.#"]
EJECT_ARROW = ["#.#", ".#.", "..."]


def paint_screen(c, g, bg, fg, rows):
    x0, y0, x1, y1 = g["screen"]
    c.rect(x0, y0, x1, y1, bg)
    for j in range(y1 - y0 + 1):
        for i in range(x1 - x0 + 1):
            if j < len(rows) and i < len(rows[j]) and rows[j][i] == "#":
                c.put(x0 + i, y0 + j, fg)


def paint_ambient(c, kind, g, fac, p):
    """Always-on lights: the emblem, plus the rack light (armory) or the sign trim (supply)."""
    px0, py0, px1, _ = g["plate"]
    if kind == "armory":
        rifles = rifle_pixels()
        gx0, gy0, gx1, _ = g["glass"]
        for y, a in ((gy0, 120), (gy0 + 1, 64), (gy0 + 2, 30)):
            for x in range(gx0, gx1 + 1):
                if (x, y) not in rifles:
                    c.put(x, y, p["acc"], a)
    else:
        # The trim pattern lights up rather than washing out into a flat block; the plate stays dark.
        sx0, sy0, sx1, sy1 = g["sign"]
        for y in range(sy0 + 1, sy1):
            for x in range(sx0 + 1, sx1):
                if px0 <= x <= px1:
                    continue
                if sy0 + 1 < y < sy1 - 1:
                    c.put(x, y, mix(trim_color(fac["trim"], x, y, sy0 + 2, sy1 - 2, p), WHITE, 0.15))
                else:
                    c.put(x, y, p["acc"])
        gx0, gy0, gx1, _ = g["glass"]
        for x in range(gx0, gx1 + 1):
            c.put(x, gy0, p["acc_lt"], 70)
    c.glyph(EMBLEMS[fac["emblem"]], px0 + 1, py0 + 1, p["acc_lt"])


def lights_normal(kind, fac, p, f):
    g = GEO[kind]
    c = Canvas()
    paint_ambient(c, kind, g, fac, p)
    paint_screen(c, g, p["acc_dk"], p["acc_lt"], SCREEN_TEXT[f % 4])
    c.put(*g["led"], LED_GO if f < 2 else LED_GO_DIM)
    return c.im


def lights_deny(kind, fac, p, f):
    g = GEO[kind]
    c = Canvas()
    paint_ambient(c, kind, g, fac, p)
    if f == 0:
        paint_screen(c, g, scale(DENY, 0.45), DENY, DENY_X)
        c.put(*g["led"], DENY)
    else:
        paint_screen(c, g, scale(DENY, 0.3), scale(DENY, 0.6), DENY_X)
    return c.im


EJECT_FRAMES = 6


def lights_eject(kind, fac, p, f):
    g = GEO[kind]
    c = Canvas()
    paint_ambient(c, kind, g, fac, p)
    rows = EJECT_ARROW if f % 2 == 0 else ["...", "#.#", ".#."]
    paint_screen(c, g, p["acc_dk"], p["acc_lt"], rows)
    c.put(*g["led"], LED_GO)
    hx0, hy, hx1, _ = g["hatch"]
    mid = (hx0 + hx1) // 2
    reach = int(round((hx1 - hx0) / 2 * min(1.0, (f + 1) / (EJECT_FRAMES - 2))))
    fade = 1.0 if f < EJECT_FRAMES - 1 else 0.5
    for x in range(mid - reach, mid + reach + 1):
        c.put(x, hy, scale(p["acc_lt"], fade))
    return c.im


# ---------------------------------------------------------------- broken / panel

CRACKS = [(0, 0), (1, 1), (1, 2), (2, 3), (3, 3), (4, 4), (4, 5), (5, 6), (3, 5), (2, 6), (6, 2), (7, 1)]


def draw_broken(kind, fac, p):
    g = GEO[kind]
    c = draw_body(kind, fac, p)
    gx0, gy0, gx1, gy1 = g["glass"]
    ox, oy = gx0 + 2, gy0 + 1
    for dx, dy in CRACKS:
        x, y = ox + dx, oy + dy
        if gx0 <= x <= gx1 and gy0 <= y <= gy1:
            c.put(x, y, GLASS_HI)
    for (x, y) in ((ox + 1, oy + 4), (ox + 5, oy + 3), (ox + 6, oy + 5)):
        if gx0 <= x <= gx1 and gy0 <= y <= gy1:
            c.put(x, y, (6, 7, 9))
    sx0, sy0, sx1, sy1 = g["screen"]
    c.rect(sx0, sy0, sx1, sy1, (4, 5, 6))
    c.put(sx0, sy0, GLASS_HI)
    c.put(sx0 + 1, sy0 + 1, GLASS_HI)
    px0, py0, _, _ = g["plate"]
    c.glyph(EMBLEMS[fac["emblem"]], px0 + 1, py0 + 1, scale(p["acc_dim"], 0.6))
    c.put(px0 + 3, py0 + 4, PLATE)
    # Scorch across the lower right.
    for (x, y) in ((20, 27), (21, 27), (22, 28), (19, 28), (21, 29), (23, 26), (22, 25)):
        r, gg, b, a = c.px[x, y]
        if a:
            c.put(x, y, scale((r, gg, b), 0.45))
    c.put(*g["led"], (30, 16, 14))
    return c.im


def draw_panel(kind, fac, p):
    g = GEO[kind]
    c = Canvas()
    x0, y0, x1, y1 = g["console"]
    y0 = g["keys"][1] - 1
    c.frame(x0, y0, x1, y1, p["out"])
    c.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, (12, 12, 14))
    for i, x in enumerate(range(x0 + 1, x1)):
        col = WIRES[i % len(WIRES)]
        for y in range(y0 + 1, y1):
            if (y + i) % 3 != 0:
                c.put(x, y, col)
    # Door swung open against the side seam.
    for y in range(y0, y1 + 1):
        c.put(x1 + 1, y, p["hi"])
    return c.im


# ---------------------------------------------------------------- output

def sheet(frames):
    cols = math.ceil(math.sqrt(len(frames)))
    rows = math.ceil(len(frames) / cols)
    im = Image.new("RGBA", (cols * S, rows * S), (0, 0, 0, 0))
    for i, fr in enumerate(frames):
        im.paste(fr, ((i % cols) * S, (i // cols) * S))
    return im


def write_rsi(kind, name, fac):
    p = palette(fac)
    path = os.path.join(OUT, f"{kind}_{name}.rsi")
    os.makedirs(path, exist_ok=True)
    states = {
        "off": [draw_body(kind, fac, p).im],
        "broken": [draw_broken(kind, fac, p)],
        "panel": [draw_panel(kind, fac, p)],
        "normal-unshaded": [lights_normal(kind, fac, p, f) for f in range(4)],
        "deny-unshaded": [lights_deny(kind, fac, p, f) for f in range(2)],
        "eject-unshaded": [lights_eject(kind, fac, p, f) for f in range(EJECT_FRAMES)],
    }
    delays = {"normal-unshaded": 0.5, "deny-unshaded": 0.25, "eject-unshaded": 0.2}
    meta_states = []
    for st, frames in states.items():
        sheet(frames).save(os.path.join(path, st + ".png"))
        entry = {"name": st}
        if len(frames) > 1:
            entry["delays"] = [[delays[st]] * len(frames)]
        meta_states.append(entry)
    meta = {
        "version": 1,
        "license": "CC-BY-SA-3.0",
        "copyright": "Original art for Eclipsion by Taleryn",
        "size": {"x": S, "y": S},
        "states": meta_states,
    }
    with open(os.path.join(path, "meta.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(meta, fh, indent=2)
        fh.write("\n")
    return states


# ---------------------------------------------------------------- shipyard console screens

SCREEN_SRC = os.path.join(REPO, "Resources/Textures/_Crescent/Structures/Machines/shipyard_console.rsi")
SCREEN_OUT = os.path.join(REPO, "Resources/Textures/_Crescent/Structures/Machines/ShipyardScreens")
# Taleryn's screen is drawn in exactly these four colours; each maps onto a step of the faction accent.
SCREEN_KEYS = {(24, 57, 70): "bg", (34, 81, 96): "edge", (72, 191, 200): "mid", (182, 246, 239): "light"}


def write_screen(name, fac):
    """Palette-swap the shared shipyard screen onto a faction accent. The original stays the neutral one."""
    acc = rgb(fac["accent"])
    ramp = {"bg": scale(acc, 0.31), "edge": scale(acc, 0.45), "mid": acc, "light": mix(acc, WHITE, 0.62)}
    im = Image.open(os.path.join(SCREEN_SRC, "screen.png")).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            key = SCREEN_KEYS.get((r, g, b))
            if key is None:
                raise ValueError(f"shipyard screen has an unmapped colour {(r, g, b)} at {x},{y}; extend SCREEN_KEYS")
            px[x, y] = ramp[key] + (a,)
    path = os.path.join(SCREEN_OUT, f"{name}.rsi")
    os.makedirs(path, exist_ok=True)
    im.save(os.path.join(path, "screen.png"))
    with open(os.path.join(SCREEN_SRC, "meta.json"), encoding="utf-8-sig") as fh:
        meta = json.load(fh)
    meta["copyright"] = "Faction recolour of Taleryn's shipyard console screen for Hullrot:Eclipsion"
    with open(os.path.join(path, "meta.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(meta, fh, indent=2)
        fh.write("\n")
    return im


def main():
    rendered = {}
    for kind in ("armory", "supply"):
        for name, fac in FACTIONS.items():
            rendered[(kind, name)] = write_rsi(kind, name, fac)
    print(f"wrote {len(rendered)} RSIs to {os.path.normpath(OUT)}")

    screens = {name: write_screen(name, fac) for name, fac in FACTIONS.items() if name != "neutral"}
    print(f"wrote {len(screens)} shipyard screens to {os.path.normpath(SCREEN_OUT)}")

    if PREVIEW:
        # Rows: faction. Columns: armory off / lit / broken+panel, supply off / lit / broken+panel. 4x.
        z, pad = 4, 4
        names = list(FACTIONS)
        cell = S * z + pad
        out = Image.new("RGBA", (6 * cell + pad, len(names) * cell + pad), (40, 44, 50, 255))
        for r, name in enumerate(names):
            for k, kind in enumerate(("armory", "supply")):
                st = rendered[(kind, name)]
                off = st["off"][0]
                lit = Image.alpha_composite(off, st["normal-unshaded"][0])
                brk = Image.alpha_composite(st["broken"][0], st["panel"][0])
                for j, im in enumerate((off, lit, brk)):
                    out.paste(im.resize((S * z, S * z), Image.NEAREST),
                              (pad + (k * 3 + j) * cell, pad + r * cell))
        out.save(PREVIEW)
        print("preview:", PREVIEW)

        # Shipyard screens: neutral original first, then each faction; first frame of each direction row.
        src = Image.open(os.path.join(SCREEN_SRC, "screen.png")).convert("RGBA")
        sheets = [src] + list(screens.values())
        strip = Image.new("RGBA", (len(sheets) * (S * z + pad) + pad, 2 * (S * z + pad) + pad), (40, 44, 50, 255))
        for i, sh in enumerate(sheets):
            for row in range(2):  # south and east sit on rows 0 and 2 of the 6-wide sheet
                fr = sh.crop((0, row * 2 * S, S, row * 2 * S + S)).resize((S * z, S * z), Image.NEAREST)
                strip.paste(fr, (pad + i * (S * z + pad), pad + row * (S * z + pad)), fr)
        screens_preview = os.path.splitext(PREVIEW)[0] + "_screens.png"
        strip.save(screens_preview)
        print("preview:", screens_preview)


if __name__ == "__main__":
    main()
