using KvtmAuto.Core.Models;

namespace KvtmAuto.Automation.Scripts;

public class VaiXanhLa(AdbController adb, ImageMatcher images, DeviceManager deviceManager)
    : ScriptBase(adb, images, deviceManager)
{
    public override string Id => "02";
    public override string Name => "Vai Xanh La";

    public override async Task RunAsync(string deviceId, GameOptions options, CancellationToken ct)
    {
        if (options.OpenGame)
            await OpenGameAsync(deviceId, ct);

        for (int i = 0; i < LoopNum; i++)
        {
            ct.ThrowIfCancellationRequested();
            Log(deviceId, $"{i}: Run vai xanh la");

            if (options.OpenChests)
                await OpenChestAsync(deviceId, ct);

            for (int j = 0; j < 10; j++)
            {
                await GoUpAsync(deviceId, ct);
                await PlantTreeAsync(deviceId, ct, "chanh");
                await GoLastAsync(deviceId, ct);
                await SleepAsync(7, ct);

                await GoUpAsync(deviceId, ct);
                await HarvestTreeAsync(deviceId, ct);
                await PlantTreeAsync(deviceId, ct, "bong", num: 18, next: false);
                await GoLastAsync(deviceId, ct);

                await GoUpAsync(deviceId, ct);
                await MakeItemsAsync(deviceId, ct, floor: 2, slot: 3, num: 6);
                await HarvestTreeAsync(deviceId, ct);
                await GoUpAsync(deviceId, ct, 2);
                await MakeItemsAsync(deviceId, ct, floor: 1, slot: 3, num: 6);
                await GoLastAsync(deviceId, ct);
            }

            if (options.SellItems)
                await SellItemsAsync(deviceId, ct, SellOption.Goods,
                [
                    new SellItem("vai-xanh-la", 6),
                ]);

            await MakeEventAsync(deviceId, ct);
        }

        Log(deviceId, "The automation completed");
    }
}
