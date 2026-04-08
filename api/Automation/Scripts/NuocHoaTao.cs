using KvtmAuto.Core.Models;

namespace KvtmAuto.Automation.Scripts;

public class NuocHoaTao(AdbController adb, ImageMatcher images, DeviceManager deviceManager)
    : ScriptBase(adb, images, deviceManager)
{
    public override string Id => "01";
    public override string Name => "Nuoc Hoa Tao";

    public override async Task RunAsync(string deviceId, GameOptions options, CancellationToken ct)
    {
        if (options.OpenGame)
            await OpenGameAsync(deviceId, ct);

        for (int i = 0; i < LoopNum; i++)
        {
            ct.ThrowIfCancellationRequested();
            Log(deviceId, $"{i}: Run nuoc hoa tao");

            if (options.OpenChests)
                await OpenChestAsync(deviceId, ct);

            for (int j = 0; j < 10; j++)
            {
                bool isEven = j % 2 == 0;

                await GoUpAsync(deviceId, ct);
                await PlantTreeAsync(deviceId, ct, "tao");
                await GoUpAsync(deviceId, ct, 4);
                await PlantTreeAsync(deviceId, ct, "tao");
                await GoLastAsync(deviceId, ct);
                await SleepAsync(1, ct);

                await GoUpAsync(deviceId, ct);
                if (isEven)
                {
                    await HarvestTreeAsync(deviceId, ct);
                    await PlantTreeAsync(deviceId, ct, "tao", num: 12);
                    await GoUpAsync(deviceId, ct, 4);
                }

                await HarvestTreeAsync(deviceId, ct);
                await PlantTreeAsync(deviceId, ct, "tuyet");
                await GoLastAsync(deviceId, ct);

                if (!isEven)
                    await SleepAsync(7, ct);

                await GoUpAsync(deviceId, ct);
                await HarvestTreeAsync(deviceId, ct);
                await MakeItemsAsync(deviceId, ct, floor: 2, slot: 0, num: 6); // nuoc tao
                await GoUpAsync(deviceId, ct, 4);
                await HarvestTreeAsync(deviceId, ct);
                await MakeItemsAsync(deviceId, ct, floor: 1, slot: 1, num: 6); // tinh dau tao
                await GoUpAsync(deviceId, ct, 2);
                await MakeItemsAsync(deviceId, ct, floor: 2, slot: 1, num: 6); // nuoc hoa tao
                await GoLastAsync(deviceId, ct);
            }

            if (options.SellItems)
                await SellItemsAsync(deviceId, ct, SellOption.Goods,
                [
                    new SellItem("nuoc-hoa-tao", 6),
                ]);

            await MakeEventAsync(deviceId, ct);
        }

        Log(deviceId, "The automation completed");
    }
}
