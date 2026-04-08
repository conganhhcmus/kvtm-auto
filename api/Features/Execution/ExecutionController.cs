using KvtmAuto.Core.Models;
using Microsoft.AspNetCore.Mvc;

namespace KvtmAuto.Features.Execution;

public record StartRequest(string DeviceId, string ScriptId, GameOptions Options);
public record StopRequest(string DeviceId);

[ApiController]
[Route("api/execute")]
public class ExecutionController(ExecutionManager executionManager) : ControllerBase
{
    [HttpPost("start")]
    public async Task<IActionResult> Start([FromBody] StartRequest req)
    {
        try
        {
            await executionManager.StartAsync(req.DeviceId, req.ScriptId, req.Options);
            return Accepted();
        }
        catch (InvalidOperationException ex)
        {
            return Problem(ex.Message, statusCode: 400);
        }
    }

    [HttpPost("stop")]
    public async Task<IActionResult> Stop([FromBody] StopRequest req)
    {
        try
        {
            await executionManager.StopAsync(req.DeviceId);
            return Ok(new { status = "stopped" });
        }
        catch (InvalidOperationException ex)
        {
            return Problem(ex.Message, statusCode: 400);
        }
    }

    [HttpPost("stop-all")]
    public async Task<IActionResult> StopAll()
    {
        await executionManager.StopAllAsync();
        return Ok(new { status = "stopped" });
    }
}
