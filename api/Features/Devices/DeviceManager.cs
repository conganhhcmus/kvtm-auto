using KvtmAuto.Infrastructure.Database;
using KvtmAuto.Hubs;
using KvtmAuto.Core.Models;
using Microsoft.AspNetCore.SignalR;
using Microsoft.EntityFrameworkCore;

namespace KvtmAuto.Features.Devices;

public class DeviceManager(
    IServiceScopeFactory scopeFactory,
    AdbController adb,
    IHubContext<LogHub> hub,
    ILogger<DeviceManager> logger) : BackgroundService
{
    private readonly TimeSpan _pollInterval = TimeSpan.FromSeconds(5);
    private readonly Dictionary<string, Device> _devices = [];
    private readonly Lock _lock = new();

    // Friendly name map (serial → display name)
    private static readonly Dictionary<string, string> NameMap = new()
    {
        ["emulator-5554"] = "Kai",
        ["emulator-5564"] = "Cong Anh",
        ["emulator-5574"] = "My Hanh",
    };

    public IReadOnlyList<Device> Devices
    {
        get { lock (_lock) return [.. _devices.Values]; }
    }

    public Device? GetDevice(string id)
    {
        lock (_lock) return _devices.GetValueOrDefault(id);
    }

    public void UpdateDevice(string id, Action<Device> update)
    {
        lock (_lock)
        {
            if (_devices.TryGetValue(id, out var device))
                update(device);
        }
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        await LoadFromDbAsync();

        while (!stoppingToken.IsCancellationRequested)
        {
            await DiscoverAsync();
            await Task.Delay(_pollInterval, stoppingToken);
        }
    }

    private async Task LoadFromDbAsync()
    {
        using var scope = scopeFactory.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        var saved = await db.Devices.ToListAsync();
        lock (_lock)
        {
            foreach (var d in saved)
            {
                d.Status = DeviceStatus.Offline;
                d.CurrentScriptId = null;
                _devices[d.Id] = d;
            }
        }
        await db.SaveChangesAsync();
        logger.LogInformation("Loaded {Count} devices from DB", saved.Count);
    }

    private async Task DiscoverAsync()
    {
        try
        {
            var connected = await adb.GetDeviceIdsAsync();
            var connectedSet = connected.ToHashSet();
            var changed = false;

            lock (_lock)
            {
                // Mark online / add new
                foreach (var id in connected)
                {
                    if (!_devices.TryGetValue(id, out var device))
                    {
                        device = new Device
                        {
                            Id = id,
                            Name = NameMap.GetValueOrDefault(id, id),
                            Status = DeviceStatus.Online,
                            LastSeen = DateTime.UtcNow,
                        };
                        _devices[id] = device;
                        changed = true;
                    }
                    else
                    {
                        device.LastSeen = DateTime.UtcNow;
                        if (device.Status == DeviceStatus.Offline)
                        {
                            device.Status = DeviceStatus.Online;
                            changed = true;
                        }
                    }
                }

                // Mark offline
                foreach (var device in _devices.Values)
                {
                    if (!connectedSet.Contains(device.Id) && device.Status != DeviceStatus.Offline)
                    {
                        device.Status = DeviceStatus.Offline;
                        changed = true;
                    }
                }
            }

            if (changed)
                await PersistAsync();
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Device discovery error");
        }
    }

    private async Task PersistAsync()
    {
        try
        {
            using var scope = scopeFactory.CreateScope();
            var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();

            List<Device> snapshot;
            lock (_lock) snapshot = [.. _devices.Values];

            foreach (var device in snapshot)
            {
                var existing = await db.Devices.FindAsync(device.Id);
                if (existing is null)
                    db.Devices.Add(device);
                else
                {
                    existing.Name = device.Name;
                    existing.Status = device.Status;
                    existing.LastSeen = device.LastSeen;
                    existing.CurrentScriptId = device.CurrentScriptId;
                }
            }

            await db.SaveChangesAsync();
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Failed to persist device state");
        }
    }

    public void AppendLog(string deviceId, string message)
    {
        var logsDir = Path.Combine("data", "logs");
        Directory.CreateDirectory(logsDir);
        var logFile = Path.Combine(logsDir, $"{deviceId}.log");
        var entry = $"[{DateTime.Now:HH:mm:ss}]: {message}";
        File.AppendAllText(logFile, entry + Environment.NewLine);

        // Push to any connected SignalR clients watching this device's logs
        _ = hub.Clients.Group($"logs-{deviceId}").SendAsync("ReceiveLog", entry);
    }

    public string[] GetLogs(string deviceId, int limit = 100)
    {
        var logFile = Path.Combine("data", "logs", $"{deviceId}.log");
        if (!File.Exists(logFile)) return [];
        var lines = File.ReadAllLines(logFile);
        return lines.Length <= limit ? lines : lines[^limit..];
    }

    public void ClearLogs(string deviceId)
    {
        var logFile = Path.Combine("data", "logs", $"{deviceId}.log");
        if (File.Exists(logFile)) File.Delete(logFile);
    }
}
