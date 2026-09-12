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

`celestials-keyed.png` is Taleryn's source atlas for Hullrot:Eclipsion, drawn against a
green color key. The build converts that key to real alpha and resizes the sprites with
nearest-neighbor sampling. `projector-base.png` preserves the existing pedestal, whose
MonkeyStation source and CC-BY-SA-3.0 license are recorded in the RSI metadata.
The other hologram states are not rebuilt by this script.
