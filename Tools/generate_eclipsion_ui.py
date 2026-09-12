"""Generates the Eclipsion HUD theme + chrome textures.

Everything is derived from one chamfered-rect ring function so slots, highlights
and buttons read as one family. Chamfer sits on the top-right / bottom-left
corners, same orientation as the stock Nano button, so OpenLeft/OpenRight
atlases keep their meaning.

Usage: python Tools/generate_eclipsion_ui.py   (needs Pillow; overwrites
Resources/Textures/_Crescent/Interface/Eclipsion in place)
"""
import os
import sys
from PIL import Image

REPO = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(REPO, "Resources/Textures/_Crescent/Interface/Eclipsion")
DEFAULT = os.path.join(REPO, "Resources/Textures/Interface/Default")

# Cool gunmetal ramp.
OUTLINE = (7, 8, 10)
FILL_TOP = (25, 29, 34)
FILL_BOT = (15, 17, 21)
EDGE = (38, 44, 51)
EDGE_HI = (60, 68, 79)
EDGE_LO = (27, 31, 37)
TICK = (92, 103, 116)
ICON_LO = (38, 45, 54)
ICON_HI = (112, 124, 139)
TICK_LEN = 4


def ring(x, y, w, h, c):
    """Distance (in rings) from the edge of a w*h rect with c-px chamfers at TR and BL
    and 1px corner cuts at TL and BR. Negative = outside."""
    r, b = w - 1, h - 1
    return min(
        x, y, r - x, b - y,
        (r - x) + y - c,        # top-right chamfer
        x + (b - y) - c,        # bottom-left chamfer
        x + y - 1,              # top-left nick
        (r - x) + (b - y) - 1,  # bottom-right nick
    )


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def tick_pixels(size=32):
    """Bracket ticks in the two un-chamfered inner corners, keyed by corner."""
    tl, br = [], []
    for i in range(TICK_LEN):
        tl += [(3 + i, 3), (3, 3 + i)]
        br += [(size - 4 - i, size - 4), (size - 4, size - 4 - i)]
    return {"tl": tl, "br": br}


def slot_background(size=32, c=5, ticks=("tl", "br")):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = im.load()
    for y in range(size):
        for x in range(size):
            k = ring(x, y, size, size, c)
            if k < 0:
                continue
            if k == 0:
                px[x, y] = OUTLINE + (245,)
            elif k == 1:
                # Frame, lit from the top-left.
                if y == 1 or x == 1:
                    col = EDGE_HI
                elif y == size - 2 or x == size - 2:
                    col = EDGE_LO
                else:
                    col = EDGE
                px[x, y] = col + (250,)
            else:
                t = (y - 2) / (size - 5)
                col = lerp(FILL_TOP, FILL_BOT, t)
                if y % 2 == 1:  # faint scanlines
                    col = tuple(max(0, v - 3) for v in col)
                if k == 2 and y == size - 3:
                    col = tuple(max(0, v - 5) for v in col)  # inner bottom shadow
                px[x, y] = col + (242,)
    all_ticks = tick_pixels(size)
    for corner in ticks:
        for (x, y) in all_ticks[corner]:
            px[x, y] = TICK + (170,)
    return im


def slot_highlight(size=32, c=5):
    """White so the stylesheet can tint it with the faction accent."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = im.load()
    corner = 8
    for y in range(size):
        for x in range(size):
            k = ring(x, y, size, size, c)
            near_corner = (min(x, size - 1 - x) < corner) and (min(y, size - 1 - y) < corner)
            if k == 1:
                px[x, y] = (255, 255, 255, 235)
            elif k == 2 and near_corner:
                px[x, y] = (255, 255, 255, 200)
    return im


def button(size=24, c=5):
    """White-based: the stylesheet modulates it, so shading here is a multiplier."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = im.load()
    for y in range(size):
        for x in range(size):
            k = ring(x, y, size, size, c)
            if k < 0:
                continue
            if k == 0:
                v = 150
            elif y == 1 and k == 1:
                v = 255
            elif y == size - 2 and k == 1:
                v = 182
            else:
                v = 214
            px[x, y] = (v, v, v, 255)
    return im


def remap(im, whiten=False):
    """Push a stock (purple-grey) texture onto the cool gunmetal ramp.
    Saturated pixels are kept, or turned white when whiten is set (tinted at runtime)."""
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            sat = max(r, g, b) - min(r, g, b)
            if sat > 40:
                if whiten:
                    px[x, y] = (255, 255, 255, a)
                continue
            px[x, y] = (
                min(255, int(lum * 0.86)),
                min(255, int(lum * 0.97)),
                min(255, int(lum * 1.12)),
                a,
            )
    return im


