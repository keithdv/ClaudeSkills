# Neatoo Migration Guide

## Migrate to 10.5.0 (RemoteFactory CancellationToken Support)

**Release:** 10.6.0 (Released 2026-01-05)
**Breaking Changes:** Minor - infrastructure delegates/interfaces updated

### Summary

Version 10.5.0 adds comprehensive CancellationToken support across the entire RemoteFactory client-server pipeline. Cancellation now flows from client to server via HTTP connection state.

### What Changed

#### Delegate Signatures Updated

| Delegate | Before | After |
|----------|--------|-------|
| `HandleRemoteDelegateRequest` | `Task<RemoteResponseDto> (RemoteRequestDto)` | `Task<RemoteResponseDto> (RemoteRequestDto, CancellationToken)` |
| `MakeRemoteDelegateRequestHttpCall` | `Task<RemoteResponseDto> (RemoteRequestDto)` | `Task<RemoteResponseDto> (RemoteRequestDto, CancellationToken)` |

#### Interface Signatures Updated

```csharp
// Before
public interface IMakeRemoteDelegateRequest
{
    Task<T> ForDelegate<T>(Type delegateType, object?[]? parameters);
    Task<T?> ForDelegateNullable<T>(Type delegateType, object?[]? parameters);
}

// After
public interface IMakeRemoteDelegateRequest
{
    Task<T> ForDelegate<T>(Type delegateType, object?[]? parameters, CancellationToken cancellationToken);
    Task<T?> ForDelegateNullable<T>(Type delegateType, object?[]? parameters, CancellationToken cancellationToken);
}
```

#### New Lifecycle Interface

```csharp
// Called when a factory operation is cancelled
public interface IFactoryOnCancelled
{
    void FactoryCancelled(FactoryOperation operation);
}

public interface IFactoryOnCancelledAsync
{
    Task FactoryCancelledAsync(FactoryOperation operation);
}
```

### Migration Steps

#### Custom HandleRemoteDelegateRequest Registrations

If you have custom registrations of `HandleRemoteDelegateRequest`:

```csharp
// Before
services.AddScoped<HandleRemoteDelegateRequest>(sp =>
{
    return (request) => { /* ... */ };
});

// After
services.AddScoped<HandleRemoteDelegateRequest>(sp =>
{
    return (request, cancellationToken) => { /* ... */ };
});
```

#### Custom IMakeRemoteDelegateRequest Implementations

If you implemented `IMakeRemoteDelegateRequest`:

```csharp
// Before
public class MyRequestHandler : IMakeRemoteDelegateRequest
{
    public Task<T> ForDelegate<T>(Type delegateType, object?[]? parameters)
    { /* ... */ }
}

// After
public class MyRequestHandler : IMakeRemoteDelegateRequest
{
    public Task<T> ForDelegate<T>(Type delegateType, object?[]? parameters, CancellationToken cancellationToken)
    { /* ... */ }
}
```

### How Cancellation Works

```
CLIENT                                          SERVER
┌─────────────────────────────────────┐         ┌─────────────────────────────────────┐
│ factory.FetchAsync(id, ct)          │         │                                     │
│   │                                 │         │                                     │
│   ▼                                 │         │                                     │
│ HttpClient.SendAsync(request, ct) ──┼── TCP ──┼──► HttpContext.RequestAborted       │
│   │                                 │         │         │                           │
│   │  ct.Cancel() ───────────────────┼─► X ────┼─► fires │                           │
│   │                                 │  close  │         ▼                           │
│   ▼                                 │  conn   │    Server stops processing          │
│ OperationCanceledException          │         │                                     │
└─────────────────────────────────────┘         └─────────────────────────────────────┘
```

1. Client's CancellationToken passed to `HttpClient.SendAsync`
2. When cancelled, HttpClient closes the TCP connection
3. Server's `HttpContext.RequestAborted` fires automatically
4. Server stops processing and cleans up

### Using Cancellation in Domain Code

```csharp
[Factory]
public class Order : EntityBase<Order>
{
    [Remote]
    [Fetch]
    public async Task<bool> FetchAsync(
        Guid id,
        CancellationToken cancellationToken,
        [Service] IDbContext db)
    {
        // Pass token to EF Core - auto-rolls back if cancelled
        var entity = await db.Orders
            .Include(o => o.Lines)
            .FirstOrDefaultAsync(o => o.Id == id, cancellationToken);

        if (entity == null) return false;

        // Check cancellation at safe points
        cancellationToken.ThrowIfCancellationRequested();

        // ... load properties
        return true;
    }
}
```

### Best Practices

1. **Always pass CancellationToken to async operations** - EF Core, HttpClient, etc.
2. **Check cancellation at safe points** - Use `cancellationToken.ThrowIfCancellationRequested()`
3. **Use transactions for atomicity** - Cancellation doesn't auto-rollback multiple operations
4. **Handle OperationCanceledException** - Client should catch and handle gracefully

---

## Migrate to 10.4.0

**Release:** 10.4.0 (2026-01-04)
**Breaking Changes:** None for application code

### Summary

Version 10.4.0 collapses the "Base" layer from all inheritance chains, making `ValidateBase<T>` the new foundation. This simplifies the framework internally while maintaining full backward compatibility for public APIs.

