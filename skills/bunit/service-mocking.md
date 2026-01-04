# Service Mocking

## Dependency Injection Basics

### Registering Services

```csharp
public class MyTests : TestContext
{
    public MyTests()
    {
        // Singleton - shared across all components in test
        Services.AddSingleton<IUserService, MockUserService>();

        // Scoped - one instance per component render
        Services.AddScoped<IDbContext, TestDbContext>();

        // Transient - new instance each injection
        Services.AddTransient<IValidator, TestValidator>();
    }
}
```

### Using Instances

```csharp
[Fact]
public void Component_UsesInjectedService()
{
    var mockService = new MockProductService();
    mockService.Products = new List<Product>
    {
        new() { Id = 1, Name = "Widget" }
    };

    Services.AddSingleton<IProductService>(mockService);

    var cut = RenderComponent<ProductList>();

    cut.Find(".product-name").TextContent.ShouldBe("Widget");
}
```

## Mocking with Moq

### Basic Mock Setup

```csharp
public class ProductTests : TestContext
{
    private readonly Mock<IProductService> _productServiceMock;

    public ProductTests()
    {
        _productServiceMock = new Mock<IProductService>();
        Services.AddSingleton(_productServiceMock.Object);
    }

    [Fact]
    public void ProductList_LoadsProducts()
    {
        _productServiceMock
            .Setup(s => s.GetAllAsync())
            .ReturnsAsync(new List<Product>
            {
                new() { Id = 1, Name = "Widget" },
                new() { Id = 2, Name = "Gadget" }
            });

        var cut = RenderComponent<ProductList>();

        cut.FindAll(".product-item").Count.ShouldBe(2);
    }
}
```

### Verifying Method Calls

```csharp
[Fact]
public void SaveButton_CallsServiceSave()
{
    _productServiceMock
        .Setup(s => s.SaveAsync(It.IsAny<Product>()))
        .ReturnsAsync(true);

    var product = new Product { Id = 1, Name = "Test" };
    var cut = RenderComponent<ProductEditor>(p => p
        .Add(x => x.Product, product));

    cut.Find(".save-btn").Click();

    _productServiceMock.Verify(
        s => s.SaveAsync(It.Is<Product>(p => p.Id == 1)),
        Times.Once);
}
```

### Throwing Exceptions

```csharp
[Fact]
public void Component_HandlesServiceError()
{
    _productServiceMock
        .Setup(s => s.GetByIdAsync(It.IsAny<int>()))
        .ThrowsAsync(new InvalidOperationException("Database error"));

    var cut = RenderComponent<ProductDetail>(p => p
        .Add(x => x.ProductId, 1));

    cut.WaitForAssertion(() =>
    {
        cut.Find(".error-message").TextContent.ShouldContain("error");
    });
}
```

### Callback for Side Effects

```csharp
[Fact]
public void Service_TracksMethodCalls()
{
    var savedProducts = new List<Product>();

    _productServiceMock
        .Setup(s => s.SaveAsync(It.IsAny<Product>()))
        .Callback<Product>(p => savedProducts.Add(p))
        .ReturnsAsync(true);

    var cut = RenderComponent<ProductEditor>();
    cut.Find("input.name").Change("New Product");
    cut.Find(".save-btn").Click();

    savedProducts.Count.ShouldBe(1);
    savedProducts[0].Name.ShouldBe("New Product");
}
```

## Mocking with KnockOff

KnockOff provides source-generated test stubs as a type-safe alternative to Moq. It generates strongly-typed `Spy` handlers for each interface member with call tracking and delegate-based callbacks.

### Basic KnockOff Setup

