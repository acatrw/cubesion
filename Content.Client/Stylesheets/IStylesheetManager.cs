using Robust.Client.UserInterface;

namespace Content.Client.Stylesheets
{
    public interface IStylesheetManager
    {
        Stylesheet SheetNano { get; }
        Stylesheet SheetSpace { get; }

        // Eclipsion Start - faction accent
        /// <summary>
        ///     Accent colour <see cref="SheetNano"/> was last built with.
        /// </summary>
        Color Accent { get; }

        /// <summary>
        ///     Rebuilds <see cref="SheetNano"/> around a new accent and swaps it in. No-op if unchanged.
        /// </summary>
        void SetAccent(Color accent);
        // Eclipsion End

        void Initialize();
    }
}
