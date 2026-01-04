# Neatoo Factory Operations Reference

## Overview

The `[Factory]` attribute marks classes for factory generation. Neatoo's source generator creates factory interfaces and implementations that handle object creation, persistence, and client-server communication.

## Factory Attributes

| Attribute | Purpose | Location | Execution |
|-----------|---------|----------|-----------|
| `[Factory]` | Marks class for factory generation | Class | N/A |
| `[Create]` | Initialize new entity | Method | Client-side |
| `[Fetch]` | Load entity from database | Method | Server-side |
| `[Insert]` | Persist new entity | Method | Server-side |
| `[Update]` | Save changes to existing entity | Method | Server-side |
| `[Delete]` | Remove entity from database | Method | Server-side |
| `[Execute]` | Run command/query operations | Method | Server-side |
| `[Remote]` | Method runs on server | Method | Server-side |
| `[Service]` | Inject service into method | Parameter | Both |

## Generated Factory Interface

For this entity:

```csharp
[Factory]
internal partial class Person : EntityBase<Person>, IPerson
{
    [Create]
    public void Create() { }

    [Remote]
    [Fetch]
    public async Task<bool> Fetch([Service] IDbContext db) { }

    [Remote]
    [Insert]
    public async Task Insert([Service] IDbContext db) { }

    [Remote]
    [Update]
    public async Task Update([Service] IDbContext db) { }

    [Remote]
    [Delete]
    public async Task Delete([Service] IDbContext db) { }
}
```

Neatoo generates:

```csharp
public interface IPersonFactory
{
    IPerson? Create();
    Task<IPerson?> Fetch(Guid id);
    Task<IPerson?> Save(IPerson target);
    Task<Authorized<IPerson>> TrySave(IPerson target);

    // Authorization methods (if authorization configured)
    Authorized CanCreate();
    Authorized CanFetch();
    Authorized CanSave();
}
```

## [Create] - Initialize New Entity

The `[Create]` method runs **client-side** to initialize a new entity.

```csharp
[Create]
public void Create()
{
    // Initialize default values
    Id = null;  // Will be assigned on Insert
    CreatedDate = DateTime.UtcNow;
    Status = OrderStatus.Draft;

    // Initialize child collections
    Lines = _lineListFactory.Create();
}
```

### Create with Parameters

```csharp
[Create]
public void Create(string customerName, OrderType type)
{
    CustomerName = customerName;
    Type = type;
    OrderDate = DateTime.Today;
    Lines = _lineListFactory.Create();
}
```

Generated factory method:

```csharp
IPerson? Create(string customerName, OrderType type);
```

### Usage

```csharp
var person = personFactory.Create();
// person.IsNew == true
// person.IsModified == false (no changes yet)

person.FirstName = "John";
// person.IsModified == true
```

## Records Support (10.1.0+)

C# records are fully supported by Neatoo's factory pattern.

### Type-Level [Create]

Records with primary constructors can use `[Create]` on the type declaration:

```csharp
[Factory]
[Create]
public record Money(decimal Amount, string Currency = "USD");

// Generated:
public interface IMoneyFactory
{
    Money Create(decimal amount, string currency = "USD");
}
```

### Records with Service Injection

Use `[Service]` in record parameters. Services are injected at creation but hidden from factory interface:

```csharp
[Factory]
[Create]
public record Address(
    string Street,
    string City,
    string State,
    string ZipCode,
    [Service] IAddressValidator validator);

// Generated (services hidden):
public interface IAddressFactory
{
    Address Create(string street, string city, string state, string zipCode);
}
```

### Records with Static [Fetch]

Static `[Fetch]` methods work with records:

