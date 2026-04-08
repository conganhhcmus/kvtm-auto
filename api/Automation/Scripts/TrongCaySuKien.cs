using KvtmAuto.Core.Models;

namespace KvtmAuto.Automation.Scripts;

public class TrongCaySuKien(AdbController adb, ImageMatcher images, DeviceManager deviceManager)
    : ScriptBase(adb, images, deviceManager)
{
    public override string Id => "98";
    public override string Name => "Trong Cay Su Kien";

    public override async Task RunAsync(string deviceId, GameOptions options, CancellationToken ct)
    {
        if (options.OpenGame)
            await OpenGameAsync(deviceId, ct);

        for (int i = 0; i < 1000; i++)
        {
            ct.ThrowIfCancellationRequested();
            Log(deviceId, $"{i}: Run trong cay su kien");

            if (options.OpenChests && i % 10 == 0)
                await OpenChestAsync(deviceId, ct);

            if (i == 0)
            {
                await GoUpAsync(deviceId, ct);
                await PlantTreeAsync(deviceId, ct);
                await GoUpAsync(deviceId, ct, 4);
                await PlantTreeAsync(deviceId, ct);
                await GoUpAsync(deviceId, ct, 4);
                await PlantTreeAsync(deviceId, ct);
                await GoLastAsync(deviceId, ct);
            }

            if (i < 999)
            {
                await GoUpAsync(deviceId, ct);
                await HarvestTreeAsync(deviceId, ct);
                await PlantTreeAsync(deviceId, ct);
                await GoUpAsync(deviceId, ct, 4);
                await HarvestTreeAsync(deviceId, ct);
                await PlantTreeAsync(deviceId, ct);
                await GoUpAsync(deviceId, ct, 4);
                await HarvestTreeAsync(deviceId, ct);
                await PlantTreeAsync(deviceId, ct);
                await GoLastAsync(deviceId, ct);
            }
            else
            {
                await GoUpAsync(deviceId, ct);
                await HarvestTreeAsync(deviceId, ct);
                await GoUpAsync(deviceId, ct, 4);
                await HarvestTreeAsync(deviceId, ct);
                await GoUpAsync(deviceId, ct, 4);
                await HarvestTreeAsync(deviceId, ct);
                await GoLastAsync(deviceId, ct);
            }
        }

        Log(deviceId, "The automation completed");
    }
}
