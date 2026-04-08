using System.Diagnostics;
using Microsoft.AspNetCore.SignalR;

namespace KvtmAuto.Hubs;

public class ScreenHub(AdbController adb, IHubContext<ScreenHub> hubContext, ILogger<ScreenHub> logger) : Hub
{
    private static readonly Dictionary<string, CancellationTokenSource> ActiveStreams = [];
    private static readonly Lock StreamsLock = new();

    public async Task StartStream(string deviceId)
    {
        var connectionId = Context.ConnectionId;

        lock (StreamsLock)
        {
            if (ActiveStreams.ContainsKey(connectionId)) return;
            ActiveStreams[connectionId] = new CancellationTokenSource();
        }

        logger.LogInformation("Screen stream started for {DeviceId} (conn: {ConnId})", deviceId, connectionId);
        _ = StreamAsync(deviceId, connectionId, ActiveStreams[connectionId].Token);

        await Clients.Caller.SendAsync("StreamStarted", deviceId);
    }

    public async Task StopStream(string deviceId)
    {
        CancelStream(Context.ConnectionId);
        await Clients.Caller.SendAsync("StreamStopped", deviceId);
    }

    public override Task OnDisconnectedAsync(Exception? exception)
    {
        CancelStream(Context.ConnectionId);
        return base.OnDisconnectedAsync(exception);
    }

    private async Task StreamAsync(string deviceId, string connectionId, CancellationToken ct)
    {
        Process? process = null;
        int totalBytes = 0;
        try
        {
            Stream stream;
            (process, stream) = adb.OpenScreenRecordExecOutStream(deviceId);

            var buffer = new byte[4096];
            var accumulator = new List<byte>(65536);
            int bytesRead;

            while (!ct.IsCancellationRequested &&
                   (bytesRead = await stream.ReadAsync(buffer, ct)) > 0)
            {
                totalBytes += bytesRead;
                for (int j = 0; j < bytesRead; j++) accumulator.Add(buffer[j]);

                int searchFrom = Math.Max(1, accumulator.Count - bytesRead - 4);
                var nalIndex = FindNalBoundary(accumulator, searchFrom);
                if (nalIndex > 0)
                {
                    var chunk = accumulator.Take(nalIndex).ToArray();
                    accumulator.RemoveRange(0, nalIndex);
                    await hubContext.Clients.Client(connectionId).SendAsync("ReceiveFrame", chunk, ct);
                }

                if (accumulator.Count > 1024 * 1024)
                {
                    var chunk = accumulator.ToArray();
                    accumulator.Clear();
                    await hubContext.Clients.Client(connectionId).SendAsync("ReceiveFrame", chunk, ct);
                }
            }
        }
        catch (OperationCanceledException) { /* stopped intentionally */ }
        catch (Exception ex)
        {
            logger.LogError(ex, "Stream error for {DeviceId} ({Bytes} bytes)", deviceId, totalBytes);
            try { await hubContext.Clients.Client(connectionId).SendAsync("StreamError", ex.Message, CancellationToken.None); } catch { }
        }
        finally
        {
            try { process?.Kill(); } catch { }
            process?.Dispose();

            logger.LogInformation("Screen stream ended for {DeviceId} ({Bytes} bytes)", deviceId, totalBytes);

            CancelStream(connectionId);

            try { await hubContext.Clients.Client(connectionId).SendAsync("StreamEnded", deviceId, CancellationToken.None); } catch { }
        }
    }

    private static void CancelStream(string connectionId)
    {
        lock (StreamsLock)
        {
            if (ActiveStreams.TryGetValue(connectionId, out var cts))
            {
                cts.Cancel();
                cts.Dispose();
                ActiveStreams.Remove(connectionId);
            }
        }
    }

    private static int FindNalBoundary(List<byte> data, int startFrom)
    {
        for (int i = startFrom; i < data.Count - 3; i++)
        {
            if (data[i] == 0x00 && data[i + 1] == 0x00)
            {
                if (data[i + 2] == 0x01) return i;
                if (i + 3 < data.Count && data[i + 2] == 0x00 && data[i + 3] == 0x01) return i;
            }
        }
        return -1;
    }
}
