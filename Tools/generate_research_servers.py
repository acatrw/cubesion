"""Generates the faction research server RSIs.

The Crescent research servers all shared vanilla's Structures/Machines/server.rsi with a purple
`variant-research` decal glued on, so ten different faction servers were indistinguishable on a map.
This draws a rack per faction from scratch instead, on vanilla's footprint (x 3..28, y 2..29) so the
machine still reads as a floor-standing cabinet next to the rest of the machine sprites.

Every rack is the same three-band chassis -- crest plate on the top face, bay column in the middle,
intake grille at the foot -- but the cap silhouette, crest glyph, bay dressing and grille pattern all
vary per faction, so two servers stay apart even in greyscale, not just by hue.

States: server (the chassis) and server_o (the open maintenance panel, WiresVisuals' layer).

Adding a faction = one FACTIONS entry (plus a GLYPHS entry if it needs a new crest).

Usage: python Tools/generate_research_servers.py [repo] [--preview out.png]   (needs Pillow; overwrites
Resources/Textures/_Crescent/Structures/Machines/ResearchServers in place)
"""
import json
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
OUT = os.path.join(REPO, "Resources/Textures/_Crescent/Structures/Machines/ResearchServers")

S = 32
X0, X1 = 3, 28          # body columns, inclusive
Y0, Y1 = 2, 29          # body rows, inclusive
PLATE_BOX = (11, 4, 19, 12)   # recessed crest plate
GLYPH_AT = (12, 5)            # 7x7 crest glyph origin
BAY_TOP, BAY_BOTTOM = 15, 25
GRILLE_TOP = 26

BAY = (18, 20, 24)
BAY_LIT = (44, 48, 58)
STEEL = (150, 156, 166)
LED_DIM = (40, 92, 48)
SHADOW = (0, 0, 0, 80)
WIRES = [(206, 62, 52), (226, 196, 64), (84, 186, 96), (74, 126, 214)]

# cap:    silhouette cut into the top two rows (cap_spans)
# emblem: crest glyph on the plate (GLYPHS)
# bays:   what fills the middle band -- blade slots, card stack, tape drums, a mixed tower
# grille: intake pattern at the foot
# Colours follow each faction's vendor chassis/accent in Tools/generate_hullrot_vendors.py where the
# server belongs to a faction; the four corporate trees (Interdyne, Cyberdawn, Pang Tai, Gliess Santo)
# get their own, since they are houses rather than powers.
FACTIONS = {
    # Divine Sol Mandate -- the Imperial tree. Sun crest, tape drums, louvred intake.
    "imperial":  dict(chassis="#48425A", accent="#9D7BE6", cap="crown",   emblem="sun",      bays="drums", grille="louvre"),
    # New Crescent Workers' League -- the Communard tree. Star crest, card stack, mesh intake.
    "communard": dict(chassis="#51533F", accent="#D9962B", cap="vents",   emblem="star",     bays="stack", grille="mesh"),
    # Shinohara Heavy Industries -- the Corporate tree. Pale industrial chassis, blade slots.
    "corporate": dict(chassis="#7F888C", accent="#6FB0A6", cap="dome",    emblem="s",        bays="slots", grille="lines"),
    # Taypani Free Companies Federation -- the Coalition tree. Diamond crest, card stack.
    "coalition": dict(chassis="#56453F", accent="#D0463F", cap="chamfer", emblem="diamonds", bays="stack", grille="louvre"),
    # Taypani-Atyrian Pact -- the Families tree. Crescent crest, tape drums, mesh intake.
    "families":  dict(chassis="#766650", accent="#5DBB5A", cap="stepped", emblem="crescent", bays="drums", grille="mesh"),
    # Colonial Minutemen. Shield crest, blade slots, notched cap.
    "minutemen": dict(chassis="#45536A", accent="#4E8FD6", cap="notch",   emblem="shield",   bays="drums", grille="lines"),
    # Gliess Santo -- harbour navy, the civilian tree the shuttles carry.
    "gliessian": dict(chassis="#25324F", accent="#9CC4EE", cap="flat",    emblem="anchor",   bays="slots", grille="mesh"),
    # Pang Tai Arms, Gu Tian works -- jade over lacquered brown, gate crest.
    "pangtai":   dict(chassis="#4A3A34", accent="#46BE92", cap="stepped", emblem="gate",     bays="slots", grille="lines"),
    # Cyberdawn Technologies -- black chassis, cyan circuitry, a readout in the tower.
    "cyberdawn": dict(chassis="#2A2E3A", accent="#25D0D0", cap="badge",   emblem="circuit",  bays="tower", grille="mesh"),
    # Interdyne Pharmaceuticals -- clinical green, flask crest, cold-storage tower.
    "interdyne": dict(chassis="#3F4A44", accent="#4FC98A", cap="arch",    emblem="flask",    bays="tower", grille="louvre"),
}

