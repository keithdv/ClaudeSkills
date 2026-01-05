# Neatoo Client-Server Architecture Reference

## Overview

Neatoo.RemoteFactory enables sharing domain models between Blazor WebAssembly clients and ASP.NET Core servers. A single HTTP endpoint handles all factory operations with automatic serialization.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Blazor WebAssembly Client                     │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │ PersonFactory │    │ OrderFactory │    │ Other Factory│       │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘       │
│         │                   │                   │                │
│         └───────────────────┼───────────────────┘                │
│                             │                                    │
│                    ┌────────▼────────┐                           │
│                    │ RemoteNeatoo    │                           │
│                    │ Portal (Client) │                           │
│                    └────────┬────────┘                           │
└─────────────────────────────┼────────────────────────────────────┘
                              │
                        HTTP POST
                      /api/neatoo
                              │
┌─────────────────────────────┼────────────────────────────────────┐
│                    ASP.NET Core Server                           │
│                             │                                    │
│                    ┌────────▼────────┐                           │
│                    │ NeatooJsonPortal│                           │
│                    │    (Server)     │                           │
│                    └────────┬────────┘                           │
│                             │                                    │
│         ┌───────────────────┼───────────────────┐                │
│         │                   │                   │                │
│  ┌──────▼───────┐    ┌──────▼───────┐    ┌──────▼───────┐       │
│  │ PersonFactory │    │ OrderFactory │    │ Other Factory│       │
│  │  (resolves    │    │  (resolves   │    │  (resolves   │       │
│  │  services)    │    │  services)   │    │  services)   │       │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘       │
│         │                   │                   │                │
│  ┌──────▼───────┐    ┌──────▼───────┐    ┌──────▼───────┐       │
│  │  DbContext   │    │  DbContext   │    │   Services   │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
└──────────────────────────────────────────────────────────────────┘
```

## Single Endpoint Design

All Neatoo operations route through one endpoint: `/api/neatoo`

### Benefits

- Simple security configuration
- Centralized logging and monitoring
- Single point for authentication/authorization
- Automatic handling of complex object graphs

### Request Format

```json
{
  "factoryType": "IPersonFactory",
  "operationType": "Fetch",
  "parameters": {
    "id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "entityData": null
}
```

### Response Format

```json
{
  "success": true,
  "entity": {
    "$type": "Person",
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "firstName": "John",
    "lastName": "Doe"
  },
  "errorMessage": null
}
```

## Server Setup

### Package Installation

```bash
dotnet add package Neatoo
dotnet add package Neatoo.RemoteFactory
```

### Program.cs Configuration

```csharp
using Neatoo;

var builder = WebApplication.CreateBuilder(args);

// Add Neatoo services in LOCAL mode (server executes operations)
builder.Services.AddNeatooServices(
    NeatooFactory.Local,
    typeof(Person).Assembly);  // Assembly containing your entities

// Register your DbContext and services
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("Default")));

builder.Services.AddScoped<IDbContext>(sp =>
    sp.GetRequiredService<AppDbContext>());

var app = builder.Build();

// Map the Neatoo endpoint
app.MapPost("/api/neatoo", async (HttpContext context) =>
{
    var portal = context.RequestServices
        .GetRequiredService<INeatooJsonPortal>();
    return await portal.Execute(context);
});

app.Run();
```

### NeatooFactory Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `NeatooFactory.Local` | Executes operations locally | Server-side |
| `NeatooFactory.Remote` | Proxies to remote server | Client-side |

## Client Setup (Blazor WebAssembly)

### Package Installation

```bash
dotnet add package Neatoo
dotnet add package Neatoo.RemoteFactory
```

### Program.cs Configuration

```csharp
using Neatoo;

var builder = WebAssemblyHostBuilder.CreateDefault(args);

// Add Neatoo services in REMOTE mode (operations sent to server)
builder.Services.AddNeatooServices(
    NeatooFactory.Remote,
    typeof(IPerson).Assembly);  // Assembly containing your interfaces

// Configure the remote portal
builder.Services.AddRemoteNeatooPortal(
    new Uri(builder.HostEnvironment.BaseAddress + "api/neatoo"));

