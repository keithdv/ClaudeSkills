# Neatoo Properties and Meta-Properties Reference

## Overview

Neatoo's property system provides enterprise-grade infrastructure through Roslyn source generators. Partial properties become managed properties with automatic change tracking, validation state, busy indicators, and UI binding.

## Partial Properties Are Required

When you add a property to a Neatoo `EntityBase<>`, it almost always should be a `partial` property. **For a property to be serialized or trigger a rule, it must be a `partial` property on a `partial` class.**

Private fields are **not** serialized by Neatoo. If you use a private field with a read-only property wrapper, the data will exist on the server but will be `null` on the client after RemoteFactory transfers the object.

```csharp
// WRONG - private fields are NOT serialized
// The _history field is populated on server, but will be null on client!
private IConsultationHistory? _history;
public IConsultationHistory? History => _history;

// WRONG - private field for child entity collection
private List<IVisit> _visits = new();
public IReadOnlyList<IVisit> Visits => _visits.AsReadOnly();

// CORRECT - partial properties ARE serialized and can trigger rules
public partial IConsultationHistory? History { get; set; }

// CORRECT - use NeatooList for child collections
public NeatooList<IVisit> Visits { get; } = new();
```

This applies to:
- Child entities in aggregates
- Any property that needs to transfer between client and server via RemoteFactory
- Any property that should trigger validation rules
- Collections of child entities

## Property Access Patterns

<!-- snippet: property-access -->
```csharp
/// <summary>
/// Entity demonstrating property access patterns.
/// </summary>
public partial interface IPropertyAccessDemo : IEntityBase
{
    string? Name { get; set; }
    string? Email { get; set; }
    int Age { get; set; }
}

[Factory]
internal partial class PropertyAccessDemo : EntityBase<PropertyAccessDemo>, IPropertyAccessDemo
{
    public PropertyAccessDemo(IEntityBaseServices<PropertyAccessDemo> services) : base(services) { }

    public partial string? Name { get; set; }

    [EmailAddress(ErrorMessage = "Invalid email format")]
    public partial string? Email { get; set; }

    public partial int Age { get; set; }

    [Create]
    public void Create() { }
}
```
<!-- /snippet -->

## Display Name Access

<!-- snippet: display-name -->
```csharp
/// <summary>
/// Entity demonstrating DisplayName attribute.
/// </summary>
public partial interface IDisplayNameDemo : IEntityBase
{
    string? FirstName { get; set; }
    string? LastName { get; set; }
    string? EmailAddress { get; set; }
}

[Factory]
internal partial class DisplayNameDemo : EntityBase<DisplayNameDemo>, IDisplayNameDemo
{
    public DisplayNameDemo(IEntityBaseServices<DisplayNameDemo> services) : base(services) { }

    [DisplayName("First Name*")]
    [Required]
    public partial string? FirstName { get; set; }

    [DisplayName("Last Name*")]
    [Required]
    public partial string? LastName { get; set; }

    [DisplayName("Email Address")]
    public partial string? EmailAddress { get; set; }

    [Create]
    public void Create() { }
}
```
<!-- /snippet -->

## SetValue and LoadProperty

<!-- snippet: setvalue-loadvalue -->
```csharp
/// <summary>
/// Entity demonstrating SetValue vs LoadValue.
/// </summary>
public partial interface ILoadValueDemo : IEntityBase
{
    Guid Id { get; }
    string? Name { get; set; }
    DateTime? LastModified { get; set; }

    /// <summary>
    /// Load data from database using LoadValue (no modification tracking).
    /// </summary>
    void LoadFromDatabase(Guid id, string name, DateTime lastModified);
}

[Factory]
internal partial class LoadValueDemo : EntityBase<LoadValueDemo>, ILoadValueDemo
{
    public LoadValueDemo(IEntityBaseServices<LoadValueDemo> services) : base(services) { }

    public partial Guid Id { get; set; }
    public partial string? Name { get; set; }
    public partial DateTime? LastModified { get; set; }

    [Create]
    public void Create()
    {
        Id = Guid.NewGuid();
    }

    /// <summary>
    /// Demonstrates using LoadValue for identity fields.
    /// </summary>
    public void LoadFromDatabase(Guid id, string name, DateTime lastModified)
    {
        // LoadValue - silent set, no rules or modification tracking
        this[nameof(Id)].LoadValue(id);
        this[nameof(Name)].LoadValue(name);
        this[nameof(LastModified)].LoadValue(lastModified);
    }
}
```
<!-- /snippet -->