# 7x7 crests. '#' is the accent, '+' its darker tone, '.' leaves the plate showing.
GLYPHS = {
    "sun":      ["#..#..#", ".+###+.", ".##.##.", "###.###", ".##.##.", ".+###+.", "#..#..#"],
    "star":     ["...#...", "...#...", "#######", ".+###+.", "..###..", ".##.##.", "#.....#"],
    "s":        [".#####.", "##...##", "##.....", ".+###+.", ".....##", "##...##", ".#####."],
    "diamonds": [".#...#.", "###+###", ".#...#.", ".......", ".#...#.", "###+###", ".#...#."],
    "crescent": ["..###..", ".##+...", "##.....", "##...#.", "##.....", ".##+...", "..###.."],
    "shield":   ["#######", "#.....#", "#.###.#", "#.###.#", "+#...#+", ".+###+.", "...#..."],
    "anchor":   ["..###..", "..#.#..", "...#...", ".#####.", "#..#..#", "#..#..#", ".+###+."],
    "gate":     ["#######", ".#####.", "..#.#..", "#######", "..#.#..", ".#####.", "#######"],
    "circuit":  ["#.#.#.#", "#+#+#+#", "#######", "...#...", "#######", "#+#+#+#", "#.#.#.#"],
    "flask":    ["..###..", "...#...", "...#...", "..#+#..", ".##+##.", "##+++##", ".#####."],
}


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def scale(c, k):
    return tuple(max(0, min(255, int(round(v * k)))) for v in c[:3])


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


