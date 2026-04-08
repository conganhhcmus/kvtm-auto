using KvtmAuto.Core.Models;

namespace KvtmAuto.Automation.Scripts;

public class VaiTim(AdbController adb, ImageMatcher images, DeviceManager deviceManager)
    : ScriptBase(adb, images, deviceManager)
{
    public override string Id => "03";
    public override string Name => "Vai Tim";

    public override async Task RunAsync(string deviceId, GameOptions options, CancellationToken ct)
    {
        if (options.OpenGame)
            await OpenGameAsync(deviceId, ct);

        for (int i = 0; i < LoopNum; i++)
        {
            ct.ThrowIfCancellationRequested();
            Log(deviceId, $"{i}: Run vai tim");

            if (options.OpenChests)
                await OpenChestAsync(deviceId, ct);

            for (int j = 0; j < 10; j++)
            {
                bool isLast = j == 9;

                await GoUpAsync(deviceId, ct);
                await PlantTreeAsync(deviceId, ct, "oai-huong");
                await GoLastAsync(deviceId, ct);
                await SleepAsync(7, ct);

                await GoUpAsync(deviceId, ct);
                await HarvestTreeAsync(deviceId, ct);
                await PlantTreeAsync(deviceId, ct, "bong", next: false);
                await GoLastAsync(deviceId, ct);

                await GoUpAsync(deviceId, ct);
                await MakeItemsAsync(deviceId, ct, floor: 1, slot: 2, num: 8); // oai huong say
                await HarvestTreeAsync(deviceId, ct);
                await GoUpAsync(deviceId, ct, 2);
                await MakeItemsAsync(deviceId, ct, floor: 1, slot: 2, num: 8); // vai tim
                await GoLastAsync(deviceId, ct);

                if (!isLast)
                    await SleepAsync(25, ct);
            }

            if (options.SellItems)
                await SellItemsAsync(deviceId, ct, SellOption.Goods,
                [
                    new SellItem("vai-tim", 8),
                ]);

            await MakeEventAsync(deviceId, ct);
        }

        Log(deviceId, "The automation completed");
    }
}
