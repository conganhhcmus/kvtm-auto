using KvtmAuto.Core.Models;
using KvtmAuto.Automation.Engine;

namespace KvtmAuto.Features.Scripts;

public class ScriptManager(AdbController adb, ImageMatcher images, DeviceManager deviceManager)
{
    private readonly List<IScript> _scripts =
    [
        new NuocHoaTao(adb, images, deviceManager),
        new VaiXanhLa(adb, images, deviceManager),
        new VaiTim(adb, images, deviceManager),
        new TinhDauChanhVaiXanhLa(adb, images, deviceManager),
        new TinhDauDuaTraHoaHong(adb, images, deviceManager),
        new TrongCaySuKien(adb, images, deviceManager),
        new MuaVpsk(adb, images, deviceManager),
    ];

    public IReadOnlyList<Script> Scripts =>
        _scripts.Select(s => new Script { Id = s.Id, Name = s.Name }).ToList();

    public Script? GetScript(string id)
    {
        var s = _scripts.FirstOrDefault(x => x.Id == id);
        return s is null ? null : new Script { Id = s.Id, Name = s.Name };
    }

    public IScript? GetIScript(string id) =>
        _scripts.FirstOrDefault(s => s.Id == id);
}
