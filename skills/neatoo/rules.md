# Neatoo Rules Engine Reference

## Overview

Neatoo's rules engine handles both **validation** (is the data correct?) and **transformation** (calculating derived values). Rules execute automatically when dependent properties change.

## Rule Types

| Type | Purpose | Example |
|------|---------|---------|
| Validation | Check data correctness | "Email must be valid format" |
| Transformation | Calculate derived values | "FullName = FirstName + LastName" |
| Async Validation | Server-side checks | "Email must be unique in database" |

## Data Annotation Validation

The simplest validation uses standard .NET data annotations:

```csharp
using Neatoo;
using Neatoo.RemoteFactory;

[Factory]
internal partial class Person : EntityBase<Person>, IPerson
{
    [Required(ErrorMessage = "First name is required")]
    [StringLength(50, ErrorMessage = "First name cannot exceed 50 characters")]
    [DisplayName("First Name")]
    public partial string? FirstName { get; set; }

    [Required]
    [StringLength(50)]
    public partial string? LastName { get; set; }

    [EmailAddress(ErrorMessage = "Invalid email format")]
    public partial string? Email { get; set; }

    [Phone]
    public partial string? Phone { get; set; }

    [Range(0, 150, ErrorMessage = "Age must be between 0 and 150")]
    public partial int Age { get; set; }

    [RegularExpression(@"^\d{5}(-\d{4})?$", ErrorMessage = "Invalid ZIP code")]
    public partial string? ZipCode { get; set; }

    [Compare(nameof(Email), ErrorMessage = "Email addresses must match")]
    public partial string? ConfirmEmail { get; set; }
}
```

### Supported Data Annotations

| Attribute | Purpose |
|-----------|---------|
| `[Required]` | Field must have a value |
| `[StringLength(max)]` | Maximum string length |
| `[MinLength(min)]` | Minimum string/collection length |
| `[MaxLength(max)]` | Maximum string/collection length |
| `[Range(min, max)]` | Numeric range |
| `[EmailAddress]` | Valid email format |
| `[Phone]` | Valid phone format |
| `[Url]` | Valid URL format |
| `[CreditCard]` | Valid credit card format |
| `[RegularExpression(pattern)]` | Regex pattern match |
| `[Compare(otherProperty)]` | Must match another property |
| `[DisplayName(name)]` | Friendly name for messages |

## RuleManager.AddAction - Transformation Rules

For calculated properties, use `AddAction` in the constructor:

```csharp
public Person(IEntityBaseServices<Person> services) : base(services)
{
    // Single trigger property
    RuleManager.AddAction(
        (Person p) => p.FullName = $"{p.FirstName} {p.LastName}",
        p => p.FirstName, p => p.LastName);

    // Multiple calculations
    RuleManager.AddAction(
        (Person p) => p.Age = CalculateAge(p.BirthDate),
        p => p.BirthDate);

    RuleManager.AddAction(
        (Person p) => p.IsAdult = p.Age >= 18,
        p => p.Age);
}

private static int CalculateAge(DateTime? birthDate)
{
    if (birthDate == null) return 0;
    var today = DateTime.Today;
    var age = today.Year - birthDate.Value.Year;
    if (birthDate.Value.Date > today.AddYears(-age)) age--;
    return age;
}
```

### AddAction Signature

```csharp
void AddAction(
    Action<T> action,           // The transformation to perform
    params Expression<Func<T, object?>>[] triggerProperties  // Properties that trigger this action
);
```

### Chained Calculations

Actions can chain - when one calculated property changes, it triggers rules dependent on it:

```csharp
// BirthDate changes -> Age calculated -> IsAdult calculated
RuleManager.AddAction(
    (Person p) => p.Age = CalculateAge(p.BirthDate),
    p => p.BirthDate);

RuleManager.AddAction(
    (Person p) => p.IsAdult = p.Age >= 18,
    p => p.Age);
```

## RuleManager.AddRule - Custom Validation Rules

For complex validation logic, create custom rule classes:

### Rule Base Class

```csharp
public class EmailDomainRule : RuleBase<IPerson>
{
    private readonly string[] _allowedDomains;

    public EmailDomainRule(string[] allowedDomains)
        : base(p => p.Email)  // Trigger property
    {
        _allowedDomains = allowedDomains;
    }

    protected override IRuleMessages Execute(IPerson target)
    {
        if (string.IsNullOrEmpty(target.Email))
            return None;  // Let [Required] handle empty

        var domain = target.Email.Split('@').LastOrDefault();

        if (!_allowedDomains.Contains(domain, StringComparer.OrdinalIgnoreCase))
        {
            return Error(
                nameof(target.Email),
                $"Email domain must be one of: {string.Join(", ", _allowedDomains)}");
        }

        return None;
    }
}
```

