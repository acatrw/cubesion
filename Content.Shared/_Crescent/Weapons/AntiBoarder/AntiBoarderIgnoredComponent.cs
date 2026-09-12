namespace Content.Shared._Crescent.Weapons.AntiBoarder;

/// <summary>
/// Eclipsion - anti-boarder point defence never picks this entity as a target.
/// </summary>
/// <remarks>
/// Service bots (cleanbots, medibots and the like) have no outer clothing slot, so the sealed-suit rule
/// counts them as boarders, and their SimpleNeutral faction is nobody's friend. Without this marker a PD
/// turret would gun down the ship's own janitor. An emagged bot is a hostile machine again and loses the
/// exemption.
/// </remarks>
[RegisterComponent]
public sealed partial class AntiBoarderIgnoredComponent : Component
{
}
