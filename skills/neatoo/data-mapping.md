# Neatoo Data Mapping Reference

## Overview

Data mapping in Neatoo transfers property values between domain entities and persistence entities. This is done through explicit property assignments in factory methods, giving you full control over data flow between rich domain objects and flat EF Core database entities.

## Key Methods

| Method | Purpose | When to Use |
|--------|---------|-------------|
| Property setter | Set data directly | Factory methods, rules (cascading is a feature) |
| `LoadProperty()` | Set without triggering rules | Rare: circular reference prevention only |
| `this[propName].IsModified` | Check if property changed | In `[Update]` methods |
| `ModifiedProperties` | List of all changed properties | Audit, debugging |

## Factory Methods - Rules Are Paused

In factory methods (`[Create]`, `[Fetch]`, `[Insert]`, `[Update]`, `[Delete]`), **rules are paused**. Use property setters directly - no special handling needed.

### Example

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
    Email = entity.Email;

    return true;
}
```

## Property Setters in Rules - Cascading is a Feature

**Cascading rule execution is a key Neatoo feature.** When a rule sets a property, dependent rules run automatically - this is the expected behavior.

### Example - Cascading Rules

```csharp
public class OrderTotalRule : RuleBase<IOrder>
{
    public override IRuleMessages Execute(IOrder target)
    {
        var total = target.Lines?.Sum(l => l.Quantity * l.UnitPrice) ?? 0;

        // Property setter triggers any rules that depend on Total - this is correct!
        target.Total = total;

        return None;
    }
}
```

If `Total` has dependent rules (e.g., discount calculation), they run automatically.

## LoadProperty() - Rare Use Cases

Use `LoadProperty()` only in **rare situations** where you need to prevent cascading:

1. **Circular reference prevention** - Rule A triggers Rule B which triggers Rule A
2. **Private interface getters** - When the getter is private, prefer `SetValue` instead

### Signature

```csharp
protected void LoadProperty(string propertyName, object? value)
```

### Circular Reference Example

```csharp
// Only use LoadProperty when you need to break a circular reference
public class RuleA : RuleBase<IOrder>
{
    public override IRuleMessages Execute(IOrder target)
    {
        // This would normally trigger RuleB, which triggers RuleA...
        // Use LoadProperty ONLY to break the cycle
        LoadProperty(nameof(target.InternalValue), calculated);

        return None;
    }
}
```

## Insert Operations

In `[Insert]` methods, copy ALL properties to the new persistence entity.

```csharp
[Remote]
[Insert]
public async Task Insert([Service] IDbContext db)
{
    Id = Guid.NewGuid();  // Generate ID
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

### With Child Collections

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

## Update Operations

In `[Update]` methods, copy only MODIFIED properties for efficiency.

### Checking Modification State

```csharp
// Check individual property
if (this[nameof(Email)].IsModified)
{
    entity.Email = Email;
}

// List all modified properties
foreach (var propName in ModifiedProperties)
{
    Console.WriteLine($"Changed: {propName}");
}
```

### Update Pattern

```csharp
[Remote]
[Update]
public async Task Update([Service] IDbContext db)
{
    var entity = await db.Persons.FindAsync(Id);

    if (entity == null)
        throw new InvalidOperationException($"Person {Id} not found");

    // Copy only MODIFIED properties
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

### Why Only Modified Properties?

1. **Efficient Updates**: Smaller UPDATE SQL statements
2. **Fewer Conflicts**: Less chance of overwriting concurrent changes
3. **Audit Clarity**: Easy to see exactly what changed
4. **Performance**: Less data transferred

## Type Conversions

Handle type differences between domain and persistence explicitly:

```csharp
// Domain entity has enum
public partial PersonStatus Status { get; set; }

// Persistence entity has string
// In Fetch (rules paused - use property setter):
Status = Enum.Parse<PersonStatus>(entity.Status);

// In Insert/Update:
entity.Status = Status.ToString();
```

## Nullable Properties

```csharp
// Fetch - null values work fine (rules paused)
MiddleName = entity.MiddleName;  // Can be null

// Update - check modification
if (this[nameof(MiddleName)].IsModified)
    entity.MiddleName = MiddleName;  // Can set to null
```

## Computed Properties

Computed properties are calculated by rules, not persisted:

```csharp
// Computed property - set by a rule
public partial string? FullName { get; set; }

// Constructor sets up the rule
public Person(IEntityBaseServices<Person> services) : base(services)
{
    RuleManager.AddAction(
        (Person p) => p.FullName = $"{p.FirstName} {p.LastName}",
        p => p.FirstName, p => p.LastName);
}

// In Fetch - DON'T load FullName, let the rule calculate it
// After loading FirstName and LastName, the rule runs automatically
```

## Child Collections

Child entities are handled through their factories:

### Loading Children

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

    // Rules are paused in factory methods - property setters work directly
    Id = entity.Id;
    FirstName = entity.FirstName;
    // ... other properties

    // Child collection loaded by its factory
    PersonPhoneList = phoneListFactory.Fetch(entity.Phones);

    return true;
}
```

### Child Collection Fetch

```csharp
using Neatoo;
using Neatoo.RemoteFactory;

[Factory]
internal partial class PersonPhoneList
    : EntityListBase<IPersonPhone>, IPersonPhoneList
{
    private readonly IPersonPhoneFactory _phoneFactory;

    public PersonPhoneList(IPersonPhoneFactory phoneFactory) : base()
    {
        _phoneFactory = phoneFactory;
    }

    [Fetch]
    public void Fetch(IEnumerable<PersonPhoneEntity> entities)
    {
        foreach (var entity in entities)
        {
            var phone = _phoneFactory.Fetch(entity);
            Add(phone);
        }
    }
}
```

### Saving Children

```csharp
[Remote]
[Update]
public async Task Update(
    Guid parentId,
    [Service] IDbContext db)
{
    // Process deletions first
    foreach (var deleted in DeletedList.Cast<IPersonPhone>())
    {
        var entity = await db.PersonPhones.FindAsync(deleted.Id);
        if (entity != null)
            db.PersonPhones.Remove(entity);
    }

    // Process remaining items
    foreach (var phone in this)
    {
        if (phone.IsNew)
        {
            // Insert
            phone.Id = Guid.NewGuid();
            var entity = new PersonPhoneEntity { PersonId = parentId };
            entity.PhoneNumber = phone.PhoneNumber;
            entity.PhoneType = phone.PhoneType;
            db.PersonPhones.Add(entity);
        }
        else if (phone.IsModified)
        {
            // Update
            var entity = await db.PersonPhones.FindAsync(phone.Id);
            if (phone[nameof(phone.PhoneNumber)].IsModified)
                entity.PhoneNumber = phone.PhoneNumber;
            if (phone[nameof(phone.PhoneType)].IsModified)
                entity.PhoneType = phone.PhoneType;
        }
    }

    await db.SaveChangesAsync();
}
```

## Concurrency Handling

For optimistic concurrency with row versions:

```csharp
// Domain entity
public partial byte[]? RowVersion { get; set; }

// In Fetch (rules paused - use property setter)
RowVersion = entity.RowVersion;

// In Update
[Remote]
[Update]
public async Task Update([Service] IDbContext db)
{
    var entity = await db.Persons.FindAsync(Id);

    // Set original row version for concurrency check
    db.Entry(entity).Property(e => e.RowVersion).OriginalValue = RowVersion;

    // Update properties...

    try
    {
        await db.SaveChangesAsync();
        // Capture new row version (rules still paused)
        RowVersion = entity.RowVersion;
    }
    catch (DbUpdateConcurrencyException)
    {
        throw new ConcurrencyException("Record was modified by another user");
    }
}
```

## Complete Entity Example

```csharp
using Neatoo;
using Neatoo.RemoteFactory;

[Factory]
internal partial class Person : EntityBase<Person>, IPerson
{
    public Person(IEntityBaseServices<Person> services) : base(services)
    {
        RuleManager.AddAction(
            (Person p) => p.FullName = $"{p.FirstName} {p.LastName}",
            p => p.FirstName, p => p.LastName);
    }

    public partial Guid? Id { get; set; }
    public partial string? FirstName { get; set; }
    public partial string? LastName { get; set; }
    public partial string? Email { get; set; }
    public partial string? FullName { get; set; }  // Computed
    public partial DateTime CreatedDate { get; set; }
    public partial DateTime? ModifiedDate { get; set; }
    public partial byte[]? RowVersion { get; set; }
    public partial IPersonPhoneList? Phones { get; set; }

    [Create]
    public void Create([Service] IPersonPhoneListFactory phoneFactory)
    {
        Phones = phoneFactory.Create();
        CreatedDate = DateTime.UtcNow;
    }

    [Remote]
    [Fetch]
    public async Task<bool> Fetch(
        [Service] IDbContext db,
        [Service] IPersonPhoneListFactory phoneFactory)
    {
        var entity = await db.Persons
            .Include(p => p.Phones)
            .FirstOrDefaultAsync(p => p.Id == Id);

        if (entity == null) return false;

        // Rules are paused in factory methods - property setters work directly
        Id = entity.Id;
        FirstName = entity.FirstName;
        LastName = entity.LastName;
        Email = entity.Email;
        CreatedDate = entity.CreatedDate;
        ModifiedDate = entity.ModifiedDate;
        RowVersion = entity.RowVersion;

        Phones = phoneFactory.Fetch(entity.Phones);
        return true;
    }

    [Remote]
    [Insert]
    public async Task Insert(
        [Service] IDbContext db,
        [Service] IPersonPhoneListFactory phoneFactory)
    {
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
        await ((PersonPhoneList)Phones).SaveInternal(Id.Value, db);
        await db.SaveChangesAsync();

        RowVersion = entity.RowVersion;
    }

    [Remote]
    [Update]
    public async Task Update(
        [Service] IDbContext db,
        [Service] IPersonPhoneListFactory phoneFactory)
    {
        ModifiedDate = DateTime.UtcNow;

        var entity = await db.Persons.FindAsync(Id);
        db.Entry(entity).Property(e => e.RowVersion).OriginalValue = RowVersion;

        if (this[nameof(FirstName)].IsModified)
            entity.FirstName = FirstName;
        if (this[nameof(LastName)].IsModified)
            entity.LastName = LastName;
        if (this[nameof(Email)].IsModified)
            entity.Email = Email;

        entity.ModifiedDate = ModifiedDate;

        await ((PersonPhoneList)Phones).SaveInternal(Id.Value, db);
        await db.SaveChangesAsync();

        RowVersion = entity.RowVersion;
    }

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
}
```

## Best Practices

1. **Use property setters in factory methods** - Rules are paused, no special handling needed
2. **Check IsModified in Update** - Only write changed properties for efficiency
3. **Use nameof()** - Avoid string literals for property names
4. **Handle nulls explicitly** - Database nulls need appropriate handling
5. **Load children through factories** - Don't manually manage child collections
6. **Use AsNoTracking()** - When you don't need EF change tracking in Fetch

## Common Pitfalls

1. **Not checking IsModified** - Unnecessary database updates
2. **Wrong property names** - Silent failures (use nameof)
3. **Forgetting child collections** - Data lost on save
4. **Not handling concurrency** - Lost updates in multi-user scenarios
5. **Overusing LoadProperty** - Use property setters in rules; cascading is a feature
