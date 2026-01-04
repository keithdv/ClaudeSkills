# Neatoo Properties and Meta-Properties Reference

## Overview

Neatoo's property system provides enterprise-grade infrastructure through Roslyn source generators. Partial properties become managed properties with automatic change tracking, validation state, busy indicators, and UI binding.

## Partial Property Declaration

Properties must be declared as `partial` for the source generator:

```csharp
[Factory]
internal partial class Person : EntityBase<Person>, IPerson
{
    // Correct - source generator provides implementation
    public partial string? FirstName { get; set; }
    public partial string? LastName { get; set; }
    public partial int Age { get; set; }

    // Incorrect - won't get Neatoo infrastructure
    // public string? BadProperty { get; set; }
}
```

## Generated Property Implementation

The source generator creates this for each partial property:

```csharp
// What you write:
public partial string? FirstName { get; set; }

// What gets generated:
public partial string? FirstName
{
    get => Getter<string?>();
    set => Setter(value);
}
```

### Getter<T>() Behavior

- Retrieves value from PropertyManager
- Tracks property access

### Setter(value) Behavior

1. Compares old and new values
2. Stores new value in PropertyManager
3. Marks property as modified
4. Raises PropertyChanged event
5. Triggers dependent rules
6. Updates busy state for async operations

## Entity-Level Meta-Properties

These properties aggregate state for the entity and all children:

### IsValid

```csharp
public virtual bool IsValid { get; }
```

Returns `true` when this entity AND all children pass validation.

```csharp
var order = await orderFactory.Create();
order.CustomerName = "John";        // order.IsSelfValid might be true

var line = await order.Lines.AddLine();
// line has empty required fields
// line.IsValid == false
// order.IsValid == false (child is invalid)

line.ProductName = "Widget";
line.Quantity = 1;
// line.IsValid == true
// order.IsValid == true
```

### IsSelfValid

```csharp
public virtual bool IsSelfValid { get; }
```

Returns `true` when THIS entity's properties pass validation, ignoring children.

```csharp
order.IsSelfValid == true   // Order's own fields are valid
order.Lines[0].IsSelfValid == false  // Line has validation errors
order.IsValid == false      // Aggregate is invalid
```

### IsModified

```csharp
public virtual bool IsModified { get; }
```

Returns `true` when this entity OR any child has changes. True when:

- Any property value changed since load/save
- `IsNew` is `true`
- `IsDeleted` is `true`
- Any child entity is modified
- `MarkModified()` was called

```csharp
var person = await personFactory.Fetch(id);
// person.IsModified == false

person.FirstName = "Updated";
// person.IsModified == true

// Or modify a child
person.Phones[0].PhoneNumber = "555-1234";
// person.Phones[0].IsModified == true
// person.IsModified == true (child modified)
```

### IsSelfModified

```csharp
public virtual bool IsSelfModified { get; }
```

Returns `true` when THIS entity has direct changes, ignoring children.

```csharp
// Only child changed
order.Lines[0].Quantity = 5;

order.Lines[0].IsSelfModified == true
order.IsSelfModified == false   // Order itself unchanged
order.IsModified == true        // Aggregate is modified
```

### IsBusy

```csharp
public virtual bool IsBusy { get; }
```

Returns `true` when async operations run on this entity OR any child.

```csharp
person.Email = "test@example.com";  // Triggers async validation
// person.IsBusy == true

await person.WaitForTasks();
// person.IsBusy == false
```

### IsSelfBusy

```csharp
public virtual bool IsSelfBusy { get; }
```

Returns `true` when THIS entity has async operations, ignoring children.

### IsNew

```csharp
public virtual bool IsNew { get; protected set; }
```

Returns `true` when created via `[Create]` and not yet persisted.

```csharp
var person = personFactory.Create();
// person.IsNew == true

person = await personFactory.Save(person);  // Calls [Insert]
// person.IsNew == false
```

### IsDeleted

```csharp
public virtual bool IsDeleted { get; protected set; }
```

Returns `true` when `Delete()` was called.

```csharp
person.Delete();
// person.IsDeleted == true

await personFactory.Save(person);  // Calls [Delete]
```

### IsSavable

```csharp
public virtual bool IsSavable => IsModified && IsValid && !IsBusy && !IsChild;
```

Returns `true` when the entity can be saved. All four conditions required:

| Condition | Required | Reason |
|-----------|----------|--------|
| `IsModified` | true | Nothing to save if unchanged |
| `IsValid` | true | Cannot persist invalid data |
| `IsBusy` | false | Async rules must complete |
| `IsChild` | false | Children save through parent |