```csharp
// Define stub once (typically in shared test file)
[KnockOff]
public partial class ProductServiceKnockOff : IProductService { }

public class ProductTests : TestContext
{
    private readonly ProductServiceKnockOff _productService;

    public ProductTests()
    {
        _productService = new ProductServiceKnockOff();
        Services.AddSingleton<IProductService>(_productService);
    }

    [Fact]
    public void ProductList_LoadsProducts()
    {
        // OnCall takes a delegate - first param is always the knockoff instance
        _productService.Spy.GetAllAsync.OnCall((ProductServiceKnockOff ko) =>
            Task.FromResult<IEnumerable<Product>>(new List<Product>
            {
                new() { Id = 1, Name = "Widget" },
                new() { Id = 2, Name = "Gadget" }
            }));

        var cut = RenderComponent<ProductList>();

        cut.FindAll(".product-item").Count.ShouldBe(2);
    }
}
```

### Verifying Method Calls

```csharp
[Fact]
public void SaveButton_CallsServiceSave()
{
    // Method with parameter - delegate includes ko + all params
    _productService.Spy.SaveAsync.OnCall((ProductServiceKnockOff ko, Product product) =>
        Task.FromResult(true));

    var product = new Product { Id = 1, Name = "Test" };
    var cut = RenderComponent<ProductEditor>(p => p
        .Add(x => x.Product, product));

    cut.Find(".save-btn").Click();

    // Verify with strongly-typed tracking
    Assert.Equal(1, _productService.Spy.SaveAsync.CallCount);
    Assert.Equal(1, _productService.Spy.SaveAsync.LastCallArg?.Id);

    // All calls are tracked
    var allCalls = _productService.Spy.SaveAsync.AllCalls;
    Assert.Single(allCalls);
}
```

### User Methods for Default Behavior

```csharp
// Define default behavior in the stub class
[KnockOff]
public partial class ProductServiceKnockOff : IProductService
{
    // Default: return empty list (called when no OnCall set)
    protected Task<IEnumerable<Product>> GetAllAsync() =>
        Task.FromResult<IEnumerable<Product>>(new List<Product>());

    // Default: save always succeeds
    protected Task<bool> SaveAsync(Product product) =>
        Task.FromResult(true);
}

// In tests, override only when needed
[Fact]
public void ProductList_ShowsProducts()
{
    // Override default for this test
    _productService.Spy.GetAllAsync.OnCall((ProductServiceKnockOff ko) =>
        Task.FromResult<IEnumerable<Product>>(testProducts));

    var cut = RenderComponent<ProductList>();
    // ...
}
```

### Throwing Exceptions

```csharp
[Fact]
public void Component_HandlesServiceError()
{
    _productService.Spy.GetByIdAsync.OnCall((ProductServiceKnockOff ko, int id) =>
        Task.FromException<Product?>(new InvalidOperationException("Database error")));

    var cut = RenderComponent<ProductDetail>(p => p
        .Add(x => x.ProductId, 1));

    cut.WaitForAssertion(() =>
    {
        cut.Find(".error-message").TextContent.ShouldContain("error");
    });
}
```

### Out and Ref Parameters

```csharp
// Interface with out parameter
public interface IParser
{
    bool TryParse(string input, out int result);
}

[KnockOff]
public partial class ParserKnockOff : IParser { }

[Fact]
public void Parser_HandlesOutParameter()
{
    var parser = new ParserKnockOff();

    // Out params use explicit types in lambda (C# requirement)
    parser.Spy.TryParse.OnCall((ParserKnockOff ko, string input, out int result) =>
    {
        if (int.TryParse(input, out result))
            return true;
        result = 0;
        return false;
    });

    Services.AddSingleton<IParser>(parser);
    var cut = RenderComponent<NumberInput>();

    // Out params not tracked (they're outputs, not inputs)
    // Only input params tracked: parser.Spy.TryParse.LastCallArg == "42"
}
```

### Method Overloads

```csharp
public interface IFormatter
{
    string Format(string input);
    string Format(string input, bool uppercase);
}

[KnockOff]
public partial class FormatterKnockOff : IFormatter { }

[Fact]
public void Formatter_HandlesOverloads()
{
    var formatter = new FormatterKnockOff();

    // Each overload has its own delegate type - cast to disambiguate
    formatter.Spy.Format.OnCall(
        (FormatterKnockOff.FormatHandler.FormatDelegate0)((ko, input) => input.Trim()));

    formatter.Spy.Format.OnCall(
        (FormatterKnockOff.FormatHandler.FormatDelegate1)((ko, input, uppercase) =>
            uppercase ? input.ToUpper() : input.ToLower()));

    // All overloads share tracking (CallCount, AllCalls)
    // Params not in all overloads are nullable in the tuple
}
```

