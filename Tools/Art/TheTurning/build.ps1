param([string] $RepositoryRoot = (Resolve-Path "$PSScriptRoot/../../.."))

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$target = Join-Path $RepositoryRoot 'Resources/Textures/_Crescent/Parallaxes/TheTurning'
New-Item -ItemType Directory -Force $target | Out-Null

# Pack the generated RGBA endpoints. Nearest-neighbor sampling preserves pixel edges.
# The shattered source has a larger silhouette; normalize its scale before packing.
$atlas = [System.Drawing.Bitmap]::new(1024, 512)
$graphics = [System.Drawing.Graphics]::FromImage($atlas)
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
try {
    $sources = @('intact-source.png', 'shattered-source.png')
    $sizes = @(512, 456)
    for ($i = 0; $i -lt 2; $i++) {
        $source = [System.Drawing.Bitmap]::new((Join-Path $PSScriptRoot $sources[$i]))
        try {
            if ($source.GetPixel(0, 0).A -ne 0) { throw "Source must have real alpha: $($sources[$i])" }
            $size = $sizes[$i]
            $margin = (512 - $size) / 2
            $rect = [System.Drawing.Rectangle]::new(($i * 512 + $margin), $margin, $size, $size)
            $graphics.DrawImage($source, $rect, 0, 0, $source.Width, $source.Height, [System.Drawing.GraphicsUnit]::Pixel)
        } finally { $source.Dispose() }
    }
    $atlas.Save((Join-Path $target 'turning.png'), [System.Drawing.Imaging.ImageFormat]::Png)
    for ($i = 0; $i -lt 2; $i++) {
        $crop = $atlas.Clone([System.Drawing.Rectangle]::new(($i * 512), 0, 512, 512), [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        try {
            $name = @('intact.png', 'shattered.png')[$i]
            $crop.Save((Join-Path $target $name), [System.Drawing.Imaging.ImageFormat]::Png)
        } finally { $crop.Dispose() }
    }
} finally { $graphics.Dispose(); $atlas.Dispose() }
$shader = [IO.File]::ReadAllText((Join-Path $RepositoryRoot 'Resources/Textures/Shaders/the_turning.swsl'))
$shaderJson = ConvertTo-Json -InputObject $shader -Compress
$imageData = [Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $target 'turning.png')))
$template = Get-Content -Raw -Encoding UTF8 (Join-Path $PSScriptRoot 'preview.template.html')
$preview = $template.Replace('__SHADER_JSON__', $shaderJson).Replace('__ATLAS_BASE64__', $imageData)
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'preview.html'), $preview, [Text.UTF8Encoding]::new($false))
Write-Output "Built The Turning atlas and endpoints in $target"
