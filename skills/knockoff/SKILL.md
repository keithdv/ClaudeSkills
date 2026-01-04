---
name: knockoff
description: KnockOff source-generated test stubs. Use when creating interface stubs for unit tests, migrating from Moq, understanding the duality pattern (user methods vs callbacks), configuring stub behavior, verifying invocations, or working with interface spy handlers for tracking calls.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(dotnet:*)
---

# KnockOff - Source-Generated Test Stubs

## Overview

KnockOff is a Roslyn Source Generator that creates test stubs for interfaces. Unlike Moq's runtime proxy generation, KnockOff generates compile-time code for type-safe, debuggable stubs.

### Key Differentiator: The Duality

KnockOff provides **two complementary patterns** for customizing stub behavior:

| Pattern | When | Scope | Use Case |
|---------|------|-------|----------|
| **User Methods** | Compile-time | All tests | Consistent defaults |
| **Callbacks** | Runtime | Per-test | Test-specific overrides |

```csharp
// Pattern 1: User method (compile-time default)
[KnockOff]
public partial class ServiceKnockOff : IService
{
    protected int GetValue(int id) => id * 2;  // Default for all tests
}

// Pattern 2: Callback (runtime override)
knockOff.IService.GetValue.OnCall = (ko, id) => id * 100;  // Override for this test
```

**Priority Order**: Callback → User method → Default

## Installation

```bash
dotnet add package KnockOff
```

## Quick Start

### 1. Create KnockOff Stub

```csharp
public interface IDataService
{
    string Name { get; set; }
    string? GetDescription(int id);
    int GetCount();
}

[KnockOff]
public partial class DataServiceKnockOff : IDataService
{
    private readonly int _count;

    public DataServiceKnockOff(int count = 42) => _count = count;

    // Define behavior for non-nullable method
    protected int GetCount() => _count;

    // GetDescription not defined - returns null by default
}
```

### 2. Use in Tests

```csharp
[Fact]
public void Test_DataService()
{
    var knockOff = new DataServiceKnockOff(count: 100);
    IDataService service = knockOff;

    // Property - uses generated backing field
    service.Name = "Test";
    Assert.Equal("Test", service.Name);
    Assert.Equal(1, knockOff.IDataService.Name.SetCount);

    // Nullable method - returns null, call is still verified
    var description = service.GetDescription(5);
    Assert.Null(description);
    Assert.True(knockOff.IDataService.GetDescription.WasCalled);
    Assert.Equal(5, knockOff.IDataService.GetDescription.LastCallArg);

    // Non-nullable method - returns constructor value
    Assert.Equal(100, service.GetCount());
}
```

## Interface Spy Properties

Each interface gets its own spy property for tracking and configuration:

```csharp
knockOff.IUserService.GetUser       // Method handler
knockOff.IUserService.Name          // Property handler
knockOff.IPropertyStore.StringIndexer // Indexer handler
knockOff.IEventSource.DataReceived  // Event handler
```

### Multiple Interfaces

When implementing multiple interfaces, each has a separate spy:

```csharp
[KnockOff]
public partial class DataContextKnockOff : IRepository, IUnitOfWork { }

// Access via interface spy properties
knockOff.IRepository.Save.WasCalled
knockOff.IUnitOfWork.Commit.WasCalled

// Use AsXxx() for explicit casting
IRepository repo = knockOff.AsRepository();
IUnitOfWork uow = knockOff.AsUnitOfWork();
```

## OnCall API

**Callbacks use property assignment** with `OnCall =`:

```csharp
// No parameters
knockOff.IService.Clear.OnCall = (ko) => { };

// Single parameter
knockOff.IRepository.GetById.OnCall = (ko, id) => new User { Id = id };

// Multiple parameters - individual params, not tuples
knockOff.IService.Find.OnCall = (ko, name, active) =>
    users.Where(u => u.Name == name && u.Active == active).ToList();

// Void method
knockOff.IService.Save.OnCall = (ko, entity) => { /* logic */ };
```

**Out/Ref parameters** - use explicit delegate type:

```csharp
knockOff.IParser.TryParse.OnCall =
    (IParser_TryParseHandler.TryParseDelegate)((ko, string input, out int result) =>
    {
        return int.TryParse(input, out result);
    });
```