```csharp
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

### Records with Validation

For validation, use a static `[Create]` method:

```csharp
[Factory]
public record Money(decimal Amount, string Currency)
{
    [Create]
    public static Money Create(decimal amount, string currency = "USD")
    {
        if (amount < 0)
            throw new ArgumentException("Amount cannot be negative");
        return new Money(amount, currency.ToUpperInvariant());
    }
}
```

### Record Type Constraints

| Type | Supported |
|------|-----------|
| `record` | ✅ Yes |
| `record class` | ✅ Yes |
| `record struct` | ❌ No (diagnostic NF0206) |

## [Fetch] - Load Entity

The `[Fetch]` method runs **server-side** to load an entity from the database.

```csharp
[Remote]
[Fetch]
public async Task<bool> Fetch([Service] IDbContext db)
{
    var entity = await db.Persons.FindAsync(Id);
    if (entity == null) return false;

    // Use LoadProperty to avoid triggering rules
    LoadProperty(nameof(Id), entity.Id);
    LoadProperty(nameof(FirstName), entity.FirstName);
    LoadProperty(nameof(LastName), entity.LastName);
    LoadProperty(nameof(Email), entity.Email);

    return true;
}
```

### Fetch with Parameters

```csharp
[Remote]
[Fetch]
public async Task<bool> Fetch(string email, [Service] IDbContext db)
{
    var entity = await db.Persons
        .FirstOrDefaultAsync(p => p.Email == email);

    if (entity == null) return false;

    LoadProperty(nameof(Id), entity.Id);
    LoadProperty(nameof(FirstName), entity.FirstName);
    // ... other properties

    return true;
}
```

Generated factory method:

```csharp
Task<IPerson?> Fetch(string email);
```

### Fetch with Child Collections

```csharp
[Remote]
[Fetch]
public async Task<bool> Fetch(
    [Service] IDbContext db,
    [Service] IPersonPhoneListFactory phoneListFactory)
{
    var entity = await db.Persons
        .Include(p => p.Phones)
        .FirstOrDefaultAsync(p => p.Id == Id);

    if (entity == null) return false;

    LoadProperty(nameof(Id), entity.Id);
    LoadProperty(nameof(FirstName), entity.FirstName);
    LoadProperty(nameof(LastName), entity.LastName);

    // Child collection loaded by its factory
    PersonPhoneList = await phoneListFactory.Fetch(entity.Phones);

    return true;
}
```

### Usage

```csharp
var person = await personFactory.Fetch(id);
// Returns null if not found
// person.IsNew == false
// person.IsModified == false
```

## [Insert] - Persist New Entity

The `[Insert]` method runs **server-side** to persist a new entity.

```csharp
[Remote]
[Insert]
public async Task Insert([Service] IDbContext db)
{
    // Generate ID if needed
    Id = Guid.NewGuid();
    CreatedDate = DateTime.UtcNow;

    var entity = new PersonEntity
    {
        Id = Id.Value,
        FirstName = FirstName,
        LastName = LastName,
        Email = Email,
        CreatedDate = CreatedDate
    };

    db.Persons.Add(entity);
    await db.SaveChangesAsync();
}
```

### Insert with Child Collections

```csharp
[Remote]
[Insert]
public async Task Insert(
    [Service] IDbContext db,
    [Service] IPersonPhoneListFactory phoneListFactory)
{
    Id = Guid.NewGuid();

    var entity = new PersonEntity
    {
        Id = Id.Value,
        FirstName = FirstName,
        LastName = LastName
    };

    db.Persons.Add(entity);

    // Save children after parent has ID
    await phoneListFactory.Save(PersonPhoneList, Id.Value);

    await db.SaveChangesAsync();
}
```

## [Update] - Save Changes

The `[Update]` method runs **server-side** to persist changes to an existing entity.

```csharp
[Remote]
[Update]
public async Task Update([Service] IDbContext db)
{
    var entity = await db.Persons.FindAsync(Id);

    if (entity == null)
        throw new InvalidOperationException($"Person {Id} not found");

    // Only update modified properties
    if (this[nameof(FirstName)].IsModified)
        entity.FirstName = FirstName;
    if (this[nameof(LastName)].IsModified)
        entity.LastName = LastName;
    if (this[nameof(Email)].IsModified)
        entity.Email = Email;

    entity.ModifiedDate = DateTime.UtcNow;

    await db.SaveChangesAsync();
}
```

### Update with Child Collections

```csharp
[Remote]
[Update]
public async Task Update(
    [Service] IDbContext db,
    [Service] IPersonPhoneListFactory phoneListFactory)
{
    var entity = await db.Persons.FindAsync(Id);

    if (this[nameof(FirstName)].IsModified)
        entity.FirstName = FirstName;
    if (this[nameof(LastName)].IsModified)
        entity.LastName = LastName;

    // Delegate child saves to collection factory
    await phoneListFactory.Save(PersonPhoneList, Id.Value);

    await db.SaveChangesAsync();
}
```

## [Delete] - Remove Entity

The `[Delete]` method runs **server-side** to remove an entity.

```csharp
[Remote]
[Delete]
public async Task Delete([Service] IDbContext db)
{
    var entity = await db.Persons.FindAsync(Id);
    if (entity != null)
    {
        db.Persons.Remove(entity);
        await db.SaveChangesAsync();
    }
}
```

### Soft Delete Pattern

```csharp
[Remote]
[Delete]
public async Task Delete([Service] IDbContext db)
{
    var entity = await db.Persons.FindAsync(Id);
    if (entity != null)
    {
        entity.IsDeleted = true;
        entity.DeletedDate = DateTime.UtcNow;
        await db.SaveChangesAsync();
    }
}
```

### Usage

```csharp
var person = await personFactory.Fetch(id);
person.Delete();
// person.IsDeleted == true