### Reset Tracking

```csharp
[Fact]
public void MultipleScenarios_ResetBetween()
{
    // First scenario
    _productService.Spy.GetAllAsync.OnCall((ProductServiceKnockOff ko) =>
        Task.FromResult<IEnumerable<Product>>(new List<Product>()));

    var cut1 = RenderComponent<ProductList>();
    Assert.Equal(1, _productService.Spy.GetAllAsync.CallCount);

    // Reset for next scenario
    _productService.Spy.GetAllAsync.Reset();
    Assert.Equal(0, _productService.Spy.GetAllAsync.CallCount);
    Assert.False(_productService.Spy.GetAllAsync.WasCalled);
}
```

### KnockOff vs Moq Comparison

| Pattern | Moq | KnockOff |
|---------|-----|----------|
| Setup returns | `.Setup(s => s.Method()).ReturnsAsync(value)` | `.Spy.Method.OnCall((ko) => Task.FromResult(value))` |
| Setup with args | `.Setup(s => s.Method(It.IsAny<int>())).Returns(...)` | `.Spy.Method.OnCall((ko, arg) => ...)` |
| Verify call count | `.Verify(s => s.Method(), Times.Once)` | `Assert.Equal(1, .Spy.Method.CallCount)` |
| Verify was called | `.Verify(s => s.Method(), Times.AtLeastOnce)` | `Assert.True(.Spy.Method.WasCalled)` |
| Last argument | `.Callback<T>(arg => captured = arg)` | `.Spy.Method.LastCallArg` or `.LastCallArgs` |
| All arguments | Manual list in callback | `.Spy.Method.AllCalls` (automatic) |
| Default behavior | Per-test `.Setup()` | User method in partial class |
| Out/ref params | `It.Ref<T>.IsAny`, callback setup | Native support with typed delegates |
| Type safety | Expression trees (runtime) | Source-generated (compile-time) |

## NavigationManager

### Using FakeNavigationManager

```csharp
public class NavigationTests : TestContext
{
    [Fact]
    public void LoginSuccess_NavigatesToDashboard()
    {
        var navManager = Services.GetRequiredService<FakeNavigationManager>();

        var cut = RenderComponent<LoginForm>();
        cut.Find("input.username").Change("admin");
        cut.Find("input.password").Change("password");
        cut.Find("form").Submit();

        navManager.Uri.ShouldEndWith("/dashboard");
    }

    [Fact]
    public void BackButton_NavigatesBack()
    {
        var navManager = Services.GetRequiredService<FakeNavigationManager>();

        var cut = RenderComponent<DetailPage>(p => p
            .Add(x => x.ReturnUrl, "/products"));

        cut.Find(".back-btn").Click();

        navManager.Uri.ShouldEndWith("/products");
    }
}
```

### Testing Navigation History

```csharp
[Fact]
public void Wizard_TracksNavigationSteps()
{
    var navManager = Services.GetRequiredService<FakeNavigationManager>();

    var cut = RenderComponent<Wizard>();

    cut.Find(".next-btn").Click();
    cut.Find(".next-btn").Click();

    navManager.History.Count.ShouldBe(3); // Initial + 2 navigations
}
```

## HttpClient Mocking

### Using MockHttpMessageHandler

```csharp
public class ApiTests : TestContext
{
    private readonly MockHttpMessageHandler _mockHttp;

    public ApiTests()
    {
        _mockHttp = new MockHttpMessageHandler();
        var client = _mockHttp.ToHttpClient();
        client.BaseAddress = new Uri("https://api.example.com/");

        Services.AddSingleton(client);
    }

    [Fact]
    public void Component_FetchesDataFromApi()
    {
        _mockHttp.When("/api/products")
            .Respond("application/json", "[{\"id\":1,\"name\":\"Widget\"}]");

        var cut = RenderComponent<ProductList>();

        cut.WaitForAssertion(() =>
        {
            cut.Find(".product-name").TextContent.ShouldBe("Widget");
        });
    }
}
```