## Stub Minimalism

**Only stub what the test needs.** Don't implement every interface member.

KnockOff generates explicit interface implementations for ALL members. Members without user-defined behavior:
- **Non-nullable returns**: throw `InvalidOperationException` (fail-fast)
- **Nullable returns**: return `null`/`default`
- **Void methods**: execute silently (tracking still works)

```csharp
// GOOD - minimal stub for a test that only calls GetUser
[KnockOff]
public partial class UserServiceKnockOff : IUserService
{
    protected User GetUser(int id) => new User { Id = id };
    // SaveUser, GetAllAsync, DeleteUser will throw if called - good!
}
```

## Handler Types

| Member Type | Tracking | Callbacks |
|-------------|----------|-----------|
| Method | `CallCount`, `WasCalled`, `LastCallArg(s)`, `AllCalls` | `OnCall` |
| Property | `GetCount`, `SetCount`, `LastSetValue` | `OnGet`, `OnSet` |
| Indexer | `GetCount`, `SetCount`, `LastGetKey`, `AllGetKeys`, `LastSetEntry`, `AllSetEntries` | `OnGet`, `OnSet` |
| Event | `SubscribeCount`, `UnsubscribeCount`, `RaiseCount`, `WasRaised`, `LastRaiseArgs`, `AllRaises` | `Raise()`, `Reset()`, `Clear()` |

### Reset

```csharp
knockOff.IService.GetUser.Reset();  // Clears tracking AND callbacks
// After reset: CallCount=0, OnCall=null
// Falls back to user method or default
```

## Customization Patterns

### User Methods (Compile-Time)

Define protected methods matching interface signatures:

```csharp
[KnockOff]
public partial class RepoKnockOff : IRepository
{
    protected User? GetById(int id) => new User { Id = id };
    protected Task<User?> GetByIdAsync(int id) => Task.FromResult<User?>(new User { Id = id });
}
```

Rules:
- Must be `protected`
- Must match method signature exactly
- Only works for methods (not properties/indexers)

### Callbacks (Runtime)

#### Method Callbacks

```csharp
// Void method
knockOff.IService.DoWork.OnCall = (ko) => { /* custom logic */ };

// Return method (single param)
knockOff.IRepository.GetById.OnCall = (ko, id) => new User { Id = id };

// Return method (multiple params) - individual parameters
knockOff.IService.Find.OnCall = (ko, name, includeDeleted) =>
    users.Where(u => u.Name == name).ToList();
```

#### Property Callbacks

```csharp
knockOff.IService.Name.OnGet = (ko) => "Computed Value";
knockOff.IService.Name.OnSet = (ko, value) =>
{
    // Custom setter logic
    // Note: Does NOT store in backing field when OnSet is set
};
```

#### Indexer Callbacks

```csharp
knockOff.IPropertyStore.StringIndexer.OnGet = (ko, key) => key switch
{
    "admin" => adminUser,
    _ => null
};

knockOff.IPropertyStore.StringIndexer.OnSet = (ko, key, value) =>
{
    // Custom setter logic
    // Note: Does NOT store in backing dictionary when OnSet is set
};
```

### Priority Order

```
1. Callback (if set) → takes precedence
2. User method (if defined) → fallback for methods
3. Default:
   - Properties: backing field value
   - Methods: null for nullable, throw for non-nullable, silent for void
   - Indexers: backing dictionary, then null/throw based on nullability
```

## Verification Patterns

### Call Tracking

```csharp
// Basic
Assert.True(knockOff.IService.GetUser.WasCalled);
Assert.Equal(3, knockOff.IService.GetUser.CallCount);

// Arguments (single param)
Assert.Equal(42, knockOff.IService.GetUser.LastCallArg);
Assert.Equal([1, 2, 42], knockOff.IService.GetUser.AllCalls);

// Arguments (multiple params - named tuple)
var args = knockOff.IService.Create.LastCallArgs;
Assert.Equal("Test", args?.name);
Assert.Equal(100, args?.value);

// Destructuring
if (knockOff.IService.Create.LastCallArgs is var (name, value))
{
    Assert.Equal("Test", name);
}
```

### Property Tracking

```csharp
Assert.Equal(2, knockOff.IService.Name.GetCount);
Assert.Equal(3, knockOff.IService.Name.SetCount);
Assert.Equal("LastValue", knockOff.IService.Name.LastSetValue);
```

