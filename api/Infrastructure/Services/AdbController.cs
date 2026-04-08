using System.Diagnostics;
using System.Text;

namespace KvtmAuto.Infrastructure.Services;

public class AdbController()
{
    // BlueStacks Virtual Touch uses 0-32767 coordinate range
    private const int DeviceMaxX = 32767;
    private const int DeviceMaxY = 32767;
    private const string TouchDevice = "/dev/input/event2";
    private const int DefaultScreenWidth = 2160;
    private const int DefaultScreenHeight = 1858;

    // sendevent codes
    private const int EvAbs = 3;
    private const int EvSyn = 0;
    private const int AbsMtPositionX = 53;
    private const int AbsMtPositionY = 54;
    private const int SynReport = 0;
    private const int SynMtReport = 2;

    // -------------------------------------------------------------------
    // Device discovery
    // -------------------------------------------------------------------

    public async Task<List<string>> GetDeviceIdsAsync()
    {
        var (stdout, _) = await RunAsync("devices");
        var ids = new List<string>();
        foreach (var line in stdout.Split('\n').Skip(1))
        {
            var parts = line.Trim().Split('\t');
            if (parts.Length == 2 && parts[1].Trim() == "device")
                ids.Add(parts[0].Trim());
        }
        return ids;
    }

    // -------------------------------------------------------------------
    // Screen capture
    // -------------------------------------------------------------------

    public async Task<byte[]> CaptureScreenAsync(string deviceId)
    {
        using var process = new Process
        {
            StartInfo = new ProcessStartInfo
            {
                FileName = "adb",
                Arguments = $"-s {deviceId} exec-out screencap -p",
                RedirectStandardOutput = true,
                UseShellExecute = false,
                CreateNoWindow = true,
            }
        };
        process.Start();
        using var ms = new MemoryStream();
        await process.StandardOutput.BaseStream.CopyToAsync(ms);
        await process.WaitForExitAsync();
        return ms.ToArray();
    }

    public (Process process, Stream stream) OpenScreenRecordExecOutStream(
        string deviceId, int bitRate = 2_500_000, int timeLimit = 180)
    {
        var process = new Process
        {
            StartInfo = new ProcessStartInfo
            {
                FileName = "adb",
                Arguments = $"-s {deviceId} exec-out screenrecord --output-format=h264 --bit-rate={bitRate} --time-limit={timeLimit} -",
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
            }
        };
        process.Start();
        return (process, process.StandardOutput.BaseStream);
    }

    // -------------------------------------------------------------------
    // UI interactions
    // -------------------------------------------------------------------

    public async Task TapAsync(string deviceId, double x, double y)
    {
        // Supports both pixel coords (>1) and percentage coords (0.0-1.0)
        await RunAsync($"-s {deviceId} shell input tap {(int)x} {(int)y}");
    }

    public async Task SwipeAsync(string deviceId, double x1, double y1, double x2, double y2, int durationMs = 300)
    {
        await RunAsync($"-s {deviceId} shell input swipe {(int)x1} {(int)y1} {(int)x2} {(int)y2} {durationMs}");
    }

    /// <summary>
    /// Smooth drag through a series of points using sendevent (BlueStacks Virtual Touch).
    /// Coordinates are pixel values relative to screen dimensions (default 2160x1858).
    /// </summary>
    public async Task DragAsync(string deviceId, (double x, double y)[] points, int screenWidth = DefaultScreenWidth, int screenHeight = DefaultScreenHeight)
    {
        if (points.Length < 2)
            throw new ArgumentException("Need at least 2 points for drag");

        var sb = new StringBuilder();
        foreach (var (x, y) in points)
        {
            var (dx, dy) = ToDeviceCoords(x, y, screenWidth, screenHeight);
            sb.Append($"sendevent {TouchDevice} {EvAbs} {AbsMtPositionX} {dx}; ");
            sb.Append($"sendevent {TouchDevice} {EvAbs} {AbsMtPositionY} {dy}; ");
            sb.Append($"sendevent {TouchDevice} {EvSyn} {SynMtReport} 0; ");
            sb.Append($"sendevent {TouchDevice} {EvSyn} {SynReport} 0; ");
        }
        // Release events
        sb.Append($"sendevent {TouchDevice} {EvSyn} {SynMtReport} 0; ");
        sb.Append($"sendevent {TouchDevice} {EvSyn} {SynReport} 0; ");
        sb.Append($"sendevent {TouchDevice} {EvSyn} {SynMtReport} 0; ");
        sb.Append($"sendevent {TouchDevice} {EvSyn} {SynReport} 0");

        await ShellAsync(deviceId, sb.ToString());
    }

    public async Task KeyEventAsync(string deviceId, int keycode)
    {
        await RunAsync($"-s {deviceId} shell input keyevent {keycode}");
    }

    public async Task StartAppAsync(string deviceId, string package)
    {
        await RunAsync($"-s {deviceId} shell monkey -p {package} -c android.intent.category.LAUNCHER 1");
    }

    public async Task StopAppAsync(string deviceId, string package)
    {
        await RunAsync($"-s {deviceId} shell am force-stop {package}");
    }

    public async Task<string> ShellAsync(string deviceId, string command)
    {
        var (stdout, _) = await RunAsync($"-s {deviceId} shell \"{command.Replace("\"", "\\\"")}\"");
        return stdout;
    }

    // -------------------------------------------------------------------
    // Screen size helper
    // -------------------------------------------------------------------

    public async Task<(int width, int height)> GetScreenSizeAsync(string deviceId)
    {
        var (stdout, _) = await RunAsync($"-s {deviceId} shell wm size");
        // "Physical size: 2160x1858"
        var part = stdout.Split(':').LastOrDefault()?.Trim();
        if (part is not null)
        {
            var dims = part.Split('x');
            if (dims.Length == 2 && int.TryParse(dims[0], out var w) && int.TryParse(dims[1], out var h))
                return (w, h);
        }
        return (DefaultScreenWidth, DefaultScreenHeight);
    }

    // -------------------------------------------------------------------
    // Internal helpers
    // -------------------------------------------------------------------

    private static (int dx, int dy) ToDeviceCoords(double x, double y, int screenWidth, int screenHeight)
    {
        // If coordinates are >= 1 they are pixels — convert to 0..1 first
        double px = x >= 1 ? x / screenWidth : x;
        double py = y >= 1 ? y / screenHeight : y;
        return ((int)(px * DeviceMaxX), (int)(py * DeviceMaxY));
    }

    private async Task<(string stdout, int exitCode)> RunAsync(string args)
    {
        using var process = new Process
        {
            StartInfo = new ProcessStartInfo
            {
                FileName = "adb",
                Arguments = args,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
            }
        };
        process.Start();
        var stdout = await process.StandardOutput.ReadToEndAsync();
        await process.WaitForExitAsync();
        return (stdout, process.ExitCode);
    }
}
