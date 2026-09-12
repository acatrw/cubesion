#nullable enable
using System.Collections.Generic;
using System.Threading.Tasks;
using Content.Shared.Construction.Components;
using Robust.Shared.GameObjects;
using Robust.Shared.Prototypes;

namespace Content.IntegrationTests.Tests._Crescent;

/// <summary>
/// A flatpack whose target is abstract passes the YAML linter (the id has a mapping) but can never be spawned:
/// unpacking throws server-side while the client plays the unpack sound, so the player sees nothing happen.
/// </summary>
[TestFixture]
public sealed class FlatpackTargetTest
{
    [Test]
    public async Task FlatpackTargetsAreSpawnable()
    {
        await using var pair = await PoolManager.GetServerClient();
        var server = pair.Server;

        var protoManager = server.ResolveDependency<IPrototypeManager>();
        var componentFactory = server.ResolveDependency<IComponentFactory>();
        var errors = new List<string>();

        await server.WaitPost(() =>
        {
            foreach (var proto in protoManager.EnumeratePrototypes<EntityPrototype>())
            {
                if (!proto.TryGetComponent<FlatpackComponent>(out var flatpack, componentFactory) ||
                    flatpack!.Entity is not { } target)
                {
                    continue;
                }

                // Abstract prototypes are never instantiated, so TryIndex fails for them just like for a missing id.
                if (!protoManager.TryIndex(target, out _))
                    errors.Add($"Flatpack '{proto.ID}' unpacks into '{target}', which is abstract or does not exist.");
            }
        });

        await pair.CleanReturnAsync();

        Assert.That(errors, Is.Empty, string.Join("\n", errors));
    }
}