## Pause Actions

<!-- snippet: pause-actions -->
```csharp
/// <summary>
/// Entity demonstrating PauseAllActions pattern.
/// </summary>
public partial interface IBulkUpdateDemo : IEntityBase
{
    string? FirstName { get; set; }
    string? LastName { get; set; }
    string? Email { get; set; }
    int Age { get; set; }
}

[Factory]
internal partial class BulkUpdateDemo : EntityBase<BulkUpdateDemo>, IBulkUpdateDemo
{
    public BulkUpdateDemo(IEntityBaseServices<BulkUpdateDemo> services) : base(services) { }

    [Required]
    public partial string? FirstName { get; set; }

    [Required]
    public partial string? LastName { get; set; }

    [EmailAddress]
    public partial string? Email { get; set; }

    [Range(0, 150)]
    public partial int Age { get; set; }

    [Create]
    public void Create() { }
}
```
<!-- /snippet -->

## Bulk Updates

<!-- snippet: bulk-updates -->
```csharp
/// <summary>
/// Examples demonstrating bulk update patterns with PauseAllActions.
/// Note: PauseAllActions is on the concrete base class, not the interface.
/// </summary>
internal static class BulkUpdateExamples
{
    /// <summary>
    /// Update multiple properties with pausing for efficiency.
    /// Without pause: 4 rule executions, 4 PropertyChanged events.
    /// With pause: 0 rule executions during block, meta-state recalculated once.
    /// </summary>
    public static async Task PerformBulkUpdate(BulkUpdateDemo person)
    {
        using (person.PauseAllActions())
        {
            person.FirstName = "John";
            person.LastName = "Doe";
            person.Email = "john@example.com";
            person.Age = 30;
        }
        // Meta-state recalculated when disposed
        // Now run rules once after all changes
        await person.RunRules();
    }

    /// <summary>
    /// Load data from external source with pause.
    /// </summary>
    public static async Task LoadExternalData(
        BulkUpdateDemo customer,
        ExternalData externalData)
    {
        using (customer.PauseAllActions())
        {
            // Load data from external source without triggering validation
            customer.FirstName = externalData.FirstName;
            customer.LastName = externalData.LastName;
            customer.Email = externalData.Email;
            customer.Age = externalData.Age;
        }
        // Validate everything once at the end
        await customer.RunRules();
    }
}

/// <summary>
/// Mock external data for demo.
/// </summary>
public class ExternalData
{
    public string? FirstName { get; set; }
    public string? LastName { get; set; }
    public string? Email { get; set; }
    public int Age { get; set; }
}
```
<!-- /snippet -->

## Meta-Properties

### Entity-Level Properties

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

### Property-Level Access

Access individual property metadata via indexer:

<!-- pseudo:property-level-access -->
```csharp
var prop = entity[nameof(entity.FirstName)];
prop.IsModified    // Was this property changed?
prop.IsBusy        // Async validation running?
prop.DisplayName   // UI-friendly label
```
<!-- /snippet -->

## Key Concepts

1. **Partial properties** - Required for source generator
2. **LoadProperty** - Sets value without triggering rules
3. **SetValue** - Sets value and triggers rules
4. **PauseAllActions** - Batch updates without individual rule execution

## Best Practices

1. **Use LoadProperty in Fetch** - Don't trigger rules when loading
2. **Use SetValue for programmatic changes** - When you want rules to run
3. **Use PauseAllActions for bulk updates** - Performance optimization
4. **Check property-level state** - `entity[propertyName].IsModified`
