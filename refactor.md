# Refactor Plan: C# + React Best Practices

## Context

KVTM Auto is a .NET 10 + React 19 monorepo for Android device automation. The current structure works but has several issues: services directly consume DbContext, no validation layer, frontend state is crammed into one App.tsx, and there is no Domain/Application separation. This refactor adopts Clean Architecture on the backend and a feature-based folder structure on the frontend.

---

## Top-Level Layout

```
kvtm-auto/
├── KvtmAuto.sln               ← Solution file
├── api/                       ← ASP.NET Core backend
├── web/                       ← React + TypeScript frontend
├── docs/                      ← Documentation, diagrams
├── release.sh                 ← Build: npm build + dotnet publish → release/
├── start.sh                   ← Run: starts the published release/
└── README.md
```

- `release.sh` — runs `dotnet publish` (which auto-builds `web/` via csproj `BuildClient` target)
- `start.sh` — runs `release/KvtmAuto.dll` on ports 3000/3001
- `web/` build outputs to `api/wwwroot/` so the .NET app serves the SPA

---

## Backend Structure (`api/`)

Vertical Slice Architecture — each feature owns its Controller, Service, Repository, and DTO. No cross-feature dependencies except through `Core/` and `Infrastructure/`.

```
api/
├── Program.cs
├── appsettings.json
├── KvtmAuto.csproj
│
├── Core/                      # Shared primitives — no framework references
│   ├── Models/
│   │   ├── Device.cs
│   │   └── Execution.cs
│   ├── Enums/
│   │   ├── DeviceStatus.cs
│   │   └── ExecutionStatus.cs
│   └── Result.cs              # Result<T> pattern
│
├── Features/                  # Vertical slices — Controller + Service + Repo + DTO per feature
│   ├── Devices/
│   │   ├── DevicesController.cs
│   │   ├── DeviceService.cs
│   │   ├── DeviceRepository.cs
│   │   └── DeviceDto.cs
│   │
│   ├── Scripts/
│   │   ├── ScriptsController.cs
│   │   ├── ScriptService.cs
│   │   └── ScriptDto.cs
│   │
│   └── Execution/
│       ├── ExecutionController.cs
│       ├── ExecutionService.cs
│       ├── ExecutionRepository.cs
│       └── ExecutionDto.cs
│
├── Infrastructure/            # Technical concerns — ADB, CV, EF Core
│   ├── Database/
│   │   └── AppDbContext.cs
│   └── Services/
│       ├── AdbController.cs
│       └── ImageMatcher.cs
│
├── Automation/                # Game automation engine — self-contained
│   ├── Engine/
│   │   ├── ScriptBase.cs
│   │   └── ScriptManager.cs
│   ├── Scripts/
│   │   └── *.cs
│   └── Assets/                # Game image templates (published as assets/ via <Link> in csproj)
│       ├── *.png
│       ├── cay/
│       └── vat-pham/
│
├── Hubs/                      # SignalR real-time
│   ├── ScreenHub.cs
│   └── LogHub.cs
│
└── wwwroot/                   # Vite build output (gitignored)
```

### Key Backend Changes

**1. Result\<T\> pattern** — no exceptions for business logic flow
```csharp
// Core/Result.cs
public record Result<T>(T? Value, string? Error, bool IsSuccess)
{
    public static Result<T> Ok(T value) => new(value, null, true);
    public static Result<T> Fail(string error) => new(default, error, false);
}
```

**2. Options pattern** — device name mapping moves to config
```json
// appsettings.json
"DeviceNames": {
  "emulator-5554": "Kai",
  "emulator-5556": "Device 2"
}
```
```csharp
// Program.cs
builder.Services.Configure<DeviceNameOptions>(builder.Configuration.GetSection("DeviceNames"));
```

**3. Problem Details** — RFC 7807 error responses
```csharp
// Program.cs
builder.Services.AddProblemDetails();
// Controllers: return Problem("message") instead of BadRequest(new { error = "..." })
```

**4. FluentValidation** — request validation per feature
```csharp
// Features/Execution/ExecutionController.cs
public class StartExecutionRequestValidator : AbstractValidator<StartExecutionRequest>
{
    public StartExecutionRequestValidator()
    {
        RuleFor(x => x.DeviceId).NotEmpty();
        RuleFor(x => x.ScriptId).NotEmpty();
    }
}
```

**5. OpenAPI** — built-in .NET 9+
```csharp
builder.Services.AddOpenApi();
app.MapOpenApi(); // → /openapi/v1.json
```

**6. csproj build hook** — auto-build frontend on publish
```xml
<Target Name="BuildClient" BeforeTargets="Publish">
  <Exec WorkingDirectory="../web" Command="npm run build" />
</Target>
```

---

## Frontend Structure (`web/`)

