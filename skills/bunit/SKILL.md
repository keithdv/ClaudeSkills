---
name: bunit
description: Blazor component testing with bUnit. Use when writing unit tests for Blazor components, testing user interactions, mocking services/dependencies, testing MudBlazor components, testing components with Neatoo domain objects, or debugging component rendering issues.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(dotnet:*), WebFetch
---

# bUnit - Blazor Component Testing

## Overview

bUnit is a testing library for Blazor components that enables testing without a browser. It provides:

- **Component rendering** in a test environment
- **DOM assertions** and markup verification
- **User interaction simulation** (clicks, inputs, form submissions)
- **Service mocking** and dependency injection
- **Async testing** with waiting utilities
- **Blazor lifecycle** testing

## Installation

### Package Installation

```bash
# Add bUnit with xUnit support
dotnet add package bunit

# Or individual packages
dotnet add package bunit.core
dotnet add package bunit.web
dotnet add package bunit.xunit   # For xUnit integration
```

### Test Project Setup

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="bunit" Version="1.31.3" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.11.0" />
    <PackageReference Include="xunit" Version="2.9.0" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.8.2" />
    <PackageReference Include="KnockOff" Version="10.3.0" /> <!-- Preferred: type-safe stubs -->
    <PackageReference Include="Moq" Version="4.20.70" /> <!-- Alternative: runtime mocking -->
    <PackageReference Include="Bogus" Version="35.6.0" />
  </ItemGroup>

  <ItemGroup>
    <!-- Reference the Blazor project being tested -->
    <ProjectReference Include="..\MyBlazorApp\MyBlazorApp.csproj" />
  </ItemGroup>
</Project>
```

### Global Usings (_Imports.cs)

```csharp
global using Bunit;
global using Bunit.TestDoubles;
global using Xunit;
global using Moq;
global using Microsoft.Extensions.DependencyInjection;
global using Microsoft.AspNetCore.Components;
```

## Quick Start

### Basic Component Test

```csharp
public class CounterTests : TestContext
{
    [Fact]
    public void Counter_InitialCount_IsZero()
    {
        // Arrange & Act
        var cut = RenderComponent<Counter>();

        // Assert
        cut.Find("p").MarkupMatches("<p>Current count: 0</p>");
    }

    [Fact]
    public void Counter_ClickButton_IncrementsCount()
    {
        // Arrange
        var cut = RenderComponent<Counter>();

        // Act
        cut.Find("button").Click();

        // Assert
        cut.Find("p").MarkupMatches("<p>Current count: 1</p>");
    }
}
```

### Component with Parameters

```csharp
[Fact]
public void Greeting_WithName_DisplaysPersonalizedMessage()
{
    // Arrange & Act
    var cut = RenderComponent<Greeting>(parameters => parameters
        .Add(p => p.Name, "Alice")
        .Add(p => p.ShowIcon, true));

    // Assert
    cut.Find("h1").TextContent.ShouldContain("Hello, Alice!");
}
```

### Component with Cascading Values

```csharp
[Fact]
public void ThemedButton_UsesCascadedTheme()
{
    // Arrange
    var theme = new AppTheme { Primary = "#1976D2" };

    // Act
    var cut = RenderComponent<ThemedButton>(parameters => parameters
        .AddCascadingValue(theme)
        .Add(p => p.Text, "Click Me"));

    // Assert
    cut.Find("button").GetAttribute("style")
        .ShouldContain("background-color: #1976D2");
}
```

## Core Concepts

### TestContext

`TestContext` is the base class for bUnit tests. It provides:

| Property/Method | Purpose |
|-----------------|---------|
| `RenderComponent<T>()` | Render a component and return `IRenderedComponent<T>` |
| `Services` | `IServiceCollection` for DI registration |
| `JSInterop` | Mock JavaScript interop calls |
| `ComponentFactories` | Register component doubles/stubs |
| `Renderer` | Access to the test renderer |
| `DisposeComponents()` | Dispose all rendered components |

```csharp
public class MyTests : TestContext
{
    public MyTests()
    {
        // Register services in constructor
        Services.AddSingleton<IMyService, MockMyService>();

        // Configure JSInterop
        JSInterop.Mode = JSRuntimeMode.Loose;
    }
}
```

### IRenderedComponent<T>

The object returned from `RenderComponent<T>()`:

| Property/Method | Purpose |
|-----------------|---------|
| `Instance` | Access the component instance directly |
| `Markup` | Get rendered HTML as string |
| `Find(selector)` | Find single element by CSS selector |
| `FindAll(selector)` | Find all matching elements |
| `FindComponent<T>()` | Find child component |
| `FindComponents<T>()` | Find all child components |
| `InvokeAsync(action)` | Invoke action on component's sync context |
| `Render()` | Force re-render |
| `SetParametersAndRender()` | Update parameters and re-render |
| `WaitForState(predicate)` | Wait for condition to be true |
| `WaitForAssertion(assertion)` | Wait for assertion to pass |

### Finding Elements

```csharp
// By CSS selector
var button = cut.Find("button");
var submitBtn = cut.Find("button[type='submit']");
var primaryBtn = cut.Find(".btn-primary");
var namedInput = cut.Find("input#username");

// Find all matching
var allButtons = cut.FindAll("button");
var listItems = cut.FindAll("li.item");

// Find child components
var childComponent = cut.FindComponent<ChildComponent>();
var allCards = cut.FindComponents<Card>();
```

### DOM Assertions

```csharp
// Markup matching (flexible whitespace)
element.MarkupMatches("<p>Expected content</p>");

