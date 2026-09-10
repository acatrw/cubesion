using System.Linq;
using System.Numerics;
using Content.Server._Crescent.RepairStation;
using Content.Server.Power.Components;
using Content.Shared._Crescent.RepairStation;
using Content.Shared.Damage;
using Content.Shared.FixedPoint;
using Robust.Shared.GameObjects;
using Robust.Shared.Map;

namespace Content.IntegrationTests.Tests._Crescent;

[TestFixture]
public sealed class DrydockReplacementTest
{
    [TestCase(false)]
    [TestCase(true)]
    public async Task ManualReplacementStaysProtectedAfterRemoval(bool installedDuringRepair)
    {
        await using var pair = await PoolManager.GetServerClient();
        var server = pair.Server;
        var map = await pair.CreateTestMap();
        var em = server.EntMan;
        var transforms = server.System<SharedTransformSystem>();

        await server.WaitAssertion(() =>
        {
            var console = em.SpawnEntity("ComputerShipRepairStation", map.GridCoords);
            var station = em.GetComponent<ShipRepairStationComponent>(console);
            station.ServiceOwnGrid = true;
            station.RepairUnregistered = true;
            station.Free = true;
            em.RemoveComponent<ApcPowerReceiverComponent>(console);
            var actor = em.SpawnEntity(null, map.GridCoords);
            var original = em.SpawnEntity("ComputerRadar", map.GridCoords);
            server.System<ShipDrydockSnapshotSystem>().Capture(map.Grid);
            var part = em.GetComponent<ShipDrydockSnapshotComponent>(map.Grid).Parts.Single(p => p.Original == original);
            em.DeleteEntity(original);

            if (installedDuringRepair)
            {
                em.EventBus.RaiseLocalEvent(console, new ShipRepairStartMessage { Actor = actor });
                Assert.That(station.Jobs.Any(j => j.Part == part), Is.True);
            }

            var replacement = em.SpawnEntity("ComputerRadar", map.GridCoords);
            if (installedDuringRepair)
            {
                station.NextTickTime = TimeSpan.Zero;
                station.PartsPerTick = station.Jobs.Count;
                server.System<ShipRepairStationSystem>().Update(0);
                Assert.That(station.Target, Is.Null);
            }

            ShipRepairStationUiState Survey()
            {
                em.EventBus.RaiseLocalEvent(console, new BoundUIOpenedEvent(ShipRepairStationUiKey.Key, console, actor));
                Assert.That(server.System<SharedUserInterfaceSystem>().TryGetUiState<ShipRepairStationUiState>(
                    console, ShipRepairStationUiKey.Key, out var state), Is.True);
                return state!;
            }

            if (!installedDuringRepair)
                Assert.That(Survey().MissingParts, Is.Zero);
            transforms.Unanchor(replacement);
            transforms.SetCoordinates(replacement, new EntityCoordinates(map.MapUid, new Vector2(10, 10)));
            Assert.That(Survey().MissingParts, Is.Zero,
                "A manually fitted replacement must not become duplicable by moving it off the hull.");
            em.DeleteEntity(replacement);
            Assert.That(Survey().MissingParts, Is.EqualTo(1),
                "Destroying the replacement must allow a legitimate repair.");
        });

        await pair.CleanReturnAsync();
    }

    [Test]
    public async Task LooseProtectedEquipmentIsNotChargedForUnperformedHealing()
    {
        await using var pair = await PoolManager.GetServerClient();
        var server = pair.Server;
        var map = await pair.CreateTestMap();
        var em = server.EntMan;

        await server.WaitAssertion(() =>
        {
            var console = em.SpawnEntity("ComputerShipRepairStation", map.GridCoords);
            var station = em.GetComponent<ShipRepairStationComponent>(console);
            station.ServiceOwnGrid = true;
            station.RepairUnregistered = true;
            var radar = em.SpawnEntity("ComputerRadar", map.GridCoords);
            server.System<ShipDrydockSnapshotSystem>().Capture(map.Grid);
            server.System<DamageableSystem>().SetAllDamage(radar, em.GetComponent<DamageableComponent>(radar), FixedPoint2.New(1));
            server.System<SharedTransformSystem>().Unanchor(radar);
            em.EventBus.RaiseLocalEvent(console, new BoundUIOpenedEvent(ShipRepairStationUiKey.Key, console, radar));
            Assert.That(server.System<SharedUserInterfaceSystem>().TryGetUiState<ShipRepairStationUiState>(
                console, ShipRepairStationUiKey.Key, out var state), Is.True);
            Assert.That(state!.DamagedParts, Is.Zero,
                "Loose equipment cannot be healed by the slip and must not appear on its bill.");
            Assert.That(state.MissingParts, Is.Zero);
        });

        await pair.CleanReturnAsync();
    }
}
