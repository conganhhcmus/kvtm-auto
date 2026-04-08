using Microsoft.AspNetCore.Mvc;

namespace KvtmAuto.Features.Devices;

[ApiController]
[Route("api/devices")]
public class DevicesController(DeviceManager deviceManager) : ControllerBase
{
    [HttpGet]
    public IActionResult GetDevices() =>
        Ok(deviceManager.Devices);

    [HttpGet("{id}")]
    public IActionResult GetDevice(string id)
    {
        var device = deviceManager.GetDevice(id);
        return device is null ? NotFound() : Ok(device);
    }
}
