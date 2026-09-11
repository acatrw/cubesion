using Content.Shared.Movement.Components;
using Content.Shared.Movement.Systems;
using Content.Shared.Temperature.Components;
using Robust.Shared.Timing;

namespace Content.Shared.Temperature.Systems;

/// <summary>
/// This handles predicting temperature based speedup.
/// </summary>
public sealed class SharedTemperatureSystem : EntitySystem
{
    [Dependency] private readonly IGameTiming _timing = default!;
    [Dependency] private readonly MovementSpeedModifierSystem _movementSpeedModifier = default!;

    /// <summary>
    /// Band-aid for unpredicted atmos. Delays the application for a short period so that laggy clients can get the replicated temperature.
    /// </summary>
    private static readonly TimeSpan SlowdownApplicationDelay = TimeSpan.FromSeconds(1f);

    public override void Initialize()
    {
        base.Initialize();

        SubscribeLocalEvent<TemperatureSpeedComponent, OnTemperatureChangeEvent>(OnTemperatureChanged);
        SubscribeLocalEvent<TemperatureSpeedComponent, RefreshMovementSpeedModifiersEvent>(OnRefreshMovementSpeedModifiers);
    }

    private void OnTemperatureChanged(Entity<TemperatureSpeedComponent> ent, ref OnTemperatureChangeEvent args)
    {
        // Derived from the current temperature rather than from which threshold was just crossed: warming up
        // across a threshold used to apply THAT threshold's slowdown (a lizard going 294K -> 296K kept 0.6 until
        // it passed 301K), and a jump over several thresholds took whichever came first in the dictionary.
        var modifier = GetSpeedModifier(ent.Comp, args.CurrentTemperature);
        if (modifier == ent.Comp.CurrentSpeedModifier)
            return;

        ent.Comp.NextSlowdownUpdate = _timing.CurTime + SlowdownApplicationDelay;
        ent.Comp.CurrentSpeedModifier = modifier;
        Dirty(ent);
    }

    /// <summary>
    /// The modifier of the coldest threshold the temperature is below, or null when it is above all of them.
    /// </summary>
    private static float? GetSpeedModifier(TemperatureSpeedComponent comp, float temperature)
    {
        float? modifier = null;
        var coldest = float.MaxValue;

        foreach (var (threshold, value) in comp.Thresholds)
        {
            if (temperature >= threshold || threshold >= coldest)
                continue;

            coldest = threshold;
            modifier = value;
        }

        return modifier;
    }

    private void OnRefreshMovementSpeedModifiers(Entity<TemperatureSpeedComponent> ent, ref RefreshMovementSpeedModifiersEvent args)
    {
        // Don't update speed and mispredict while we're compensating for lag.
        if (ent.Comp.NextSlowdownUpdate != null || ent.Comp.CurrentSpeedModifier == null)
            return;

        args.ModifySpeed(ent.Comp.CurrentSpeedModifier.Value, ent.Comp.CurrentSpeedModifier.Value);
    }

    public override void Update(float frameTime)
    {
        base.Update(frameTime);

        var query = EntityQueryEnumerator<TemperatureSpeedComponent, MovementSpeedModifierComponent>();
        while (query.MoveNext(out var uid, out var temp, out var movement))
        {
            if (temp.NextSlowdownUpdate == null)
                continue;

            if (_timing.CurTime < temp.NextSlowdownUpdate)
                continue;

            temp.NextSlowdownUpdate = null;
            _movementSpeedModifier.RefreshMovementSpeedModifiers(uid, movement);
            Dirty(uid, temp);
        }
    }
}
