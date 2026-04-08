using KvtmAuto.Core.Models;

namespace KvtmAuto.Automation.Scripts;

public class MuaVpsk(AdbController adb, ImageMatcher images, DeviceManager deviceManager)
    : ScriptBase(adb, images, deviceManager)
{
    public override string Id => "99";
    public override string Name => "Mua Vat Pham Su Kien";

    public override async Task RunAsync(string deviceId, GameOptions options, CancellationToken ct)
    {
        if (options.OpenGame)
            await OpenGameAsync(deviceId, ct);

        if (options.OpenChests)
            await OpenChestAsync(deviceId, ct);

        await GoFriendAsync(deviceId, ct, slot: 1);

        for (int i = 0; i < 100_000; i++)
        {
            ct.ThrowIfCancellationRequested();
            Log(deviceId, $"{i}: Run mua vat pham su kien");
            await Buy8SlotAsync(deviceId, ct);
        }

        await GoHomeAsync(deviceId, ct);
        Log(deviceId, "The automation completed");
    }
}