await builder.Build().RunAsync();
```

### HTTP Client Configuration

The `AddRemoteNeatooPortal` configures an `HttpClient` for Neatoo requests:

```csharp
// Custom configuration
builder.Services.AddRemoteNeatooPortal(
    new Uri(builder.HostEnvironment.BaseAddress + "api/neatoo"),
    httpClientBuilder =>
    {
        httpClientBuilder.ConfigureHttpClient(client =>
        {
            client.Timeout = TimeSpan.FromMinutes(5);
        });
    });
```

## Project Structure

### Recommended Solution Layout

```
Solution/
├── MyApp.Shared/           # Shared interfaces and contracts
│   ├── Interfaces/
│   │   ├── IPerson.cs
│   │   └── IOrder.cs
│   └── DTOs/
│       └── CustomerResult.cs
│
├── MyApp.Domain/           # Domain entities and business logic
│   ├── Entities/
│   │   ├── Person.cs
│   │   └── Order.cs
│   ├── Rules/
│   │   └── EmailValidationRule.cs
│   └── Services/
│       └── IEmailService.cs
│
├── MyApp.Server/           # ASP.NET Core server
│   ├── Program.cs
│   ├── Data/
│   │   └── AppDbContext.cs
│   └── Services/
│       └── EmailService.cs
│
└── MyApp.Client/           # Blazor WebAssembly client
    └── Program.cs
```

### Assembly References

| Project | References |
|---------|------------|
| Shared | Neatoo (interfaces only) |
| Domain | Shared, Neatoo |
| Server | Domain, Shared, Neatoo.RemoteFactory |
| Client | Shared, Neatoo.RemoteFactory |

### Key Principle

- **Client** references interfaces (IPerson) from Shared
- **Server** references implementations (Person) from Domain
- **Both** can create/manipulate entities through factories

## [Remote] Attribute

The `[Remote]` attribute marks methods that execute on the server:

```csharp
[Factory]
internal partial class Person : EntityBase<Person>, IPerson
{
    // Runs on CLIENT - no [Remote]
    [Create]
    public void Create()
    {
        Status = Status.Draft;
    }

    // Runs on SERVER - has [Remote]
    [Remote]
    [Fetch]
    public async Task<bool> Fetch([Service] IDbContext db)
    {
        var entity = await db.Persons.FindAsync(Id);
        // ...
    }

    // Runs on SERVER - has [Remote]
    [Remote]
    [Insert]
    public async Task Insert([Service] IDbContext db)
    {
        // ...
    }
}
```

### When Methods Run

| Scenario | [Create] | [Fetch]/[Insert]/[Update]/[Delete] |
|----------|----------|-------------------------------------|
| Client calls factory | Client | Server (via HTTP) |
| Server calls factory | Server | Server (local) |

## Serialization

Neatoo uses System.Text.Json with custom converters for:

- Entity graphs with circular references
- Interface-based deserialization
- Meta-property preservation

### Automatic Handling

- Entity references serialize by ID then full object
- Child collections serialize inline
- Validation state transfers with entity

### Property Requirements

Properties must be `partial` and have public getters for serialization:

```csharp
// Serializable
public partial string? FirstName { get; set; }
public partial IOrderLineList? Lines { get; set; }

// Not serialized (no setter or private)
public string FullName => $"{FirstName} {LastName}";
```

### Ordinal Serialization (10.2.0+)

Ordinal serialization reduces payload sizes by 40-50% by using numeric indices instead of property names:

```csharp
// Named format (legacy)
{"firstName":"John","lastName":"Doe","age":30}

// Ordinal format (default since 10.2.0)
{"0":"John","1":"Doe","2":30}
```

#### Configuration

```csharp
// Server configuration
builder.Services.AddNeatooServices(
    NeatooFactory.Local,
    typeof(Person).Assembly,
    options =>
    {
        options.SerializationFormat = SerializationFormat.Ordinal; // Default
        // options.SerializationFormat = SerializationFormat.Named; // Legacy
    });
