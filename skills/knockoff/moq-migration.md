# Moq Migration

Step-by-step patterns for migrating from Moq to KnockOff.

## Quick Reference

| Moq | KnockOff |
|-----|----------|
| `new Mock<IService>()` | `new ServiceKnockOff()` |
| `mock.Object` | Cast or `knockOff.AsService()` |
| `.Setup(x => x.M())` | `IService.M.OnCall = (ko, ...) => ...` |
| `.Returns(v)` | `OnCall = (ko) => v` |
| `.ReturnsAsync(v)` | `OnCall = (ko) => Task.FromResult(v)` |
| `.Callback(a)` | Logic inside `OnCall` callback |
| `.Verify(Times.Once)` | `Assert.Equal(1, IService.M.CallCount)` |
| `It.IsAny<T>()` | Implicit |
| `It.Is<T>(p)` | Check in callback |

## Migration Steps

### Step 1: Create KnockOff Class

```csharp
// Before: Moq
var mock = new Mock<IUserService>();

// After: Create class once
[KnockOff]
public partial class UserServiceKnockOff : IUserService { }

// In test
var knockOff = new UserServiceKnockOff();
```

### Step 2: Replace mock.Object

```csharp
// Before
var service = mock.Object;
DoWork(mock.Object);

// After
IUserService service = knockOff;
DoWork(knockOff.AsUserService());
```

### Step 3: Convert Setup/Returns

```csharp
// Before
mock.Setup(x => x.GetUser(It.IsAny<int>()))
    .Returns(new User { Id = 1 });

// After
knockOff.IUserService.GetUser.OnCall = (ko, id) =>
    new User { Id = id };
```

### Step 4: Convert ReturnsAsync

```csharp
// Before
mock.Setup(x => x.GetUserAsync(It.IsAny<int>()))
    .ReturnsAsync(new User { Id = 1 });

// After
knockOff.IUserService.GetUserAsync.OnCall = (ko, id) =>
    Task.FromResult<User?>(new User { Id = id });
```

### Step 5: Convert Verify

```csharp
// Before
mock.Verify(x => x.Save(It.IsAny<User>()), Times.Once);
mock.Verify(x => x.Delete(It.IsAny<int>()), Times.Never);
mock.Verify(x => x.GetAll(), Times.AtLeastOnce);
mock.Verify(x => x.Update(It.IsAny<User>()), Times.Exactly(3));

// After
Assert.Equal(1, knockOff.IUserService.Save.CallCount);
Assert.Equal(0, knockOff.IUserService.Delete.CallCount);
Assert.True(knockOff.IUserService.GetAll.WasCalled);
Assert.Equal(3, knockOff.IUserService.Update.CallCount);
```

### Step 6: Convert Callback

```csharp
// Before
User? captured = null;
mock.Setup(x => x.Save(It.IsAny<User>()))
    .Callback<User>(u => captured = u);

// After (automatic tracking)
service.Save(user);
var captured = knockOff.IUserService.Save.LastCallArg;

// Or with callback
knockOff.IUserService.Save.OnCall = (ko, user) =>
{
    customList.Add(user);
};
```

## Common Patterns

### Static Returns

```csharp
// Moq
mock.Setup(x => x.GetConfig()).Returns(new Config { Timeout = 30 });

// KnockOff Option 1: User method
[KnockOff]
public partial class ConfigKnockOff : IConfigService
{
    protected Config GetConfig() => new Config { Timeout = 30 };
}

// KnockOff Option 2: Callback
knockOff.IConfigService.GetConfig.OnCall = (ko) => new Config { Timeout = 30 };
```

### Conditional Returns

```csharp
// Moq
mock.Setup(x => x.GetUser(1)).Returns(new User { Name = "Admin" });
mock.Setup(x => x.GetUser(2)).Returns(new User { Name = "Guest" });
mock.Setup(x => x.GetUser(It.IsAny<int>())).Returns((User?)null);

// KnockOff
knockOff.IUserService.GetUser.OnCall = (ko, id) => id switch
{
    1 => new User { Name = "Admin" },
    2 => new User { Name = "Guest" },
    _ => null
};
```

### Throwing Exceptions

```csharp
// Moq
mock.Setup(x => x.Connect()).Throws(new TimeoutException());

// KnockOff
knockOff.IService.Connect.OnCall = (ko) =>
    throw new TimeoutException();
```

### Sequential Returns

