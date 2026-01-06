---
name: neatoo
description: Neatoo DDD framework for .NET with Blazor WebAssembly. Use when building domain entities with EntityBase, implementing business rules and validation, creating factories with [Factory] attribute, setting up client-server communication with RemoteFactory, working with aggregates and parent-child relationships, or troubleshooting source generator issues.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(dotnet:*), WebFetch, WebSearch
---

# Neatoo Framework Skill

## Description

Neatoo is a Domain-Driven Design (DDD) framework for .NET that simplifies building business applications with Blazor WebAssembly and WPF. It combines two core repositories:

- **Neatoo Core**: DDD framework with entities, rules, validation, and Roslyn source generators
- **Neatoo.RemoteFactory**: Client-server communication layer enabling shared domain models

## When to Use This Skill

Use this skill when:

- Building domain entities with EntityBase or ValidateBase classes
- Implementing business rules and validation logic
- Creating factory classes with [Factory] attribute
- Setting up client-server communication with RemoteFactory
- Working with aggregates and parent-child entity relationships
- Implementing data mapping between domain and persistence entities
- Building Blazor UI components with MudNeatoo
- Configuring authorization for factory operations
- Implementing cancellation support with CancellationToken and IFactoryOnCancelled
- Configuring logging and distributed tracing with CorrelationId
- Optimizing serialization with ordinal format
- Troubleshooting Neatoo source generator issues
- Understanding Neatoo's property system and meta-properties

## Quick Reference

### Essential Attributes

| Attribute | Purpose | Location |
|-----------|---------|----------|
| `[Factory]` | Marks class/record for factory generation | Class/record declaration |
| `[Create]` | Initialize new entity (client-side) | Factory method or record type |
| `[Fetch]` | Load entity from database | Factory method |
| `[Insert]` | Persist new entity | Factory method |
| `[Update]` | Save changes to existing entity | Factory method |
| `[Delete]` | Remove entity from database | Factory method |
| `[Execute]` | Run command/query operations | Factory method |
| `[Remote]` | Method runs on server | Factory method |
| `[Service]` | Inject service into method/record | Method parameter or record parameter |
| `[AuthorizeFactory]` | Define authorization rule | Authorization method |
| `IFactoryOnCancelled` | Cleanup callback on cancellation | Interface on entity |
| `IFactoryOnCancelledAsync` | Async cleanup on cancellation | Interface on entity |

**Note**: C# records (10.1.0+) support `[Create]` on the type declaration for concise Value Objects.

### Class Hierarchy

```
ValidateBase<T>            - INotifyPropertyChanged, property management, validation, rules engine
    EntityBase<T>          - Adds persistence awareness, modification tracking

ValidateListBase<I>        - Observable collection, validation aggregation
    EntityListBase<I>      - Adds DeletedList, persistence
```

### Entity Meta-Properties

| Property | Scope | Description |
|----------|-------|-------------|
| `IsValid` | Aggregate | True when entity AND all children pass validation |
| `IsSelfValid` | Entity only | True when this entity's properties pass validation |
| `IsModified` | Aggregate | True when entity OR any child has changes |
| `IsSelfModified` | Entity only | True when this entity has changes |
| `IsBusy` | Aggregate | True when async operations running on entity or children |
| `IsSelfBusy` | Entity only | True when this entity has async operations |
| `IsNew` | Entity | True when created but not yet persisted |
| `IsDeleted` | Entity | True when Delete() was called |
| `IsSavable` | Entity | `IsModified && IsValid && !IsBusy && !IsChild` |
| `IsChild` | Entity | True when part of parent aggregate |

### Property-Level Meta-Properties

Access via indexer: `entity[nameof(entity.PropertyName)]`

| Property | Description |
|----------|-------------|
| `IsModified` | Property value changed since load/save |
| `IsValid` | Property passes all validation rules |
| `IsBusy` | Async validation running for this property |
| `PropertyMessages` | Validation messages for this property |

### Basic Entity Pattern

```csharp
using System.ComponentModel.DataAnnotations;
using Neatoo;
using Neatoo.RemoteFactory;

namespace MyApp.Domain;

public interface IPerson : IEntityBase
{
    Guid? Id { get; set; }
    string? FirstName { get; set; }
    string? LastName { get; set; }
    string? FullName { get; }
}

[Factory]
internal partial class Person : EntityBase<Person>, IPerson
{
    public Person(IEntityBaseServices<Person> services) : base(services)
    {
        // Add computed property rule
        RuleManager.AddAction(
            (Person p) => p.FullName = $"{p.FirstName} {p.LastName}",
            p => p.FirstName, p => p.LastName);
    }

    public partial Guid? Id { get; set; }

    [Required]
    public partial string? FirstName { get; set; }

    [Required]
    public partial string? LastName { get; set; }

    public partial string? FullName { get; set; }

    [Create]
    public void Create()
    {
        // Initialize new entity
    }
}
```

For database operations (Fetch, Insert, Update, Delete), see the **data-mapping.md** reference file.

### Record Value Objects (10.1.0+)

Records provide concise Value Object definitions:

```csharp
// Basic record with type-level [Create]
[Factory]
[Create]
public record Money(decimal Amount, string Currency = "USD");

// Usage
var price = moneyFactory.Create(99.99m, "USD");
```

```csharp
// Record with service injection
[Factory]
[Create]
public record Address(
    string Street,
    string City,
    string State,
    string ZipCode,
    [Service] IAddressValidator validator);

// Factory hides [Service] parameters
// IAddressFactory.Create(string street, string city, string state, string zipCode)
```

