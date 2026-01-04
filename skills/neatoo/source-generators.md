# Neatoo Source Generators Reference

## Overview

Neatoo uses Roslyn source generators to create factory interfaces, implementations, and property infrastructure at compile time. This eliminates boilerplate while maintaining type safety.

## What Gets Generated

### For [Factory] Classes

```csharp
// Your code:
[Factory]
internal partial class Person : EntityBase<Person>, IPerson
{
    public partial string? FirstName { get; set; }
    public partial string? LastName { get; set; }

    [Create]
    public void Create() { }

    [Remote]
    [Fetch]
    public async Task<bool> Fetch([Service] IDbContext db) { }
}
```

**Generated:**

1. **Factory Interface** (`IPersonFactory`)
2. **Factory Implementation** (`PersonFactory`)
3. **Property Implementations** (Getter/Setter bodies)
4. **DI Registration Methods**

### Factory Interface Generation

```csharp
// Generated interface
public interface IPersonFactory
{
    // From [Create] method
    IPerson? Create();

    // From [Fetch] method (non-service params become factory params)
    Task<IPerson?> Fetch(Guid id);

    // Standard save methods
    Task<IPerson?> Save(IPerson target);
    Task<Authorized<IPerson>> TrySave(IPerson target);

    // Authorization methods (if [AuthorizeFactory] configured)
    Authorized CanCreate();
    Authorized CanFetch();
    Authorized CanSave();
}
```

### Property Implementation Generation

```csharp
// Your declaration:
public partial string? FirstName { get; set; }

// Generated implementation:
public partial string? FirstName
{
    get => Getter<string?>();
    set => Setter(value);
}
```

## Marker Attributes

### [Factory]

Marks a class for factory generation:

```csharp
[Factory]
internal partial class Person : EntityBase<Person>, IPerson
{
    // ...
}
```

**Requirements:**
- Class must be `partial`
- Class should be `internal` (implementation detail)
- Must implement an interface (for public API)

### [Create]

Marks method as entity initialization (client-side):

```csharp
[Create]
public void Create()
{
    // Initialize defaults
}

[Create]
public void Create(string name)
{
    // Create with parameters
}
```

**Generates:** `Create()` and `Create(string name)` on factory interface

### [Fetch]

Marks method as data retrieval (server-side):

```csharp
[Remote]
[Fetch]
public async Task<bool> Fetch([Service] IDbContext db)
{
    // Load by Id (Id is a property)
}

[Remote]
[Fetch]
public async Task<bool> Fetch(string email, [Service] IDbContext db)
{
    // Load by email parameter
}
```

**Generates:** `Fetch(Guid id)` and `Fetch(string email)` on factory interface

### [Insert], [Update], [Delete]

Mark persistence methods (server-side):

```csharp
[Remote]
[Insert]
public async Task Insert([Service] IDbContext db) { }

[Remote]
[Update]
public async Task Update([Service] IDbContext db) { }

[Remote]
[Delete]
public async Task Delete([Service] IDbContext db) { }
```

**Generates:** `Save()` method that routes based on entity state

### [Execute]

Marks command/query execution:

```csharp
[Remote]
[Execute]
public async Task Execute([Service] IUserService userService)
{
    // Command logic
}
```

**Generates:** `Execute(T target)` on factory interface

### [Remote]

Marks method for server-side execution:

```csharp
[Remote]  // Runs on server
[Fetch]
public async Task<bool> Fetch([Service] IDbContext db) { }

// No [Remote] - runs on client
[Create]
public void Create() { }
```

### [Service]

Marks parameter for DI injection:

```csharp
[Fetch]
public async Task<bool> Fetch(
    Guid id,                      // From factory call
    [Service] IDbContext db,      // From DI container
    [Service] ILogger logger)     // From DI container
{
}
```

**Note:** Service parameters don't appear in generated factory interface.

### [AuthorizeFactory]

Marks authorization methods:

```csharp
public interface IPersonAuth
{
    [AuthorizeFactory(AuthorizeFactoryOperation.Create)]
    Authorized CanCreate();

    [AuthorizeFactory(AuthorizeFactoryOperation.Fetch)]
    Authorized CanFetch();
}
```

