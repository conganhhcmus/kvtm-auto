using KvtmAuto.Core.Models;

namespace KvtmAuto.Automation.Engine;

public enum SellOption { Trees = 0, Goods = 1, Others = 2, Mineral = 3, Events = 4 }

/// <summary>Port of core.py — all shared game automation methods.</summary>
public abstract class ScriptBase(AdbController adb, ImageMatcher images, DeviceManager deviceManager)
    : IScript
{
    public abstract string Id { get; }
    public abstract string Name { get; }
    public abstract Task RunAsync(string deviceId, GameOptions options, CancellationToken ct);

    protected const int LoopNum = 1000;
    private const string GamePackage = "vn.kvtm.js";

    // Screen layout constants (pixels on 2160x1858 screen)
    private static readonly (double x, double y)[] FullTreePoint =
    [
        (850, 1730), (1015, 1730), (1180, 1730), (1345, 1730), (1510, 1730), (1675, 1730),
        (1675, 1245), (1510, 1245), (1345, 1245), (1180, 1245), (1015, 1245), (850, 1245),
        (850, 770),  (1015, 770),  (1180, 770),  (1345, 770),  (1510, 770),  (1675, 770),
        (1675, 290), (1510, 290),  (1345, 290),  (1180, 290),  (1015, 290),  (850, 290),
    ];

    private static readonly (double x, double y)[] FullItemPoint =
    [
        (1000, 1000), (1140, 1000), (1280, 1000), (1140, 1150), (1280, 1150),
    ];

    private static readonly (double x, double y)[] SellOptions =
    [
        (975, 650), (975, 800), (975, 950), (975, 1100), (975, 1250),
    ];

    private static readonly (double x, double y)[] SellSlotPoint =
    [
        (630, 790), (920, 790),  (1210, 790),  (1500, 790),
        (630, 1210),(920, 1210), (1210, 1210), (1500, 1210),
    ];

    private static readonly (double x, double y)[] FriendHousePoint =
    [
        (590, 1470), (860, 1470), (1130, 1470), (1400, 1470), (1670, 1470),
    ];

    // -------------------------------------------------------------------
    // Logging
    // -------------------------------------------------------------------

    protected void Log(string deviceId, string message) =>
        deviceManager.AppendLog(deviceId, message);

    // -------------------------------------------------------------------
    // Core.py methods
    // -------------------------------------------------------------------

    protected async Task CloseAllPopupsAsync(string id, CancellationToken ct, int num = 3)
    {
        for (int i = 0; i < num; i++)
        {
            await adb.KeyEventAsync(id, 4); // BACK
            await SleepAsync(0.25, ct);
        }
        await adb.TapAsync(id, 1240, 1150);
        await SleepAsync(0.5, ct);
    }

    protected async Task OpenGameAsync(string id, CancellationToken ct)
    {
        Log(id, "Opening game...");
        await adb.KeyEventAsync(id, 3); // HOME
        await adb.StopAppAsync(id, GamePackage);
        await adb.StartAppAsync(id, GamePackage);
        await SleepAsync(10, ct);
        await adb.TapAsync(id, 1600, 2020);
        await SleepAsync(1, ct);
        await ClickImageAsync(id, "game", ct);
        await SleepAsync(10, ct);
        await CloseAllPopupsAsync(id, ct, 15);
    }

    protected async Task OpenChestAsync(string id, CancellationToken ct)
    {
        var pos = await FindImageAsync(id, "ruong-bau", ct);
        if (pos is null) { await SleepAsync(0.5, ct); return; }

        Log(id, "Opening chests...");
        await adb.TapAsync(id, 810, 1040);
        await SleepAsync(0.5, ct);
        await adb.TapAsync(id, 810, 1040);
        await adb.TapAsync(id, 570, 1240);
        await adb.TapAsync(id, 570, 1240);
        await SleepAsync(0.5, ct);
        await adb.TapAsync(id, 1075, 1050);
        await adb.TapAsync(id, 1075, 1050);
        for (int i = 0; i < 10; i++)
        {
            await adb.TapAsync(id, 1080, 1050);
            await SleepAsync(0.25, ct);
        }
        await CloseAllPopupsAsync(id, ct);
        await SleepAsync(0.5, ct);
    }

    protected async Task MakeEventAsync(string id, CancellationToken ct)
    {
        var found = await ClickImageAsync(id, "event", ct);
        if (!found) return;

        await SleepAsync(2, ct);
        for (int i = 0; i < 5; i++)
        {
            await adb.TapAsync(id, 550, 1100);
            await SleepAsync(1, ct);
        }
        for (int i = 0; i < 3; i++)
        {
            await adb.SwipeAsync(id, 870, 690, 500, 1100, 100);
            await SleepAsync(1, ct);
        }
        await CloseAllPopupsAsync(id, ct);
        await SleepAsync(1, ct);
        await CloseAllPopupsAsync(id, ct);
    }

    protected async Task GoUpAsync(string id, CancellationToken ct, int times = 1)
    {
        for (int i = 0; i < times; i++)
        {
            await adb.SwipeAsync(id, 1160, 1050, 1160, 1700, 100);
            await SleepAsync(0.1, ct);
        }
        await SleepAsync(0.5, ct);
    }

    protected async Task GoDownAsync(string id, CancellationToken ct, int times = 1)
    {
        for (int i = 0; i < times; i++)
        {
            await adb.SwipeAsync(id, 1160, 1050, 1160, 400, 100);
            await SleepAsync(0.1, ct);
        }
        await SleepAsync(0.5, ct);
    }

    protected async Task GoLastAsync(string id, CancellationToken ct)
    {
        await GoUpAsync(id, ct);
        await adb.TapAsync(id, 0.51 * 2160, 0.98 * 1858);
        await SleepAsync(1, ct);
    }

    protected async Task PlantTreeAsync(string id, CancellationToken ct, string? tree = null, int num = 24, bool next = true)
    {
        await adb.TapAsync(id, FullTreePoint[0].x, FullTreePoint[0].y);
        await SleepAsync(0.5, ct);

        (double x, double y) slot = (640, 1640);

        if (tree is not null)
        {
            var found = await FindImageAsync(id, $"cay/{tree}", ct);
            int attempt = 5;
            while (found is null && attempt-- > 0)
            {
                await adb.TapAsync(id, next ? 905 : 360, 1530);
                await SleepAsync(0.5, ct);
                found = await FindImageAsync(id, $"cay/{tree}", ct);
            }
            if (found is null) throw new InvalidOperationException($"Tree image not found: {tree}");
            slot = found.Value;
        }

        var points = new[] { slot }.Concat(FullTreePoint.Take(num)).ToArray();
        await adb.DragAsync(id, points);
        await SleepAsync(0.5, ct);
    }

    protected async Task HarvestTreeAsync(string id, CancellationToken ct, int num = 24)
    {
        await adb.TapAsync(id, FullTreePoint[0].x, FullTreePoint[0].y);
        await SleepAsync(0.5, ct);

        (double x, double y)? slot = await FindImageAsync(id, "thu-hoach", ct);
        int attempt = 3;
        while (slot is null && attempt-- > 0)
        {
            await adb.TapAsync(id, FullTreePoint[0].x, FullTreePoint[0].y);
            await SleepAsync(0.5, ct);
            slot = await FindImageAsync(id, "thu-hoach", ct);
        }
        if (slot is null) throw new InvalidOperationException("Harvest icon not found");

        var points = new[] { slot.Value }.Concat(FullTreePoint.Take(num)).ToArray();
        await adb.DragAsync(id, points);
        await SleepAsync(0.5, ct);
    }

    protected async Task MakeItemsAsync(string id, CancellationToken ct, int floor = 1, int slot = 0, int num = 1)
    {
        var position = floor == 1 ? (560.0, 1700.0) : (560.0, 1220.0);

        for (int i = 0; i < Math.Max(10, 2 * num); i++)
        {
            await adb.TapAsync(id, position.Item1, position.Item2);
            await SleepAsync(0.25, ct);
        }

        int attempt = 5;
        while (attempt-- > 0 && await FindImageAsync(id, "o-trong-san-xuat", ct) is null)
        {
            await adb.TapAsync(id, position.Item1, position.Item2);
            await SleepAsync(0.25, ct);
        }
        if (attempt < 0) throw new InvalidOperationException("Production slot not found");

        for (int i = 0; i < num; i++)
        {
            await adb.DragAsync(id, [FullItemPoint[slot], (1420, 1680)]);
            await SleepAsync(0.25, ct);
        }

        await adb.TapAsync(id, 360, floor == 1 ? 1550 : 1090);
        await SleepAsync(0.1, ct);
        await adb.TapAsync(id, 1600, 1140);
        await SleepAsync(0.1, ct);
        await CloseAllPopupsAsync(id, ct);
    }

    protected async Task SellItemsAsync(string id, CancellationToken ct, SellOption option, List<SellItem> items)
    {
        var chooseType = SellOptions[(int)option];
        int count = 0;

        await adb.TapAsync(id, 1375, 1530);
        await SleepAsync(1, ct);

        // Back to front market
        for (int i = 0; i < 2; i++)
        {
            await adb.SwipeAsync(id, 500, 1000, 1650, 1000, 300);
            await SleepAsync(0.5, ct);
        }

        string? item = GetRemainItem(items);
        while (item is not null)
        {
            ct.ThrowIfCancellationRequested();

            var soldSlot = await FindImageAsync(id, "o-da-ban", ct);
            if (soldSlot is not null)
            {
                await adb.TapAsync(id, soldSlot.Value.x, soldSlot.Value.y);
                await SleepAsync(0.25, ct);
                await adb.TapAsync(id, soldSlot.Value.x, soldSlot.Value.y);
                await SleepAsync(0.25, ct);
                await adb.TapAsync(id, chooseType.x, chooseType.y);
                await SleepAsync(0.5, ct);
                await ClickImageAsync(id, $"vat-pham/{item}", ct);
                await SellAsync(id, ct);
                item = GetRemainItem(items);
                continue;
            }

            var emptySlot = await FindImageAsync(id, "o-trong-ban", ct);
            if (emptySlot is not null)
            {
                await adb.TapAsync(id, emptySlot.Value.x, emptySlot.Value.y);
                await SleepAsync(0.5, ct);
                await adb.TapAsync(id, chooseType.x, chooseType.y);
                await SleepAsync(0.5, ct);
                await ClickImageAsync(id, $"vat-pham/{item}", ct);
                await SellAsync(id, ct);
                item = GetRemainItem(items);
                continue;
            }

            // Move to next page
            await adb.SwipeAsync(id, 1650, 1000, 500, 1000, 3000);
            await SleepAsync(0.5, ct);
            count++;

            if (count > 2)
            {
                int randSlot = Random.Shared.Next(0, 4);
                await adb.TapAsync(id, SellSlotPoint[randSlot].x, SellSlotPoint[randSlot].y);
                await SleepAsync(0.5, ct);
                await adb.TapAsync(id, 1080, 1360);
                await SleepAsync(0.5, ct);
                await adb.TapAsync(id, 1310, 500);
                await SleepAsync(0.5, ct);
                await CloseAllPopupsAsync(id, ct);
                RollBackItem(items, item);
                // Recurse for remaining items
                await SellItemsAsync(id, ct, option, items);
                return;
            }
        }

        await CloseAllPopupsAsync(id, ct);
    }

    protected async Task GoFriendAsync(string id, CancellationToken ct, int slot = 0)
    {
        if (await ClickImageAsync(id, "nha-ban", ct))
        {
            await SleepAsync(1, ct);
            await adb.TapAsync(id, FriendHousePoint[slot].x, FriendHousePoint[slot].y);
            await SleepAsync(2, ct);
        }
    }

    protected async Task GoHomeAsync(string id, CancellationToken ct)
    {
        if (await ClickImageAsync(id, "nha-minh", ct))
            await SleepAsync(2, ct);
    }

    protected async Task Buy8SlotAsync(string id, CancellationToken ct)
    {
        await adb.TapAsync(id, 1375, 1530);
        await SleepAsync(1, ct);

        for (int round = 0; round < 2; round++)
        {
            foreach (var point in SellSlotPoint)
            {
                await adb.TapAsync(id, point.x, point.y);
                await SleepAsync(0.1, ct);
                await adb.TapAsync(id, point.x, point.y);
                await SleepAsync(0.1, ct);
            }
        }

        await CloseAllPopupsAsync(id, ct);
    }

    // -------------------------------------------------------------------
    // Internal helpers
    // -------------------------------------------------------------------

    private async Task SellAsync(string id, CancellationToken ct, bool setAds = true)
    {
        await SleepAsync(0.5, ct);
        for (int i = 0; i < 10; i++)
        {
            await adb.TapAsync(id, 1835, 1020);
            await SleepAsync(0.01, ct);
        }
        await SleepAsync(0.5, ct);

        if (!setAds)
        {
            await adb.TapAsync(id, 1685, 1220);
            await SleepAsync(0.5, ct);
            await adb.TapAsync(id, 1685, 1330);
        }
        else
        {
            await adb.TapAsync(id, 1685, 1330);
            await SleepAsync(0.5, ct);
            await adb.TapAsync(id, 1080, 1360);
        }
        await SleepAsync(0.5, ct);
        await adb.TapAsync(id, 1310, 500);
        await SleepAsync(0.5, ct);
    }

    private async Task<(double x, double y)?> FindImageAsync(string deviceId, string assetPath, CancellationToken ct, double threshold = 0.9)
    {
        ct.ThrowIfCancellationRequested();
        var screen = await adb.CaptureScreenAsync(deviceId);
        // Run CPU-bound template matching on a dedicated thread to avoid blocking the ASP.NET thread pool
        return await Task.Run(() => images.FindOnScreen(screen, assetPath, threshold), ct);
    }

    private async Task<bool> ClickImageAsync(string deviceId, string assetPath, CancellationToken ct, double threshold = 0.9)
    {
        var pos = await FindImageAsync(deviceId, assetPath, ct, threshold);
        if (pos is null) return false;
        await adb.TapAsync(deviceId, pos.Value.x, pos.Value.y);
        return true;
    }

    protected static Task SleepAsync(double seconds, CancellationToken ct) =>
        Task.Delay(TimeSpan.FromSeconds(seconds), ct);

    private static string? GetRemainItem(List<SellItem> items)
    {
        foreach (var item in items)
        {
            if (item.Value > 0)
            {
                item.Value--;
                return item.Key;
            }
        }
        return null;
    }

    private static void RollBackItem(List<SellItem> items, string key)
    {
        var item = items.FirstOrDefault(i => i.Key == key);
        if (item is not null) item.Value++;
    }
}

/// <summary>Mutable sell item entry (key = asset path, Value = remaining quantity).</summary>
public class SellItem(string key, int value)
{
    public string Key { get; } = key;
    public int Value { get; set; } = value;
}
