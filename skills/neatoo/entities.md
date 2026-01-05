# Neatoo Entities Reference

## Class Hierarchy

Neatoo provides a hierarchy of base classes, each adding capabilities:

```
ValidateBase<T>            - Property management, INotifyPropertyChanged, validation, rules engine
    EntityBase<T>          - Persistence awareness, modification tracking, IsNew/IsDeleted

ValidateListBase<I>        - Observable collection, parent-child, validation aggregation
    EntityListBase<I>      - DeletedList, persistence integration
```

## EntityBase<T> - Full Persistence Support

Use `EntityBase<T>` for domain entities that persist to a database.

### Interface Pattern

```csharp
public interface IPerson : IEntityBase
{
    Guid? Id { get; set; }
    string? FirstName { get; set; }
    string? LastName { get; set; }
    string? Email { get; set; }
    string? FullName { get; }
    IPersonPhoneList? PersonPhoneList { get; }
}
```

### Class Implementation

```csharp
using Neatoo;
using Neatoo.RemoteFactory;

[Factory]
internal partial class Person : EntityBase<Person>, IPerson
{
    private readonly IPersonPhoneListFactory _phoneListFactory;

    public Person(
        IEntityBaseServices<Person> services,
        IPersonPhoneListFactory phoneListFactory) : base(services)
    {
        _phoneListFactory = phoneListFactory;

        // Add computed property rule
        RuleManager.AddAction(
            (Person p) => p.FullName = $"{p.FirstName} {p.LastName}",
            p => p.FirstName, p => p.LastName);
    }

    public partial Guid? Id { get; set; }

    [Required]
    [StringLength(50)]
    public partial string? FirstName { get; set; }

    [Required]
    [StringLength(50)]
    public partial string? LastName { get; set; }

    [EmailAddress]
    public partial string? Email { get; set; }

    public partial string? FullName { get; set; }

    public partial IPersonPhoneList? PersonPhoneList { get; set; }
}
```

### Key Requirements

1. **Class is `partial` and `internal`** - Source generator needs partial; internal for encapsulation
2. **Inherits `EntityBase<T>`** - Where T is the class itself
3. **Implements interface** - Public interface for external code
4. **Constructor accepts services** - Pass `IEntityBaseServices<T>` to base
5. **Properties are `partial`** - Source generator provides implementation

### EntityBase Meta-Properties

| Property | Type | Description |
|----------|------|-------------|
| `IsValid` | bool | Entity AND all children pass validation |
| `IsSelfValid` | bool | This entity's properties pass validation |
| `IsModified` | bool | Entity OR any child has changes |
| `IsSelfModified` | bool | This entity has direct changes |
| `IsBusy` | bool | Async operations running (entity or children) |
| `IsSelfBusy` | bool | Async operations on this entity |
| `IsNew` | bool | Created but not yet persisted |
| `IsDeleted` | bool | Delete() was called |
| `IsSavable` | bool | `IsModified && IsValid && !IsBusy && !IsChild` |
| `IsChild` | bool | Part of parent aggregate |
| `Parent` | IValidateBase? | Immediate parent in object graph |
| `Root` | IValidateBase? | Aggregate root (null if this IS the root) |
| `ModifiedProperties` | IEnumerable<string> | Names of changed properties |
| `PropertyMessages` | IReadOnlyCollection | Validation messages |

### Save Routing

The framework uses entity state to route Save() calls:

| IsNew | IsDeleted | Operation Called |
|-------|-----------|------------------|
| true | false | `[Insert]` |
| false | false | `[Update]` |
| any | true | `[Delete]` |

### Save with Cancellation

Save operations support `CancellationToken` for graceful shutdown or navigation:

```csharp
try
{
    person = await person.Save(cancellationToken);
}
catch (OperationCanceledException)
{
    // Save was cancelled before persistence began
    // Entity remains in its original state
}
```

Note: Cancellation only occurs before the `[Insert]`/`[Update]`/`[Delete]` method executes. Once persistence begins, cancellation is not supported to avoid partial writes.

## ValidateBase<T> - Validation Without Persistence

Use `ValidateBase<T>` for objects that need validation but are not persisted independently.

```csharp
using Neatoo;
using Neatoo.RemoteFactory;

[Factory]
internal partial class SearchCriteria : ValidateBase<SearchCriteria>, ISearchCriteria
{
    public SearchCriteria(IValidateBaseServices<SearchCriteria> services)
        : base(services)
    {
    }

    [Required]
    public partial string? SearchTerm { get; set; }

    [Range(1, 100)]
    public partial int MaxResults { get; set; }

    public partial DateTime? StartDate { get; set; }
    public partial DateTime? EndDate { get; set; }

    [Create]
    public void Create()
    {
        MaxResults = 25;
    }
}
```

### ValidateBase Features

- Validation rules via attributes and RuleManager
- `IsValid`, `IsSelfValid`, `PropertyMessages`
- `IsBusy`, `IsSelfBusy` for async rules
- No persistence tracking (no IsNew, IsModified, IsDeleted)

## Value Objects

Value Objects represent concepts defined by attributes, not identity. Use plain classes with `[Factory]`:

