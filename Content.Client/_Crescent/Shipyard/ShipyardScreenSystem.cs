using Content.Shared.Shipyard.Components;
using Robust.Client.GameObjects;
using Robust.Shared.Utility;

namespace Content.Client._Crescent.Shipyard;

/// <summary>
///   Swaps a faction shipyard console's screen layer onto that faction's recoloured screen RSI. Only the RSI
///   changes, so the layer keeps its state and the power visualizer keeps toggling it as before.
/// </summary>
public sealed class ShipyardScreenSystem : EntitySystem
{
    private const string ScreenLayer = "computerLayerScreen";

    [Dependency] private readonly SpriteSystem _sprite = default!;

    public override void Initialize()
    {
        base.Initialize();
        SubscribeLocalEvent<ShipyardScreenComponent, ComponentStartup>(OnStartup);
    }

    private void OnStartup(Entity<ShipyardScreenComponent> ent, ref ComponentStartup args)
    {
        if (!TryComp<SpriteComponent>(ent, out var sprite))
            return;

        var rsi = new ResPath($"_Crescent/Structures/Machines/ShipyardScreens/{ent.Comp.Faction.Id.ToLowerInvariant()}.rsi");
        _sprite.LayerSetRsi((ent, sprite), ScreenLayer, rsi);
    }
}