```csharp
// Record with static [Fetch]
[Factory]
[Create]
public record CustomerSummary(Guid Id, string? Name, string? Email)
{
    [Remote]
    [Fetch]
    public static async Task<CustomerSummary?> Fetch(
        Guid id,
        [Service] IDbContext db)
    {
        var entity = await db.Customers.FindAsync(id);
        return entity is null ? null
            : new CustomerSummary(entity.Id, entity.Name, entity.Email);
    }
}
```

**Constraints**: `record` and `record class` supported; `record struct` NOT supported (NF0206).

### Factory Usage

```csharp
// Create new
var person = personFactory.Create();
person.FirstName = "John";
person.LastName = "Doe";

// Wait for async validation
await person.WaitForTasks();

// Save (routes to Insert for new, Update for existing)
if (person.IsSavable)
{
    person = await personFactory.Save(person);  // ALWAYS reassign!
}

// Fetch existing
var existingPerson = await personFactory.Fetch(id);

// Delete
existingPerson.Delete();
await personFactory.Save(existingPerson);
```

### Critical Pattern: Always Reassign After Save

```csharp
// WRONG - stale reference after save
await personFactory.Save(person);
// person still has old values, wrong ID

// CORRECT - capture new instance
person = await personFactory.Save(person);
// person now has server-generated values
```

### Data Loading Pattern

In factory methods, **rules are paused** - use property setters directly. See **data-mapping.md** for full CRUD examples and infrastructure setup.

```csharp
[Remote]
[Fetch]
public async Task<bool> Fetch([Service] IDbContext db)
{
    var entity = await db.Persons.FindAsync(Id);
    if (entity == null) return false;

    // Rules are paused in factory methods - property setters work directly
    Id = entity.Id;
    FirstName = entity.FirstName;
    LastName = entity.LastName;
    return true;
}
```

### Client-Server Setup

**Required NuGet Packages:**
- **Domain project**: `Neatoo`, `Neatoo.RemoteFactory`
- **Server project**: `Neatoo.RemoteFactory.AspNetCore` (+ reference to Domain project)
- **Client project**: Reference to Domain project (gets Neatoo packages transitively)

**Server (Program.cs):**
```csharp
using Neatoo;
using Neatoo.RemoteFactory;
using Neatoo.RemoteFactory.AspNetCore;
using MyApp.Domain;  // Import your domain namespace

var builder = WebApplication.CreateBuilder(args);

// Both calls are required - use a public type (like interface) to get assembly
builder.Services.AddNeatooServices(NeatooFactory.Server, typeof(IPerson).Assembly);
builder.Services.AddNeatooAspNetCore(typeof(IPerson).Assembly);

var app = builder.Build();

app.UseNeatoo();  // Maps /api/neatoo with cancellation support

app.Run();
```

**Client (Program.cs):**
```csharp
using Neatoo;
using Neatoo.RemoteFactory;
using MyApp.Domain;  // Import your domain namespace

builder.Services.AddNeatooServices(NeatooFactory.Remote, typeof(IPerson).Assembly);

builder.Services.AddKeyedScoped(RemoteFactoryServices.HttpClientKey, (sp, key) =>
    new HttpClient { BaseAddress = new Uri(builder.HostEnvironment.BaseAddress) });
```

**Note**: Use a public type (like the interface `IPerson`) to get the assembly reference. The entity class is typically `internal`.

## Supporting Reference Files

This skill includes detailed reference documentation:

- **entities.md** - EntityBase, ValidateBase classes, Value Objects
- **aggregates.md** - Aggregate roots, entity graphs, parent-child propagation
- **rules.md** - Rules engine, validation attributes, custom rules
- **factories.md** - Factory operations, Commands & Queries pattern
- **client-server.md** - RemoteFactory, serialization, logging, CorrelationId
- **properties.md** - Meta-properties, INotifyPropertyChanged, dirty tracking
- **blazor-integration.md** - MudNeatoo components, binding patterns
- **source-generators.md** - What gets generated, marker attributes
- **data-mapping.md** - Factory methods (rules paused), IsModified patterns
- **authorization.md** - AuthorizeFactory, role-based access
- **migration.md** - Version migration guides (10.4.0: Base layer collapse)

## Common Pitfalls

1. **Forgetting to reassign after Save()** - Server returns new instance
2. **Not waiting for async rules** - Call `await entity.WaitForTasks()` before checking validity
3. **Saving child entities directly** - Children save through parent aggregate
4. **Missing [Remote] attribute** - Server methods need [Remote]
5. **Not handling null from Fetch** - Fetch returns null/false when not found
6. **Checking IsValid instead of IsSavable** - IsSavable includes all necessary checks
7. **Overusing LoadProperty** - Cascading rules are a feature; LoadProperty only for circular references
8. **Missing namespace declaration** - Entities without a namespace generate into `MissingNamespace`
9. **Missing using for validation attributes** - `[Required]` needs `using System.ComponentModel.DataAnnotations;`

## Repository References

| Repository | Purpose |
|------------|---------|
| [NeatooDotNet/Neatoo](https://github.com/NeatooDotNet/Neatoo) | Core DDD framework |
| [NeatooDotNet/RemoteFactory](https://github.com/NeatooDotNet/RemoteFactory) | Client-server communication |
| [NeatooDotNet/neatoodotnet.github.io](https://github.com/NeatooDotNet/neatoodotnet.github.io) | Documentation site |

## Skill Sync Status

| Repository | Last Synced Commit | Date |
|------------|-------------------|------|
| Neatoo | v10.6.0 (RemoteFactory Upgrade) | 2026-01-05 |
| RemoteFactory | v10.5.0 (CancellationToken) | 2026-01-05 |