**Generates:** Authorization checks in factory and `Can*()` methods on interface

## Partial Properties

### Declaration Requirements

Properties must be `partial`:

```csharp
// Correct - generator provides implementation
public partial string? FirstName { get; set; }

// Wrong - no generation occurs
public string? FirstName { get; set; }
```

### What Gets Generated

For each partial property:

```csharp
// Generated getter/setter
public partial string? FirstName
{
    get => Getter<string?>();
    set => Setter(value);
}
```

### Data Annotation Preservation

Annotations are preserved and processed:

```csharp
[Required]
[StringLength(50)]
[DisplayName("First Name")]
public partial string? FirstName { get; set; }
```

These annotations:
- Generate validation rules
- Provide display names for UI
- Are available via reflection

## DI Registration

### Generated Registration Method

```csharp
// Generated in assembly
public static class NeatooServiceExtensions
{
    public static IServiceCollection AddNeatooServices(
        this IServiceCollection services,
        NeatooFactory mode,
        params Assembly[] assemblies)
    {
        // Registers all factories
        // Registers all authorization services
        // Configures serialization
    }
}
```

### Usage

```csharp
// Server
builder.Services.AddNeatooServices(
    NeatooFactory.Local,
    typeof(Person).Assembly);

// Client
builder.Services.AddNeatooServices(
    NeatooFactory.Remote,
    typeof(IPerson).Assembly);
```

## Factory Implementation Details

### Generated Factory Class

```csharp
// Simplified generated factory
internal class PersonFactory : IPersonFactory
{
    private readonly IServiceProvider _serviceProvider;

    public PersonFactory(IServiceProvider serviceProvider)
    {
        _serviceProvider = serviceProvider;
    }

    public IPerson? Create()
    {
        // Check authorization
        var auth = _serviceProvider.GetService<IPersonAuth>();
        if (auth != null && !auth.CanCreate().IsAuthorized)
            return null;

        // Create instance
        var person = ActivatorUtilities.CreateInstance<Person>(_serviceProvider);

        // Call create method
        person.Create();

        return person;
    }

    public async Task<IPerson?> Fetch(Guid id)
    {
        // For remote mode: serialize and send to server
        // For local mode: execute locally

        var person = ActivatorUtilities.CreateInstance<Person>(_serviceProvider);
        person.Id = id;

        var success = await person.Fetch(
            _serviceProvider.GetRequiredService<IDbContext>());

        return success ? person : null;
    }

    public async Task<IPerson?> Save(IPerson target)
    {
        var person = (Person)target;

        if (person.IsDeleted)
        {
            await person.Delete(/* resolved services */);
        }
        else if (person.IsNew)
        {
            await person.Insert(/* resolved services */);
        }
        else
        {
            await person.Update(/* resolved services */);
        }

        return person;
    }
}
```

## Collection Factory Generation

For `EntityListBase` collections:

```csharp
[Factory]
internal partial class PersonPhoneList
    : EntityListBase<IPersonPhone>, IPersonPhoneList
{
    [Fetch]
    public async Task Fetch(
        IEnumerable<PersonPhoneEntity> entities,
        [Service] IPersonPhoneFactory phoneFactory)
    {
        // ...
    }

    [Remote]
    [Update]
    public async Task Update(
        Guid personId,
        [Service] IDbContext db)
    {
        // ...
    }
}
```

**Generates:**

```csharp
public interface IPersonPhoneListFactory
{
    IPersonPhoneList Create();
    Task<IPersonPhoneList> Fetch(IEnumerable<PersonPhoneEntity> entities);
    Task<IPersonPhoneList?> Save(IPersonPhoneList target, Guid personId);
}
```

## Method Overloading

Multiple methods generate multiple factory methods:

```csharp
[Factory]
internal partial class Person : EntityBase<Person>, IPerson
{
    [Create]
    public void Create() { }

    [Create]
    public void Create(string email) { Email = email; }

    [Remote]
    [Fetch]
    public async Task<bool> Fetch([Service] IDbContext db) { }

    [Remote]
    [Fetch]
    public async Task<bool> Fetch(string email, [Service] IDbContext db) { }
}
```