### Indexer Tracking

```csharp
Assert.Equal("key1", knockOff.IPropertyStore.StringIndexer.LastGetKey);
Assert.Equal(["key1", "key2"], knockOff.IPropertyStore.StringIndexer.AllGetKeys);

var setEntry = knockOff.IPropertyStore.StringIndexer.LastSetEntry;
Assert.Equal("key", setEntry?.key);
Assert.Equal(value, setEntry?.value);
```

## Backing Storage

### Properties

```csharp
// Direct access to backing field (interface-prefixed)
knockOff.IService_NameBacking = "Pre-populated value";

// Without OnGet, getter returns backing field
Assert.Equal("Pre-populated value", service.Name);
```

### Indexers

```csharp
// Pre-populate backing dictionary (interface-prefixed)
knockOff.IPropertyStore_StringIndexerBacking["key1"] = value1;
knockOff.IPropertyStore_StringIndexerBacking["key2"] = value2;

// Without OnGet, getter checks backing dictionary
Assert.Equal(value1, store["key1"]);
```

**Important**: `Reset()` does NOT clear backing storage.

## Supported Features

| Feature | Status |
|---------|--------|
| Properties (get/set, get-only, set-only) | Supported |
| Void methods | Supported |
| Methods with return values | Supported |
| Methods with parameters | Supported |
| Method overloads (separate handlers) | Supported |
| Out parameters | Supported |
| Ref parameters | Supported |
| Async methods (Task, Task<T>, ValueTask, ValueTask<T>) | Supported |
| Generic interfaces (concrete types) | Supported |
| Multiple interfaces | Supported |
| Interface inheritance | Supported |
| Indexers | Supported |
| Events | Supported |
| User method detection | Supported |
| OnCall/OnGet/OnSet callbacks | Supported |
| Named tuple argument tracking | Supported |

## Common Patterns

### Conditional Returns

```csharp
knockOff.IService.GetUser.OnCall = (ko, id) => id switch
{
    1 => new User { Name = "Admin" },
    2 => new User { Name = "Guest" },
    _ => null
};
```

### Throwing Exceptions

```csharp
knockOff.IService.Connect.OnCall = (ko) =>
    throw new TimeoutException("Connection failed");

knockOff.IService.SaveAsync.OnCall = (ko, entity) =>
    Task.FromException<int>(new DbException("Save failed"));
```

### Sequential Returns

```csharp
var results = new Queue<int>([1, 2, 3]);
knockOff.IService.GetNext.OnCall = (ko) => results.Dequeue();
```

### Async Methods

```csharp
knockOff.IRepository.GetUserAsync.OnCall = (ko, id) =>
    Task.FromResult<User?>(new User { Id = id });

knockOff.IRepository.SaveAsync.OnCall = (ko, entity) =>
    Task.FromResult(1);
```

### Events

```csharp
public interface IEventSource
{
    event EventHandler<string> DataReceived;
    event Action<int> ProgressChanged;
}

[KnockOff]
public partial class EventSourceKnockOff : IEventSource { }

var knockOff = new EventSourceKnockOff();
IEventSource source = knockOff;

// Subscribe tracking
source.DataReceived += (s, e) => Console.WriteLine(e);
Assert.Equal(1, knockOff.IEventSource.DataReceived.SubscribeCount);
Assert.True(knockOff.IEventSource.DataReceived.HasSubscribers);

// Raise events from tests
knockOff.IEventSource.DataReceived.Raise("test data");
Assert.True(knockOff.IEventSource.DataReceived.WasRaised);
Assert.Equal(1, knockOff.IEventSource.DataReceived.RaiseCount);

// Action-style events
knockOff.IEventSource.ProgressChanged.Raise(75);

// Reset vs Clear
knockOff.IEventSource.DataReceived.Reset();  // Clears tracking, keeps handlers
knockOff.IEventSource.DataReceived.Clear();  // Clears tracking AND handlers
```

### Method Overloads

When an interface has overloaded methods, each overload gets its own handler with a **numeric suffix** (1-based):

