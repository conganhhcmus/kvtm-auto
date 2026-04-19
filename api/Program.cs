using System.Text.Json;
using System.Text.Json.Serialization;
using KvtmAuto.Features.Devices;
using KvtmAuto.Features.Execution;
using KvtmAuto.Features.Scripts;
using KvtmAuto.Hubs;
using KvtmAuto.Infrastructure.Database;
using KvtmAuto.Infrastructure.Services;
using Microsoft.EntityFrameworkCore;
using Serilog;

Log.Logger = new LoggerConfiguration()
    .WriteTo.Console()
    .CreateBootstrapLogger();

// Ensure enough thread pool threads for both script tasks and HTTP request handling
ThreadPool.GetMinThreads(out int workerThreads, out int completionThreads);
ThreadPool.SetMinThreads(Math.Max(workerThreads, 32), completionThreads);

var builder = WebApplication.CreateBuilder(args);

builder.Host.UseSerilog((ctx, cfg) => cfg.ReadFrom.Configuration(ctx.Configuration));

// Database
builder.Services.AddDbContext<AppDbContext>(opt =>
    opt.UseSqlite(builder.Configuration.GetConnectionString("Default") ?? "Data Source=data/kvtm.db"));

// Infrastructure services
builder.Services.AddSingleton<AdbController>();
builder.Services.AddSingleton<ImageMatcher>();

// Feature services
builder.Services.AddHostedService<DeviceManager>();
builder.Services.AddSingleton<DeviceManager>(sp =>
    (DeviceManager)sp.GetServices<IHostedService>().First(s => s is DeviceManager));
builder.Services.AddSingleton<ScriptManager>();
builder.Services.AddSingleton<ExecutionManager>();

// Controllers + JSON
builder.Services.AddControllers().AddJsonOptions(opt =>
{
    opt.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower;
    opt.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter(JsonNamingPolicy.SnakeCaseLower));
});

// SignalR
builder.Services.AddSignalR();

// OpenAPI
builder.Services.AddOpenApi();

// Problem Details (RFC 7807)
builder.Services.AddProblemDetails();

var app = builder.Build();

// Ensure DB schema exists
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.EnsureCreated();
}

// OpenAPI endpoint
app.MapOpenApi();

// Static files (Vite build output)
app.UseDefaultFiles();
app.UseStaticFiles();

app.MapControllers();
app.MapHub<ScreenHub>("/hubs/screen");
app.MapHub<LogHub>("/hubs/logs");

// Fallback to index.html for SPA routing
app.MapFallbackToFile("index.html");

app.Run();
