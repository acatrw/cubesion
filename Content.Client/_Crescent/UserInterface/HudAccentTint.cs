using Robust.Client.UserInterface;
using Robust.Client.UserInterface.Themes;

namespace Content.Client._Crescent.UserInterface;

/// <summary>
///     The Eclipsion HUD theme draws a few pieces (the active hand frame, the item status highlight) in
///     white and lets the stylesheet tint them with the faction accent. Only themes that opt in through
///     the <see cref="ThemeKey"/> colour entry get the style class, so stock themes keep their baked-in
///     gold and teal instead of having them multiplied by the accent.
/// </summary>
public static class HudAccentTint
{
    public const string StyleClass = "HudAccentTint";

    /// <summary>
    ///     Marker colour entry on a uiTheme. Its value is unused, only its presence counts.
    /// </summary>
    public const string ThemeKey = "_accentTint";

    public static void Apply(Control control, UITheme theme)
    {
        // Colors directly, not ResolveColor: that falls back to the default theme, which is Eclipsion,
        // so every theme would appear to opt in.
        var wants = theme.Colors?.ContainsKey(ThemeKey) == true;

        if (wants && !control.HasStyleClass(StyleClass))
            control.AddStyleClass(StyleClass);
        else if (!wants && control.HasStyleClass(StyleClass))
            control.RemoveStyleClass(StyleClass);
    }
}
