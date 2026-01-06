# bUnit Best Practices

## 1. Inherit from TestContext

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

## 2. Use Semantic Markup Matching

```csharp
// GOOD: Semantic comparison (ignores whitespace, attribute order)
cut.Find("div").MarkupMatches(@"
    <div class=""card"" data-id=""1"">
        <h2>Title</h2>
    </div>");

// BAD: Exact string matching (brittle)
cut.Markup.ShouldBe("<div class=\"card\" data-id=\"1\"><h2>Title</h2></div>");
```

## 3. Test Behavior, Not Implementation

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

## 4. Arrange-Act-Assert Pattern

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

## 5. Use Test Data Generators

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

## 6. Prefer Role-Based and Semantic Selectors

```csharp
// GOOD: Semantic selectors (resilient to refactoring)
cut.Find("button[type='submit']");
cut.Find("[data-testid='login-button']");
cut.FindAll("li.product-item");

// AVOID: Overly specific CSS paths (brittle)
cut.Find("div.container > div.wrapper > button.btn");
```

## 7. Keep Tests Focused

Each test should verify one behavior:

```csharp
// GOOD: Single responsibility
[Fact]
public void Counter_ClickIncrement_UpdatesDisplay() { /* ... */ }

[Fact]
public void Counter_ClickDecrement_UpdatesDisplay() { /* ... */ }

// BAD: Testing multiple behaviors
[Fact]
public void Counter_AllOperations_WorkCorrectly()
{
    // Tests increment, decrement, reset, display... too much!
}
```

## 8. Use WaitForAssertion for Async UI Updates

```csharp
[Fact]
public void SearchResults_LoadAsync()
{
    var cut = RenderComponent<SearchPage>();
    cut.Find("input").Change("test query");
    cut.Find("button").Click();

    // Wait for async results
    cut.WaitForAssertion(() =>
    {
        cut.FindAll(".result-item").Count.ShouldBeGreaterThan(0);
    });
}
```

## 9. Mock External Dependencies

```csharp
public class DashboardTests : TestContext
{
    public DashboardTests()
    {
        // Register mocked services
        Services.AddSingleton<IApiClient>(new MockApiClient());

        // Or use KnockOff stubs
        var apiStub = new ApiClientStub();
        apiStub.GetDataAsync.SetReturnValue(testData);
        Services.AddSingleton<IApiClient>(apiStub);
    }
}
```

## 10. Dispose Resources Properly

```csharp
public class ResourceTests : TestContext
{
    [Fact]
    public void Component_DisposesResources()
    {
        var cut = RenderComponent<ResourceComponent>();

        // Trigger disposal
        DisposeComponents();

        // Verify cleanup (if observable)
    }
}
```
