# Customization Patterns

KnockOff provides **two complementary patterns** for customizing stub behavior. This is a key differentiator from Moq.

## The Duality

| Pattern | When | Scope | Precedence |
|---------|------|-------|------------|
| User Methods | Compile-time | All tests | 2nd |
| Callbacks | Runtime | Per-test | 1st |

## Pattern 1: User-Defined Methods

Define protected methods in your stub class matching interface method signatures.

### Basic Example

```csharp
public interface ICalculator
{
    int Add(int a, int b);
    double Divide(int numerator, int denominator);
}

[KnockOff]
public partial class CalculatorKnockOff : ICalculator
{
    protected int Add(int a, int b) => a + b;

    protected double Divide(int numerator, int denominator) =>
        denominator == 0 ? 0 : (double)numerator / denominator;
}
```

### Async Methods

```csharp
[KnockOff]
public partial class RepoKnockOff : IRepository
{
    protected Task<User?> GetByIdAsync(int id) =>
        Task.FromResult<User?>(new User { Id = id });

    protected ValueTask<int> CountAsync() =>
        new ValueTask<int>(100);
}
```

### Rules

| Rule | Description |
|------|-------------|
| Access modifier | Must be `protected` |
| Name | Must match interface method name exactly |
| Parameters | Must match types and count |
| Return type | Must match (including Task/ValueTask) |
| Applies to | Methods only (not properties/indexers) |

### When to Use

- Same behavior needed across all tests using this stub
- Shared test fixtures
- Simple, deterministic returns
- No access to test-specific state needed

## Pattern 2: Callbacks

Set delegates on interface spy handlers at runtime for per-test customization.

### Method Callbacks

Use `OnCall =` property assignment:

```csharp
// Void, no params
knockOff.IService.Initialize.OnCall = (ko) =>
{
    // Custom initialization logic
};

// Return, single param
knockOff.IRepository.GetById.OnCall = (ko, id) =>
    new User { Id = id, Name = "Mocked" };

// Return, multiple params - individual parameters
knockOff.IService.Search.OnCall = (ko, query, limit, offset) =>
    results.Skip(offset).Take(limit).ToList();
```

### Property Callbacks

```csharp
// Getter
knockOff.IService.CurrentUser.OnGet = (ko) =>
    new User { Name = "TestUser" };

// Setter
knockOff.IService.CurrentUser.OnSet = (ko, value) =>
{
    capturedUser = value;
    // Note: Value does NOT go to backing field
};
```

### Indexer Callbacks

```csharp
// Getter (receives key)
knockOff.IPropertyStore.StringIndexer.OnGet = (ko, key) => key switch
{
    "admin" => adminConfig,
    "guest" => guestConfig,
    _ => null
};

// Setter (receives key and value)
knockOff.IPropertyStore.StringIndexer.OnSet = (ko, key, value) =>
{
    // Custom logic
    // Note: Value does NOT go to backing dictionary
};
```

### Overloaded Method Callbacks

When an interface has overloaded methods, each overload has its own handler with a numeric suffix (1-based):

```csharp
public interface IService
{
    void Process(string data);
    void Process(string data, int priority);
    int Calculate(int value);
    int Calculate(int a, int b);
}

[KnockOff]
public partial class ServiceKnockOff : IService { }

var knockOff = new ServiceKnockOff();

// Each overload has its own handler
knockOff.IService.Process1.OnCall = (ko, data) => { /* 1-param overload */ };
knockOff.IService.Process2.OnCall = (ko, data, priority) => { /* 2-param overload */ };

// Methods with return values work the same way
knockOff.IService.Calculate1.OnCall = (ko, value) => value * 2;
knockOff.IService.Calculate2.OnCall = (ko, a, b) => a + b;
```

### Out Parameter Callbacks

Methods with `out` parameters require explicit delegate type:

```csharp
public interface IParser
{
    bool TryParse(string input, out int result);
    void GetStats(out int count, out double average);
}

[KnockOff]
public partial class ParserKnockOff : IParser { }

var knockOff = new ParserKnockOff();

// REQUIRED: Explicit delegate type
knockOff.IParser.TryParse.OnCall =
    (IParser_TryParseHandler.TryParseDelegate)((ko, string input, out int result) =>
    {
        if (int.TryParse(input, out result))
            return true;
        result = 0;
        return false;
    });

// Void with multiple out params
knockOff.IParser.GetStats.OnCall =
    (IParser_GetStatsHandler.GetStatsDelegate)((ko, out int count, out double average) =>
    {
        count = 42;
        average = 3.14;
    });
```