**Generates:**

```csharp
public interface IPersonFactory
{
    IPerson? Create();
    IPerson? Create(string email);
    Task<IPerson?> Fetch(Guid id);
    Task<IPerson?> Fetch(string email);
    // ...
}
```

## Serialization Support

### Type Information

Generators create type mappings for JSON serialization:

```csharp
// Generated type resolver
internal class NeatooTypeResolver : IJsonTypeInfoResolver
{
    public JsonTypeInfo? GetTypeInfo(Type type, JsonSerializerOptions options)
    {
        if (type == typeof(IPerson))
            return CreateTypeInfo<Person>(options);
        // ...
    }
}
```

### Interface to Concrete Mapping

```csharp
// Serialization knows IPerson -> Person
var json = JsonSerializer.Serialize<IPerson>(person);
var restored = JsonSerializer.Deserialize<IPerson>(json);
// restored is actually a Person instance
```

## Debugging Generated Code

### Viewing Generated Code

In Visual Studio:
1. Expand Dependencies > Analyzers > Neatoo.SourceGenerators
2. View generated `.g.cs` files

In Rider:
1. Navigate to generated sources folder
2. Files are in `obj/Generated/`

### Common Generator Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Class must be partial" | Missing `partial` keyword | Add `partial` to class |
| "Property must be partial" | Missing `partial` keyword | Add `partial` to property |
| "No suitable constructor" | Missing services constructor | Add constructor with `IEntityBaseServices<T>` |
| "Duplicate method signature" | Same parameters on multiple methods | Differentiate parameter types |

### Forcing Regeneration

```bash
dotnet clean
dotnet build
```

Or in Visual Studio: Build > Rebuild Solution

## Performance Considerations

### Compile-Time Generation

- No runtime reflection for factory operations
- Type-safe factory methods
- Efficient property access

### Generated Code Quality

- Minimal allocations in property getters/setters
- Direct method calls (no dynamic dispatch)
- Optimized serialization paths

## Customization Points

### Constructor Injection

Add dependencies in constructor:

```csharp
public Person(
    IEntityBaseServices<Person> services,
    ICustomService customService) : base(services)
{
    _customService = customService;
}
```

Generator ensures `IEntityBaseServices<T>` is resolved.

### Non-Generated Properties

Regular (non-partial) properties bypass Neatoo:

```csharp
// Generated - full Neatoo infrastructure
public partial string? FirstName { get; set; }

// Not generated - regular property
public string FullName => $"{FirstName} {LastName}";

// Not generated - backing field
private readonly ICustomService _customService;
```

## Best Practices

### Use Interfaces for Public API

```csharp
// Interface is public
public interface IPerson : IEntityBase
{
    Guid? Id { get; set; }
    string? FirstName { get; set; }
}

// Implementation is internal
[Factory]
internal partial class Person : EntityBase<Person>, IPerson
{
}
```

### Keep Factory Methods Focused

```csharp
// Each method has single responsibility
[Create]
public void Create() { }  // Default initialization

[Create]
public void Create(string email) { }  // Create with email

[Fetch]
public async Task<bool> Fetch([Service] IDbContext db) { }  // By ID

[Fetch]
public async Task<bool> FetchByEmail(string email, [Service] IDbContext db) { }  // By email
```

### Mark All Properties as Partial

```csharp
// All entity properties should be partial
public partial Guid? Id { get; set; }
public partial string? FirstName { get; set; }
public partial string? LastName { get; set; }
public partial IPhoneList? Phones { get; set; }
```

## Common Pitfalls

1. **Missing `partial` keyword** - No generation occurs
2. **Public implementation class** - Should be internal
3. **Missing constructor parameter** - `IEntityBaseServices<T>` required
4. **Non-partial properties** - Won't have Neatoo infrastructure
5. **Service parameters in Create** - Services only available in [Remote] methods
6. **Wrong service type** - Use `IEntityBaseServices<T>` not `IValidateBaseServices<T>`
