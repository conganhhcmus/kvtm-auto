# KVTM Auto

**KVTM Auto** is a full-stack Android device automation platform for automating mobile games via ADB (Android Debug Bridge). Built as a .NET 10 + React monorepo, it provides a web-based interface for managing multiple devices, executing automation scripts, and monitoring real-time logs.

## Features

- **Multi-Device Management**: Connect and control multiple Android devices simultaneously
- **Web-Based UI**: React 19 + Vite interface for managing devices and scripts
- **Live Screen Streaming**: Real-time H.264 video streaming via SignalR WebSocket
- **Real-Time Logging**: Live log streaming from running automation scripts
- **Image Recognition**: OpenCvSharp-based template matching for visual automation
- **Script Library**: Extensible C# script system with shared base class
- **Auto-Discovery**: Automatic detection and registration of connected ADB devices

## Tech Stack

### Backend
- **.NET 10** — ASP.NET Core Web API
- **SignalR** — real-time screen streaming and log push
- **EF Core + SQLite** — device and execution persistence
- **AdvancedSharpAdbClient** — ADB device control
- **OpenCvSharp4** — image recognition and template matching
- **Serilog** — structured logging
- **FluentValidation** — request validation
- **OpenAPI** — built-in .NET 9+ spec at `/openapi/v1.json`

### Frontend
- **React 19** + **TypeScript** — UI library
- **Vite** — build tool (outputs to `api/wwwroot/`)
- **TanStack Query** — data fetching and caching
- **@microsoft/signalr** — WebSocket communication
- **JMuxer** — H.264 video playback
- **Tailwind CSS v4** — utility-first styling
- **Axios** — HTTP client

## Prerequisites

- **.NET 10 SDK**
- **Node.js** >= 18 + **npm** >= 10
- **ADB (Android Debug Bridge)** — from Android SDK Platform Tools
- **Android Device/Emulator** — with USB debugging enabled

### ADB Setup

1. Download [Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools)
2. Add ADB to your system PATH
3. Verify: `adb version`
4. Enable USB debugging on device: Settings → About Phone → tap Build Number 7× → Developer Options → USB Debugging

## Project Structure

```
kvtm-auto/
├── KvtmAuto.sln
├── api/                       # ASP.NET Core backend
│   ├── Program.cs
│   ├── KvtmAuto.csproj
│   ├── Core/                  # Shared models, enums, Result<T>
│   ├── Features/              # Vertical slices (Devices, Scripts, Execution)
│   ├── Infrastructure/        # ADB, OpenCV, EF Core DbContext
│   ├── Automation/            # Game automation engine + scripts + assets
│   ├── Hubs/                  # SignalR hubs (ScreenHub, LogHub)
│   └── wwwroot/               # Vite build output (gitignored)
├── web/                       # React + TypeScript frontend
│   └── src/
│       ├── features/          # devices, scripts, execution, stream
│       ├── shared/            # api-client, signalr factory, shared components
│       └── pages/             # HomePage
├── release.sh                 # Build: dotnet publish (auto-builds web/)
├── start.sh                   # Run: starts release/KvtmAuto.dll
└── README.md
```

## Quick Start

### Development

```bash
# Terminal 1 — backend
cd api
dotnet run

# Terminal 2 — frontend
cd web
npm install
npm run dev
```

- Backend API: `http://localhost:5000`
- Frontend dev server: `http://localhost:5173` (proxies `/api` and `/hubs` to backend)

### Production Build

```bash
# Builds web/ and publishes .NET app to release/
./release.sh

# Start the published app
./start.sh
```

The app is served on ports **3000** (HTTP) and **3001** (HTTPS) from `release/`.

## Configuration

Device display names are configured in `api/appsettings.json`:

```json
"DeviceNames": {
  "emulator-5554": "Kai",
  "emulator-5556": "Device 2"
}
```

## API Reference

**Devices**
- `GET /api/devices` — list all devices
- `GET /api/devices/{id}` — device details

**Scripts**
- `GET /api/scripts` — list available scripts

**Execution**
- `POST /api/execute/start` — start script on device(s)
- `POST /api/execute/stop` — stop a specific execution
- `POST /api/execute/stop-all` — stop all running scripts

**SignalR Hubs**
- `/hubs/screen` — H.264 screen stream (`StartStream`, `StopStream`, `ReceiveFrame`)
- `/hubs/log` — real-time log push (`JoinDevice`, `LeaveDevice`, `ReceiveLog`)

**OpenAPI**
- `GET /openapi/v1.json` — OpenAPI spec

## Writing Custom Scripts

Create a new class in `api/Automation/Scripts/` that extends `ScriptBase`:

```csharp
public class MyScript : ScriptBase
{
    public override string Id => "my_script";
    public override string Name => "My Script";

    protected override async Task RunAsync(string deviceId, GameOptions options, CancellationToken ct)
    {
        Log("Starting...");
        await Adb.TapAsync(0.5, 0.5, ct);   // percentage coordinates
        await Adb.SleepAsync(2000, ct);

        if (options.OpenGame)
            await OpenGameAsync(ct);

        Log("Done.");
    }
}
```

Scripts are auto-discovered at startup via reflection.

## Troubleshooting

**Devices not detected** — run `adb devices`, check USB debugging, restart ADB server (`adb kill-server && adb start-server`).

**NuGet restore fails** — use the official source: `dotnet restore --source https://api.nuget.org/v3/index.json`

**OpenCV on Apple Silicon** — requires `OpenCvSharp4.runtime.osx.10.15-universal` (4.7.0), not the x64-only package.

**Live streaming not working** — check SignalR connection in browser DevTools → Network → WS; ensure device supports `screenrecord`.

## License

[Add your license here]
