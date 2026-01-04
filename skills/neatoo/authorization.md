# Neatoo Authorization Reference

## Overview

Neatoo's authorization system controls access to factory operations. Authorization checks run both client-side (for UI decisions) and server-side (for enforcement), ensuring security through the `[AuthorizeFactory]` attribute.

## Key Concepts

| Concept | Purpose |
|---------|---------|
| `[AuthorizeFactory]` | Marks authorization methods |
| `IPersonAuth` interface | Defines authorization rules for an entity |
| `Authorized` struct | Return type with success/failure and message |
| `Can*()` methods | Generated factory methods for UI checks |

## AuthorizeFactoryOperation Enum

```csharp
[Flags]
public enum AuthorizeFactoryOperation
{
    Create  = 1,    // Creating new instances
    Fetch   = 2,    // Reading/fetching instances
    Insert  = 4,    // Inserting new records
    Update  = 8,    // Modifying existing records
    Delete  = 16,   // Removing records
    Read    = 32,   // General read access
    Write   = 64,   // General write access
    Execute = 128   // Executing special operations
}
```

## Defining Authorization Interface

```csharp
public interface IPersonAuth
{
    [AuthorizeFactory(AuthorizeFactoryOperation.Create)]
    Authorized CanCreate();

    [AuthorizeFactory(AuthorizeFactoryOperation.Fetch)]
    Authorized CanFetch();

    [AuthorizeFactory(AuthorizeFactoryOperation.Update)]
    Authorized CanUpdate();

    [AuthorizeFactory(AuthorizeFactoryOperation.Delete)]
    Authorized CanDelete();
}
```

## Implementing Authorization

```csharp
public class PersonAuth : IPersonAuth
{
    private readonly IUser _user;

    public PersonAuth(IUser user)
    {
        _user = user ?? throw new ArgumentNullException(nameof(user));
    }

    public Authorized CanCreate()
    {
        if (_user.Role < Role.Admin)
            return Authorized.No("Only administrators can create persons.");
        return Authorized.Yes;
    }

    public Authorized CanFetch()
    {
        if (_user.Role < Role.User)
            return Authorized.No("You don't have permission to view persons.");
        return Authorized.Yes;
    }

    public Authorized CanUpdate()
    {
        if (_user.Role < Role.Editor)
            return Authorized.No("You don't have permission to edit persons.");
        return Authorized.Yes;
    }

    public Authorized CanDelete()
    {
        if (_user.Role < Role.Admin)
            return Authorized.No("Only administrators can delete persons.");
        return Authorized.Yes;
    }
}
```

## The Authorized Struct

### Basic Usage

```csharp
// Success
return Authorized.Yes;

// Failure with message
return Authorized.No("You don't have permission.");

// Implicit conversion from bool
return _user.IsAdmin;  // Converts to Authorized
```

### Structure

```csharp
public readonly struct Authorized
{
    public bool IsAuthorized { get; }
    public string? Message { get; }

    public static Authorized Yes => new(true, null);
    public static Authorized No(string? message = null) => new(false, message);

    // Implicit conversions
    public static implicit operator Authorized(bool value) => new(value, null);
    public static implicit operator bool(Authorized auth) => auth.IsAuthorized;
}
```

### Generic Authorized<T>

For operations returning values:

```csharp
public readonly struct Authorized<T>
{
    public bool IsAuthorized { get; }
    public string? Message { get; }
    public T? Value { get; }

    public static Authorized<T> Yes(T value) => new(true, null, value);
    public static Authorized<T> No(string? message = null) => new(false, message, default);
}
```

Used by `TrySave()`:

```csharp
var result = await factory.TrySave(person);
if (result.IsAuthorized)
{
    var savedPerson = result.Value;
}
else
{
    ShowError(result.Message);
}
```

## Generated Factory Methods

When authorization is configured, the factory includes these methods:

```csharp
public interface IPersonFactory
{
    // Standard operations - return null if unauthorized
    IPerson? Create();
    Task<IPerson?> Fetch(Guid id);
    Task<IPerson?> Save(IPerson target);

    // Try version with detailed result
    Task<Authorized<IPerson>> TrySave(IPerson target);

    // Authorization check methods
    Authorized CanCreate();
    Authorized CanFetch();
    Authorized CanInsert();
    Authorized CanUpdate();
    Authorized CanDelete();
    Authorized CanSave();  // Routes based on entity state
}
```