class Canvas:
    def __init__(self):
        self.im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        self.px = self.im.load()

    def put(self, x, y, c):
        if 0 <= x < S and 0 <= y < S and c is not None:
            self.px[x, y] = c if len(c) == 4 else c + (255,)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.put(x, y, c)

    def clear(self, x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if 0 <= x < S and 0 <= y < S:
                    self.px[x, y] = (0, 0, 0, 0)

    def glyph(self, art, x0, y0, on, dim):
        for dy, row in enumerate(art):
            for dx, ch in enumerate(row):
                if ch == "#":
                    self.put(x0 + dx, y0 + dy, on)
                elif ch == "+":
                    self.put(x0 + dx, y0 + dy, dim)


def cap_spans(cap):
    """Columns kept in the top rows, as {row: [(x0, x1), ...]}.

    Row Y0 is the cabinet's own top row, so trimming it is what cuts the silhouette; row Y0 - 1 is a
    crest rising above the cabinet. Everything below Y0 is always the full width.
    """
    mid = (X0 + X1) // 2
    if cap == "flat":
        return {Y0: [(X0, X1)]}
    if cap == "notch":
        return {Y0: [(X0, mid - 3), (mid + 4, X1)]}
    if cap == "crown":
        return {Y0 - 1: [(X0 + 1, X0 + 3), (mid - 1, mid + 2), (X1 - 3, X1 - 1)],
                Y0: [(X0, X1)]}
    if cap == "vents":
        spans, x = [], X0
        while x <= X1:
            spans.append((x, min(x + 3, X1)))
            x += 6
        return {Y0: spans}
    if cap == "dome":
        return {Y0: [(X0 + 3, X1 - 3)]}
    if cap == "chamfer":
        return {Y0: [(X0 + 2, X1 - 2)]}
    if cap == "stepped":
        return {Y0 - 1: [(X0 + 6, X1 - 6)], Y0: [(X0 + 2, X1 - 2)]}
    if cap == "badge":
        return {Y0 - 1: [(mid - 2, mid + 3)], Y0: [(X0 + 1, X1 - 1)]}
    if cap == "arch":
        return {Y0 - 1: [(mid - 3, mid + 4)], Y0: [(X0 + 3, X1 - 3)]}
    raise KeyError(cap)


def draw_bays(c, style, pal):
    """The middle band: how this faction stores the research it is sitting on."""
    body, lit, dark, accent, accent_dim = pal
    if style == "slots":
        # Four hot-swap blades, each with a puller handle and a status LED pair.
        for i, y in enumerate(range(BAY_TOP, BAY_BOTTOM, 3)):
            c.rect(X0 + 2, y, X1 - 4, y + 1, BAY)
            c.rect(X0 + 3, y, X0 + 7, y, STEEL)
            c.rect(X0 + 9, y + 1, X1 - 6, y + 1, BAY_LIT)
            c.put(X1 - 3, y, accent if i != 2 else LED_DIM)
            c.put(X1 - 2, y, accent_dim)
    elif style == "stack":
        # Vertical cards edge-on in a cage, the way a filing rack reads from above.
        c.rect(X0 + 1, BAY_TOP, X1 - 1, BAY_BOTTOM, BAY)
        for i, x in enumerate(range(X0 + 3, X1 - 2, 3)):
            c.rect(x, BAY_TOP + 1, x + 1, BAY_BOTTOM - 1, dark)
            c.put(x, BAY_TOP + 1, accent if i % 2 == 0 else STEEL)
            c.put(x + 1, BAY_TOP + 1, accent_dim if i % 2 == 0 else BAY_LIT)
        c.rect(X0 + 1, BAY_BOTTOM, X1 - 1, BAY_BOTTOM, lit)
    elif style == "drums":
        # Two archival tape drums -- the old houses never stopped spooling their records.
        c.rect(X0 + 1, BAY_TOP, X1 - 1, BAY_BOTTOM, BAY)
        cy = (BAY_TOP + BAY_BOTTOM) // 2
        for cx in (X0 + 7, X1 - 7):
            for dy in range(-4, 5):
                for dx in range(-4, 5):
                    d = dx * dx + dy * dy
                    if d > 17:
                        continue
                    # Light flange, dark spooled tape inside it, lit hub at the spindle.
                    c.put(cx + dx, cy + dy, STEEL if d > 8 else BAY)
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                c.put(cx + dx, cy + dy, accent_dim)
            c.put(cx, cy, accent)
        c.rect(X0 + 1, BAY_BOTTOM, X1 - 1, BAY_BOTTOM, lit)
    elif style == "tower":
        # A readout panel beside a bank of chilled cores: the corporate laboratory build.
        c.rect(X0 + 1, BAY_TOP, X1 - 1, BAY_BOTTOM, BAY)
        c.rect(X0 + 2, BAY_TOP + 1, X0 + 12, BAY_TOP + 7, (10, 14, 18))
        # Readout: three bars of unequal length, each on its own line so they stay countable.
        for i, width in enumerate((8, 4, 6)):
            y = BAY_TOP + 2 + i * 2
            c.rect(X0 + 3, y, X0 + 3 + width, y, accent if i != 1 else accent_dim)
        for x in range(X1 - 10, X1 - 1, 3):
            c.rect(x, BAY_TOP + 1, x + 1, BAY_BOTTOM - 2, dark)
            c.put(x, BAY_TOP + 1, accent_dim)
        c.rect(X0 + 2, BAY_BOTTOM - 2, X0 + 12, BAY_BOTTOM - 1, dark)
        c.rect(X0 + 1, BAY_BOTTOM, X1 - 1, BAY_BOTTOM, lit)
    else:
        raise KeyError(style)


def draw_grille(c, style, pal):
    body, lit, dark, accent, accent_dim = pal
    top, bottom = GRILLE_TOP, Y1 - 1
    c.rect(X0 + 1, top, X1 - 1, bottom, dark)
    if style == "lines":
        for y in range(top, bottom + 1, 2):
            c.rect(X0 + 2, y, X1 - 2, y, BAY)
    elif style == "mesh":
        for y in range(top, bottom + 1):
            for x in range(X0 + 2, X1 - 1):
                if (x + y) % 2 == 0:
                    c.put(x, y, BAY)
    elif style == "louvre":
        for x in range(X0 + 2, X1 - 1, 3):
            c.rect(x, top, x + 1, bottom, BAY)
    else:
        raise KeyError(style)


def build_server(f):
    body = rgb(f["chassis"])
    lit = scale(body, 1.28)
    dark = scale(body, 0.66)
    edge = scale(body, 0.40)
    plate = scale(body, 0.52)
    accent = rgb(f["accent"])
    accent_dim = scale(accent, 0.58)
    pal = (body, lit, dark, accent, accent_dim)

    c = Canvas()
    # Chassis, then the silhouette cut out of the top rows.
    c.rect(X0, Y0, X1, Y1, body)
    spans = cap_spans(f["cap"])
    c.clear(X0, Y0, X1, Y0)
    for a, b in spans.get(Y0, []):
        c.rect(a, Y0, b, Y0, lit)
    for a, b in spans.get(Y0 - 1, []):
        c.rect(a, Y0 - 1, b, Y0 - 1, lit)
    # Edges: lifted along the left, shaded down the right, black along the foot.
    c.rect(X0, Y0 + 1, X0, Y1, mix(body, lit, 0.5))
    c.rect(X1, Y0 + 1, X1, Y1, dark)
    c.rect(X0, Y1, X1, Y1, edge)

    # Crest plate on the top face.
    px0, py0, px1, py1 = PLATE_BOX
    c.rect(px0, py0, px1, py1, plate)
    c.rect(px0, py0, px1, py0, edge)
    c.rect(px0, py0, px0, py1, edge)
    c.rect(px1, py0 + 1, px1, py1, mix(body, lit, 0.35))
    c.rect(px0 + 1, py1, px1, py1, mix(body, lit, 0.35))
    c.glyph(GLYPHS[f["emblem"]], GLYPH_AT[0], GLYPH_AT[1], accent, accent_dim)
    # Rivet column either side of the plate, so the top face is not bare.
    for y in range(py0 + 1, py1, 2):
        c.put(X0 + 2, y, dark)
        c.put(X1 - 2, y, dark)

    # Divider between the top face and the bays.
    c.rect(X0, 13, X1, 13, edge)
    c.rect(X0, 14, X1, 14, dark)
    draw_bays(c, f["bays"], pal)
    draw_grille(c, f["grille"], pal)

    # Drop shadow, one pixel out on the shaded sides.
    for y in range(Y0 + 2, Y1 + 2):
        c.put(X1 + 1, y, SHADOW)
    for x in range(X0 + 1, X1 + 2):
        c.put(x, Y1 + 1, SHADOW)
    return c.im


def build_panel(f):
    """The open maintenance hatch: cavity, four wires, and the flap folded down below it."""
    body = rgb(f["chassis"])
    c = Canvas()
    x0, y0, x1, y1 = X0 + 1, 16, X0 + 10, 24
    c.rect(x0, y0, x1, y1, (14, 16, 20))
    c.rect(x0, y0, x1, y0, (6, 7, 9))
    c.rect(x0, y0 + 1, x0, y1, (6, 7, 9))
    for i, w in enumerate(WIRES):
        y = y0 + 2 + i * 2
        c.rect(x0 + 1, y, x1 - 2, y, w)
        c.put(x1 - 1, y, scale(w, 0.6))
    c.rect(x0, y1 + 1, x1, y1 + 2, scale(body, 0.85))
    c.rect(x0, y1 + 1, x1, y1 + 1, scale(body, 1.15))
    return c.im


def meta():
    return {
        "version": 1,
        "size": {"x": 32, "y": 32},
        "license": "CC-BY-SA-3.0",
        "copyright": "Made for Eclipsion by Taleryn, generated by Tools/generate_research_servers.py",
        "states": [{"name": "server"}, {"name": "server_o"}],
    }


def main():
    previews = []
    for name, f in FACTIONS.items():
        rsi = os.path.join(OUT, name + ".rsi")
        os.makedirs(rsi, exist_ok=True)
        server = build_server(f)
        panel = build_panel(f)
        server.save(os.path.join(rsi, "server.png"))
        panel.save(os.path.join(rsi, "server_o.png"))
        with open(os.path.join(rsi, "meta.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(meta(), fh, indent=4)
            fh.write("\n")
        previews.append((server, panel))
        print("wrote", os.path.relpath(rsi, REPO))

    if PREVIEW:
        sheet = Image.new("RGBA", (S * len(previews), S * 2), (24, 24, 28, 255))
        for i, (server, panel) in enumerate(previews):
            sheet.alpha_composite(server, (i * S, 0))
            sheet.alpha_composite(server, (i * S, S))
            sheet.alpha_composite(panel, (i * S, S))
        sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(PREVIEW)
        print("preview ->", PREVIEW)


if __name__ == "__main__":
    main()
