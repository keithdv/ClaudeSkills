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

<!-- snippet: skill:moq-migration:step1-create -->
```csharp
// Before: Moq
// var mock = new Mock<IMmUserService>();

// After: Create class once
[KnockOff]
public partial class MmUserServiceKnockOff : IMmUserService { }

// In test
// var knockOff = new MmUserServiceKnockOff();
```
<!-- /snippet -->

### Step 2: Replace mock.Object

<!-- snippet: skill:moq-migration:step2-object -->
```csharp
// Before
// var service = mock.Object;
// DoWork(mock.Object);

// After
// IMmUserService service = knockOff;
// DoWork(knockOff.AsMmUserService());
```
<!-- /snippet -->

### Step 3: Convert Setup/Returns

<!-- snippet: skill:moq-migration:step3-setup -->
```csharp
// Before
// mock.Setup(x => x.GetUser(It.IsAny<int>()))
//     .Returns(new MmUser { Id = 1 });

// After
// knockOff.GetUser.OnCall = (ko, id) =>
//     new MmUser { Id = id };
```
<!-- /snippet -->

### Step 4: Convert ReturnsAsync

<!-- snippet: skill:moq-migration:step4-async -->
```csharp
// Before
// mock.Setup(x => x.GetUserAsync(It.IsAny<int>()))
//     .ReturnsAsync(new MmUser { Id = 1 });

// After
// knockOff.GetUserAsync.OnCall = (ko, id) =>
//     Task.FromResult<MmUser?>(new MmUser { Id = id });
```
<!-- /snippet -->

### Step 5: Convert Verify

<!-- snippet: skill:moq-migration:step5-verify -->
```csharp
// Before
// mock.Verify(x => x.Save(It.IsAny<MmUser>()), Times.Once);
// mock.Verify(x => x.Delete(It.IsAny<int>()), Times.Never);
// mock.Verify(x => x.GetAll(), Times.AtLeastOnce);
// mock.Verify(x => x.Update(It.IsAny<MmUser>()), Times.Exactly(3));

// After
// Assert.Equal(1, knockOff.Save.CallCount);
// Assert.Equal(0, knockOff.Delete.CallCount);
// Assert.True(knockOff.GetAll.WasCalled);
// Assert.Equal(3, knockOff.Update.CallCount);
```
<!-- /snippet -->

### Step 6: Convert Callback

<!-- snippet: skill:moq-migration:step6-callback -->
```csharp
// Before
// MmUser? captured = null;
// mock.Setup(x => x.Save(It.IsAny<MmUser>()))
//     .Callback<MmUser>(u => captured = u);

// After (automatic tracking)
// service.Save(user);
// var captured = knockOff.Save.LastCallArg;

// Or with callback
// knockOff.Save.OnCall = (ko, user) =>
// {
//     customList.Add(user);
// };
```
<!-- /snippet -->

## Common Patterns

### Static Returns

<!-- snippet: skill:moq-migration:static-returns -->
```csharp
// Moq
// mock.Setup(x => x.GetConfig()).Returns(new MmConfig { Timeout = 30 });

// KnockOff Option 1: User method
[KnockOff]
public partial class MmConfigServiceKnockOff : IMmConfigService
{
    protected MmConfig GetConfig() => new MmConfig { Timeout = 30 };
}

// KnockOff Option 2: Callback
// knockOff.GetConfig2.OnCall = (ko) => new MmConfig { Timeout = 30 };
```
<!-- /snippet -->

### Conditional Returns

<!-- snippet: skill:moq-migration:conditional-returns -->
```csharp
// Moq
// mock.Setup(x => x.GetUser(1)).Returns(new MmUser { Name = "Admin" });
// mock.Setup(x => x.GetUser(2)).Returns(new MmUser { Name = "Guest" });
// mock.Setup(x => x.GetUser(It.IsAny<int>())).Returns((MmUser?)null);

// KnockOff
// knockOff.GetUser.OnCall = (ko, id) => id switch
// {
//     1 => new MmUser { Name = "Admin" },
//     2 => new MmUser { Name = "Guest" },
//     _ => null
// };
```
<!-- /snippet -->

### Throwing Exceptions

<!-- snippet: skill:moq-migration:throwing-exceptions -->
```csharp
[KnockOff]
public partial class MmConnectionKnockOff : IMmConnectionService { }

// Moq
// mock.Setup(x => x.Connect()).Throws(new TimeoutException());

// KnockOff
// knockOff.Connect.OnCall = (ko) =>
//     throw new TimeoutException();
```
<!-- /snippet -->

### Sequential Returns

