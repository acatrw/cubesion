namespace Content.Shared._Crescent.Factions;

/// <summary>
/// Turns a gameplay faction ID into the abbreviation players are supposed to read. Prototype IDs are frozen for
/// save and map compatibility, so the Taypani Free Companies Federation still answers to the legacy
/// <c>TFSC</c> ID everywhere in data — announcements, examines and radar names have to translate it on the way out
/// or the retired name leaks back into the round.
/// </summary>
public static class FactionDisplay
{
    /// <summary>
    /// Legacy faction IDs whose canonical abbreviation no longer matches. Every other faction's ID already is its
    /// abbreviation, so it needs no entry here.
    /// </summary>
    private static readonly Dictionary<string, string> Abbreviations = new(StringComparer.OrdinalIgnoreCase)
    {
        ["TFSC"] = "TFCF",
    };

    /// <summary>
    /// The player-visible abbreviation for <paramref name="factionId"/>. Unknown and empty IDs come back unchanged,
    /// so this is safe to wrap around anything a mapper or admin may have typed.
    /// </summary>
    public static string Abbreviation(string? factionId)
    {
        if (string.IsNullOrWhiteSpace(factionId))
            return factionId ?? string.Empty;

        return Abbreviations.TryGetValue(factionId, out var display) ? display : factionId;
    }

    /// <summary>
    /// The prototype ID behind an abbreviation players and admins actually type. Anything that is not a renamed
    /// abbreviation comes back unchanged, so callers can hand this straight to their own ID validation.
    /// </summary>
    public static string ResolveId(string? abbreviation)
    {
        if (string.IsNullOrWhiteSpace(abbreviation))
            return abbreviation ?? string.Empty;

        foreach (var (id, display) in Abbreviations)
        {
            if (string.Equals(abbreviation, display, StringComparison.OrdinalIgnoreCase))
                return id;
        }

        return abbreviation;
    }

    /// <summary>
    /// Every spelling a faction may appear under in text written before or after a rename — the ID itself plus its
    /// current abbreviation. Used to strip an owner prefix off a name without caring which era wrote it.
    /// </summary>
    public static IEnumerable<string> Spellings(string factionId)
    {
        yield return factionId;

        var display = Abbreviation(factionId);
        if (!string.Equals(display, factionId, StringComparison.OrdinalIgnoreCase))
            yield return display;
    }
}