await personFactory.Save(person);
// Calls [Delete] method
```

## Save() Routing

The `Save()` method routes to the appropriate operation based on entity state:

| IsNew | IsDeleted | Operation |
|-------|-----------|-----------|
| true | false | `[Insert]` |
| false | false | `[Update]` |
| any | true | `[Delete]` |

```csharp
// New entity
var person = personFactory.Create();
person.FirstName = "John";
person = await personFactory.Save(person);  // Calls [Insert]

// Existing entity
person.LastName = "Updated";
person = await personFactory.Save(person);  // Calls [Update]

// Delete
person.Delete();
person = await personFactory.Save(person);  // Calls [Delete]
```

## Critical: Always Reassign After Save

**IMPORTANT**: `Save()` returns a new object instance. You must reassign:

```csharp
// WRONG - stale reference
await personFactory.Save(person);
// person still has old values

// CORRECT - capture new instance
person = await personFactory.Save(person);
// person now has server-generated values
```

### Why Reassignment is Required

The save process:
1. Serializes entity to server
2. Server creates new instance from data
3. Server persists and updates (ID, timestamps)
4. Server serializes updated entity back
5. Client deserializes into NEW object
6. `Save()` returns this new instance

Your original variable still points to the old object.

## [Execute] - Commands and Queries

Use `[Execute]` for operations that don't follow the standard CRUD lifecycle.

### Command Pattern

```csharp
[Factory]
internal partial class ChangePasswordCommand : Base<ChangePasswordCommand>, IChangePasswordCommand
{
    public partial Guid UserId { get; set; }
    public partial string? CurrentPassword { get; set; }
    public partial string? NewPassword { get; set; }
    public partial bool Success { get; set; }
    public partial string? ErrorMessage { get; set; }

    [Create]
    public void Create(Guid userId)
    {
        UserId = userId;
    }

    [Remote]
    [Execute]
    public async Task Execute([Service] IUserService userService)
    {
        var result = await userService.ChangePasswordAsync(
            UserId,
            CurrentPassword,
            NewPassword);

        Success = result.Success;
        ErrorMessage = result.ErrorMessage;
    }
}
```

Usage:

```csharp
var command = changePasswordFactory.Create(userId);
command.CurrentPassword = "oldPass";
command.NewPassword = "newPass";

command = await changePasswordFactory.Execute(command);

if (command.Success)
{
    ShowMessage("Password changed");
}
else
{
    ShowError(command.ErrorMessage);
}
```

### Query Pattern

```csharp
[Factory]
internal partial class CustomerSearchQuery
    : Base<CustomerSearchQuery>, ICustomerSearchQuery
{
    public partial string? SearchTerm { get; set; }
    public partial int MaxResults { get; set; }
    public partial IList<CustomerResult>? Results { get; set; }

    [Create]
    public void Create()
    {
        MaxResults = 25;
        Results = new List<CustomerResult>();
    }

    [Remote]
    [Execute]
    public async Task Execute([Service] ICustomerRepository repo)
    {
        var customers = await repo.SearchAsync(SearchTerm, MaxResults);

        Results = customers.Select(c => new CustomerResult
        {
            Id = c.Id,
            Name = c.Name,
            Email = c.Email
        }).ToList();
    }
}
```

## [Service] - Dependency Injection

The `[Service]` attribute injects dependencies into factory methods:

```csharp
[Remote]
[Fetch]
public async Task<bool> Fetch(
    [Service] IDbContext db,
    [Service] IPersonPhoneListFactory phoneListFactory,
    [Service] ILogger<Person> logger)
{
    logger.LogInformation("Fetching person {Id}", Id);

    var entity = await db.Persons.FindAsync(Id);
    // ...
}
```

### Service Resolution

- Services resolve from the DI container
- On server: Full service resolution
- On client: Only client-registered services available
- Method parameters without `[Service]` come from factory call

```csharp
// This signature:
[Fetch]
public async Task<bool> Fetch(
    Guid id,                    // From factory call
    [Service] IDbContext db)    // From DI container