<!-- snippet: skill:moq-migration:sequential-returns -->
```csharp
[KnockOff]
public partial class MmSequenceKnockOff : IMmSequenceService { }

// Moq
// mock.SetupSequence(x => x.GetNext())
//     .Returns(1)
//     .Returns(2)
//     .Returns(3);

// KnockOff
// var results = new Queue<int>([1, 2, 3]);
// knockOff.GetNext.OnCall = (ko) => results.Dequeue();
```
<!-- /snippet -->

### Property Setup

<!-- snippet: skill:moq-migration:property-setup -->
```csharp
[KnockOff]
public partial class MmPropServiceKnockOff : IMmPropService { }

// Moq
// mock.Setup(x => x.Name).Returns("Test");
// mock.SetupSet(x => x.Name = It.IsAny<string>()).Verifiable();

// KnockOff
// knockOff.Name.OnGet = (ko) => "Test";
// Setter tracking is automatic
// service.Name = "Value";
// Assert.Equal("Value", knockOff.Name.LastSetValue);
```
<!-- /snippet -->

### Multiple Interfaces

<!-- snippet: skill:moq-migration:multiple-interfaces -->
```csharp
// Moq
// var mock = new Mock<IMmRepository>();
// mock.As<IMmUnitOfWork>()
//     .Setup(x => x.SaveChangesAsync(It.IsAny<CancellationToken>()))
//     .ReturnsAsync(1);

// KnockOff - create separate stubs
[KnockOff]
public partial class MmRepositoryKnockOff : IMmRepository { }

[KnockOff]
public partial class MmUnitOfWorkKnockOff : IMmUnitOfWork { }

// repoKnockOff.Save.OnCall = (ko, entity) => { };
// uowKnockOff.SaveChangesAsync2.OnCall = (ko, ct) => Task.FromResult(1);
```
<!-- /snippet -->

### Argument Matching

<!-- snippet: skill:moq-migration:argument-matching -->
```csharp
[KnockOff]
public partial class MmLoggerKnockOff : IMmLogger { }

// Moq
// mock.Setup(x => x.Log(It.Is<string>(s => s.Contains("error"))))
//     .Callback<string>(s => errors.Add(s));

// KnockOff
// knockOff.Log.OnCall = (ko, message) =>
// {
//     if (message.Contains("error"))
//         errors.Add(message);
// };
```
<!-- /snippet -->

### Method Overloads

<!-- snippet: skill:moq-migration:method-overloads -->
```csharp
[KnockOff]
public partial class MmProcessorKnockOff : IMmProcessorService { }

// Moq - can setup specific overloads
// mock.Setup(x => x.Process("specific")).Returns(...);
// mock.Setup(x => x.Process(It.IsAny<string>(), It.IsAny<int>())).Returns(...);

// KnockOff - each overload has its own handler (1-based suffix)
// knockOff.Process1.OnCall = (ko, data) => { /* 1-param overload */ };
// knockOff.Process2.OnCall = (ko, data, priority) => { /* 2-param overload */ };

// For return values
// knockOff.Calculate1.OnCall = (ko, value) => value * 2;
// knockOff.Calculate2.OnCall = (ko, a, b) => a + b;
```
<!-- /snippet -->

### Out Parameters

<!-- snippet: skill:moq-migration:out-params -->
```csharp
[KnockOff]
public partial class MmParserKnockOff : IMmParser { }

// Moq
// mock.Setup(x => x.TryParse(It.IsAny<string>(), out It.Ref<int>.IsAny))
//     .Returns(new TryParseDelegate((string input, out int result) =>
//     {
//         return int.TryParse(input, out result);
//     }));

// KnockOff - explicit delegate type required
// knockOff.TryParse.OnCall =
//     (TryParseHandler.TryParseDelegate)((ko, string input, out int result) =>
//     {
//         return int.TryParse(input, out result);
//     });

// Tracking: only input params (out excluded)
// Assert.Equal("42", knockOff.TryParse.LastCallArg);
```
<!-- /snippet -->

### Ref Parameters

<!-- snippet: skill:moq-migration:ref-params -->
```csharp
[KnockOff]
public partial class MmRefProcessorKnockOff : IMmRefProcessor { }

// Moq
// mock.Setup(x => x.Increment(ref It.Ref<int>.IsAny))
//     .Callback(new IncrementDelegate((ref int value) => value++));

// KnockOff - explicit delegate type required
// knockOff.Increment.OnCall =
//     (IncrementHandler.IncrementDelegate)((ko, ref int value) =>
//     {
//         value++;
//     });

// Tracking captures INPUT value (before modification)
// int x = 5;
// processor.Increment(ref x);
// Assert.Equal(6, x);  // Modified
// Assert.Equal(5, knockOff.Increment.LastCallArg);  // Original
```
<!-- /snippet -->

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
