using KvtmAuto.Core.Models;

namespace KvtmAuto.Automation.Engine;

public interface IScript
{
    string Id { get; }
    string Name { get; }
    Task RunAsync(string deviceId, GameOptions options, CancellationToken ct);
}
