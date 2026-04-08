using Microsoft.AspNetCore.Mvc;

namespace KvtmAuto.Features.Scripts;

[ApiController]
[Route("api/scripts")]
public class ScriptsController(ScriptManager scriptManager) : ControllerBase
{
    [HttpGet]
    public IActionResult GetScripts() =>
        Ok(scriptManager.Scripts);

    [HttpGet("{id}")]
    public IActionResult GetScript(string id)
    {
        var script = scriptManager.GetScript(id);
        return script is null ? NotFound() : Ok(script);
    }
}