def slot_icon(name):
    """Lift the silhouette off the stock slot icon and re-seat it on our background."""
    # Stock icons are blue-tinted on a grey slot, and a few (belt, id) sit on a differently
    # sized slot, so pick the silhouette by saturation rather than by diffing backgrounds.
    src = Image.open(os.path.join(DEFAULT, "Slots", name + ".png")).convert("RGBA")
    sp = src.load()
    mask = {}
    for y in range(32):
        for x in range(32):
            s = sp[x, y]
            if s[3] > 0 and max(s[:3]) - min(s[:3]) >= 18:
                mask[(x, y)] = 0.299 * s[0] + 0.587 * s[1] + 0.114 * s[2]
    # Drop a corner tick if the silhouette crowds it (the "R" on hand_r sits top-left).
    keep = []
    for corner, pts in tick_pixels().items():
        near = any(abs(mx - tx) <= 1 and abs(my - ty) <= 1 for (tx, ty) in pts for (mx, my) in mask)
        if not near:
            keep.append(corner)
    out = slot_background(ticks=tuple(keep))
    if not mask:
        return out
    lo, hi = min(mask.values()), max(mask.values())
    span = max(1.0, hi - lo)
    op = out.load()
    for (x, y), lum in mask.items():
        t = (lum - lo) / span
        op[x, y] = lerp(ICON_LO, ICON_HI, t) + (255,)
    return out


NANO = os.path.join(REPO, "Resources/Textures/Interface/Nano")
# Stock Nano panel colours -> Eclipsion gunmetal. Same geometry, so patch margins keep working.
NANO_MAP = {
    (0x25, 0x25, 0x26): (0x16, 0x19, 0x1D),  # window body
    (0x35, 0x35, 0x37): (0x2B, 0x31, 0x38),  # bordered panel edge
    (0x24, 0x24, 0x25): (0x13, 0x16, 0x1A),  # bordered panel centre
    (0x30, 0x30, 0x31): (0x0F, 0x12, 0x16),  # window header strip
    (0x3A, 0x3A, 0x3D): (0x32, 0x39, 0x41),  # tooltip / light panel edge
    (0x1B, 0x1B, 0x1C): (0x10, 0x12, 0x15),  # tooltip centre
    (0x41, 0x41, 0x45): (0x3A, 0x42, 0x4B),
    (0x38, 0x38, 0x3A): (0x2F, 0x36, 0x3E),
    (0x1D, 0x1D, 0x1E): (0x0E, 0x10, 0x13),
    (0x4A, 0x4A, 0x4A): (0x3A, 0x42, 0x4B),  # search box edge
    (0x00, 0x00, 0x00): (0x07, 0x08, 0x0A),
}
NANO_FILES = (
    "window_background", "window_background_bordered", "window_header", "tooltip", "lineedit",
    "tabcontainer_panel", "transparent_window_background_bordered", "light_panel_background_bordered",
    "black_panel_dark_thin_border",
)


def nano_panel(name):
    im = Image.open(os.path.join(NANO, name + ".png")).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a == 0 and (r, g, b) == (0, 0, 0):
                continue
            # window_header's drop shadow rows are pure black with partial alpha: leave them.
            if (r, g, b) == (0, 0, 0) and a < 255:
                continue
            new = NANO_MAP.get((r, g, b))
            if new is None:
                raise SystemExit(f"unmapped colour #{r:02x}{g:02x}{b:02x} in {name}")
            px[x, y] = new + (a,)
    return im


def save(im, rel):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, optimize=True)


def main():
    hud = "Hud"
    bg = slot_background()
    save(bg, f"{hud}/SlotBackground.png")
    save(slot_highlight(), f"{hud}/slot_highlight.png")

    for f in sorted(os.listdir(os.path.join(DEFAULT, "Slots"))):
        if f.endswith(".png"):
            save(slot_icon(f[:-4]), f"{hud}/Slots/{f}")

    for f in ("item_status_left", "item_status_right", "template_small"):
        save(remap(Image.open(os.path.join(DEFAULT, f + ".png"))), f"{hud}/{f}.png")
    for f in ("item_status_left_highlight", "item_status_right_highlight"):
        save(remap(Image.open(os.path.join(DEFAULT, f + ".png")), whiten=True), f"{hud}/{f}.png")

    for f in sorted(os.listdir(os.path.join(DEFAULT, "Storage"))):
        if f.endswith(".png") and not f.startswith("marked_"):
            save(remap(Image.open(os.path.join(DEFAULT, "Storage", f))), f"{hud}/Storage/{f}")

    save(button(), "Nano/button.png")
    for f in NANO_FILES:
        save(nano_panel(f), f"Nano/{f}.png")


if __name__ == "__main__":
    main()
