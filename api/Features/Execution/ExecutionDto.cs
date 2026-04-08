namespace KvtmAuto.Features.Execution;

public record ExecutionDto(
    int Id,
    string DeviceId,
    string ScriptId,
    string Status,
    DateTime StartedAt,
    DateTime? EndedAt
);