```
web/src/
├── main.tsx
├── App.tsx                    # Providers + routing only
│
├── features/
│   ├── devices/
│   │   ├── api.ts             # Device API calls
│   │   ├── hooks.ts           # useDevices, useDevice
│   │   ├── types.ts           # Device, DeviceStatus
│   │   └── components/
│   │       ├── DeviceCard.tsx
│   │       ├── DeviceDetailModal.tsx
│   │       └── DeviceLogModal.tsx
│   │
│   ├── scripts/
│   │   ├── api.ts
│   │   ├── hooks.ts           # useScripts
│   │   ├── types.ts
│   │   └── components/
│   │       └── ScriptSelect.tsx
│   │
│   ├── execution/
│   │   ├── api.ts
│   │   ├── hooks.ts           # useStartExecution, useStopExecution
│   │   ├── types.ts           # GameOptions, ExecutionRequest
│   │   └── components/
│   │       └── ControlPanel.tsx
│   │
│   └── stream/
│       ├── hooks/
│       │   ├── useScreenStream.ts   # ScreenHub + JMuxer
│       │   └── useDeviceLogs.ts     # LogHub
│       └── components/
│           └── LiveScreenModal.tsx
│
├── shared/
│   ├── components/
│   │   ├── Modal.tsx
│   │   ├── MultiSelect.tsx
│   │   └── SearchableSelect.tsx
│   ├── lib/
│   │   ├── api-client.ts      # Axios instance with interceptors
│   │   └── signalr.ts         # SignalR connection factory
│   └── types/
│       └── common.ts
│
└── pages/
    └── HomePage.tsx           # Composes features — replaces monolithic App.tsx
```

### Key Frontend Changes

**1. Centralized Axios instance**
```typescript
// shared/lib/api-client.ts
const apiClient = axios.create({ baseURL: '/api' });
apiClient.interceptors.response.use(
  r => r,
  e => Promise.reject(e.response?.data?.detail ?? e.message)
);
```

**2. Feature-scoped query hooks**
```typescript
// features/devices/hooks.ts
export function useDevices() {
  return useQuery({ queryKey: ['devices'], queryFn: deviceApi.getDevices, refetchInterval: 5000 });
}
```

**3. SignalR as custom hooks**
```typescript
// features/stream/hooks/useDeviceLogs.ts
export function useDeviceLogs(deviceId: string) {
  const [logs, setLogs] = useState<string[]>([]);
  useEffect(() => { /* setup LogHub, subscribe, return cleanup */ }, [deviceId]);
  return logs;
}
```

**4. vite.config.ts — build output**
```ts
build: { outDir: '../api/wwwroot', emptyOutDir: true }
```

---

## What NOT to Change

| Area                             | Reason                                 |
| -------------------------------- | -------------------------------------- |
| SignalR hubs (ScreenHub, LogHub) | Well-implemented, no structural issues |
| ScriptBase + Impl scripts        | Internal only, already well-structured |
| AdbController internals          | Working; only extract interface        |
| EF Core snake_case config        | Correct and clean                      |
| Tailwind CSS v4 setup            | Already following best practices       |
| Thread pool + Lock usage         | Correct for this workload              |

---

## Implementation Order

### Phase 1 — Structural migration
1. Move `src/KvtmAuto.Web/` → `api/`, rename `KvtmAuto.Web.csproj` → `KvtmAuto.csproj`
2. Move `client/` → `web/`, update `vite.config.ts` output path to `../api/wwwroot`
3. Update `.sln` project reference to `api/KvtmAuto.csproj`
4. Update `release.sh` — point to `api/KvtmAuto.csproj`
5. Update `start.sh` — change `KvtmAuto.Web.dll` → `KvtmAuto.dll`
6. Verify `dotnet build` + `npm run build` still work

### Phase 2 — Backend refactor
7. Create `Core/` — move models, enums; add `Result.cs`
8. Reorganize into `Features/Devices/`, `Features/Scripts/`, `Features/Execution/`
9. Move `AppDbContext.cs` → `Infrastructure/Database/`
10. Move `AdbController`, `ImageMatcher` → `Infrastructure/Services/`
11. Move automation code → `Automation/` (Engine, Scripts, Assets)
12. Move device name map to `appsettings.json` + Options pattern
13. Add FluentValidation + Problem Details
14. Add OpenAPI + `.csproj` publish hook for `web/`

### Phase 3 — Frontend refactor
15. Create `web/src/features/` folder structure
16. Split `App.tsx` → `pages/HomePage.tsx` + feature components
17. Create `shared/lib/api-client.ts` (Axios instance with interceptors)
18. Extract SignalR into `useDeviceLogs` + `useScreenStream` hooks
19. Move shared components to `shared/components/`

---

## Verification Checklist

- [ ] `dotnet build` — 0 errors, 0 warnings
- [ ] `npm run build` in `web/` — builds to `api/wwwroot/`
- [ ] `./release.sh` — builds and publishes to `release/`
- [ ] `./start.sh` — app starts and serves SPA
- [ ] `GET /api/devices` — returns device list
- [ ] `GET /api/scripts` — returns script list
- [ ] `POST /api/execute/start` — starts script on device
- [ ] `POST /api/execute/start` with missing fields — returns Problem Details (400)
- [ ] DeviceLogModal — SignalR connects, logs stream in real time
- [ ] LiveScreenModal — H.264 stream plays
- [ ] `GET /openapi/v1.json` — OpenAPI spec accessible
