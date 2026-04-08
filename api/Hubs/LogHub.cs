using Microsoft.AspNetCore.SignalR;

namespace KvtmAuto.Hubs;

public class LogHub(DeviceManager deviceManager) : Hub
{
    public async Task SubscribeLogs(string deviceId)
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, $"logs-{deviceId}");
    }

    public async Task UnsubscribeLogs(string deviceId)
    {
        await Groups.RemoveFromGroupAsync(Context.ConnectionId, $"logs-{deviceId}");
    }

    public Task<string[]> GetLogs(string deviceId) =>
        Task.FromResult(deviceManager.GetLogs(deviceId));
}