```

#### Format Negotiation

The `X-Neatoo-Format` HTTP header controls format selection:

| Header Value | Format |
|--------------|--------|
| `ordinal` | Compact numeric indices (default) |
| `named` | Traditional property names |

Client and server automatically negotiate format via this header.

## Logging and Distributed Tracing (10.3.0+)

RemoteFactory provides structured logging with CorrelationId for distributed tracing.

### Setup

```csharp
// Server Program.cs
builder.Services.AddLogging(logging =>
{
    logging.AddConsole();
    logging.SetMinimumLevel(LogLevel.Information);
});

var app = builder.Build();

// Enable ambient logging for static contexts
NeatooLogging.SetLoggerFactory(
    app.Services.GetRequiredService<ILoggerFactory>());
```

### CorrelationId

Requests are traced across client and server with a unique correlation ID:

```
[a1b2c3d4] Remote delegate call started: PersonFactory+FetchByIdDelegate
[a1b2c3d4] Handling remote request for delegate PersonFactory+FetchByIdDelegate
[a1b2c3d4] Factory operation Fetch started for Person
[a1b2c3d4] Factory operation Fetch completed for Person in 12ms
[a1b2c3d4] Remote request completed in 45ms
```

The ID propagates via:
- `CorrelationContext.CorrelationId` ambient property (AsyncLocal)
- `X-Correlation-Id` HTTP header

### Event ID Ranges

| Range | Subsystem | Examples |
|-------|-----------|----------|
| 1xxx | Serialization | Serialize, Deserialize, Format selection |
| 2xxx | Factory Operations | Create, Fetch, Insert, Update, Delete |
| 3xxx | Remote Calls (Client) | HTTP request/response, errors |
| 4xxx | Converter Factory | Converter creation, cache hits |
| 5xxx | Authorization | Auth checks, grants, denials |
| 6xxx | Service Registration | DI registration events |
| 7xxx | Server-Side Handling | Request handling, completion |
| 8xxx | Factory Lifecycle | Start, Complete, Cancelled |

### Logger Categories

| Category | Purpose |
|----------|---------|
| `Neatoo.RemoteFactory.Internal.FactoryCore` | Factory operation lifecycle |
| `Neatoo.RemoteFactory.Internal.NeatooJsonSerializer` | Serialization events |
| `Neatoo.RemoteFactory.Server` | Server-side request handling |

### Recommended Configuration

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Warning",
      "Neatoo.RemoteFactory": "Information"
    }
  }
}
```

| Environment | Recommended Level |
|-------------|------------------|
| Production | Information |
| Development | Debug |
| Troubleshooting | Trace |

## Authentication Integration

### Server-Side Authentication

```csharp
// Program.cs
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        // Configure JWT validation
    });

var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();

// Neatoo endpoint with authorization
app.MapPost("/api/neatoo", async (HttpContext context) =>
{
    var portal = context.RequestServices
        .GetRequiredService<INeatooJsonPortal>();
    return await portal.Execute(context);
}).RequireAuthorization();
```

### Client-Side Token Handling

```csharp
builder.Services.AddRemoteNeatooPortal(
    new Uri(builder.HostEnvironment.BaseAddress + "api/neatoo"),
    httpClientBuilder =>
    {
        httpClientBuilder.AddHttpMessageHandler<AuthorizationMessageHandler>();
    });

// Custom handler to add JWT token
public class AuthorizationMessageHandler : DelegatingHandler
{
    private readonly IAuthService _authService;

    public AuthorizationMessageHandler(IAuthService authService)
    {
        _authService = authService;
    }

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        var token = await _authService.GetTokenAsync();
        if (!string.IsNullOrEmpty(token))
        {
            request.Headers.Authorization =
                new AuthenticationHeaderValue("Bearer", token);
        }
        return await base.SendAsync(request, cancellationToken);
    }
}
```

### Accessing User in Factory Methods

```csharp
[Remote]
[Fetch]
public async Task<bool> Fetch(
    [Service] IDbContext db,
    [Service] IHttpContextAccessor httpContextAccessor)
{
    var userId = httpContextAccessor.HttpContext?.User
        .FindFirst(ClaimTypes.NameIdentifier)?.Value;

    // Use userId for row-level security
    var entity = await db.Persons
        .Where(p => p.Id == Id && p.OwnerId == userId)
        .FirstOrDefaultAsync();

    // ...
}
```