// Generates:
Task<IPerson?> Fetch(Guid id);  // Only non-service params
```

## [Remote] Attribute

The `[Remote]` attribute indicates a method runs on the server:

```csharp
[Remote]
[Fetch]
public async Task<bool> Fetch([Service] IDbContext db)
{
    // This code runs on server, even when called from client
}
```

### When to Use [Remote]

| Method | Needs [Remote]? | Reason |
|--------|-----------------|--------|
| `[Create]` | No | Runs client-side for initialization |
| `[Fetch]` | Yes | Database access on server |
| `[Insert]` | Yes | Database write on server |
| `[Update]` | Yes | Database write on server |
| `[Delete]` | Yes | Database write on server |
| `[Execute]` | Yes | Server-side operations |

### Client-Side Create

```csharp
[Create]  // No [Remote] - runs on client
public void Create()
{
    // Fast, no server round-trip
    Id = null;
    Status = Status.Draft;
}
```

## Collection Factory Methods

Collections typically have `[Fetch]` and `[Update]` methods:

```csharp
[Factory]
internal partial class OrderLineList
    : EntityListBase<IOrderLine>, IOrderLineList
{
    [Fetch]
    public async Task Fetch(
        IEnumerable<OrderLineEntity> entities,
        [Service] IOrderLineFactory lineFactory)
    {
        foreach (var entity in entities)
        {
            var line = await lineFactory.Fetch(entity);
            Add(line);
        }
    }

    [Remote]
    [Update]
    public async Task Update(Guid orderId, [Service] IDbContext db)
    {
        // Process deletions
        foreach (var deleted in DeletedList.Cast<IOrderLine>())
        {
            var entity = await db.OrderLines.FindAsync(deleted.Id);
            if (entity != null)
                db.OrderLines.Remove(entity);
        }

        // Process inserts and updates
        foreach (var line in this)
        {
            if (line.IsNew)
            {
                // Insert...
            }
            else if (line.IsModified)
            {
                // Update...
            }
        }

        await db.SaveChangesAsync();
    }
}
```

## Multiple Factory Methods

You can have multiple methods for each operation:

```csharp
[Factory]
internal partial class Person : EntityBase<Person>, IPerson
{
    // Multiple Create overloads
    [Create]
    public void Create() { }

    [Create]
    public void Create(string email) { Email = email; }

    // Multiple Fetch overloads
    [Remote]
    [Fetch]
    public async Task<bool> Fetch([Service] IDbContext db)
    {
        // Fetch by Id
    }

    [Remote]
    [Fetch]
    public async Task<bool> Fetch(string email, [Service] IDbContext db)
    {
        // Fetch by email
    }
}
```

Generated interface:

```csharp
public interface IPersonFactory
{
    IPerson? Create();
    IPerson? Create(string email);
    Task<IPerson?> Fetch(Guid id);
    Task<IPerson?> Fetch(string email);
}
```

## Error Handling

### Factory Return Values

| Method | Success | Failure |
|--------|---------|---------|
| `Create()` | Entity instance | null (if unauthorized) |
| `Fetch()` | Entity instance | null (not found or unauthorized) |
| `Save()` | Updated entity | null (if unauthorized) or throws |
| `TrySave()` | `Authorized<T>` with value | `Authorized<T>` with message |
| `Execute()` | Updated object | Throws on error |

### TrySave Pattern

```csharp
var result = await personFactory.TrySave(person);

if (result.IsAuthorized)
{
    person = result.Value;
    ShowSuccess("Saved");
}
else
{
    ShowError(result.Message);
}
```

### Exception Handling

```csharp
try
{
    person = await personFactory.Save(person);
}
catch (ConcurrencyException ex)
{
    ShowError("Record was modified by another user");
}
catch (ValidationException ex)
{
    ShowErrors(ex.Errors);
}
catch (Exception ex)
{
    ShowError($"Save failed: {ex.Message}");
}
```

## Best Practices

### Use LoadProperty in Fetch

```csharp
[Fetch]
public async Task<bool> Fetch([Service] IDbContext db)
{
    // CORRECT - no rules triggered
    LoadProperty(nameof(FirstName), entity.FirstName);

    // WRONG - triggers rules and modification tracking
    // FirstName = entity.FirstName;
}
```

### Check IsModified Before Update

```csharp
[Update]
public async Task Update([Service] IDbContext db)
{
    // Only update changed properties
    if (this[nameof(FirstName)].IsModified)
        entity.FirstName = FirstName;
}
```

### Generate IDs on Insert

```csharp
[Insert]
public async Task Insert([Service] IDbContext db)
{
    Id = Guid.NewGuid();  // Generate here, not in Create
}
```

### Handle Concurrency

```csharp
[Update]
public async Task Update([Service] IDbContext db)
{
    var entity = await db.Persons.FindAsync(Id);

    // Set original row version for concurrency check
    db.Entry(entity).Property(e => e.RowVersion)
        .OriginalValue = RowVersion;

    // ... update properties

    try
    {
        await db.SaveChangesAsync();
        LoadProperty(nameof(RowVersion), entity.RowVersion);
    }
    catch (DbUpdateConcurrencyException)
    {
        throw new ConcurrencyException("Record modified by another user");
    }
}
```

## Common Pitfalls

1. **Missing [Remote]** - Server methods need [Remote] attribute
2. **Not reassigning after Save** - `person = await factory.Save(person)`
3. **Using property setters in Fetch** - Use `LoadProperty()` instead
4. **Not processing DeletedList** - Collections need to handle deletions
5. **Missing await** - All factory methods are async
