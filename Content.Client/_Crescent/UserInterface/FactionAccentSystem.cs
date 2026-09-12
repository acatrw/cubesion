using Content.Client.Stylesheets;
using Content.Shared._Crescent.HullrotFaction;
using Content.Shared.CCVar;
using Content.Shared.Roles;
using Robust.Client.Player;
using Robust.Shared.Configuration;
using Robust.Shared.Prototypes;

namespace Content.Client._Crescent.UserInterface;

/// <summary>
///     Keeps the UI accent in step with the local player's faction. The accent lives in the Nano
///     stylesheet, so a change rebuilds and swaps that sheet; it only happens when the faction actually
///     changes (spawn, ghosting, recruitment), never per frame.
/// </summary>
/// <remarks>
///     Polls rather than listening for attach/state events: the check is one TryComp a frame, and it
///     catches every way the controlled mob or its <see cref="HullrotFactionComponent"/> can change
///     without claiming any component/event subscription pair.
/// </remarks>
public sealed class FactionAccentSystem : EntitySystem
{
    [Dependency] private readonly IConfigurationManager _cfg = default!;
    [Dependency] private readonly IPlayerManager _player = default!;
    [Dependency] private readonly IPrototypeManager _proto = default!;
    [Dependency] private readonly IStylesheetManager _stylesheets = default!;

    private bool _enabled;

    /// <summary>
    ///     Faction the current accent was picked for; null for none.
    /// </summary>
    private string? _faction;

    public override void Initialize()
    {
        base.Initialize();
        Subs.CVar(_cfg, CCVars.HudFactionAccent, OnEnabledChanged, true);
    }

    public override void Shutdown()
    {
        base.Shutdown();

        // The stylesheet outlives the connection; don't carry a faction colour back to the main menu.
        _faction = null;
        _stylesheets.SetAccent(StyleNano.AccentNeutral);
    }

    private void OnEnabledChanged(bool enabled)
    {
        _enabled = enabled;
        _faction = CurrentFaction();
        ApplyAccent();
    }

    public override void FrameUpdate(float frameTime)
    {
        base.FrameUpdate(frameTime);

        var faction = CurrentFaction();
        if (faction == _faction)
            return;

        _faction = faction;
        ApplyAccent();
    }

    private string? CurrentFaction()
    {
        if (!_enabled
            || _player.LocalEntity is not { } local
            || !TryComp<HullrotFactionComponent>(local, out var comp)
            || string.IsNullOrEmpty(comp.Faction))
        {
            return null;
        }

        return comp.Faction;
    }

    private void ApplyAccent()
    {
        var accent = StyleNano.AccentNeutral;
        if (_faction != null
            && _proto.TryIndex<FactionPrototype>(_faction, out var faction)
            && faction.UiAccent is { } factionAccent)
        {
            accent = factionAccent;
        }

        _stylesheets.SetAccent(accent);
    }
}