## Error Handling

### Server Errors

Exceptions on the server are caught and serialized:

```csharp
// Server throws
[Remote]
[Update]
public async Task Update([Service] IDbContext db)
{
    var entity = await db.Persons.FindAsync(Id);
    if (entity == null)
        throw new InvalidOperationException($"Person {Id} not found");
}

// Client receives exception
try
{
    person = await personFactory.Save(person);
}
catch (InvalidOperationException ex)
{
    // ex.Message contains server error
}
```

### Authorization Failures

```csharp
var result = await personFactory.TrySave(person);
if (!result.IsAuthorized)
{
    // result.Message contains authorization failure reason
    ShowError(result.Message);
}
```

### Network Errors

```csharp
try
{
    person = await personFactory.Save(person);
}
catch (HttpRequestException ex)
{
    ShowError("Network error: " + ex.Message);
}
catch (TaskCanceledException)
{
    ShowError("Request timed out");
}
```

## Local vs Remote Execution

### Running Locally (Testing/Debugging)

You can run the client without a server by using Local mode:

```csharp
// For testing without server
builder.Services.AddNeatooServices(
    NeatooFactory.Local,  // Changes to local mode
    typeof(Person).Assembly);

// Register services normally
builder.Services.AddDbContext<AppDbContext>();
```

### Conditional Configuration

```csharp
var isClientSide = builder.HostEnvironment.IsEnvironment("ClientSide");

if (isClientSide)
{
    builder.Services.AddNeatooServices(
        NeatooFactory.Remote,
        typeof(IPerson).Assembly);

    builder.Services.AddRemoteNeatooPortal(
        new Uri(builder.HostEnvironment.BaseAddress + "api/neatoo"));
}
else
{
    builder.Services.AddNeatooServices(
        NeatooFactory.Local,
        typeof(Person).Assembly);

    // Register local services
}
```

## Performance Considerations

### Minimize Round Trips

```csharp
// INEFFICIENT - multiple round trips
var person = await personFactory.Fetch(id);
var orders = await orderFactory.FetchByPerson(id);
var addresses = await addressFactory.FetchByPerson(id);

// BETTER - fetch aggregate with children
var person = await personFactory.FetchWithDetails(id);
// Includes orders and addresses in one call
```

### Lazy Loading Alternatives

Neatoo doesn't support lazy loading across the wire. Include related data in Fetch:

```csharp
[Remote]
[Fetch]
public async Task<bool> FetchWithDetails(
    [Service] IDbContext db,
    [Service] IOrderListFactory orderListFactory)
{
    var entity = await db.Persons
        .Include(p => p.Orders)
        .Include(p => p.Addresses)
        .FirstOrDefaultAsync(p => p.Id == Id);

    if (entity == null) return false;

    LoadProperty(nameof(Id), entity.Id);
    // ... other properties

    Orders = await orderListFactory.Fetch(entity.Orders);

    return true;
}
```

### Payload Size

Only modified properties serialize for updates:

```csharp
// Full entity serialized on first send
var person = await personFactory.Fetch(id);

// Only modified properties + metadata sent on save
person.Email = "new@email.com";
person = await personFactory.Save(person);
```

## WPF Applications

For WPF apps, use Local mode since there's no client-server split:

```csharp
// App.xaml.cs or service configuration
services.AddNeatooServices(
    NeatooFactory.Local,
    typeof(Person).Assembly);

services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(connectionString));
```

### Separate Server for WPF

If WPF needs to call a central server:

```csharp
services.AddNeatooServices(
    NeatooFactory.Remote,
    typeof(IPerson).Assembly);

services.AddRemoteNeatooPortal(
    new Uri("https://api.myapp.com/api/neatoo"));
```

## Best Practices

### Keep Shared Assembly Thin

Only interfaces and shared DTOs in Shared project:

