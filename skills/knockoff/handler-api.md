# Handler API Reference

Every interface member gets a dedicated Handler class in its interface spy property. Access handlers via `knockOff.IInterfaceName.MemberName`.

## Handler Types

| Interface Member | Handler Type | Access Pattern |
|------------------|--------------|----------------|
| Method | `{InterfaceName}_{MethodName}Handler` | `IInterface.MethodName` |
| Property | `{InterfaceName}_{PropertyName}Handler` | `IInterface.PropertyName` |
| Indexer | `{InterfaceName}_{KeyType}IndexerHandler` | `IInterface.StringIndexer`, `IInterface.IntIndexer`, etc. |
| Event | `{InterfaceName}_{EventName}Handler` | `IInterface.EventName` |
| Generic Method | `{InterfaceName}_{MethodName}Handler` | `IInterface.MethodName.Of<T>()` |

## Method Handler

For interface methods: `void M()`, `T M()`, `void M(args)`, `T M(args)`

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `CallCount` | `int` | Number of times the method was called |
| `WasCalled` | `bool` | `true` if `CallCount > 0` |
| `LastCallArg` | `T` | Last argument (single-param methods only) |
| `LastCallArgs` | `(T1, T2, ...)?` | Last arguments as named tuple (multi-param methods) |
| `AllCalls` | `List<T>` or `List<(T1, T2, ...)>` | All call arguments in order |

### Callbacks

| Property | Type | Description |
|----------|------|-------------|
| `OnCall` | See below | Callback invoked when method is called |

**OnCall Signatures:**

| Method Signature | OnCall Type |
|------------------|-------------|
| `void M()` | `Action<TKnockOff>?` |
| `void M(T arg)` | `Action<TKnockOff, T>?` |
| `void M(T1 a, T2 b, ...)` | `Action<TKnockOff, T1, T2, ...>?` |
| `R M()` | `Func<TKnockOff, R>?` |
| `R M(T arg)` | `Func<TKnockOff, T, R>?` |
| `R M(T1 a, T2 b, ...)` | `Func<TKnockOff, T1, T2, ..., R>?` |

### Methods

| Method | Description |
|--------|-------------|
| `Reset()` | Clears `CallCount`, `AllCalls`, and `OnCall` |
| `RecordCall(...)` | Internal - records invocation (called by generated code) |

### Examples

```csharp
// Void method, no params
Assert.True(knockOff.IService.Initialize.WasCalled);
knockOff.IService.Initialize.OnCall = (ko) => { };

// Return method, single param
Assert.Equal(42, knockOff.IService.GetById.LastCallArg);
knockOff.IService.GetById.OnCall = (ko, id) => new User { Id = id };

// Multiple params
var args = knockOff.IService.Create.LastCallArgs;
Assert.Equal("Test", args?.name);
knockOff.IService.Create.OnCall = (ko, name, value) =>
    new Entity { Name = name };
```

## Property Handler

For interface properties: `T Prop { get; }`, `T Prop { set; }`, `T Prop { get; set; }`

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `GetCount` | `int` | Number of getter invocations |
| `SetCount` | `int` | Number of setter invocations |
| `LastSetValue` | `T?` | Last value passed to setter |
| `OnGet` | `Func<TKnockOff, T>?` | Getter callback |
| `OnSet` | `Action<TKnockOff, T>?` | Setter callback |

### Methods

| Method | Description |
|--------|-------------|
| `Reset()` | Clears counts, `LastSetValue`, `OnGet`, and `OnSet` |

### Behavior

- When `OnGet` is set, backing field is NOT read
- When `OnSet` is set, backing field is NOT written
- `Reset()` does NOT clear backing field

### Backing Field

Each property has a backing field with interface prefix:
- `IService_NameBacking` for `Name` property on `IService`

### Examples

```csharp
// Tracking
Assert.Equal(3, knockOff.IService.Name.GetCount);
Assert.Equal(2, knockOff.IService.Name.SetCount);
Assert.Equal("Last", knockOff.IService.Name.LastSetValue);

// Callbacks
knockOff.IService.Name.OnGet = (ko) => "Always This";
knockOff.IService.Name.OnSet = (ko, value) => capturedValue = value;

// Backing field (direct access)
knockOff.IService_NameBacking = "Pre-populated";
```

## Indexer Handler

For interface indexers. Named by key type: `StringIndexer`, `IntIndexer`, etc.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `GetCount` | `int` | Number of getter invocations |
| `SetCount` | `int` | Number of setter invocations |
| `LastGetKey` | `TKey?` | Last key accessed |
| `AllGetKeys` | `List<TKey>` | All keys accessed |
| `LastSetEntry` | `(TKey, TValue)?` | Last key-value from setter |
| `AllSetEntries` | `List<(TKey, TValue)>` | All set entries |
| `OnGet` | `Func<TKnockOff, TKey, TValue>?` | Getter callback |
| `OnSet` | `Action<TKnockOff, TKey, TValue>?` | Setter callback |

