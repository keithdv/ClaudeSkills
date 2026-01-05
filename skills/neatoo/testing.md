# Testing Neatoo Rules

## Quick Reference

### Key Pattern: Use `RunRule`

```csharp
// Sync rule
var result = rule.RunRule(mockTarget.Object);

// Async rule
var result = await rule.RunRule(mockTarget.Object);
```

**Do NOT** create wrapper classes to expose the protected `Execute` method.

## Sync Rule Testing

```csharp
[TestMethod]
public void RunRule_WhenInvalid_ReturnsError()
{
    var rule = new NameValidationRule();

    var mockTarget = new Mock<INamedEntity>();
    mockTarget.Setup(e => e.Name).Returns(string.Empty);

    var result = rule.RunRule(mockTarget.Object);

    var messages = result.Result.ToList();
    Assert.AreEqual(1, messages.Count);
    Assert.AreEqual("Name", messages[0].PropertyName);
}
```

## Async Rule Testing

```csharp
[TestMethod]
public async Task RunRule_WhenNotUnique_ReturnsError()
{
    // Mock the dependency
    var mockCheckUnique = new Mock<ICheckNameUnique>();
    mockCheckUnique
        .Setup(c => c.IsUnique(It.IsAny<string>(), It.IsAny<int?>()))
        .ReturnsAsync(false);

    var rule = new UniqueNameAsyncRule(mockCheckUnique.Object);

    // Mock target with IsModified
    var mockTarget = new Mock<INamedEntityWithTracking>();
    mockTarget.Setup(e => e.Name).Returns("Duplicate");

    var mockProperty = new Mock<IEntityProperty>();
    mockProperty.Setup(p => p.IsModified).Returns(true);
    mockTarget.Setup(e => e["Name"]).Returns(mockProperty.Object);

    var result = await rule.RunRule(mockTarget.Object);

    Assert.IsTrue(result.Any());
    mockCheckUnique.Verify(c => c.IsUnique("Duplicate", null), Times.Once);
}
```

## Testing Rules with Parent Access

```csharp
[TestMethod]
public void RunRule_WhenExceedsParentLimit_ReturnsError()
{
    var rule = new QuantityLimitRule();

    var mockParent = new Mock<IOrderHeader>();
    mockParent.Setup(p => p.MaxQuantityPerLine).Returns(100);

    var mockTarget = new Mock<ILineItem>();
    mockTarget.Setup(l => l.Quantity).Returns(150);
    mockTarget.Setup(l => l.Parent).Returns(mockParent.Object);

    var result = rule.RunRule(mockTarget.Object);

    Assert.IsTrue(result.Result.Any(m => m.PropertyName == "Quantity"));
}
```

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Create wrapper class to expose `Execute` | Use `RunRule` |
| Mock `IValidateBase` or Neatoo interfaces | Mock your domain interfaces |
| Test rules only through domain objects | Unit test rules in isolation |

## Asserting Results

```csharp
var result = rule.RunRule(mockTarget.Object);
var messages = result.Result.ToList();

// No errors
Assert.IsFalse(messages.Any());

// Has specific error
Assert.IsTrue(messages.Any(m => m.PropertyName == "Email"));
Assert.IsTrue(messages.Any(m => m.Message.Contains("required")));

// Verify dependency was/wasn't called
mockService.Verify(s => s.CheckAsync(email), Times.Once);
mockService.Verify(s => s.CheckAsync(It.IsAny<string>()), Times.Never);
```

## Interface Requirements

| Interface | Has `IsModified` | When to Use |
|-----------|------------------|-------------|
| `IValidateBase` | No | Simple validation rules |
| `IEntityBase` | Yes (via `IEntityProperty`) | Rules checking modification state |

When mocking `IsModified`:
```csharp
var mockProperty = new Mock<IEntityProperty>();
mockProperty.Setup(p => p.IsModified).Returns(true);
mockTarget.Setup(e => e["PropertyName"]).Returns(mockProperty.Object);
```