**Pattern change:** `Entity → Validate → Base` becomes `Entity → Validate`

### For Application Developers

**No action required.** All public APIs remain unchanged. Code using `ValidateBase<T>`, `EntityBase<T>`, `ValidateListBase<I>`, and `EntityListBase<I>` works without modification.

### For Framework Extenders

If you have code that directly references internal Neatoo types, update as follows:

#### Type Replacements

| Before (10.3.x) | After (10.4.0) |
|-----------------|----------------|
| `Base<T>` | `ValidateBase<T>` |
| `ListBase<I>` | `ValidateListBase<I>` |
| `IBase` | `IValidateBase` |
| `IListBase` | `IValidateListBase` |
| `IListBase<I>` | `IValidateListBase<I>` |
| `IBaseServices<T>` | `IValidateBaseServices<T>` |
| `IBaseMetaProperties` | `IValidateMetaProperties` |
| `IProperty` | `IValidateProperty` |
| `IProperty<T>` | `IValidateProperty<T>` |
| `IPropertyManager<P>` | `IValidatePropertyManager<P>` |
| `Property<T>` | `ValidateProperty<T>` |
| `PropertyManager<P>` | `ValidatePropertyManager<P>` |
| `BaseServices<T>` | `ValidateBaseServices<T>` |

#### Property Type References

```csharp
// Before
IProperty prop = entity[nameof(entity.Name)];
IBase? parent = entity.Parent;

// After
IValidateProperty prop = entity[nameof(entity.Name)];
IValidateBase? parent = entity.Parent;
```

#### Service Injection

```csharp
// Before
public MyEntity(IBaseServices<MyEntity> services) : base(services) { }

// After - use ValidateBaseServices or EntityBaseServices
public MyEntity(IValidateBaseServices<MyEntity> services) : base(services) { }
// or for EntityBase:
public MyEntity(IEntityBaseServices<MyEntity> services) : base(services) { }
```

#### Property Manager Access

```csharp
// Before
IPropertyManager<IProperty> manager = PropertyManager;

// After
IValidatePropertyManager<IValidateProperty> manager = PropertyManager;
```

### Deleted Types

The following types no longer exist:

**Classes:**
- `Base<T>` → Use `ValidateBase<T>`
- `ListBase<I>` → Use `ValidateListBase<I>`
- `Property<T>` → Use `ValidateProperty<T>`
- `PropertyManager<P>` → Use `ValidatePropertyManager<P>`
- `BaseServices<T>` → Use `ValidateBaseServices<T>`

**Interfaces:**
- `IBase` → Use `IValidateBase`
- `IListBase` / `IListBase<I>` → Use `IValidateListBase` / `IValidateListBase<I>`
- `IBaseServices<T>` → Use `IValidateBaseServices<T>`
- `IBaseMetaProperties` → Use `IValidateMetaProperties`
- `IProperty` / `IProperty<T>` → Use `IValidateProperty` / `IValidateProperty<T>`
- `IPropertyManager<P>` → Use `IValidatePropertyManager<P>`
- `IBaseInternal` → Use `IValidateBaseInternal`
- `IPropertyInternal` → Use `IValidatePropertyInternal`

### Factory Method Changes

The `IFactory.CreateProperty<P>()` method was removed. Only `CreateValidateProperty<P>()` and `CreateEntityProperty<P>()` remain.

```csharp
// Before
public interface IFactory
{
    Property<P> CreateProperty<P>(IPropertyInfo propertyInfo);        // REMOVED
    ValidateProperty<P> CreateValidateProperty<P>(IPropertyInfo propertyInfo);
    EntityProperty<P> CreateEntityProperty<P>(IPropertyInfo propertyInfo);
}

// After
public interface IFactory
{
    ValidateProperty<P> CreateValidateProperty<P>(IPropertyInfo propertyInfo);
    EntityProperty<P> CreateEntityProperty<P>(IPropertyInfo propertyInfo);
}
```

### Why This Change?

The `Base<T>` layer existed as an abstraction for "property management without validation." In practice:

1. All user code uses `ValidateBase<T>` or `EntityBase<T>` (with validation)
2. No valid use case exists for property management without validation
3. The extra abstraction added cognitive overhead without benefit
4. Duplicate code existed across Base and Validate layers

Benefits of 10.4.0:
- ~800 lines of duplicate code removed
- 8 source files deleted
- Simpler inheritance hierarchy
- Easier to understand and maintain
- Fewer types for developers to navigate

### Hierarchy Comparison

**Before (10.3.x):**
```
Base<T>                    - Property management, INotifyPropertyChanged
  ValidateBase<T>          - Validation, rules engine
    EntityBase<T>          - Persistence awareness, modification tracking

ListBase<I>                - Observable collection
  ValidateListBase<I>      - Validation aggregation
    EntityListBase<I>      - DeletedList, persistence
```

**After (10.4.0):**
```
ValidateBase<T>            - Property management, INotifyPropertyChanged, validation, rules
    EntityBase<T>          - Persistence awareness, modification tracking

ValidateListBase<I>        - Observable collection, validation aggregation
    EntityListBase<I>      - DeletedList, persistence
```