### Registering Custom Rules

```csharp
public Person(IEntityBaseServices<Person> services) : base(services)
{
    RuleManager.AddRule(new EmailDomainRule(new[] { "company.com", "corp.net" }));
    RuleManager.AddRule(new AgeRestrictionRule());
    RuleManager.AddRule(new PhoneFormatRule());
}
```

### Multiple Trigger Properties

```csharp
public class DateRangeRule : RuleBase<IDateRange>
{
    public DateRangeRule()
        : base(r => r.StartDate, r => r.EndDate)  // Multiple triggers
    {
    }

    protected override IRuleMessages Execute(IDateRange target)
    {
        if (target.StartDate == null || target.EndDate == null)
            return None;

        if (target.EndDate < target.StartDate)
        {
            return Error(
                nameof(target.EndDate),
                "End date must be after start date");
        }

        return None;
    }
}
```

### Multiple Error Messages

```csharp
protected override IRuleMessages Execute(IOrder target)
{
    var messages = new List<(string, string)>();

    if (target.OrderDate > DateTime.Today)
        messages.Add((nameof(target.OrderDate), "Order date cannot be in the future"));

    if (target.ShipDate < target.OrderDate)
        messages.Add((nameof(target.ShipDate), "Ship date must be after order date"));

    if (target.Total <= 0)
        messages.Add((nameof(target.Total), "Order total must be greater than zero"));

    return messages.AsRuleMessages();
}
```

## Async Rules - Server-Side Validation

For validation requiring database access, use async rules:

```csharp
public class UniqueEmailRule : RuleBaseAsync<IPerson>
{
    private readonly IEmailService _emailService;

    public UniqueEmailRule(IEmailService emailService)
        : base(p => p.Email)
    {
        _emailService = emailService;
    }

    protected override async Task<IRuleMessages> ExecuteAsync(IPerson target)
    {
        if (string.IsNullOrEmpty(target.Email))
            return None;

        var exists = await _emailService.EmailExistsAsync(
            target.Email,
            target.Id);  // Exclude current entity

        return exists
            ? Error(nameof(target.Email), "Email address is already registered")
            : None;
    }
}
```

### Registering Async Rules

```csharp
public Person(
    IEntityBaseServices<Person> services,
    IEmailService emailService) : base(services)
{
    RuleManager.AddRule(new UniqueEmailRule(emailService));
}
```

### Waiting for Async Rules

```csharp
person.Email = "test@example.com";
// Async rule starts executing
// person.IsBusy == true
// person[nameof(person.Email)].IsBusy == true

await person.WaitForTasks();
// Async rules complete
// person.IsBusy == false

if (person.IsValid)
{
    await personFactory.Save(person);
}
```

## Cancellation Support

All async operations support `CancellationToken` for graceful shutdown, navigation, or timeouts.

### Running Rules with Cancellation

```csharp
using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(30));

try
{
    await entity.RunRules(RunRulesFlag.All, cts.Token);
}
catch (OperationCanceledException)
{
    // Validation was cancelled
    // entity.IsValid == false (marked invalid via MarkInvalid)
}
```

### Waiting for Tasks with Cancellation

```csharp
try
{
    await entity.WaitForTasks(cancellationToken);
}
catch (OperationCanceledException)
{
    // Wait was cancelled - running tasks still complete
}
```

### Save with Cancellation

```csharp
try
{
    person = await person.Save(cancellationToken);
}
catch (OperationCanceledException)
{
    // Cancelled before persistence began
}
```

### Async Rules with CancellationToken

Async rules receive the cancellation token:

```csharp
public class UniqueEmailRule : AsyncRuleBase<IPerson>
{
    protected override async Task<IRuleMessages> Execute(
        IPerson target,
        CancellationToken? token = null)
    {
        // Pass token to async operations
        var exists = await _service.CheckAsync(target.Email, token ?? CancellationToken.None);

        // Or check manually
        token?.ThrowIfCancellationRequested();

        return exists ? Error(nameof(target.Email), "In use") : None;
    }
}
```

### Fluent Rules with CancellationToken

```csharp
// Token is passed to your delegate
RuleManager.AddActionAsync(
    async (target, token) => target.Rate = await service.GetRateAsync(target.ZipCode, token),
    t => t.ZipCode);

RuleManager.AddValidationAsync(
    async (target, token) => await service.ExistsAsync(target.Email, token) ? "In use" : "",
    t => t.Email);
```

### Cancellation Design Philosophy

