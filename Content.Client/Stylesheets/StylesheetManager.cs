using Robust.Client.ResourceManagement;
using Robust.Client.UserInterface;
using Robust.Shared.IoC;

namespace Content.Client.Stylesheets
{
    public sealed class StylesheetManager : IStylesheetManager
    {
        [Dependency] private readonly IUserInterfaceManager _userInterfaceManager = default!;
        [Dependency] private readonly IResourceCache _resourceCache = default!;

        public Stylesheet SheetNano { get; private set; } = default!;
        public Stylesheet SheetSpace { get; private set; } = default!;

        public Color Accent { get; private set; } = StyleNano.AccentNeutral; // Eclipsion - faction accent

        public void Initialize()
        {
            SheetNano = new StyleNano(_resourceCache, Accent).Stylesheet;
            SheetSpace = new StyleSpace(_resourceCache).Stylesheet;

            _userInterfaceManager.Stylesheet = SheetNano;
        }

        // Eclipsion Start - faction accent
        public void SetAccent(Color accent)
        {
            if (accent == Accent)
                return;

            Accent = accent;
            SheetNano = new StyleNano(_resourceCache, accent).Stylesheet;
            _userInterfaceManager.Stylesheet = SheetNano;
        }
        // Eclipsion End
    }
}