```csharp
// In Shared - interface only
public interface IPerson : IEntityBase
{
    Guid? Id { get; set; }
    string? FirstName { get; set; }
}

// In Domain - implementation
[Factory]
internal partial class Person : EntityBase<Person>, IPerson { }
```

### Use [Service] for Dependencies

```csharp
// Dependencies resolved from server DI container
[Remote]
[Fetch]
public async Task<bool> Fetch(
    [Service] IDbContext db,
    [Service] ILogger<Person> logger,
    [Service] ICacheService cache)
{
    // ...
}
```

### Handle Offline Scenarios

```csharp
public async Task<IPerson?> FetchWithFallback(Guid id)
{
    try
    {
        return await personFactory.Fetch(id);
    }
    catch (HttpRequestException)
    {
        // Fall back to local cache
        return await localCache.GetPersonAsync(id);
    }
}
```

## Cancellation Support

### How It Works

Cancellation flows from client to server via HTTP connection state:

```
CLIENT                                          SERVER
┌─────────────────────────────────────┐         ┌─────────────────────────────────────┐
│ factory.FetchAsync(id, ct)          │         │                                     │
│   │                                 │         │                                     │
│   ▼                                 │         │                                     │
│ HttpClient.SendAsync(request, ct) ──┼── TCP ──┼──► HttpContext.RequestAborted       │
│   │                                 │         │         │                           │
│   │  ct.Cancel() ───────────────────┼─► X ────┼─► fires │                           │
│   │                                 │  close  │         ▼                           │
│   ▼                                 │  conn   │    Server stops processing          │
│ OperationCanceledException          │         │                                     │
└─────────────────────────────────────┘         └─────────────────────────────────────┘
```

### Client Usage

```csharp
// With explicit CancellationToken
using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(30));
try
{
    var person = await personFactory.FetchAsync(id, cts.Token);
}
catch (OperationCanceledException)
{
    // Request was cancelled (timeout or explicit cancellation)
}

// Cancel on user action
private CancellationTokenSource? _cts;

async Task LoadData()
{
    _cts?.Cancel();
    _cts = new CancellationTokenSource();

    try
    {
        Data = await factory.FetchAsync(id, _cts.Token);
    }
    catch (OperationCanceledException)
    {
        // Previous request cancelled, new one in progress
    }
}
```

### Server-Side Handling

The server combines multiple cancellation sources:

| Source | When it fires |
|--------|---------------|
| `HttpContext.RequestAborted` | Client disconnects, browser closes, network failure |
| `IHostApplicationLifetime.ApplicationStopping` | Server graceful shutdown |

Both trigger the same CancellationToken in your factory methods.

### Domain Method Implementation

```csharp
[Remote]
[Fetch]
public async Task<bool> FetchAsync(
    Guid id,
    CancellationToken cancellationToken,
    [Service] IDbContext db)
{
    // Pass token to EF Core
    var entity = await db.Orders
        .Include(o => o.Lines)
        .FirstOrDefaultAsync(o => o.Id == id, cancellationToken);

    if (entity == null) return false;

    // Check at safe points for long operations
    cancellationToken.ThrowIfCancellationRequested();

    // ... process data
    return true;
}
```

### Lifecycle Hooks

```csharp
[Factory]
public class Order : EntityBase<Order>, IFactoryOnCancelled
{
    public void FactoryCancelled(FactoryOperation operation)
    {
        // Clean up resources when operation is cancelled
        _tempFile?.Delete();
    }
}
```

### Best Practices

1. **Pass CancellationToken to all async calls** - EF Core, HttpClient, file I/O
2. **Check cancellation at safe points** - Before expensive operations
3. **Use transactions for atomicity** - Cancellation between DB calls leaves partial state
4. **Handle OperationCanceledException** - Don't let it crash your UI

## Common Pitfalls

1. **Wrong NeatooFactory mode** - Server needs Local, Client needs Remote
2. **Missing [Remote] attribute** - Server methods won't execute on server
3. **Referencing Domain from Client** - Client should only reference Shared
4. **Not configuring authentication** - Endpoint unprotected by default
5. **Large payloads** - Include only needed data in responses
6. **Ignoring CancellationToken** - Operations continue after client disconnects
