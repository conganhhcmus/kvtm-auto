namespace KvtmAuto.Core;

public record Result<T>(T? Value, string? Error, bool IsSuccess)
{
    public static Result<T> Ok(T value) => new(value, null, true);
    public static Result<T> Fail(string error) => new(default, error, false);
}

public record Result(string? Error, bool IsSuccess)
{
    public static Result Ok() => new(null, true);
    public static Result Fail(string error) => new(error, false);
}