### Methods

| Method | Description |
|--------|-------------|
| `Reset()` | Clears tracking and callbacks |

### Backing Dictionary

Each indexer has a backing dictionary with interface prefix:
- `IPropertyStore_StringIndexerBacking` for `this[string key]` on `IPropertyStore`
- `IList_IntIndexerBacking` for `this[int index]` on `IList`

### Getter Behavior

When **no `OnGet`** is set:
1. Backing dictionary checked first
2. Then `default(TValue)`

When **`OnGet` is set**:
- Callback completely replaces getter logic
- Backing dictionary NOT checked automatically
- Include it manually in your callback if needed

### Examples

```csharp
// Pre-populate backing
knockOff.IPropertyStore_StringIndexerBacking["Key1"] = value1;
knockOff.IPropertyStore_StringIndexerBacking["Key2"] = value2;

// Track access
_ = store["Key1"];
_ = store["Key2"];
Assert.Equal(2, knockOff.IPropertyStore.StringIndexer.GetCount);
Assert.Equal("Key2", knockOff.IPropertyStore.StringIndexer.LastGetKey);

// Dynamic getter
knockOff.IPropertyStore.StringIndexer.OnGet = (ko, key) =>
{
    if (key == "special") return specialValue;
    return ko.IPropertyStore_StringIndexerBacking.GetValueOrDefault(key);
};

// Track setter
store["NewKey"] = newValue;
Assert.Equal("NewKey", knockOff.IPropertyStore.StringIndexer.LastSetEntry?.key);

// Intercept setter
knockOff.IPropertyStore.StringIndexer.OnSet = (ko, key, value) =>
{
    // Custom logic
    // Value does NOT go to backing dictionary
};
```

## Event Handler

For interface events: `event EventHandler E`, `event EventHandler<T> E`, `event Action<T> E`

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `SubscribeCount` | `int` | Number of times handlers were added |
| `UnsubscribeCount` | `int` | Number of times handlers were removed |
| `HasSubscribers` | `bool` | `true` if at least one handler is attached |
| `RaiseCount` | `int` | Number of times event was raised |
| `WasRaised` | `bool` | `true` if `RaiseCount > 0` |
| `LastRaiseArgs` | `T?` | Arguments from most recent raise |
| `AllRaises` | `IReadOnlyList<T>` | All raise arguments in order |

### Args Type by Delegate

| Delegate Type | Args Tracking Type |
|--------------|-------------------|
| `EventHandler` | `(object? sender, EventArgs e)` |
| `EventHandler<T>` | `(object? sender, T e)` |
| `Action` | None (no args) |
| `Action<T>` | `T` |
| `Action<T1, T2>` | `(T1 arg1, T2 arg2)` |
| `Action<T1, T2, T3>` | `(T1 arg1, T2 arg2, T3 arg3)` |

### Methods

| Method | Description |
|--------|-------------|
| `Raise(...)` | Raises the event and records arguments |
| `Reset()` | Clears counts and `AllRaises`, keeps handlers attached |
| `Clear()` | Clears counts, `AllRaises`, AND removes all handlers |

### Raise Signatures

| Delegate Type | Raise Overloads |
|--------------|----------------|
| `EventHandler` | `Raise()`, `Raise(sender, e)` |
| `EventHandler<T>` | `Raise(e)`, `Raise(sender, e)` |
| `Action` | `Raise()` |
| `Action<T>` | `Raise(arg)` |
| `Action<T1, T2>` | `Raise(arg1, arg2)` |

### Behavior Notes

- `Raise()` works even with no subscribers (no exception)
- `Reset()` clears tracking but keeps handlers attached
- `Clear()` clears both tracking and handlers
- All raises are tracked in `AllRaises` regardless of subscriber count

### Examples

```csharp
// Subscribe tracking
source.DataReceived += handler;
Assert.Equal(1, knockOff.IEventSource.DataReceived.SubscribeCount);
Assert.True(knockOff.IEventSource.DataReceived.HasSubscribers);

// Raise event
knockOff.IEventSource.DataReceived.Raise("test data");
Assert.True(knockOff.IEventSource.DataReceived.WasRaised);
Assert.Equal("test data", knockOff.IEventSource.DataReceived.LastRaiseArgs?.e);

// EventHandler (non-generic)
knockOff.IEventSource.Completed.Raise(); // null sender, EventArgs.Empty

// Action with params
knockOff.IEventSource.ProgressChanged.Raise(75);
knockOff.IEventSource.DataUpdated.Raise("key", 42);

// All raises
var allRaises = knockOff.IEventSource.DataReceived.AllRaises;
Assert.Equal(3, allRaises.Count);

// Reset vs Clear
knockOff.IEventSource.DataReceived.Reset();  // Clears tracking, keeps handlers
knockOff.IEventSource.DataReceived.Clear();  // Clears tracking AND handlers
```

