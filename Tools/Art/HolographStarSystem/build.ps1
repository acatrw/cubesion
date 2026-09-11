param(
    [string] $RepositoryRoot = (Resolve-Path "$PSScriptRoot/../../.."),
    [string] $PreviewDirectory = "$PSScriptRoot/preview"
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

# Generated artwork is color-keyed, resized, and packed into an RSI animation.
# Keep the source artwork here so rebuilding never requires an image service.
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.IO;

public static class AlienOrrery
{
    const int Count = 96;
    const double Tau = Math.PI * 2;

    static Color C(int a, int r, int g, int b) { return Color.FromArgb(a,r,g,b); }

    static Bitmap Sprite(Bitmap source, Rectangle crop, int width, int height)
    {
        using (var cut = source.Clone(crop, PixelFormat.Format32bppArgb))
        {
            // Decode the generated atlas's green export key into actual alpha.
            for (int y = 0; y < cut.Height; y++)
            for (int x = 0; x < cut.Width; x++)
            {
                var p = cut.GetPixel(x,y);
                if (p.G > 100 && p.G > p.R * 1.5 && p.G > p.B * 1.5)
                    cut.SetPixel(x,y,Color.Transparent);
            }
            var result = new Bitmap(width,height,PixelFormat.Format32bppArgb);
            using (var g = Graphics.FromImage(result))
            {
                g.InterpolationMode = InterpolationMode.NearestNeighbor;
                g.PixelOffsetMode = PixelOffsetMode.Half;
                g.DrawImage(cut,new Rectangle(0,0,width,height),0,0,cut.Width,cut.Height,GraphicsUnit.Pixel);
            }
            return result;
        }
    }

    static PointF Orbit(double angle, double radius, double height, double tilt)
    {
        double x = Math.Cos(angle)*radius, y = Math.Sin(angle)*height;
        return new PointF((float)(31.5+x*Math.Cos(tilt)-y*Math.Sin(tilt)),
                          (float)(19+y*Math.Cos(tilt)+x*Math.Sin(tilt)));
    }

    static void Dot(Graphics g, Color color, float x, float y)
    {
        using (var brush = new SolidBrush(color))
            g.FillRectangle(brush,(int)Math.Round(x),(int)Math.Round(y),1,1);
    }

    static void Body(Graphics g, Bitmap sprite, PointF p)
    {
        g.DrawImageUnscaled(sprite,(int)Math.Round(p.X-sprite.Width/2.0),
                                  (int)Math.Round(p.Y-sprite.Height/2.0));
    }

    public static void Build(string sourcePath, string basePath, string target, string preview)
    {
        Directory.CreateDirectory(preview);
        using (var source = new Bitmap(sourcePath))
        using (var pedestal = new Bitmap(basePath))
        using (var sun = Sprite(source,new Rectangle(20,40,490,530),17,18))
        using (var gas = Sprite(source,new Rectangle(519,158,510,340),16,11))
        using (var broken = Sprite(source,new Rectangle(1105,148,400,347),12,11))
        using (var fissure = Sprite(source,new Rectangle(108,620,315,318),7,7))
        using (var moon = Sprite(source,new Rectangle(661,680,208,213),4,4))
        using (var crystal = Sprite(source,new Rectangle(1110,613,340,343),7,7))
        using (var sheet = new Bitmap(64*12,64*8,PixelFormat.Format32bppArgb))
        using (var sheetG = Graphics.FromImage(sheet))
        using (var contact = new Bitmap(64*4,64*2,PixelFormat.Format32bppArgb))
        using (var contactG = Graphics.FromImage(contact))
        {
            var sprites = new [] {moon,fissure,broken,gas,crystal};
            double[] radii = {10,14,19,24,27};
            double[] heights = {6,8,10,12,15};
            double[] phases = {0.7,3.9,2.65,0.1,4.9};
            int[] turns = {4,3,2,1,-1};
            double[] tilts = {-0.14,-0.14,-0.14,-0.14,0.05};
            var random = new Random(1709);
            var stars = new Point[22];
            for (int s=0;s<stars.Length;s++) stars[s]=new Point(random.Next(3,61),random.Next(2,35));

            for (int f=0;f<Count;f++)
            using (var frame = new Bitmap(64,64,PixelFormat.Format32bppArgb))
            using (var g = Graphics.FromImage(frame))
            {
                g.SmoothingMode = SmoothingMode.None;
                double t=Tau*f/Count;
                g.DrawImageUnscaled(pedestal,0,37);

                // A faint projected volume and distant stars suggest alien space.
                using (var beam = new SolidBrush(C(12,130,72,238)))
                    g.FillPolygon(beam,new [] {new Point(26,40),new Point(5,15),new Point(59,15),new Point(38,40)});
                using (var pen = new Pen(C(32,158,88,248)))
                {
                    g.DrawLine(pen,24,39,7,19);
                    g.DrawLine(pen,40,39,57,19);
                }
                for (int s=0;s<stars.Length;s++)
                {
                    int alpha=(int)(45+40*(0.5+0.5*Math.Sin(t*2+s*2.4)));
                    Dot(g,C(alpha,160+s%3*25,135+s%2*45,245),stars[s].X,stars[s].Y);
                }

                // Sparse orbit guides leave the worlds readable at native scale.
                foreach (int orbit in new [] {1,3,4})
                for (int step=0;step<180;step++)
                {
                    if (step%13>8) continue;
                    double a=Tau*step/180;
                    var p=Orbit(a,radii[orbit],heights[orbit],tilts[orbit]);
                    Dot(g,C(Math.Sin(a)>0?58:30,148,106,215),p.X,p.Y);
                }

                // Debris travels with a periodic orbit, including across the loop seam.
                for (int rock=0;rock<24;rock++)
                {
                    double a=Tau*rock/24+t;
                    var p=Orbit(a,21+(rock%3-1)*0.7,11,-0.14);
                    Dot(g,C(90+rock%3*25,170,135,200),p.X,p.Y);
                }

                var positions = new PointF[5];
                for (int i=0;i<5;i++) positions[i]=Orbit(t*turns[i]+phases[i],radii[i],heights[i],tilts[i]);
                for (int i=4;i>=0;i--) if (positions[i].Y<19) Body(g,sprites[i],positions[i]);

                // Pulse only the halo: the violet primary stays anchored at the center.
                using (var halo = new SolidBrush(C((int)(15+5*Math.Sin(t*3)),163,43,255)))
                {
                    g.FillEllipse(halo,21,9,21,21);
                    g.FillEllipse(halo,23,11,17,17);
                }
                Body(g,sun,new PointF(31.5f,19));
                for (int i=0;i<5;i++) if (positions[i].Y>=19) Body(g,sprites[i],positions[i]);

                sheetG.DrawImageUnscaled(frame,(f%12)*64,(f/12)*64);
                if (f%12==0) contactG.DrawImageUnscaled(frame,((f/12)%4)*64,((f/12)/4)*64);
                if (f==0) frame.Save(Path.Combine(preview,"frame.png"),ImageFormat.Png);
            }
            sheet.Save(target,ImageFormat.Png);
            sheet.Save(Path.Combine(preview,"animation.png"),ImageFormat.Png);
            using (var enlarged = new Bitmap(1024,512))
            using (var g=Graphics.FromImage(enlarged))
            {
                g.Clear(Color.FromArgb(13,11,23));
                g.InterpolationMode=InterpolationMode.NearestNeighbor;
                g.PixelOffsetMode=PixelOffsetMode.Half;
                g.DrawImage(contact,new Rectangle(0,0,1024,512),0,0,256,128,GraphicsUnit.Pixel);
                enlarged.Save(Path.Combine(preview,"contact.png"),ImageFormat.Png);
            }
        }
    }
}
'@

$rsi = Join-Path $RepositoryRoot 'Resources/Textures/DeltaV/Structures/Decoration/shuttle_manipulator.rsi'
[AlienOrrery]::Build("$PSScriptRoot/celestials-keyed.png", "$PSScriptRoot/projector-base.png", "$rsi/holograph_star_system.png", $PreviewDirectory)
Write-Output "Built 96 frames (64 x 64), 12 columns, 9.6-second loop."
