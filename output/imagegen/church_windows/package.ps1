Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System.Drawing;
public static class ChurchSpriteBounds {
    public static Rectangle Find(Bitmap image) {
        int left=image.Width, top=image.Height, right=-1, bottom=-1;
        for(int y=0;y<image.Height;y++) for(int x=0;x<image.Width;x++) {
            if(image.GetPixel(x,y).A < 128) continue;
            left=System.Math.Min(left,x); top=System.Math.Min(top,y);
            right=System.Math.Max(right,x); bottom=System.Math.Max(bottom,y);
        }
        return Rectangle.FromLTRB(left,top,right+1,bottom+1);
    }
}
'@
$repoPath = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$generatedPath = 'C:/Users/emred/.codex/generated_images/01a0941a-c68f-79e0-93c9-7deb7425c820'
$variants = @(
    @{ Name='sword'; File='exec-f3e8555a-d31c-48df-9eb3-6630e3c6aae8.png' },
    @{ Name='torch'; File='exec-9486aeed-a71c-4ba8-bf18-c5581c8eaef8.png' },
    @{ Name='wings'; File='exec-a760b9ba-4374-4ddc-afea-81fea05adad7.png' }
)
$preview = New-Object System.Drawing.Bitmap 640, 384
$previewGraphics = [System.Drawing.Graphics]::FromImage($preview)
$previewGraphics.Clear([System.Drawing.Color]::FromArgb(36,39,45))
$previewGraphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$previewGraphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
$reference = [System.Drawing.Bitmap]::FromFile((Join-Path $repoPath 'Resources/Textures/_Crescent/Structures/churchglass.rsi/icon.png'))
$previewGraphics.DrawImage($reference, [System.Drawing.Rectangle]::new(16,48,128,280))
$reference.Dispose()
$font = New-Object System.Drawing.Font 'Consolas', 11
$previewGraphics.DrawString('Original', $font, [System.Drawing.Brushes]::White, 16, 16)
$index=1
foreach ($variant in $variants) {
    $sourcePath = Join-Path $generatedPath $variant.File
    Copy-Item -LiteralPath $sourcePath -Destination (Join-Path $PSScriptRoot ($variant.Name + '-source.png'))
    $source = [System.Drawing.Bitmap]::FromFile($sourcePath)
    $bounds = [ChurchSpriteBounds]::Find($source)
    $sprite = New-Object System.Drawing.Bitmap 32, 70
    $graphics = [System.Drawing.Graphics]::FromImage($sprite)
    $graphics.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
    $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
    $graphics.DrawImage($source, [System.Drawing.Rectangle]::new(0,0,32,70), $bounds, [System.Drawing.GraphicsUnit]::Pixel)
    $assetPath = Join-Path $repoPath ('Resources/Textures/_Crescent/Structures/churchglass_' + $variant.Name + '.rsi')
    New-Item -ItemType Directory -Path $assetPath -Force | Out-Null
    $sprite.Save((Join-Path $assetPath 'icon.png'), [System.Drawing.Imaging.ImageFormat]::Png)
    $metadata = [ordered]@{
        version=1
        license=''
        copyright='Generated with OpenAI image_gen; churchglass.rsi used as a style reference. Cropped and resized to 32x70 with nearest-neighbor sampling.'
        size=@{x=32;y=70}
        states=@(@{name='icon'})
    }
    [System.IO.File]::WriteAllText((Join-Path $assetPath 'meta.json'), ($metadata | ConvertTo-Json -Depth 4) + "`n")
    $previewGraphics.DrawImage($sprite, [System.Drawing.Rectangle]::new(16+160*$index,48,128,280))
    $previewGraphics.DrawString($variant.Name, $font, [System.Drawing.Brushes]::White, (16+160*$index), 16)
    Write-Output ($assetPath + ': 32x70, state icon')
    $index++
    $graphics.Dispose(); $sprite.Dispose(); $source.Dispose()
}
$preview.Save((Join-Path $PSScriptRoot 'preview.png'), [System.Drawing.Imaging.ImageFormat]::Png)
$font.Dispose(); $previewGraphics.Dispose(); $preview.Dispose()
