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

<!-- snippet: skill:customization-patterns:user-method-basic -->
```csharp
[KnockOff]
public partial class CpCalculatorKnockOff : ICpCalculator
{
    protected int Add(int a, int b) => a + b;

    protected double Divide(int numerator, int denominator) =>
        denominator == 0 ? 0 : (double)numerator / denominator;
}
```
<!-- /snippet -->

### Async Methods

<!-- snippet: skill:customization-patterns:user-method-async -->
```csharp
[KnockOff]
public partial class CpRepoKnockOff : ICpRepository
{
    protected Task<CpUser?> GetByIdAsync(int id) =>
        Task.FromResult<CpUser?>(new CpUser { Id = id });

    protected ValueTask<int> CountAsync() =>
        new ValueTask<int>(100);
}
```
<!-- /snippet -->

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

<!-- snippet: skill:customization-patterns:callback-method -->
```csharp
[KnockOff]
public partial class CpCallbackServiceKnockOff : ICpCallbackService { }

// Void, no params
// knockOff.ICpCallbackService.Initialize.OnCall = (ko) =>
// {
//     // Custom initialization logic
// };

// Return, single param
// knockOff.ICpCallbackService.GetById.OnCall = (ko, id) =>
//     new CpUser { Id = id, Name = "Mocked" };

// Return, multiple params - individual parameters
// knockOff.ICpCallbackService.Search.OnCall = (ko, query, limit, offset) =>
//     results.Skip(offset).Take(limit).ToList();
```
<!-- /snippet -->

### Property Callbacks

<!-- snippet: skill:customization-patterns:callback-property -->
```csharp
[KnockOff]
public partial class CpPropertyServiceKnockOff : ICpPropertyService { }

// Getter
// knockOff.ICpPropertyService.CurrentUser.OnGet = (ko) =>
//     new CpUser { Name = "TestUser" };

// Setter
// knockOff.ICpPropertyService.CurrentUser.OnSet = (ko, value) =>
// {
//     capturedUser = value;
//     // Note: Value does NOT go to backing field
// };
```
<!-- /snippet -->

### Indexer Callbacks

<!-- snippet: skill:customization-patterns:callback-indexer -->
```csharp
[KnockOff]
public partial class CpPropertyStoreKnockOff : ICpPropertyStore { }

// Getter (receives key)
// knockOff.ICpPropertyStore.StringIndexer.OnGet = (ko, key) => key switch
// {
//     "admin" => adminConfig,
//     "guest" => guestConfig,
//     _ => null
// };

// Setter (receives key and value)
// knockOff.ICpPropertyStore.StringIndexer.OnSet = (ko, key, value) =>
// {
//     // Custom logic
//     // Note: Value does NOT go to backing dictionary
// };
```
<!-- /snippet -->

### Overloaded Method Callbacks

When an interface has overloaded methods, each overload has its own handler with a numeric suffix (1-based):

<!-- snippet: skill:customization-patterns:callback-overloads -->
```csharp
[KnockOff]
public partial class CpOverloadServiceKnockOff : ICpOverloadService { }

// var knockOff = new CpOverloadServiceKnockOff();

// Each overload has its own handler
// knockOff.ICpOverloadService.Process1.OnCall = (ko, data) => { /* 1-param overload */ };
// knockOff.ICpOverloadService.Process2.OnCall = (ko, data, priority) => { /* 2-param overload */ };

// Methods with return values work the same way
// knockOff.ICpOverloadService.Calculate1.OnCall = (ko, value) => value * 2;
// knockOff.ICpOverloadService.Calculate2.OnCall = (ko, a, b) => a + b;
```
<!-- /snippet -->

### Out Parameter Callbacks

Methods with `out` parameters require explicit delegate type:

<!-- snippet: skill:customization-patterns:callback-out-params -->
```csharp
[KnockOff]
public partial class CpParserKnockOff : ICpParser { }

// var knockOff = new CpParserKnockOff();

// REQUIRED: Explicit delegate type
// knockOff.ICpParser.TryParse.OnCall =
//     (ICpParser_TryParseHandler.TryParseDelegate)((ko, string input, out int result) =>
//     {
//         if (int.TryParse(input, out result))
//             return true;
//         result = 0;
//         return false;
//     });

// Void with multiple out params
// knockOff.ICpParser.GetStats.OnCall =
//     (ICpParser_GetStatsHandler.GetStatsDelegate)((ko, out int count, out double average) =>
//     {
//         count = 42;
//         average = 3.14;
//     });
```
<!-- /snippet -->