## Overloaded Method Handlers

When an interface has overloaded methods, each overload gets its own handler with a **numeric suffix** (1-based):

- `Process1` - first overload
- `Process2` - second overload
- `Process3` - third overload

Methods without overloads don't get a suffix.

### Properties

Each overload handler has its own tracking:

| Property | Type | Description |
|----------|------|-------------|
| `CallCount` | `int` | Calls to this specific overload |
| `WasCalled` | `bool` | `CallCount > 0` |
| `LastCallArg` / `LastCallArgs` | varies | Arguments for this overload only |
| `AllCalls` | varies | All calls to this overload only |

### Examples

```csharp
public interface IService
{
    void Process(string data);
    void Process(string data, int priority);
    int Calculate(int value);
    int Calculate(int a, int b);
}

var knockOff = new ServiceKnockOff();
IService service = knockOff;

// Each overload tracked separately
service.Process("a");
service.Process("b", 1);
Assert.Equal(1, knockOff.IService.Process1.CallCount);  // Process(string)
Assert.Equal(1, knockOff.IService.Process2.CallCount);  // Process(string, int)

// Each overload has its own callback
knockOff.IService.Process1.OnCall = (ko, data) => { };
knockOff.IService.Process2.OnCall = (ko, data, priority) => { };

// Return methods
knockOff.IService.Calculate1.OnCall = (ko, value) => value * 2;
knockOff.IService.Calculate2.OnCall = (ko, a, b) => a + b;

Assert.Equal(10, service.Calculate(5));    // Calculate1
Assert.Equal(8, service.Calculate(3, 5));  // Calculate2
```

## Out Parameter Methods

Methods with `out` parameters require explicit delegate type for callbacks.

### Tracking Behavior

- **Out params are NOT tracked** - they're outputs, not inputs
- Only input parameters appear in `LastCallArg`/`LastCallArgs`/`AllCalls`
- Methods with only out params track `CallCount` only

### Callback Syntax

```csharp
// Explicit delegate type required
knockOff.IParser.TryParse.OnCall =
    (IParser_TryParseHandler.TryParseDelegate)((ko, string input, out int result) =>
    {
        result = int.Parse(input);
        return true;
    });

// Void with multiple out params
knockOff.IService.GetData.OnCall =
    (IService_GetDataHandler.GetDataDelegate)((ko, out string name, out int count) =>
    {
        name = "Test";
        count = 42;
    });
```

### No Callback Behavior

Without a callback:
- Out params initialize to `default`
- Void methods complete silently
- Methods with return values throw `InvalidOperationException`

## Ref Parameter Methods

Methods with `ref` parameters track the **input value** before any modification.

### Tracking Behavior

- **Ref params ARE tracked** - they have an input value
- `LastCallArg`/`AllCalls` contains the value at call time
- Modifications by callback are NOT reflected in tracking

### Callback Syntax

```csharp
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
        value = value.ToUpper();
        return true;
    });
```

### Tracking Example

```csharp
int x = 5;
processor.Increment(ref x);

Assert.Equal(10, x);  // Modified
Assert.Equal(5, knockOff.IProcessor.Increment.LastCallArg);  // Original input value
```

## Reset Behavior Summary

| Handler Type | Reset Clears | Reset Does NOT Clear |
|--------------|--------------|----------------------|
| Method | `CallCount`, `AllCalls`, `OnCall` | - |
| Property | `GetCount`, `SetCount`, `LastSetValue`, `OnGet`, `OnSet` | Backing field |
| Indexer | `GetCount`, `SetCount`, `AllGetKeys`, `AllSetEntries`, `OnGet`, `OnSet` | Backing dictionary |
| Event | `SubscribeCount`, `UnsubscribeCount`, `RaiseCount`, `AllRaises` | Handlers (use `Clear()` to remove) |
| Generic Method | All typed handlers, `CalledTypeArguments` | - |
| Generic Method `.Of<T>()` | `CallCount`, `AllCalls`, `OnCall` | - |

## Async Method Handlers

Async methods use the same handler structure as sync methods. The `OnCall` callback returns the async type:

| Return Type | OnCall Return Type |
|-------------|-------------------|
| `Task` | `Task` |
| `Task<T>` | `Task<T>` |
| `ValueTask` | `ValueTask` |
| `ValueTask<T>` | `ValueTask<T>` |

```csharp
knockOff.IRepository.GetByIdAsync.OnCall = (ko, id) =>
    Task.FromResult<User?>(new User { Id = id });

knockOff.IRepository.SaveAsync.OnCall = (ko, entity) =>
    Task.FromException<int>(new DbException("Failed"));
```

