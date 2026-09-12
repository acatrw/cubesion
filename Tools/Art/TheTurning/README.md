# The Turning — Taypan Core

The single white planet shifts between its intact past and purple shattered future.
The temporal coloration and horizontal tearing reference the existing
`holograph_planet` animation, without its projector.

## Integration

`gliessbiome` (Taypan Core, the Gliess Santo approach at sector origin) uses
`TaypanCoreTurning`. The planet is a non-tiled parallax layer in both
high and low quality modes. Other biomes retain their existing backgrounds.

The scene uses the classic `/Textures/Parallaxes/layer1.png` space background,
with no Aspid green background or nebula. The planet is drawn next, followed by
the transparent standard SS14 star layers (four in HQ, two in LQ).
Its atlas scale is `1, 2`, producing a 1024px square, 20% smaller than the previous
1280px version. `slowness: 0.995` and `worldHomePosition: "0, 0"` give it distant
parallax relative to the sector origin: 100m of player travel shifts its screen
position by 16 texture pixels at native scale. This keeps it visible across the
Gliess approach without locking it to the camera. A value of zero confines the
32m-wide layer to the origin, where station floors can hide it. Stars retain
their own parallax movement in front of the planet.

Runtime assets are in `Resources/Textures/_Crescent/Parallaxes/TheTurning/`:

- `intact.png`: 512 × 512 transparent white endpoint.
- `shattered.png`: 512 × 512 transparent purple endpoint.
- `turning.png`: 1024 × 512 atlas, intact left and shattered right.

The original RGBA source images are preserved here as `intact-source.png`
and `shattered-source.png`. The build normalizes the framing and packs the atlas
using nearest-neighbor sampling. Nothing outside the repository is
required at runtime or to rebuild.

## Animation

The shader `Resources/Textures/Shaders/the_turning.swsl` runs a 24-second loop:

| Seconds | State |
| --- | --- |
| 0–7 | Stable white planet |
| 7–9 | Planet turns violet |
| 9–11 | Temporal tearing and transition into the shattered state |
| 11–17 | Purple halves and suspended debris |
| 17–19 | Purple temporal images merge back into a whole planet |
| 19–21 | Whole planet fades from violet to white |
| 21–24 | Stable white planet; seamless return to the start |

Both images are sampled in one shader with premultiplied interpolation and
straight-alpha output. This avoids background rectangles and dark alpha fringes.
Only the planet's physical states change; the surrounding space stays stable.
Disabling parallax entirely also disables this background.

## Preview and rebuild

Open [preview.html](preview.html) directly in a WebGL-capable browser. It embeds
the runtime atlas and the actual shader; no local server or image service is
needed. Pause or scrub the timeline. Reduced-motion preferences start paused.
This is an isolated animation preview; the in-game scale, space background,
and foreground star ordering are configured in the parallax prototype.

Rebuild from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Tools/Art/TheTurning/build.ps1
```

Requires Windows PowerShell and System.Drawing. Edit `preview.template.html`
rather than the generated preview. The build embeds the current shader source.

## Validation

- Parsed successfully with the repository's built Robust ShaderParser.
- Compiled and rendered in Edge WebGL using the actual shader source.
- Preview checked distinct frames at 0, 8, 12, 18, and 20 seconds, real transparent
  corners, nonempty subjects, and identical output at 0 and 24 seconds.
- Inspected intact, shattered, and reassembly screenshots.
- Validated resource paths, HQ/LQ layers, no tiling, and the Taypan Core binding.
- No live in-game visual test was performed. Engine color management can slightly
  change the displayed brightness relative to the browser preview.
