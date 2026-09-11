# Alien star system hologram

Source artwork and reproducible animation assembly for `holograph_star_system`.
The game uses the PNG and metadata in
`Resources/Textures/DeltaV/Structures/Decoration/shuttle_manipulator.rsi/`.
Open `preview.html` directly in a browser to play that actual game sprite sheet.

## Rebuild

Run on Windows from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Tools/Art/HolographStarSystem/build.ps1
python RobustToolbox/Schemas/validate_rsis.py Resources/Textures/DeltaV/Structures/Decoration
```

Requires Windows PowerShell and System.Drawing; the validator requires Pillow and jsonschema.
The build writes 96 transparent 64×64 frames in 12 columns. Metadata uses 0.1 seconds
per frame for a 9.6-second loop. All orbital speeds and pulses complete whole cycles;
front and back passes place planets on the appropriate side of the central sun.
The generated `preview/` directory contains enlarged contact frames and is ignored.

`celestials-keyed.png` was created using the built-in OpenAI image generation tool,
then exported against a green color key. The build converts that key to real alpha
and resizes the sprites with nearest-neighbor sampling. No API key or image service
is needed to rebuild. `projector-base.png` preserves the existing pedestal, whose
MonkeyStation source and CC-BY-SA-3.0 license are recorded in the RSI metadata.
The other hologram states are not rebuilt by this script.

## Generation prompt

Use case: stylized-concept. Asset type: transparent game sprite source atlas for a 64x64 pixel holographic alien solar system animation in Space Station 14. Generate ONE atlas with EXACTLY 3 columns and 2 rows of evenly sized square cells, overall landscape 1536x1024. Genuine transparent background; no backdrop, no checkerboard, no text, no grid lines. Every cell contains ONE isolated celestial sprite, fully inside its cell with ample transparent margin, centered exactly in that cell. Strict chunky low-resolution pixel art, each sprite should look like 16x16 to 24x24 pixel art enlarged using nearest neighbor, hard square pixel clusters, no smooth illustration. Rich luminous colors and dark opaque shaded silhouettes for readability. Top-left: brilliant PURPLE SUN, round violet plasma sphere, hot pale lavender core and vivid purple/magenta jagged solar corona; no white star spikes. Top-middle: alien turquoise gas giant with conspicuous thin tilted lavender planetary ring and teal cloud stripes. Top-right: shattered orange/ochre planet, two visibly separated halves with a dark diagonal gap, glowing orange magma fracture and 3 small rock shards beside it. Bottom-left: smaller sinister indigo planet with unnatural branching bright pink glowing fissures. Bottom-middle: very small icy pale mint irregular cratered moon. Bottom-right: medium lavender crystal world, angular rocky asymmetric silhouette, luminous pale violet crystalline plates and dark purple shadow. All lit from upper left with deep shadows at lower right. No Earth continents, no familiar solar system. These six assets will be downscaled individually, then animated in orbits in the game. Prioritize strong distinguishable silhouettes and restrained pixel details; isolated bodies only, no scenery, no orbital lines between cells.

## Final export edit prompt

Production export correction of this exact sprite atlas: replace every checkerboard/background pixel with solid flat chroma-key green RGB(0,255,0), hex #00FF00. No checkerboard, no background texture, no gradients, no glow outside the sprite outlines. Preserve the exact six pixel art bodies and their layout and colors. The diagonal gap inside the orange broken planet, spaces between fragments and planetary rings must be the same solid #00FF00 too. Hard outlines for game-sprite color-key conversion. The background must be perfectly uniform bright green, every empty area exactly same green. Keep all sprites fully in frame. 1536x1024.