## Generic Method Handlers

Generic methods use a two-tier handler with the `.Of<T>()` pattern.

### Base Handler Properties

| Property | Type | Description |
|----------|------|-------------|
| `TotalCallCount` | `int` | Total calls across all type arguments |
| `WasCalled` | `bool` | `true` if called with any type argument |
| `CalledTypeArguments` | `IReadOnlyList<Type>` | All type arguments used |

### Base Handler Methods

| Method | Description |
|--------|-------------|
| `Of<T>()` | Get typed handler for specific type argument(s) |
| `Reset()` | Clear all typed handlers |

For multiple type parameters: `Of<T1, T2>()` or `Of<T1, T2, T3>()`.

### Typed Handler Properties (via `.Of<T>()`)

| Property | Type | Description |
|----------|------|-------------|
| `CallCount` | `int` | Calls with this type argument |
| `WasCalled` | `bool` | `true` if `CallCount > 0` |
| `LastCallArg` | `T?` | Last non-generic argument (if method has params) |
| `AllCalls` | `IReadOnlyList<T>` | All non-generic arguments |
| `OnCall` | Delegate | Callback for this type argument |

### Typed Handler Methods

| Method | Description |
|--------|-------------|
| `Reset()` | Clear this typed handler |

### OnCall Signatures

| Method Signature | OnCall Type |
|------------------|-------------|
| `void M<T>()` | `Action<TKnockOff>?` |
| `void M<T>(T value)` | `Action<TKnockOff, T>?` |
| `T M<T>()` | `Func<TKnockOff, T>?` |
| `T M<T>(string json)` | `Func<TKnockOff, string, T>?` |
| `TOut M<TIn, TOut>(TIn input)` | `Func<TKnockOff, TIn, TOut>?` |

### Examples

```csharp
// Configure per type
knockOff.ISerializer.Deserialize.Of<User>().OnCall = (ko, json) =>
    JsonSerializer.Deserialize<User>(json)!;

// Per-type tracking
Assert.Equal(2, knockOff.ISerializer.Deserialize.Of<User>().CallCount);
Assert.Equal("{...}", knockOff.ISerializer.Deserialize.Of<User>().LastCallArg);

// Aggregate tracking
Assert.Equal(5, knockOff.ISerializer.Deserialize.TotalCallCount);
var types = knockOff.ISerializer.Deserialize.CalledTypeArguments;

// Multiple type parameters
knockOff.IConverter.Convert.Of<string, int>().OnCall = (ko, s) => s.Length;

// Reset single type vs all types
knockOff.ISerializer.Deserialize.Of<User>().Reset();  // Single type
knockOff.ISerializer.Deserialize.Reset();              // All types
```

### Smart Defaults for Generic Methods

Without `OnCall`, generic methods use runtime defaults:

| Return Type | Default Behavior |
|-------------|------------------|
| Value type | `default(T)` |
| Type with parameterless ctor | `new T()` |
| Nullable reference (`T?`) | `null` |
| Other | Throws `InvalidOperationException` |

## Smart Default Return Values

Without callback or user method, KnockOff returns sensible defaults:

| Return Type | Default Value | Example |
|-------------|---------------|---------|
| Value types | `default` | `int` → `0`, `bool` → `false` |
| Nullable refs | `null` | `string?` → `null` |
| Types with `new()` | `new T()` | `List<T>` → empty list |
| Collection interfaces | concrete type | `IList<T>` → `new List<T>()` |
| `Task` | `Task.CompletedTask` | async void-like |
| `Task<T>` | `Task.FromResult(smartDefault)` | applies smart default to `T` |
| `ValueTask` | `default(ValueTask)` | async void-like |
| `ValueTask<T>` | `new ValueTask<T>(smartDefault)` | applies smart default to `T` |
| Other non-nullable | throws `InvalidOperationException` | `string`, `IDisposable` |

**Collection Interface Mapping:**

| Interface | Concrete Type |
|-----------|---------------|
| `IEnumerable<T>`, `ICollection<T>`, `IList<T>` | `List<T>` |
| `IReadOnlyList<T>`, `IReadOnlyCollection<T>` | `List<T>` |
| `IDictionary<K,V>`, `IReadOnlyDictionary<K,V>` | `Dictionary<K,V>` |
| `ISet<T>` | `HashSet<T>` |

```csharp
// Examples of smart defaults
service.GetCount();       // 0 (int)
service.GetItems();       // new List<string>()
service.GetIList();       // new List<string>() (from IList<string>)
service.GetOptional();    // null (nullable ref)
service.GetDisposable();  // throws (can't instantiate interface)

// Task<T> applies smart default to inner type
await service.GetListAsync();  // Task.FromResult(new List<string>())
```