```csharp
using Neatoo.RemoteFactory;

[Factory]
public class Money
{
    public decimal Amount { get; private set; }
    public string Currency { get; private set; } = "USD";

    public Money Add(Money other, IMoneyFactory factory)
    {
        if (Currency != other.Currency)
            throw new InvalidOperationException("Cannot add different currencies");
        return factory.Create(Amount + other.Amount, Currency);
    }

    public Money Multiply(decimal factor, IMoneyFactory factory)
    {
        return factory.Create(Amount * factor, Currency);
    }

    [Create]
    public void Create(decimal amount, string currency = "USD")
    {
        if (amount < 0)
            throw new ArgumentException("Amount cannot be negative");
        Amount = amount;
        Currency = currency.ToUpperInvariant();
    }
}
```

### Value Object Characteristics

1. **Identity-less** - Equality based on attributes, not identity
2. **Immutable** - Private setters, operations return new instances
3. **Self-validating** - Throw from Create for invalid inputs
4. **No base class** - Plain class with [Factory] attribute

### Using Value Objects in Entities

```csharp
using Neatoo;
using Neatoo.RemoteFactory;

[Factory]
internal partial class Order : EntityBase<Order>, IOrder
{
    public partial Money? TotalAmount { get; set; }
    public partial Address? ShippingAddress { get; set; }

    [Remote]
    [Fetch]
    public async Task<bool> Fetch(
        [Service] IDbContext db,
        [Service] IMoneyFactory moneyFactory,
        [Service] IAddressFactory addressFactory)
    {
        var entity = await db.Orders.FindAsync(Id);
        if (entity == null) return false;

        LoadProperty(nameof(Id), entity.Id);

        // Reconstruct Value Objects from flat columns
        TotalAmount = moneyFactory.Create(
            entity.TotalAmount,
            entity.TotalCurrency);

        ShippingAddress = addressFactory.Create(
            entity.ShipStreet,
            entity.ShipCity,
            entity.ShipState,
            entity.ShipZip);

        return true;
    }
}
```

## EntityListBase<I> - Child Collections

Collections of child entities use `EntityListBase<I>`. The list is a simple container - it doesn't create children.

### List with Helper Methods (Preferred)

The list constructor-injects the child factory and provides helper methods:

```csharp
using Neatoo;
using Neatoo.RemoteFactory;

public interface IOrderLineList : IEntityListBase<IOrderLine>
{
    IOrderLine AddLine();
    void RemoveLine(IOrderLine line);
}

[Factory]
internal partial class OrderLineList
    : EntityListBase<IOrderLine>, IOrderLineList
{
    private readonly IOrderLineFactory _lineFactory;

    public OrderLineList(IOrderLineFactory lineFactory) : base()
    {
        _lineFactory = lineFactory;
    }

    public IOrderLine AddLine()
    {
        var line = _lineFactory.Create();
        Add(line);
        return line;
    }

    public void RemoveLine(IOrderLine line)
    {
        Remove(line);
    }

    [Create]
    public void Create()
    {
        // Empty collection ready for items
    }

    [Fetch]
    public async Task Fetch(
        IEnumerable<OrderLineEntity> entities,
        [Service] IOrderLineFactory lineFactory)
    {
        foreach (var entity in entities)
        {
            var line = await lineFactory.Fetch(entity);
            if (line != null) Add(line);
        }
    }
}
```

### Simple List (Alternative)

When the UI manages child creation directly:

```csharp
using Neatoo;
using Neatoo.RemoteFactory;

public interface IOrderLineList : IEntityListBase<IOrderLine>
{
}

[Factory]
internal partial class OrderLineList
    : EntityListBase<IOrderLine>, IOrderLineList
{
    public OrderLineList() : base()
    {
    }

    [Create]
    public void Create()
    {
    }
}

// In Blazor page - UI injects factory
@inject IOrderLineFactory LineFactory

private void AddLineItem()
{
    var line = LineFactory.Create();
    _order!.Lines!.Add(line);
}
```

### Anti-Pattern - Factory as Method Parameter

**Never** require callers to provide factories as method parameters:

```csharp
// WRONG - forces caller to inject and pass factory
public IOrderLine AddLine(IOrderLineFactory lineFactory)
{
    var line = lineFactory.Create();
    Add(line);
    return line;
}
```

Services should be constructor-injected, not passed by callers

### Collection Behavior

| Item State | On Remove() |
|------------|-------------|
| `IsNew == true` | Removed completely |
| `IsNew == false` | Marked deleted, moved to DeletedList |

### Delete/Remove Consistency

Calling `entity.Delete()` on an entity in a list is equivalent to calling `list.Remove(entity)`. Both operations:

1. Remove the entity from the list
2. Mark it as deleted (`IsDeleted = true`)
3. Add it to the `DeletedList` (if not new)

```csharp
// These are equivalent:
order.Lines.Remove(line);
line.Delete();
```

For standalone entities (not in a list), `Delete()` simply sets `IsDeleted = true`.

### Intra-Aggregate Moves

Entities can be moved between lists within the same aggregate:

