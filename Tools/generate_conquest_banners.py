#!/usr/bin/env python3
"""Generate the faction conquest banner states in medieval_pole_banners.rsi.

DSM, NCWL and TAP were drawn by hand (black-purple, brown-ncwl, green-gold) and are left alone.
Every other faction's banner is recoloured from `neutral-white`, the clean four-tone master:

    (236,236,232) highlight   (209,209,205) light   (180,180,176) base   (56,56,52) dark

The pole and its finial stay grey — only the cloth is tinted. Inside the cloth, the dark tone is
the border where it touches empty space (that becomes the faction's trim colour, matching the gold
edging on green-gold) and a fold shadow where it does not (that stays a darker primary).

Run from the repo root:  python Tools/generate_conquest_banners.py
"""

import json
import os

from PIL import Image

RSI = os.path.join("Resources", "Textures", "_Crescent", "Structures", "medieval_pole_banners.rsi")
MASTER = "neutral-white"

HIGHLIGHT = (236, 236, 232)
LIGHT = (209, 209, 205)
BASE = (180, 180, 176)
DARK = (56, 56, 52)

# Rows the cloth hangs across. Above and below this band the sprite is pure pole.
CLOTH_TOP = 11
CLOTH_BOTTOM = 28
# Down to this row the cloth touches the pole, so the pole is the leftmost two pixels. Below it the
# cloth has receded and a transparent gap separates them, so the first opaque run is the pole.
POLE_ADJACENT_UNTIL = 24

# primary: cloth base. trim: the border that reads as the banner's edging.
# Colours follow each faction's uiAccent in Resources/Prototypes/_Crescent/Roles/factions.yml.
BANNERS = {
    # Shinohara Heavy Industries - corporate teal, steel edging.
    "teal-steel": {"primary": (23, 138, 156), "trim": (206, 220, 224)},
    # Taypani Free Companies Federation - federation crimson, gunmetal edging.
    "crimson-steel": {"primary": (176, 46, 42), "trim": (168, 176, 184)},
    # Gliess Santo - harbour navy, bleached white edging.
    "navy-white": {"primary": (37, 66, 122), "trim": (232, 236, 240)},
    # Colonial Minutemen - militia azure, buff canvas edging.
    "azure-buff": {"primary": (62, 118, 190), "trim": (214, 190, 140)},
    # The Saint's Militia - funeral black, bone edging.
    "black-bone": {"primary": (34, 32, 36), "trim": (184, 169, 122)},
    # Crown Expeditionary Force - Imperial ivory, Crown gold edging.
    "ivory-gold": {"primary": (223, 219, 200), "trim": (208, 170, 64)},
}


def scale(color, factor):
    return tuple(min(255, max(0, round(c * factor))) for c in color)


def cloth_ramp(primary):
    """Four cloth tones from one primary, mirroring neutral-white's own spacing."""
    return {
        HIGHLIGHT: scale(primary, 1.34),
        LIGHT: scale(primary, 1.16),
        BASE: primary,
        DARK: scale(primary, 0.62),  # interior fold shadow
    }


def pole_mask(px, width, height):
    """Pixels belonging to the pole and its finial, which keep the master's grey."""
    mask = set()
    for y in range(height):
        opaque = [x for x in range(width) if px[x, y][3] > 0]
        if not opaque:
            continue
        if y < CLOTH_TOP or y > CLOTH_BOTTOM:
            mask.update((x, y) for x in opaque)
        elif y <= POLE_ADJACENT_UNTIL:
            mask.update((opaque[0] + i, y) for i in (0, 1))
        else:
            # First contiguous run from the left.
            run = [opaque[0]]
            for x in opaque[1:]:
                if x != run[-1] + 1:
                    break
                run.append(x)
            mask.update((x, y) for x in run)
    return mask


def nearest_tone(rgb):
    """Snap an antialiased stray to the nearest of the four master tones."""
    return min((HIGHLIGHT, LIGHT, BASE, DARK), key=lambda t: sum((a - b) ** 2 for a, b in zip(rgb, t)))


def build(master, name, primary, trim):
    width, height = master.size
    src = master.convert("RGBA").load()
    pole = pole_mask(src, width, height)
    ramp = cloth_ramp(primary)
    trim_shadow = scale(trim, 0.72)

    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    dst = out.load()

    def transparent(x, y):
        return not (0 <= x < width and 0 <= y < height) or src[x, y][3] == 0

    for y in range(height):
        for x in range(width):
            r, g, b, a = src[x, y]
            if a == 0:
                continue
            if (x, y) in pole:
                dst[x, y] = (r, g, b, a)
                continue

            tone = nearest_tone((r, g, b))
            if tone is DARK:
                # Border against empty space or against the pole becomes trim; anything the cloth
                # closes over is a fold, and stays a dark primary.
                edge = any(
                    transparent(x + dx, y + dy) or (x + dx, y + dy) in pole
                    for dx in (-1, 0, 1)
                    for dy in (-1, 0, 1)
                    if (dx, dy) != (0, 0)
                )
                dst[x, y] = (trim if edge else ramp[DARK]) + (a,)
            elif tone is HIGHLIGHT and any((x + dx, y + dy) in pole for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                # Highlights hugging the pole read as the cloth's inner seam.
                dst[x, y] = trim_shadow + (a,)
            else:
                dst[x, y] = ramp[tone] + (a,)

    out.save(os.path.join(RSI, name + ".png"))


def main():
    if not os.path.isdir(RSI):
        raise SystemExit("run this from the repo root: " + RSI + " not found")

    master = Image.open(os.path.join(RSI, MASTER + ".png")).convert("RGBA")
    for name, colors in BANNERS.items():
        build(master, name, colors["primary"], colors["trim"])
        print("wrote", name + ".png")

    meta_path = os.path.join(RSI, "meta.json")
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)
    known = {s["name"] for s in meta["states"]}
    for name in BANNERS:
        if name not in known:
            meta["states"].append({"name": name})
    with open(meta_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, indent=2)
        f.write("\n")
    print("updated meta.json")


if __name__ == "__main__":
    main()