```csharp
public interface IOverloadedService
{
    void Process(string data);                           // Overload 1
    void Process(string data, int priority);             // Overload 2
    void Process(string data, int priority, bool async); // Overload 3
}

[KnockOff]
public partial class OverloadedServiceKnockOff : IOverloadedService { }

var knockOff = new OverloadedServiceKnockOff();
IOverloadedService service = knockOff;

// Each overload has its own handler (1-based numbering)
knockOff.IOverloadedService.Process1.CallCount;  // Calls to Process(string)
knockOff.IOverloadedService.Process2.CallCount;  // Calls to Process(string, int)
knockOff.IOverloadedService.Process3.CallCount;  // Calls to Process(string, int, bool)

// Set callbacks for each overload
knockOff.IOverloadedService.Process1.OnCall = (ko, data) => { /* 1-param */ };
knockOff.IOverloadedService.Process2.OnCall = (ko, data, priority) => { /* 2-param */ };
knockOff.IOverloadedService.Process3.OnCall = (ko, data, priority, async) => { /* 3-param */ };

// Proper types - no nullable wrappers
var args = knockOff.IOverloadedService.Process3.LastCallArgs;
Assert.Equal("test", args.Value.data);
Assert.Equal(5, args.Value.priority);  // int, not int?
Assert.True(args.Value.async);
```

Methods without overloads don't get a suffix:
```csharp
knockOff.IEmailService.SendEmail.CallCount;  // Single method - no suffix
```

### Out Parameters

Methods with `out` parameters are fully supported. Out parameters are outputs, not inputs, so they're excluded from tracking but included in callbacks.

```csharp
public interface IParser
{
    bool TryParse(string input, out int result);
    void GetData(out string name, out int count);
}

[KnockOff]
public partial class ParserKnockOff : IParser { }

var knockOff = new ParserKnockOff();
IParser parser = knockOff;

// Callback requires explicit delegate type for out/ref
knockOff.IParser.TryParse.OnCall =
    (IParser_TryParseHandler.TryParseDelegate)((ko, string input, out int result) =>
    {
        if (int.TryParse(input, out result))
            return true;
        result = 0;
        return false;
    });

// Call the method
var success = parser.TryParse("42", out var value);
Assert.True(success);
Assert.Equal(42, value);

// Tracking only includes INPUT params (not out params)
Assert.Equal("42", knockOff.IParser.TryParse.LastCallArg);
Assert.Equal(1, knockOff.IParser.TryParse.CallCount);
```

### Ref Parameters

Methods with `ref` parameters track the **input value** (before any callback modification).

```csharp
public interface IProcessor
{
    void Increment(ref int value);
    bool TryUpdate(string key, ref string value);
}

[KnockOff]
public partial class ProcessorKnockOff : IProcessor { }

var knockOff = new ProcessorKnockOff();
IProcessor processor = knockOff;

// Callback can modify ref params - explicit delegate type required
knockOff.IProcessor.Increment.OnCall =
    (IProcessor_IncrementHandler.IncrementDelegate)((ko, ref int value) =>
    {
        value = value * 2;  // Double it
    });

int x = 5;
processor.Increment(ref x);
Assert.Equal(10, x);  // Modified by callback

// Tracking captures INPUT value (before modification)
Assert.Equal(5, knockOff.IProcessor.Increment.LastCallArg);
```

## Moq Migration Quick Reference

| Moq | KnockOff |
|-----|----------|
| `new Mock<IService>()` | `new ServiceKnockOff()` |
| `mock.Object` | Cast or `knockOff.AsService()` |
| `.Setup(x => x.Method())` | `IService.Method.OnCall = (ko, ...) => ...` |
| `.Returns(value)` | `OnCall = (ko) => value` |
| `.ReturnsAsync(value)` | `OnCall = (ko) => Task.FromResult(value)` |
| `.Callback(action)` | Logic inside `OnCall` callback |
| `.Verify(Times.Once)` | `Assert.Equal(1, IService.Method.CallCount)` |
| `It.IsAny<T>()` | Implicit (callback receives all args) |
| `It.Is<T>(pred)` | Check in callback body |

## Additional Resources

For detailed guidance, see:
- [Customization Patterns](customization-patterns.md) - Deep dive on user methods vs callbacks
- [Handler API Reference](handler-api.md) - Complete API for all handler types
- [Moq Migration](moq-migration.md) - Step-by-step migration patterns