```csharp
// Company aggregate with two departments
var project = dept1.Projects[0];

// Remove from Dept1's projects
dept1.Projects.Remove(project);
// project.IsDeleted = true
// project in dept1.Projects.DeletedList

// Add to Dept2's projects (same aggregate)
dept2.Projects.Add(project);
// project removed from dept1.Projects.DeletedList
// project.IsDeleted = false (undeleted)
// project now in dept2.Projects
```

Cross-aggregate moves throw `InvalidOperationException`.

### DeletedList Processing

```csharp
[Remote]
[Update]
public async Task Update(Guid parentId, [Service] IDbContext db)
{
    // Process deletions first
    foreach (var deleted in DeletedList.Cast<IOrderLine>())
    {
        var entity = await db.OrderLines.FindAsync(deleted.Id);
        if (entity != null)
            db.OrderLines.Remove(entity);
    }

    // Process remaining items
    foreach (var line in this)
    {
        if (line.IsNew)
        {
            var entity = new OrderLineEntity { OrderId = parentId };
            // Map properties...
            db.OrderLines.Add(entity);
        }
        else if (line.IsModified)
        {
            var entity = await db.OrderLines.FindAsync(line.Id);
            // Map modified properties...
        }
    }

    await db.SaveChangesAsync();
}
```

## Dependency Injection Patterns

### Constructor Injection - For Ongoing Use

Constructor-inject dependencies you need throughout the entity's lifetime:

```csharp
public Person(
    IEntityBaseServices<Person> services,
    IEmailValidator emailValidator) : base(services)
{
    _emailValidator = emailValidator;

    // Validator used in rules - needed throughout lifetime
    RuleManager.AddRule(new EmailValidationRule(_emailValidator));
}
```

```csharp
// List needs factory for ongoing AddLine() calls
public OrderLineList(IOrderLineFactory lineFactory) : base()
{
    _lineFactory = lineFactory;
}

public IOrderLine AddLine()
{
    var line = _lineFactory.Create();  // Called multiple times
    Add(line);
    return line;
}
```

### [Service] Injection - For Factory Methods Only

Use `[Service]` for dependencies only needed in `[Create]`, `[Fetch]`, etc.:

```csharp
public Person(IEntityBaseServices<Person> services) : base(services)
{
    // No child factory needed here - only used once in Create
}

[Create]
public void Create([Service] IPersonPhoneListFactory phoneListFactory)
{
    Id = null;
    PersonPhoneList = phoneListFactory.Create();  // One-time initialization
}
```

```csharp
[Create]
public void Create([Service] IOrderLineListFactory lineListFactory)
{
    OrderDate = DateTime.Today;
    Lines = lineListFactory.Create();  // One-time initialization
}
```

### ValidateBase Constructor

```csharp
public SearchCriteria(IValidateBaseServices<SearchCriteria> services)
    : base(services)
{
    RuleManager.AddRule(new DateRangeRule());
}
```

### EntityListBase Constructor

```csharp
public OrderLineList(IOrderLineFactory lineFactory) : base()
{
    _lineFactory = lineFactory;
}
```

Note: EntityListBase uses a parameterless base constructor. Dependencies are constructor-injected into your class.

## Partial Property Requirements

Properties must be declared as `partial` for the source generator:

```csharp
// Correct - source generator provides implementation
public partial string? FirstName { get; set; }

// Incorrect - source generator cannot process
public string? FirstName { get; set; }
```

### Property Features Provided by Generator

- Value storage in PropertyManager
- Change detection (old vs new value)
- PropertyChanged events
- Modification tracking
- Rule triggering on change
- Busy state management for async operations

## Best Practices

### Use Interfaces for Public API

```csharp
// Interface is public - used by consumers
public interface IPerson : IEntityBase { }

// Class is internal - implementation detail
[Factory]
internal partial class Person : EntityBase<Person>, IPerson { }
```

### Inject Dependencies via Constructor

```csharp
public Person(
    IEntityBaseServices<Person> services,
    IPersonPhoneListFactory phoneListFactory,
    IEmailValidator emailValidator) : base(services)
{
    _phoneListFactory = phoneListFactory;
    _emailValidator = emailValidator;
}
```

### Initialize Collections in Create

```csharp
[Create]
public void Create()
{
    Id = null;  // Will be assigned on Insert
    PersonPhoneList = _phoneListFactory.Create();
}
```

### Access Parent from Child

```csharp
internal partial class OrderLine : EntityBase<OrderLine>, IOrderLine
{
    public IOrder? ParentOrder => Parent as IOrder;

    // Access parent's properties in rules
    public void CalculateDiscount()
    {
        if (ParentOrder?.CustomerType == CustomerType.VIP)
        {
            DiscountPercent = 10;
        }
    }
}
```

## Common Pitfalls

1. **Non-partial properties** - Source generator requires `partial` keyword
2. **Public class** - Classes should be `internal`, interfaces public
3. **Missing base constructor call** - Must call `base(services)`
4. **Wrong services type** - Use `IEntityBaseServices<T>` for EntityBase, etc.
5. **Direct instantiation** - Always use factories, never `new Entity()`