**Tracking**: Out parameters are NOT tracked (they're outputs). Only input parameters appear in `LastCallArg`/`AllCalls`.

### Ref Parameter Callbacks

Methods with `ref` parameters also require explicit delegate type. Ref parameters ARE tracked (input value before modification).

<!-- snippet: skill:customization-patterns:callback-ref-params -->
```csharp
[KnockOff]
public partial class CpProcessorKnockOff : ICpProcessor { }

// var knockOff = new CpProcessorKnockOff();

// Explicit delegate type required
// knockOff.ICpProcessor.Increment.OnCall =
//     (ICpProcessor_IncrementHandler.IncrementDelegate)((ko, ref int value) =>
//     {
//         value = value * 2;  // Modify the ref param
//     });

// Mixed regular + ref params
// knockOff.ICpProcessor.TryUpdate.OnCall =
//     (ICpProcessor_TryUpdateHandler.TryUpdateDelegate)((ko, string key, ref string value) =>
//     {
//         if (key == "valid")
//         {
//             value = value.ToUpper();
//             return true;
//         }
//         return false;
//     });

// Tracking captures INPUT value (before modification)
// int x = 5;
// processor.Increment(ref x);
// Assert.Equal(10, x);  // Modified
// Assert.Equal(5, knockOff.ICpProcessor.Increment.LastCallArg);  // Original input
```
<!-- /snippet -->

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

<!-- snippet: skill:customization-patterns:priority-in-action -->
```csharp
[KnockOff]
public partial class CpPriorityServiceKnockOff : ICpPriorityService
{
    protected int Calculate(int x) => x * 2;  // User method
}

// var knockOff = new CpPriorityServiceKnockOff();
// ICpPriorityService service = knockOff;

// No callback -> uses user method
// var r1 = service.Calculate(5);  // Returns 10

// Callback -> overrides user method
// knockOff.ICpPriorityService.Calculate.OnCall = (ko, x) => x * 100;
// var r2 = service.Calculate(5);  // Returns 500

// Reset -> back to user method
// knockOff.ICpPriorityService.Calculate.Reset();
// var r3 = service.Calculate(5);  // Returns 10
```
<!-- /snippet -->

## Reset Behavior

`Reset()` clears:
- Call tracking (`CallCount`, `AllCalls`, etc.)
- Callbacks (`OnCall`, `OnGet`, `OnSet`)

Does NOT clear:
- Backing fields for properties
- Backing dictionaries for indexers

<!-- snippet: skill:customization-patterns:reset-behavior -->
```csharp
[KnockOff]
public partial class CpResetRepositoryKnockOff : ICpResetRepository { }

// knockOff.ICpResetRepository.GetUser.OnCall = (ko, id) => specialUser;
// service.GetUser(1);
// service.GetUser(2);

// knockOff.ICpResetRepository.GetUser.Reset();

// Assert.Equal(0, knockOff.ICpResetRepository.GetUser.CallCount);  // Tracking cleared
// Callback also cleared - now falls back to user method or default
```
<!-- /snippet -->

## Combining Both Patterns

<!-- snippet: skill:customization-patterns:combining-patterns -->
```csharp
[KnockOff]
public partial class CpCombinedRepoKnockOff : ICpCombinedRepository
{
    // Default: not found
    protected CpUser? GetById(int id) => null;
}

// Test 1: Uses default
// Assert.Null(knockOff.AsCustCombinedRepository().GetById(999));

// Test 2: Override for specific IDs
// knockOff.ICpCombinedRepository.GetById.OnCall = (ko, id) => id == 1
//     ? new CpUser { Name = "Admin" }
//     : null;

// Test 3: Reset and different behavior
// knockOff.ICpCombinedRepository.GetById.Reset();
// knockOff.ICpCombinedRepository.GetById.OnCall = (ko, id) =>
//     new CpUser { Name = $"User-{id}" };
```
<!-- /snippet -->

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