**Tracking**: Out parameters are NOT tracked (they're outputs). Only input parameters appear in `LastCallArg`/`AllCalls`.

### Ref Parameter Callbacks

Methods with `ref` parameters also require explicit delegate type. Ref parameters ARE tracked (input value before modification).

```csharp
public interface IProcessor
{
    void Increment(ref int value);
    bool TryUpdate(string key, ref string value);
}

[KnockOff]
public partial class ProcessorKnockOff : IProcessor { }

var knockOff = new ProcessorKnockOff();

// Explicit delegate type required
knockOff.IProcessor.Increment.OnCall =
    (IProcessor_IncrementHandler.IncrementDelegate)((ko, ref int value) =>
    {
        value = value * 2;  // Modify the ref param
    });

// Mixed regular + ref params
knockOff.IProcessor.TryUpdate.OnCall =
    (IProcessor_TryUpdateHandler.TryUpdateDelegate)((ko, string key, ref string value) =>
    {
        if (key == "valid")
        {
            value = value.ToUpper();
            return true;
        }
        return false;
    });

// Tracking captures INPUT value (before modification)
int x = 5;
processor.Increment(ref x);
Assert.Equal(10, x);  // Modified
Assert.Equal(5, knockOff.IProcessor.Increment.LastCallArg);  // Original input
```

### Callback Signatures

| Member | Callback | Signature |
|--------|----------|-----------|
| Method (no params) | `OnCall =` | `Action<TKnockOff>` or `Func<TKnockOff, R>` |
| Method (with params) | `OnCall =` | `Action<TKnockOff, T1, T2, ...>` or `Func<TKnockOff, T1, T2, ..., R>` |
| Property getter | `OnGet =` | `Func<TKnockOff, T>` |
| Property setter | `OnSet =` | `Action<TKnockOff, T>` |
| Indexer getter | `OnGet =` | `Func<TKnockOff, TKey, TValue>` |
| Indexer setter | `OnSet =` | `Action<TKnockOff, TKey, TValue>` |

### When to Use

- Different behavior needed per test
- Dynamic returns based on arguments
- Side effects (capturing, logging)
- Access to Spy state (check if other methods called)
- Temporarily override user method

## Priority Order

```
+---------------------------------------------+
| 1. CALLBACK (if set)                        |
|    -> Takes precedence, stops here          |
+---------------------------------------------+
| 2. USER METHOD (if defined)                 |
|    -> Methods only, stops here              |
+---------------------------------------------+
| 3. DEFAULT                                  |
|    -> Properties: backing field             |
|    -> Methods: null (nullable) or           |
|               throw (non-nullable) or       |
|               silent (void)                 |
|    -> Indexers: backing dict -> null/throw  |
+---------------------------------------------+
```

### Priority in Action

```csharp
[KnockOff]
public partial class ServiceKnockOff : IService
{
    protected int Calculate(int x) => x * 2;  // User method
}

var knockOff = new ServiceKnockOff();
IService service = knockOff;

// No callback -> uses user method
var r1 = service.Calculate(5);  // Returns 10

// Callback -> overrides user method
knockOff.IService.Calculate.OnCall = (ko, x) => x * 100;
var r2 = service.Calculate(5);  // Returns 500

// Reset -> back to user method
knockOff.IService.Calculate.Reset();
var r3 = service.Calculate(5);  // Returns 10
```

## Reset Behavior

`Reset()` clears:
- Call tracking (`CallCount`, `AllCalls`, etc.)
- Callbacks (`OnCall`, `OnGet`, `OnSet`)

Does NOT clear:
- Backing fields for properties
- Backing dictionaries for indexers

```csharp
knockOff.IRepository.GetUser.OnCall = (ko, id) => specialUser;
service.GetUser(1);
service.GetUser(2);

knockOff.IRepository.GetUser.Reset();

Assert.Equal(0, knockOff.IRepository.GetUser.CallCount);  // Tracking cleared
// Callback also cleared - now falls back to user method or default
```

## Combining Both Patterns

```csharp
[KnockOff]
public partial class RepoKnockOff : IRepository
{
    // Default: not found
    protected User? GetById(int id) => null;
}

// Test 1: Uses default
Assert.Null(knockOff.AsRepository().GetById(999));

// Test 2: Override for specific IDs
knockOff.IRepository.GetById.OnCall = (ko, id) => id == 1
    ? new User { Name = "Admin" }
    : null;

// Test 3: Reset and different behavior
knockOff.IRepository.GetById.Reset();
knockOff.IRepository.GetById.OnCall = (ko, id) =>
    new User { Name = $"User-{id}" };
```

## Decision Guide

| Question | Recommendation |
|----------|----------------|
| Same behavior in all tests? | User method |
| Different per test? | Callback |
| Need to capture call info? | Either (tracking always available) |
| Shared across test classes? | User method |
| Complex conditional logic? | Callback |
| Just static value? | User method (simpler) |
| Need to verify side effects? | Callback |