// Text content
element.TextContent.ShouldBe("Expected text");
element.TextContent.ShouldContain("partial");

// Attributes
element.GetAttribute("class").ShouldContain("active");
element.HasAttribute("disabled").ShouldBeTrue();
element.Id.ShouldBe("my-element");

// Element existence
cut.FindAll(".item").Count.ShouldBe(5);
cut.Find(".error").ShouldNotBeNull();

// Semantic HTML diff (ignores insignificant differences)
element.MarkupMatches(@"
    <div class=""container"">
        <span>Content</span>
    </div>");
```

### User Interactions

```csharp
// Click events
cut.Find("button").Click();
cut.Find("button").DoubleClick();

// Input events
cut.Find("input").Change("new value");
cut.Find("input").Input("typing...");

// Form submission
cut.Find("form").Submit();

// Keyboard events
cut.Find("input").KeyDown(Key.Enter);
cut.Find("input").KeyUp(Key.Escape);
cut.Find("input").KeyPress("a");

// Focus events
cut.Find("input").Focus();
cut.Find("input").Blur();

// Mouse events
cut.Find("div").MouseOver();
cut.Find("div").MouseOut();

// Checkbox/radio
cut.Find("input[type='checkbox']").Change(true);

// Select dropdown
cut.Find("select").Change("option-value");
```

## Best Practices

### 1. Inherit from TestContext

```csharp
// GOOD: Clean syntax with TestContext
public class MyTests : TestContext
{
    [Fact]
    public void Test()
    {
        var cut = RenderComponent<MyComponent>();
    }
}

// ALTERNATIVE: Create TestContext instance (for shared fixtures)
public class MyTests : IDisposable
{
    private readonly TestContext _ctx = new TestContext();

    [Fact]
    public void Test()
    {
        var cut = _ctx.RenderComponent<MyComponent>();
    }

    public void Dispose() => _ctx.Dispose();
}
```

### 2. Use Semantic Markup Matching

```csharp
// GOOD: Semantic comparison (ignores whitespace, attribute order)
cut.Find("div").MarkupMatches(@"
    <div class=""card"" data-id=""1"">
        <h2>Title</h2>
    </div>");

// BAD: Exact string matching (brittle)
cut.Markup.ShouldBe("<div class=\"card\" data-id=\"1\"><h2>Title</h2></div>");
```

### 3. Test Behavior, Not Implementation

```csharp
// GOOD: Test user-visible behavior
[Fact]
public void SubmitButton_WhenFormInvalid_ShowsErrorMessage()
{
    var cut = RenderComponent<LoginForm>();
    cut.Find("button").Click();
    cut.Find(".error-message").TextContent.ShouldContain("required");
}

// BAD: Testing internal state
[Fact]
public void Form_SetsInternalValidationFlag()
{
    var cut = RenderComponent<LoginForm>();
    cut.Instance._isValid.ShouldBeFalse(); // Don't test internals!
}
```

### 4. Arrange-Act-Assert Pattern

```csharp
[Fact]
public void AddToCart_WithValidProduct_UpdatesCartCount()
{
    // Arrange
    var product = new Product { Id = 1, Name = "Widget" };
    var cut = RenderComponent<AddToCartButton>(p => p
        .Add(x => x.Product, product));

    // Act
    cut.Find("button").Click();

    // Assert
    cut.Find(".cart-count").TextContent.ShouldBe("1");
}
```

### 5. Use Test Data Generators

```csharp
public class ProductTests : TestContext
{
    private readonly Faker<Product> _productFaker = new Faker<Product>()
        .RuleFor(p => p.Id, f => f.IndexFaker + 1)
        .RuleFor(p => p.Name, f => f.Commerce.ProductName())
        .RuleFor(p => p.Price, f => f.Finance.Amount(10, 1000));

    [Fact]
    public void ProductCard_DisplaysProductInfo()
    {
        var product = _productFaker.Generate();
        var cut = RenderComponent<ProductCard>(p => p.Add(x => x.Product, product));

        cut.Find(".product-name").TextContent.ShouldBe(product.Name);
        cut.Find(".product-price").TextContent.ShouldContain(product.Price.ToString("C"));
    }
}
```

## Running Tests

```bash
# Run all tests
dotnet test

# Run specific test class
dotnet test --filter "FullyQualifiedName~CounterTests"

# Run specific test method
dotnet test --filter "FullyQualifiedName~CounterTests.Counter_ClickButton_IncrementsCount"

# Run with verbose output
dotnet test --logger "console;verbosity=detailed"

# Run with coverage
dotnet test --collect:"XPlat Code Coverage"
```

## Additional Resources

For detailed guidance, see:
- [Component Testing Patterns](component-testing.md) - Parameters, templates, child components
- [Service Mocking](service-mocking.md) - DI, KnockOff stubs, Moq patterns, HttpClient
- [MudBlazor Testing](mudblazor-testing.md) - Testing MudBlazor components
- [Async Testing](async-testing.md) - WaitForState, WaitForAssertion, timers
- [Neatoo Testing](neatoo-testing.md) - Testing with Neatoo domain objects

## Official Documentation

- [bUnit Documentation](https://bunit.dev/docs/getting-started/)
- [bUnit GitHub](https://github.com/bUnit-dev/bUnit)
- [Blazor Testing Best Practices](https://docs.microsoft.com/aspnet/core/blazor/test)
