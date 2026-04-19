using System.Text.Json;
using KvtmAuto.Core.Models;
using Microsoft.EntityFrameworkCore;

namespace KvtmAuto.Infrastructure.Database;

public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<Device> Devices => Set<Device>();
    public DbSet<Execution> Executions => Set<Execution>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Execution>()
            .Property(e => e.Options)
            .HasConversion(
                v => JsonSerializer.Serialize(v, JsonSerializerOptions.Default),
                v => JsonSerializer.Deserialize<GameOptions>(v, JsonSerializerOptions.Default));
    }
}