```csharp
// Moq
mock.SetupSequence(x => x.GetNext())
    .Returns(1)
    .Returns(2)
    .Returns(3);

// KnockOff
var results = new Queue<int>([1, 2, 3]);
knockOff.IService.GetNext.OnCall = (ko) => results.Dequeue();
```

### Property Setup

```csharp
// Moq
mock.Setup(x => x.Name).Returns("Test");
mock.SetupSet(x => x.Name = It.IsAny<string>()).Verifiable();

// KnockOff
knockOff.IService.Name.OnGet = (ko) => "Test";
// Setter tracking is automatic
service.Name = "Value";
Assert.Equal("Value", knockOff.IService.Name.LastSetValue);
```

### Multiple Interfaces

```csharp
// Moq
var mock = new Mock<IRepository>();
mock.As<IUnitOfWork>()
    .Setup(x => x.SaveChangesAsync(It.IsAny<CancellationToken>()))
    .ReturnsAsync(1);

// KnockOff
[KnockOff]
public partial class DataContextKnockOff : IRepository, IUnitOfWork { }

knockOff.IUnitOfWork.SaveChangesAsync.OnCall = (ko, ct) =>
    Task.FromResult(1);
IRepository repo = knockOff.AsRepository();
IUnitOfWork uow = knockOff.AsUnitOfWork();
```

### Argument Matching

```csharp
// Moq
mock.Setup(x => x.Log(It.Is<string>(s => s.Contains("error"))))
    .Callback<string>(s => errors.Add(s));

// KnockOff
knockOff.ILogger.Log.OnCall = (ko, message) =>
{
    if (message.Contains("error"))
        errors.Add(message);
};
```

### Method Overloads

```csharp
// Moq - can setup specific overloads
mock.Setup(x => x.Process("specific")).Returns(...);
mock.Setup(x => x.Process(It.IsAny<string>(), It.IsAny<int>())).Returns(...);

// KnockOff - each overload has its own handler (1-based suffix)
knockOff.IService.Process1.OnCall = (ko, data) => { /* 1-param overload */ };
knockOff.IService.Process2.OnCall = (ko, data, priority) => { /* 2-param overload */ };

// For return values
knockOff.IService.Calculate1.OnCall = (ko, value) => value * 2;
knockOff.IService.Calculate2.OnCall = (ko, a, b) => a + b;
```

### Out Parameters

```csharp
// Moq
mock.Setup(x => x.TryParse(It.IsAny<string>(), out It.Ref<int>.IsAny))
    .Returns(new TryParseDelegate((string input, out int result) =>
    {
        return int.TryParse(input, out result);
    }));

// KnockOff - explicit delegate type required
knockOff.IParser.TryParse.OnCall =
    (IParser_TryParseHandler.TryParseDelegate)((ko, string input, out int result) =>
    {
        return int.TryParse(input, out result);
    });

// Tracking: only input params (out excluded)
Assert.Equal("42", knockOff.IParser.TryParse.LastCallArg);
```

### Ref Parameters

```csharp
// Moq
mock.Setup(x => x.Increment(ref It.Ref<int>.IsAny))
    .Callback(new IncrementDelegate((ref int value) => value++));

// KnockOff - explicit delegate type required
knockOff.IProcessor.Increment.OnCall =
    (IProcessor_IncrementHandler.IncrementDelegate)((ko, ref int value) =>
    {
        value++;
    });

// Tracking captures INPUT value (before modification)
int x = 5;
processor.Increment(ref x);
Assert.Equal(6, x);  // Modified
Assert.Equal(5, knockOff.IProcessor.Increment.LastCallArg);  // Original
```

## Features Comparison

| Feature | Moq | KnockOff |
|---------|-----|----------|
| Runtime config | Supported | Supported (callbacks) |
| Compile-time config | Not supported | Supported (user methods) |
| Type-safe setup | Expression-based | Strongly-typed delegates |
| Argument capture | Via Callback | Automatic tracking |
| Call counting | Verify(Times.X) | CallCount property |
| Out parameters | Supported | Supported |
| Ref parameters | Supported | Supported |
| Events | Supported | Supported (with Raise/tracking) |
| Strict mode | Supported | Not supported |
| VerifyNoOtherCalls | Supported | Not supported |
| Generic methods | Supported | Not supported |

## Keep Using Moq For

- Strict mode requirements
- `VerifyNoOtherCalls` verification
- Generic methods on interfaces

## Gradual Migration

Use both in same project:

```csharp
// New tests: KnockOff
var userKnockOff = new UserServiceKnockOff();

// Legacy tests: Keep Moq until migrated
var orderMock = new Mock<IOrderService>();
```
