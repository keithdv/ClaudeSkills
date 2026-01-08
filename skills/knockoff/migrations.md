# KnockOff Migration Guide

Breaking changes across KnockOff versions and how to migrate.

## v10.9.0

### Class Stub Composition Pattern

Class stubs now use composition instead of inheritance, providing a unified API with interface stubs.

| Before (v10.8.0) | After (v10.9.0) |
|------------------|-----------------|
| `stub.Interceptor.Member` | `stub.Member` |
| `stub.Interceptor.Member.OnCall` | `stub.Member.OnCall` |
| `TargetClass x = stub;` | `TargetClass x = stub.Object;` |
| `PassToMethod(stub)` | `PassToMethod(stub.Object)` |

**Before (v10.8.0):**
```csharp
var stub = new Stubs.UserService();
stub.Interceptor.GetUser.OnCall = (ko, id) => new User { Id = id };
UserService service = stub;  // Direct assignment
```

**After (v10.9.0):**
```csharp
var stub = new Stubs.UserService();
stub.GetUser.OnCall = (ko, id) => new User { Id = id };  // Direct access!
UserService service = stub.Object;  // Use .Object for type
```

**Why This Change:**
- Unified API: Interface and class stubs now use identical patterns
- No naming conflicts: Interceptor properties can match class member names
- Clearer semantics: Stub is configuration, `.Object` is the instance

### v10.9.0 Checklist

1. [ ] Search for `.Interceptor.` on class stubs → remove `.Interceptor`
2. [ ] Search for assignments of class stubs to target type → add `.Object`
3. [ ] Search for class stub passed as method argument → add `.Object`
4. [ ] Rebuild and run tests

---

## v10.8.0

### Terminology Change: Handler → Interceptor

Generated tracking/callback classes now use "Interceptor" naming:

| Before (v10.7.0) | After (v10.8.0) |
|------------------|-----------------|
| `IUserService_GetUserHandler` | `IUserService_GetUserInterceptor` |
| `IUserServiceKO` | `IUserServiceInterceptors` |

**Most code unaffected.** The common access pattern is unchanged:

```csharp
// Works the same
knockOff.IUserService.GetUser.CallCount
knockOff.IUserService.GetUser.OnCall = (ko, id) => new User();
```

**Migration required** only if you:
1. Reference generated interceptor class types directly
2. Use out/ref parameter callbacks with explicit delegate types

```csharp
// Before
IUserServiceKO ko = knockOff.IUserService;
knockOff.IParser.TryParse.OnCall =
    (IParser_TryParseHandler.TryParseDelegate)(...);

// After
IUserServiceInterceptors interceptors = knockOff.IUserService;
knockOff.IParser.TryParse.OnCall =
    (IParser_TryParseInterceptor.TryParseDelegate)(...);
```

### v10.8.0 Checklist

1. [ ] Search for `KO` property type references → rename to `Interceptors`
2. [ ] Search for `Handler.` in delegate casts → rename to `Interceptor.`
3. [ ] Rebuild and run tests

---

## v10.7.0

> **Note:** The KO suffix introduced in v10.7.0 was further renamed to `Interceptors` in v10.8.0.

### Container Class Rename: Spy to KO

Generated container classes renamed from `{Interface}Spy` to `{Interface}KO`.

| Before | After |
|--------|-------|
| `ILoggerSpy` | `ILoggerKO` |
| `IUserServiceSpy` | `IUserServiceKO` |

**Most code unaffected.** The common access pattern is unchanged:

```csharp
// Works the same
knockOff.ILogger.Log.CallCount
knockOff.IUserService.Name.OnGet = (ko) => "Test";
```

**Migration required** only if you directly reference the container class type:

```csharp
// Before
ILoggerSpy spy = knockOff.ILogger;

// After
ILoggerKO ko = knockOff.ILogger;
```

### Zero-Allocation Tracking: Removed Properties

| Interceptor Type | Removed |
|--------------|---------|
| Method | `AllCalls` |
| Indexer | `AllGetKeys`, `AllSetEntries` |
| Generic `.Of<T>()` | `AllCalls` |

**Migration:**

```csharp
// Before
var allCalls = knockOff.IService.GetUser.AllCalls;
Assert.Equal(3, allCalls.Count);

// After - use count and last value
Assert.Equal(3, knockOff.IService.GetUser.CallCount);
Assert.Equal(42, knockOff.IService.GetUser.LastCallArg);

// Or capture in callback if you need full history
var allCalls = new List<int>();
knockOff.IService.GetUser.OnCall = (ko, id) =>
{
    allCalls.Add(id);
    return new User { Id = id };
};
```

### v10.7.0 Checklist

1. [ ] Search for `Spy` class references -> rename to `KO`
2. [ ] Search for `.AllCalls` -> use `CallCount` + `LastCallArg`
3. [ ] Search for `.AllGetKeys` -> use `GetCount` + `LastGetKey`
4. [ ] Search for `.AllSetEntries` -> use `SetCount` + `LastSetEntry`
5. [ ] Rebuild and run tests