### HttpClientFactory

```csharp
public class HttpClientTests : TestContext
{
    [Fact]
    public void Component_UsesNamedClient()
    {
        var mockHandler = new MockHttpMessageHandler();
        mockHandler.When("/api/users").Respond("application/json", "[]");

        Services.AddHttpClient("UsersApi", client =>
        {
            client.BaseAddress = new Uri("https://users.api.com/");
        }).ConfigurePrimaryHttpMessageHandler(() => mockHandler);

        var cut = RenderComponent<UserList>();

        mockHandler.VerifyNoOutstandingExpectation();
    }
}
```

## JavaScript Interop

### Loose Mode (Allow All)

```csharp
public class JsTests : TestContext
{
    public JsTests()
    {
        // Allow all JS calls without explicit setup
        JSInterop.Mode = JSRuntimeMode.Loose;
    }

    [Fact]
    public void Component_CallsJs()
    {
        var cut = RenderComponent<ChartComponent>();
        // Any JS calls are allowed in loose mode
    }
}
```

### Strict Mode (Explicit Setup)

```csharp
public class JsTests : TestContext
{
    public JsTests()
    {
        JSInterop.Mode = JSRuntimeMode.Strict;
    }

    [Fact]
    public void Component_InitializesChart()
    {
        // Must explicitly set up expected calls
        JSInterop.SetupVoid("initChart", "chartElement", 100, 200);

        var cut = RenderComponent<ChartComponent>(p => p
            .Add(x => x.Width, 100)
            .Add(x => x.Height, 200));

        JSInterop.VerifyInvoke("initChart");
    }
}
```

### Returning Values from JS

```csharp
[Fact]
public void Component_GetsWindowSize()
{
    JSInterop
        .Setup<int[]>("getWindowSize")
        .SetResult(new[] { 1920, 1080 });

    var cut = RenderComponent<ResponsiveLayout>();

    cut.Find(".resolution").TextContent.ShouldContain("1920x1080");
}
```

### Async JS Interop

```csharp
[Fact]
public async Task Component_LoadsFromLocalStorage()
{
    JSInterop
        .Setup<string>("localStorage.getItem", "theme")
        .SetResult("dark");

    var cut = RenderComponent<ThemeProvider>();

    await cut.WaitForStateAsync(() => cut.Instance.CurrentTheme == "dark");

    cut.Find("body").ClassList.ShouldContain("dark-theme");
}
```

### Module Imports

```csharp
[Fact]
public void Component_ImportsJsModule()
{
    var moduleInterop = JSInterop.SetupModule("./chart.js");
    moduleInterop.SetupVoid("renderChart", _ => true);

    var cut = RenderComponent<ModularChart>();

    moduleInterop.VerifyInvoke("renderChart");
}
```

## Authorization

### Mocking AuthenticationState

```csharp
public class AuthTests : TestContext
{
    public AuthTests()
    {
        // Create authenticated user
        var authContext = this.AddTestAuthorization();
        authContext.SetAuthorized("TestUser");
        authContext.SetRoles("Admin", "User");
        authContext.SetClaims(new Claim("email", "test@example.com"));
    }

    [Fact]
    public void AdminPanel_ShowsForAdmin()
    {
        var cut = RenderComponent<AdminPanel>();

        cut.FindAll(".admin-content").Count.ShouldBe(1);
    }
}
```

### Testing Unauthenticated State

```csharp
[Fact]
public void ProtectedContent_HiddenWhenNotAuthenticated()
{
    var authContext = this.AddTestAuthorization();
    authContext.SetNotAuthorized();

    var cut = RenderComponent<ProtectedPage>();

    cut.FindAll(".protected-content").Count.ShouldBe(0);
    cut.Find(".login-prompt").ShouldNotBeNull();
}
```

