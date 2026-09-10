using Content.Server.Explosion.EntitySystems;
using Robust.Shared.Audio;

namespace Content.Server.Explosion.Components;

/// <summary>
/// Will play sound from the attached entity upon a <see cref="TriggerEvent"/>.
/// </summary>
[RegisterComponent]
public sealed partial class SoundOnTriggerComponent : Component
{
    [DataField("removeOnTrigger")]
    public bool RemoveOnTrigger = true;

    // Eclipsion - the file lives under Grenades/Supermatter/; the flat path resolved to nothing, so any
    // SoundOnTrigger that did not override this default played silence and logged a missing-resource error.
    [DataField("sound")]
    public SoundSpecifier? Sound = new SoundPathSpecifier("/Audio/Effects/Grenades/Supermatter/supermatter_start.ogg");
}
