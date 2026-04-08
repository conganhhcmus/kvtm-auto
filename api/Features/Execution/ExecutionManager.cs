using KvtmAuto.Core.Models;

namespace KvtmAuto.Features.Execution;

public class ExecutionManager(
    DeviceManager deviceManager,
    ScriptManager scriptManager,
    ILogger<ExecutionManager> logger)
{
    private readonly Dictionary<string, (Task task, CancellationTokenSource cts)> _running = [];
    private readonly Lock _lock = new();

    public Task StartAsync(string deviceId, string scriptId, GameOptions options)
    {
        var device = deviceManager.GetDevice(deviceId)
            ?? throw new InvalidOperationException("Device not found");

        if (device.Status == DeviceStatus.Busy)
            throw new InvalidOperationException("Device is busy");

        var script = scriptManager.GetIScript(scriptId)
            ?? throw new InvalidOperationException("Script not found");

        deviceManager.ClearLogs(deviceId);

        var cts = new CancellationTokenSource();

        var task = Task.Run(async () =>
        {
            try
            {
                await script.RunAsync(deviceId, options, cts.Token);

                deviceManager.UpdateDevice(deviceId, d =>
                {
                    d.Status = DeviceStatus.Online;
                    d.CurrentScriptId = null;
                });
                deviceManager.AppendLog(deviceId, "Script execution completed");
            }
            catch (OperationCanceledException)
            {
                // stopped intentionally — state already reset in StopAsync
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Script error for {DeviceId}", deviceId);
                deviceManager.AppendLog(deviceId, $"Script error: {ex.Message}");
                deviceManager.UpdateDevice(deviceId, d =>
                {
                    d.Status = DeviceStatus.Online;
                    d.CurrentScriptId = null;
                });
            }
            finally
            {
                lock (_lock) _running.Remove(deviceId);
                cts.Dispose();
            }
        }, cts.Token);

        lock (_lock) _running[deviceId] = (task, cts);

        deviceManager.UpdateDevice(deviceId, d =>
        {
            d.Status = DeviceStatus.Busy;
            d.CurrentScriptId = scriptId;
        });

        deviceManager.AppendLog(deviceId, $"Script {script.Name} started");

        return Task.CompletedTask;
    }

    public async Task StopAsync(string deviceId)
    {
        (Task task, CancellationTokenSource cts) entry;
        lock (_lock)
        {
            if (!_running.TryGetValue(deviceId, out entry))
                throw new InvalidOperationException("No running script for device");
            _running.Remove(deviceId);
        }

        entry.cts.Cancel();

        try
        {
            await entry.task.WaitAsync(TimeSpan.FromSeconds(10));
        }
        catch (TimeoutException)
        {
            logger.LogWarning("Script for {DeviceId} did not stop within timeout", deviceId);
        }
        catch (OperationCanceledException) { /* expected */ }
        catch (Exception ex)
        {
            logger.LogWarning(ex, "Error stopping script for {DeviceId}", deviceId);
        }

        deviceManager.UpdateDevice(deviceId, d =>
        {
            d.Status = DeviceStatus.Online;
            d.CurrentScriptId = null;
        });

        deviceManager.AppendLog(deviceId, "Script execution stopped");
    }

    public async Task StopAllAsync()
    {
        List<string> ids;
        lock (_lock) ids = [.. _running.Keys];
        foreach (var id in ids)
        {
            try { await StopAsync(id); }
            catch (Exception ex) { logger.LogWarning(ex, "Error stopping {DeviceId}", id); }
        }
    }

    public bool IsRunning(string deviceId)
    {
        lock (_lock) return _running.ContainsKey(deviceId);
    }
}
