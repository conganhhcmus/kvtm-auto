using KvtmAuto.Core.Models;

namespace KvtmAuto.Automation.Scripts;

public class TinhDauChanhVaiXanhLa(AdbController adb, ImageMatcher images, DeviceManager deviceManager)
    : ScriptBase(adb, images, deviceManager)
{
    public override string Id => "04";
    public override string Name => "Tinh Dau Chanh & Vai Xanh La";

    public override async Task RunAsync(string deviceId, GameOptions options, CancellationToken ct)
    {
        if (options.OpenGame)
            await OpenGameAsync(deviceId, ct);

        for (int i = 0; i < LoopNum; i++)
        {
            ct.ThrowIfCancellationRequested();
            Log(deviceId, $"{i}: Run tinh dau chanh, vai xanh la");

            if (options.OpenChests)
                await OpenChestAsync(deviceId, ct);

            for (int j = 0; j < 10; j++)
            {
                bool isEven = j % 2 == 0;

                await GoUpAsync(deviceId, ct);
                await PlantTreeAsync(deviceId, ct, "chanh");
                await GoUpAsync(deviceId, ct);
                await SleepAsync(6, ct);

                if (isEven)
                {
                    await HarvestTreeAsync(deviceId, ct);
                    await PlantTreeAsync(deviceId, ct, "hong");
                    await GoUpAsync(deviceId, ct, 2);
                    await HarvestTreeAsync(deviceId, ct);
                    await PlantTreeAsync(deviceId, ct, "hong");
                    await GoUpAsync(deviceId, ct, 2);
                    await HarvestTreeAsync(deviceId, ct);
                    await PlantTreeAsync(deviceId, ct, "hong");
                    await GoDownAsync(deviceId, ct, 4);
                }

                await HarvestTreeAsync(deviceId, ct);
                await PlantTreeAsync(deviceId, ct, "dua");
                await GoUpAsync(deviceId, ct, 2);
                await HarvestTreeAsync(deviceId, ct);
                await PlantTreeAsync(deviceId, ct, "dua");
                await GoUpAsync(deviceId, ct, 2);
                await HarvestTreeAsync(deviceId, ct);
                await PlantTreeAsync(deviceId, ct, "dua", num: 6);
                await GoDownAsync(deviceId, ct, 4);

                await MakeItemsAsync(deviceId, ct, floor: 1, slot: 0, num: 6); // hoa hong say
                await MakeItemsAsync(deviceId, ct, floor: 2, slot: 1, num: 3); // nuoc tuyet
                await HarvestTreeAsync(deviceId, ct);
                await GoUpAsync(deviceId, ct, 2);
                await HarvestTreeAsync(deviceId, ct);
                await GoUpAsync(deviceId, ct, 2);
                await HarvestTreeAsync(deviceId, ct);
                await MakeItemsAsync(deviceId, ct, floor: 1, slot: 3, num: 6); // tinh dau dua
                await MakeItemsAsync(deviceId, ct, floor: 2, slot: 0, num: 3); // tra hoa hong
                await GoLastAsync(deviceId, ct);
            }

            if (options.SellItems)
                await SellItemsAsync(deviceId, ct, SellOption.Goods,
                [
                    new SellItem("vai-xanh-la", 6),
                    new SellItem("tinh-dau-chanh", 6),
                ]);

            await MakeEventAsync(deviceId, ct);
        }

        Log(deviceId, "The automation completed");
    }
}