## Authorization Flow

### Operation to Authorization Mapping

| Operation | Authorization Method |
|-----------|---------------------|
| `factory.Create()` | `CanCreate()` |
| `factory.Fetch()` | `CanFetch()` |
| `factory.Save()` (new) | `CanCreate()` or `CanInsert()` |
| `factory.Save()` (existing) | `CanUpdate()` |
| `factory.Save()` (deleted) | `CanDelete()` |

### CanSave() Routing

```csharp
public Authorized CanSave()
{
    // Routes based on entity state:
    // - IsDeleted? -> CanDelete()
    // - IsNew? -> CanInsert() or CanCreate()
    // - Otherwise -> CanUpdate()
}
```

## DI Registration

```csharp
// Program.cs
builder.Services.AddScoped<IPersonAuth, PersonAuth>();
builder.Services.AddScoped<IUser, User>();
```

## Populating User Context

```csharp
// Server-side middleware
app.Use(async (context, next) =>
{
    var user = context.RequestServices.GetRequiredService<IUser>();

    if (context.User.Identity?.IsAuthenticated == true)
    {
        user.UserId = context.User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        user.Role = Enum.Parse<Role>(
            context.User.FindFirst(ClaimTypes.Role)?.Value ?? "None");
    }

    await next();
});
```

## ASP.NET Core Integration

### Using IAuthorizationService

```csharp
public class PersonAuth : IPersonAuth
{
    private readonly IAuthorizationService _authService;
    private readonly IHttpContextAccessor _httpContextAccessor;

    public PersonAuth(
        IAuthorizationService authService,
        IHttpContextAccessor httpContextAccessor)
    {
        _authService = authService;
        _httpContextAccessor = httpContextAccessor;
    }

    private ClaimsPrincipal User =>
        _httpContextAccessor.HttpContext?.User ?? new ClaimsPrincipal();

    public Authorized CanCreate()
    {
        var result = _authService.AuthorizeAsync(User, "CanCreatePerson")
            .GetAwaiter().GetResult();

        return result.Succeeded
            ? Authorized.Yes
            : Authorized.No("Policy 'CanCreatePerson' not satisfied.");
    }
}
```

### Defining Policies

```csharp
builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("CanCreatePerson", policy =>
        policy.RequireRole("Admin"));

    options.AddPolicy("CanEditPerson", policy =>
        policy.RequireRole("Admin", "Editor"));

    options.AddPolicy("CanViewPerson", policy =>
        policy.RequireAuthenticatedUser());
});
```

## Authorization Patterns

### Hierarchical Roles

```csharp
public enum Role
{
    None = 0,
    Guest = 1,
    User = 2,
    Editor = 3,
    Admin = 4,
    SuperAdmin = 5
}

public class PersonAuth : IPersonAuth
{
    public Authorized CanFetch() =>
        _user.Role >= Role.Guest
            ? Authorized.Yes
            : Authorized.No("Guests and above can view.");

    public Authorized CanUpdate() =>
        _user.Role >= Role.Editor
            ? Authorized.Yes
            : Authorized.No("Editors and above can modify.");

    public Authorized CanCreate() =>
        _user.Role >= Role.Admin
            ? Authorized.Yes
            : Authorized.No("Admins and above can create.");
}
```

### Resource-Based Authorization

```csharp
public class PersonAuth : IPersonAuth
{
    private readonly IUser _user;
    private readonly IContextAccessor<IPerson> _context;

    public PersonAuth(IUser user, IContextAccessor<IPerson> context)
    {
        _user = user;
        _context = context;
    }

    public Authorized CanUpdate()
    {
        var person = _context.Current;

        // Admins can update anyone
        if (_user.Role >= Role.Admin)
            return Authorized.Yes;

        // Users can update their own record
        if (person?.OwnerId == _user.UserId)
            return Authorized.Yes;

        return Authorized.No("You can only edit your own profile.");
    }
}
```