| Principle | Behavior |
|-----------|----------|
| **For stopping, not recovering** | Cancellation marks the object invalid |
| **Running tasks complete** | Only waiting is cancelled, not executing tasks |
| **No mid-persistence cancellation** | Save only cancels before Insert/Update/Delete |
| **Recovery requires re-validation** | Call `RunRules(RunRulesFlag.All)` to clear cancelled state |

### When to Use Cancellation

| Scenario | Pattern |
|----------|---------|
| Component disposal | `cts.Cancel()` in `Dispose()` |
| Navigation away | Cancel before changing routes |
| Request timeout | `new CancellationTokenSource(TimeSpan.FromSeconds(n))` |
| User-initiated | Button triggers `cts.Cancel()` |

## Cross-Entity Validation

### Accessing Parent

```csharp
public class QuantityLimitRule : RuleBase<IOrderLine>
{
    public QuantityLimitRule()
        : base(l => l.Quantity)
    {
    }

    protected override IRuleMessages Execute(IOrderLine target)
    {
        var order = target.Parent as IOrder;
        if (order == null) return None;

        // Business rule: VIP customers can order more
        var maxQuantity = order.CustomerType == CustomerType.VIP ? 1000 : 100;

        return target.Quantity > maxQuantity
            ? Error(nameof(target.Quantity),
                   $"Maximum quantity is {maxQuantity}")
            : None;
    }
}
```

### Accessing Siblings

```csharp
public class UniqueProductRule : RuleBase<IOrderLine>
{
    public UniqueProductRule()
        : base(l => l.ProductName)
    {
    }

    protected override IRuleMessages Execute(IOrderLine target)
    {
        var order = target.Parent as IOrder;
        if (order?.Lines == null) return None;

        var isDuplicate = order.Lines
            .Where(l => l != target)
            .Any(l => l.ProductName == target.ProductName);

        return isDuplicate
            ? Error(nameof(target.ProductName), "Product already in order")
            : None;
    }
}
```

### Triggering Sibling Validation

When one item changes, siblings may need revalidation:

```csharp
using Neatoo;
using Neatoo.RemoteFactory;

[Factory]
internal partial class OrderLineList
    : EntityListBase<IOrderLine>, IOrderLineList
{
    protected override async Task HandleNeatooPropertyChanged(
        NeatooPropertyChangedEventArgs eventArgs)
    {
        await base.HandleNeatooPropertyChanged(eventArgs);

        if (eventArgs.PropertyName == nameof(IOrderLine.ProductName))
        {
            // Re-run uniqueness rule on siblings
            foreach (var sibling in this.Where(l => l != eventArgs.Source))
            {
                await sibling.RunRules(nameof(IOrderLine.ProductName));
            }
        }
    }
}
```

## Rule Execution Control

### RunRules Method

Manually trigger rule execution:

```csharp
// Run rules for specific property
await entity.RunRules(nameof(entity.Email));

// Run all rules
await entity.RunRules(RunRulesFlag.All);
```

### RunRulesFlag Options

| Flag | Behavior |
|------|----------|
| `RunRulesFlag.All` | Run all rules regardless of state |
| Default | Run rules for modified properties |

### Factory Methods - Rules Are Paused

In factory methods (`[Create]`, `[Fetch]`, etc.), **rules are paused**. Use property setters directly:

```csharp
[Fetch]
public async Task<bool> Fetch([Service] IDbContext db)
{
    var entity = await db.Persons.FindAsync(Id);
    if (entity == null) return false;

    // Rules are paused in factory methods - property setters work directly
    Id = entity.Id;
    FirstName = entity.FirstName;
    LastName = entity.LastName;

    return true;
}
```

### Cascading Rules - A Key Feature

When a rule sets a property, **dependent rules run automatically**. This cascading behavior is intentional and essential for maintaining domain consistency.

```csharp
public class OrderTotalRule : RuleBase<IOrder>
{
    public override IRuleMessages Execute(IOrder target)
    {
        var total = target.Lines?.Sum(l => l.Quantity * l.UnitPrice) ?? 0;

        // Property setter triggers any rules that depend on Total - this is correct!
        target.Total = total;

        return None;
    }
}
```

### LoadProperty - Rare Use Cases Only

Use `LoadProperty()` **only** to prevent circular references:

```csharp
// Rule A triggers Rule B which triggers Rule A - break the cycle
LoadProperty(nameof(target.InternalValue), calculated);
```

## Rule Messages

### Creating Messages

```csharp
// Single error
return Error(nameof(target.Email), "Invalid email");

// No errors
return None;

// Multiple errors
return new[]
{
    (nameof(target.StartDate), "Start date is required"),
    (nameof(target.EndDate), "End date is required")
}.AsRuleMessages();
```

### Message Severity

