namespace KvtmAuto.Features.Devices;

public record DeviceDto(
    string Id,
    string Name,
    string Status,
    string? CurrentScriptId,
    DateTime? LastSeen
);
