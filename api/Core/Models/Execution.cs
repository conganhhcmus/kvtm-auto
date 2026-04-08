using System.ComponentModel.DataAnnotations;

namespace KvtmAuto.Core.Models;

public enum ExecutionStatus
{
    Running,
    Stopped,
    Completed,
    Failed
}

public class Execution
{
    [Key]
    public int Id { get; set; }
    public string DeviceId { get; set; } = string.Empty;
    public string ScriptId { get; set; } = string.Empty;
    public ExecutionStatus Status { get; set; } = ExecutionStatus.Running;
    public DateTime StartedAt { get; set; } = DateTime.UtcNow;
    public DateTime? EndedAt { get; set; }
    public GameOptions? Options { get; set; }

    public Device? Device { get; set; }
}