```csharp
// Use for save button
<button disabled="@(!person.IsSavable)">Save</button>

// Debug why not savable
if (!person.IsSavable)
{
    if (!person.IsModified) Console.WriteLine("No changes");
    if (!person.IsValid) Console.WriteLine("Validation errors");
    if (person.IsBusy) Console.WriteLine("Async operations pending");
    if (person.IsChild) Console.WriteLine("Save parent instead");
}
```

### IsChild

```csharp
public virtual bool IsChild { get; protected set; }
```

Returns `true` when part of a parent aggregate.

```csharp
var order = await orderFactory.Create();
var line = await order.Lines.AddLine();

// line.IsChild == true
// line.Parent == order

await lineFactory.Save(line);  // Throws! Cannot save child
await orderFactory.Save(order); // Correct - saves aggregate
```

### ModifiedProperties

```csharp
public virtual IEnumerable<string> ModifiedProperties { get; }
```

Returns names of properties that changed since load/save.

```csharp
person.FirstName = "John";
person.Email = "john@example.com";

foreach (var prop in person.ModifiedProperties)
{
    Console.WriteLine($"Changed: {prop}");
}
// Output:
// Changed: FirstName
// Changed: Email
```

### PropertyMessages

```csharp
public IReadOnlyCollection<IPropertyMessage> PropertyMessages { get; }
```

All validation messages for this entity.

```csharp
foreach (var msg in person.PropertyMessages)
{
    Console.WriteLine($"{msg.PropertyName}: {msg.Message}");
}
// Output:
// FirstName: First Name is required
// Email: Invalid email format
```

## Property-Level Meta-Properties

Access per-property state through the indexer:

```csharp
IEntityProperty firstNameProp = person[nameof(person.FirstName)];
```

### Property.IsModified

```csharp
bool IsModified { get; }  // On IEntityProperty
```

True when this specific property changed.

```csharp
person.FirstName = "John";

var firstNameProp = person[nameof(person.FirstName)];
// firstNameProp.IsModified == true

var lastNameProp = person[nameof(person.LastName)];
// lastNameProp.IsModified == false
```

### Property.IsValid

```csharp
bool IsValid { get; }
```

True when this property passes all validation rules.

```csharp
var emailProp = person[nameof(person.Email)];

if (!emailProp.IsValid)
{
    // Show error styling
}
```

### Property.IsBusy

```csharp
bool IsBusy { get; }
```

True when async validation runs for this property.

```csharp
person.Email = "test@example.com";  // Triggers async validation

var emailProp = person[nameof(person.Email)];
// emailProp.IsBusy == true (while rule executes)

await person.WaitForTasks();
// emailProp.IsBusy == false
```

### Property.PropertyMessages

```csharp
IEnumerable<IPropertyMessage> PropertyMessages { get; }
```

Validation messages for this specific property.

```csharp
var emailProp = person[nameof(person.Email)];

foreach (var msg in emailProp.PropertyMessages)
{
    Console.WriteLine(msg.Message);
}
```

## Property Setters and Rules

### Factory Methods - Rules Are Paused

In factory methods (`[Create]`, `[Fetch]`, etc.), **rules are paused**. Use property setters directly:

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

### Cascading Rules - A Key Feature

When a rule sets a property, **dependent rules run automatically**. This is intentional:

```csharp
public class OrderTotalRule : RuleBase<IOrder>
{
    public override IRuleMessages Execute(IOrder target)
    {
        var total = target.Lines?.Sum(l => l.Quantity * l.UnitPrice) ?? 0;
        target.Total = total;  // Triggers any rules that depend on Total
        return None;
    }
}
```

### LoadProperty - Rare Use Cases

Use `LoadProperty()` **only** to break circular rule dependencies:

```csharp
// Rule A triggers Rule B which triggers Rule A - break the cycle
LoadProperty(nameof(target.InternalValue), calculated);
```

## Property Propagation

Meta-properties propagate UP the aggregate hierarchy:

```
┌─────────────────────────────────────────────────┐
│                 Order (Root)                     │
│  IsValid = IsSelfValid && Lines.IsValid          │
│  IsModified = IsSelfModified || Lines.IsModified │
│  IsBusy = IsSelfBusy || Lines.IsBusy             │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌─────────────────────────────────────────────┐│
│  │            OrderLineList                    ││
│  │  IsValid = All(line => line.IsValid)        ││
│  │  IsModified = Any(line => line.IsModified)  ││
│  ├─────────────────────────────────────────────┤│
│  │  ┌─────────────┐  ┌─────────────┐           ││
│  │  │ OrderLine 1 │  │ OrderLine 2 │           ││
│  │  │ IsValid     │  │ IsValid     │           ││
│  │  │ IsModified  │  │ IsModified  │           ││
│  │  └─────────────┘  └─────────────┘           ││
│  └─────────────────────────────────────────────┘│
└─────────────────────────────────────────────────┘

Changes propagate UP:
  OrderLine.IsModified changes
    → OrderLineList re-evaluates
      → Order.IsModified updates
        → PropertyChanged fires
```