```csharp
// Error - prevents save
return Error(propertyName, message);

// Warning - allows save but shows warning
return Warning(propertyName, message);

// Information - informational message
return Info(propertyName, message);
```

### Accessing Messages

```csharp
// All entity messages
foreach (var msg in person.PropertyMessages)
{
    Console.WriteLine($"{msg.PropertyName}: {msg.Message} ({msg.Severity})");
}

// Messages for specific property
var emailMessages = person[nameof(person.Email)].PropertyMessages;
foreach (var msg in emailMessages)
{
    Console.WriteLine(msg.Message);
}
```

## Database-Dependent Validation

For validation requiring database access:

### Pattern 1: Async Rule with Injected Service

```csharp
public class UniqueEmailRule : RuleBaseAsync<IPerson>
{
    private readonly IPersonRepository _repository;

    public UniqueEmailRule(IPersonRepository repository)
        : base(p => p.Email)
    {
        _repository = repository;
    }

    protected override async Task<IRuleMessages> ExecuteAsync(IPerson target)
    {
        if (string.IsNullOrEmpty(target.Email))
            return None;

        var exists = await _repository.EmailExistsAsync(
            target.Email,
            target.Id);

        return exists
            ? Error(nameof(target.Email), "Email already registered")
            : None;
    }
}
```

### Pattern 2: Registration in Constructor

```csharp
public Person(
    IEntityBaseServices<Person> services,
    IPersonRepository repository) : base(services)
{
    RuleManager.AddRule(new UniqueEmailRule(repository));
}
```

### Pattern 3: Client-Side Optimization

Check only on server to avoid unnecessary API calls:

```csharp
public class UniqueEmailRule : RuleBaseAsync<IPerson>
{
    private readonly IPersonRepository? _repository;

    public UniqueEmailRule(IPersonRepository? repository = null)
        : base(p => p.Email)
    {
        _repository = repository;
    }

    protected override async Task<IRuleMessages> ExecuteAsync(IPerson target)
    {
        // Skip on client (repository not available)
        if (_repository == null)
            return None;

        // Full check on server
        var exists = await _repository.EmailExistsAsync(
            target.Email,
            target.Id);

        return exists
            ? Error(nameof(target.Email), "Email already registered")
            : None;
    }
}
```

## Rule Order and Dependencies

### Execution Order

1. Data annotation validation runs first
2. Custom rules run in registration order
3. Transformation actions run after rules

### Cascading Rules

```csharp
// When FirstName changes:
// 1. [Required] annotation validates FirstName
// 2. FullName transformation runs
// 3. Any rules dependent on FullName run

RuleManager.AddAction(
    (Person p) => p.FullName = $"{p.FirstName} {p.LastName}",
    p => p.FirstName, p => p.LastName);

RuleManager.AddRule(new FullNameLengthRule());  // Triggers on FullName
```

## Best Practices

### Keep Rules Focused

```csharp
// GOOD - single responsibility
public class EmailFormatRule : RuleBase<IPerson>
{
    protected override IRuleMessages Execute(IPerson target)
    {
        // Only validates format
    }
}

public class UniqueEmailRule : RuleBaseAsync<IPerson>
{
    protected override async Task<IRuleMessages> ExecuteAsync(IPerson target)
    {
        // Only checks uniqueness
    }
}
```

### Use Data Annotations for Simple Validation

```csharp
// Prefer this for simple cases
[Required]
[StringLength(50)]
public partial string? FirstName { get; set; }

// Over creating custom rules for basic checks
```

### Inject Dependencies for Database Access

```csharp
public Person(
    IEntityBaseServices<Person> services,
    IEmailService emailService,
    IPersonRepository repository) : base(services)
{
    RuleManager.AddRule(new UniqueEmailRule(emailService));
    RuleManager.AddRule(new ManagerExistsRule(repository));
}
```

### Handle Null Values Gracefully

```csharp
protected override IRuleMessages Execute(IPerson target)
{
    // Let [Required] handle null/empty
    if (string.IsNullOrEmpty(target.Email))
        return None;

    // Now validate format
    // ...
}
```

## Common Pitfalls

1. **Forgetting await on WaitForTasks** - Checking validity before async rules complete
2. **Not handling null in rules** - Let [Required] handle empty, check for null
3. **Circular rule dependencies** - A triggers B triggers A (use LoadProperty to break)
4. **Database access in sync rules** - Use async rules for database operations
5. **Overusing LoadProperty** - Cascading is a feature; only use LoadProperty for circular references
6. **Not handling OperationCanceledException** - When using cancellation tokens, handle the exception
7. **Expecting recovery after cancellation** - Cancellation marks object invalid; must call `RunRules(RunRulesFlag.All)` to recover