### Policy-Based Authorization

```csharp
[Fact]
public void AdminFeature_RequiresPolicy()
{
    var authContext = this.AddTestAuthorization();
    authContext.SetAuthorized("TestUser");
    authContext.SetPolicies("RequireAdmin");

    var cut = RenderComponent<AdminFeature>();

    cut.Find(".admin-only").ShouldNotBeNull();
}
```

## State Management (Flux/Redux Patterns)

### Mocking State Container

```csharp
public class StateTests : TestContext
{
    private readonly Mock<IAppState> _stateMock;

    public StateTests()
    {
        _stateMock = new Mock<IAppState>();
        _stateMock.Setup(s => s.CurrentUser).Returns(new User { Name = "TestUser" });
        _stateMock.Setup(s => s.CartItems).Returns(new List<CartItem>());

        Services.AddSingleton(_stateMock.Object);
    }

    [Fact]
    public void Header_ShowsCurrentUser()
    {
        var cut = RenderComponent<Header>();

        cut.Find(".username").TextContent.ShouldBe("TestUser");
    }
}
```

### Testing State Changes

```csharp
[Fact]
public void AddToCart_UpdatesState()
{
    var state = new AppState();
    Services.AddSingleton<IAppState>(state);

    var cut = RenderComponent<ProductCard>(p => p
        .Add(x => x.Product, new Product { Id = 1, Name = "Widget" }));

    cut.Find(".add-to-cart").Click();

    state.CartItems.Count.ShouldBe(1);
}
```

## Logger Mocking

### Using NullLogger

```csharp
public class LogTests : TestContext
{
    public LogTests()
    {
        // Simple: just ignore all logging
        Services.AddSingleton<ILogger<MyComponent>>(NullLogger<MyComponent>.Instance);
    }
}
```

### Capturing Log Output

```csharp
public class LogTests : TestContext
{
    private readonly List<string> _logMessages = new();

    public LogTests()
    {
        var mockLogger = new Mock<ILogger<MyComponent>>();
        mockLogger
            .Setup(l => l.Log(
                It.IsAny<LogLevel>(),
                It.IsAny<EventId>(),
                It.IsAny<It.IsAnyType>(),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()))
            .Callback<LogLevel, EventId, object, Exception, Delegate>(
                (level, id, state, ex, formatter) =>
                    _logMessages.Add(state.ToString()!));

        Services.AddSingleton(mockLogger.Object);
    }

    [Fact]
    public void Component_LogsOnError()
    {
        var cut = RenderComponent<ErrorProneComponent>();
        cut.Find(".trigger-error").Click();

        _logMessages.ShouldContain(m => m.Contains("Error occurred"));
    }
}
```

## Scoped Service Pattern

### Per-Test Service Registration

```csharp
public class ScopedServiceTests : TestContext
{
    [Fact]
    public void Test_WithSpecificService()
    {
        // Register for this test only
        Services.AddScoped<IDataService, HappyPathDataService>();

        var cut = RenderComponent<DataDisplay>();

        cut.Find(".data").TextContent.ShouldBe("Happy data");
    }

    [Fact]
    public void Test_WithErrorService()
    {
        // Different service for this test
        Services.AddScoped<IDataService, ErrorDataService>();

        var cut = RenderComponent<DataDisplay>();

        cut.Find(".error").ShouldNotBeNull();
    }
}
```

### Shared Test Fixture

```csharp
public class SharedServicesFixture : IDisposable
{
    public Mock<IExternalApi> ApiMock { get; } = new();
    public Mock<IEmailService> EmailMock { get; } = new();

    public void Dispose() { }
}

public class SharedTests : TestContext, IClassFixture<SharedServicesFixture>
{
    public SharedTests(SharedServicesFixture fixture)
    {
        Services.AddSingleton(fixture.ApiMock.Object);
        Services.AddSingleton(fixture.EmailMock.Object);
    }

    [Fact]
    public void Test_UsesSharedMocks()
    {
        // Tests using shared fixture mocks
    }
}
```
