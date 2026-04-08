using System.ComponentModel.DataAnnotations;

namespace KvtmAuto.Core.Models;

public enum DeviceStatus
{
    Online,
    Offline,
    Busy
}

public class Device
{
    [Key]
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public DeviceStatus Status { get; set; } = DeviceStatus.Offline;
    public string? CurrentScriptId { get; set; }
    public DateTime? LastSeen { get; set; }

    public ICollection<Execution> Executions { get; set; } = [];
}