### Feature Flag Integration

```csharp
public class PersonAuth : IPersonAuth
{
    private readonly IUser _user;
    private readonly IFeatureManager _features;

    public PersonAuth(IUser user, IFeatureManager features)
    {
        _user = user;
        _features = features;
    }

    public Authorized CanCreate()
    {
        if (!_features.IsEnabled("PersonCreation"))
            return Authorized.No("Person creation is currently disabled.");

        if (_user.Role < Role.Admin)
            return Authorized.No("Only administrators can create persons.");

        return Authorized.Yes;
    }
}
```

## Blazor UI Integration

### Hiding Unauthorized Actions

```razor
@if (PersonFactory.CanCreate().IsAuthorized)
{
    <MudButton OnClick="CreateNew" Color="Color.Primary">
        Create New Person
    </MudButton>
}

@if (PersonFactory.CanDelete().IsAuthorized && !_person.IsNew)
{
    <MudButton OnClick="Delete" Color="Color.Error">
        Delete
    </MudButton>
}
```

### Displaying Authorization Messages

```razor
@{
    var canUpdate = PersonFactory.CanUpdate();
}

@if (!canUpdate.IsAuthorized)
{
    <MudAlert Severity="Severity.Warning">
        @canUpdate.Message
    </MudAlert>
    <PersonReadOnlyView Person="_person" />
}
else
{
    <PersonEditForm Person="_person" />
}
```

### Using TrySave

```csharp
private async Task Save()
{
    var result = await PersonFactory.TrySave(_person);

    if (result.IsAuthorized)
    {
        _person = result.Value;
        Snackbar.Add("Saved successfully", Severity.Success);
    }
    else
    {
        Snackbar.Add(result.Message, Severity.Error);
    }
}
```

## Unit Testing

### Testing Authorization Classes

```csharp
[TestMethod]
public void CanCreate_WhenAdmin_ReturnsAuthorized()
{
    // Arrange
    var user = new User { Role = Role.Admin };
    var auth = new PersonAuth(user);

    // Act
    var result = auth.CanCreate();

    // Assert
    Assert.IsTrue(result.IsAuthorized);
}

[TestMethod]
public void CanCreate_WhenUser_ReturnsUnauthorizedWithMessage()
{
    // Arrange
    var user = new User { Role = Role.User };
    var auth = new PersonAuth(user);

    // Act
    var result = auth.CanCreate();

    // Assert
    Assert.IsFalse(result.IsAuthorized);
    Assert.AreEqual("Only administrators can create persons.", result.Message);
}
```

### Integration Testing

```csharp
[TestMethod]
public void Create_WhenUnauthorized_ReturnsNull()
{
    // Arrange
    SetCurrentUser(Role.User);  // Not admin
    var factory = GetService<IPersonFactory>();

    // Act
    var person = factory.Create();

    // Assert
    Assert.IsNull(person);
}

[TestMethod]
public async Task TrySave_WhenUnauthorized_ReturnsFalseWithMessage()
{
    // Arrange
    SetCurrentUser(Role.Admin);
    var factory = GetService<IPersonFactory>();
    var person = factory.Create();
    person.FirstName = "Test";

    SetCurrentUser(Role.User);  // Downgrade permissions

    // Act
    var result = await factory.TrySave(person);

    // Assert
    Assert.IsFalse(result.IsAuthorized);
    Assert.IsNotNull(result.Message);
}
```

## Best Practices

1. **Use descriptive messages** - Help users understand why they're denied
2. **Check on client and server** - Client for UX, server for security
3. **Keep authorization logic simple** - Complex logic should be in services
4. **Use role hierarchies** - Avoid repetitive checks with `>=` comparisons
5. **Test all paths** - Both authorized and unauthorized scenarios
6. **Inject dependencies** - Use DI for user context and services

## Common Pitfalls

1. **Forgetting server-side checks** - UI checks alone are not secure
2. **Not registering authorization service** - Factory won't find it
3. **Blocking bool returns** - Async authorization must be awaited properly
4. **Missing role in claims** - Ensure authentication populates roles
5. **Not using TrySave** - Missing opportunity for graceful error handling
