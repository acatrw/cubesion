using System.Numerics;
using Robust.Client.UserInterface.Controls;

namespace Content.Client._Crescent.UserInterface;

/// <summary>
///     A texture that fills the width it is given and keeps its aspect ratio, up to
///     <see cref="MaxDisplayWidth"/>. A plain TextureRect asks for a fixed size, so a wide banner forces its
///     whole column to that width and squeezes everything next to it.
/// </summary>
public sealed class AspectTextureRect : TextureRect
{
    /// <summary>
    ///     Widest the texture is drawn, in UI units. Null lets it fill any width.
    /// </summary>
    public float? MaxDisplayWidth { get; set; }

    public AspectTextureRect()
    {
        Stretch = StretchMode.KeepAspectCentered;
        HorizontalExpand = true;
    }

    protected override Vector2 MeasureOverride(Vector2 availableSize)
    {
        if (Texture == null)
            return Vector2.Zero;

        var native = Texture.Size;
        if (native.X <= 0)
            return Vector2.Zero;

        var width = float.IsFinite(availableSize.X) ? availableSize.X : MaxDisplayWidth ?? native.X;
        if (MaxDisplayWidth is { } max)
            width = MathF.Min(width, max);

        // Width 0: take whatever the parent hands out rather than claiming it up front.
        return new Vector2(0, width * native.Y / native.X);
    }
}