## WaitForTasks

Wait for all async operations to complete:

```csharp
person.Email = "test@example.com";  // Triggers async rule
// person.IsBusy == true

await person.WaitForTasks();
// All async rules complete
// person.IsBusy == false

// NOW safe to check validation
if (person.IsValid)
{
    await personFactory.Save(person);
}
```

### Critical: Always Wait Before Save

```csharp
// WRONG - might save before validation completes
if (person.IsSavable)  // IsSavable includes !IsBusy check
{
    await personFactory.Save(person);
}

// CORRECT - ensure async rules finish
await person.WaitForTasks();
if (person.IsSavable)
{
    await personFactory.Save(person);
}
```

## PauseAllActions

Defer events and rules during bulk updates:

```csharp
using (person.PauseAllActions())
{
    // These changes do NOT trigger individual events or rules
    person.FirstName = "John";
    person.LastName = "Doe";
    person.Email = "john@example.com";
}
// Events fire and rules execute AFTER dispose
```

**Use for:**
- Bulk data import
- Resetting multiple fields
- Complex initialization sequences

## MarkModified

Force an entity to be marked as modified:

```csharp
// Entity hasn't changed but needs to be saved
person.MarkModified();
// person.IsModified == true
```

**Use for:**
- Forcing save of unchanged entities
- Triggering re-validation
- Testing scenarios

## Reacting to Property Changes

### ChildNeatooPropertyChanged

Override in parent to react to any descendant change:

```csharp
protected override Task ChildNeatooPropertyChanged(
    NeatooPropertyChangedEventArgs eventArgs)
{
    if (eventArgs.PropertyName == nameof(IOrderLine.Quantity) ||
        eventArgs.PropertyName == nameof(IOrderLine.UnitPrice))
    {
        RecalculateTotal();
    }

    return base.ChildNeatooPropertyChanged(eventArgs);
}
```

### HandleNeatooPropertyChanged (Collections)

Override in collections to react to item changes:

```csharp
protected override async Task HandleNeatooPropertyChanged(
    NeatooPropertyChangedEventArgs eventArgs)
{
    await base.HandleNeatooPropertyChanged(eventArgs);

    if (eventArgs.PropertyName == nameof(IOrderLine.ProductName))
    {
        // Re-validate siblings for uniqueness
        foreach (var sibling in this.Where(l => l != eventArgs.Source))
        {
            await sibling.RunRules(nameof(IOrderLine.ProductName));
        }
    }
}
```

## Data Annotations on Properties

```csharp
[Required(ErrorMessage = "First name is required")]
[StringLength(50, ErrorMessage = "First name cannot exceed 50 characters")]
[DisplayName("First Name")]
public partial string? FirstName { get; set; }

[EmailAddress(ErrorMessage = "Invalid email format")]
public partial string? Email { get; set; }

[Range(0, 150)]
public partial int Age { get; set; }

[RegularExpression(@"^\d{5}(-\d{4})?$")]
public partial string? ZipCode { get; set; }
```

## Best Practices

### Always Use Partial Properties

```csharp
// Correct
public partial string? FirstName { get; set; }

// Won't get Neatoo infrastructure
public string? FirstName { get; set; }
```

### Wait Before Checking Validity

```csharp
person.Email = "test@example.com";  // Async rule starts

// Wrong - rule might not be complete
if (person.IsValid) Save();

// Correct
await person.WaitForTasks();
if (person.IsValid) Save();
```

### Bind UI to Meta-Properties

```razor
<button disabled="@(!entity.IsSavable)">Save</button>

<span class="@(entity.IsBusy ? "loading" : "")">
    @(entity.IsBusy ? "Validating..." : "")
</span>

<div class="@(entity[nameof(entity.Email)].IsValid ? "" : "has-error")">
    <input @bind="entity.Email" />
</div>
```

## Common Pitfalls

1. **Non-partial properties** - Must use `partial` keyword
2. **Not waiting for async rules** - Call `WaitForTasks()` before validity checks
3. **Checking IsValid not IsSavable** - IsSavable includes all necessary checks
4. **Missing PropertyChanged subscription cleanup** - Unsubscribe on dispose
5. **Overusing LoadProperty** - Cascading rules are a feature; LoadProperty only for circular references
