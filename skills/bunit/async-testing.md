# Async Testing Patterns

## WaitForState

Wait for a specific condition to become true:

```csharp
[Fact]
public void Component_LoadsData()
{
    Services.AddSingleton<IDataService>(new SlowDataService());

    var cut = RenderComponent<DataLoader>();

    // Wait for loading to complete
    cut.WaitForState(() => !cut.Instance.IsLoading);

    cut.Find(".data-content").ShouldNotBeNull();
}
```

### With Timeout

```csharp
[Fact]
public void Component_LoadsWithinTimeout()
{
    var cut = RenderComponent<SlowComponent>();

    // Wait up to 5 seconds
    cut.WaitForState(
        () => cut.Instance.DataLoaded,
        timeout: TimeSpan.FromSeconds(5));
}
```

### Checking Intermediate States

```csharp
[Fact]
public void Component_ShowsLoadingThenData()
{
    var tcs = new TaskCompletionSource<List<Product>>();
    var mockService = new Mock<IProductService>();
    mockService.Setup(s => s.GetAllAsync()).Returns(tcs.Task);
    Services.AddSingleton(mockService.Object);

    var cut = RenderComponent<ProductList>();

    // Should show loading initially
    cut.Find(".loading-spinner").ShouldNotBeNull();

    // Complete the task
    tcs.SetResult(new List<Product> { new() { Name = "Widget" } });

    // Wait for data to appear
    cut.WaitForState(() => cut.FindAll(".product-item").Count > 0);

    cut.Find(".product-name").TextContent.ShouldBe("Widget");
}
```

## WaitForAssertion

Retry an assertion until it passes:

```csharp
[Fact]
public void Counter_IncrementsTwice()
{
    var cut = RenderComponent<Counter>();

    cut.Find("button").Click();
    cut.Find("button").Click();

    // Retry until the assertion passes
    cut.WaitForAssertion(() =>
    {
        cut.Find(".count").TextContent.ShouldBe("2");
    });
}
```

### Multiple Assertions

```csharp
[Fact]
public void Form_ShowsMultipleValidationErrors()
{
    var cut = RenderComponent<RegistrationForm>();

    cut.Find("form").Submit();

    cut.WaitForAssertion(() =>
    {
        var errors = cut.FindAll(".validation-error");
        errors.Count.ShouldBe(3);
        errors[0].TextContent.ShouldContain("Name is required");
        errors[1].TextContent.ShouldContain("Email is required");
        errors[2].TextContent.ShouldContain("Password is required");
    });
}
```

### Async Version

```csharp
[Fact]
public async Task Component_UpdatesAfterAsyncOperation()
{
    var cut = RenderComponent<AsyncComponent>();

    cut.Find(".trigger-btn").Click();

    await cut.WaitForAssertionAsync(() =>
    {
        cut.Find(".result").TextContent.ShouldBe("Complete");
    });
}
```

## InvokeAsync

Execute code on the component's synchronization context:

```csharp
[Fact]
public async Task Component_HandlesDirectMethodCall()
{
    var cut = RenderComponent<DataComponent>();

    // Call async method on component instance
    await cut.InvokeAsync(async () =>
    {
        await cut.Instance.RefreshDataAsync();
    });

    cut.Find(".data").TextContent.ShouldNotBeEmpty();
}
```

### Triggering StateHasChanged

```csharp
[Fact]
public void Component_UpdatesAfterExternalChange()
{
    var state = new AppState();
    Services.AddSingleton(state);

    var cut = RenderComponent<StateConsumer>();

    // Modify state externally
    state.Counter = 10;

    // Force component to re-render
    cut.InvokeAsync(() => cut.Instance.StateHasChanged());

    cut.Find(".counter").TextContent.ShouldBe("10");
}
```

## Testing OnInitializedAsync

```csharp
[Fact]
public void Component_ShowsLoadingDuringInit()
{
    var tcs = new TaskCompletionSource<Data>();
    var mockService = new Mock<IDataService>();
    mockService.Setup(s => s.LoadAsync()).Returns(tcs.Task);
    Services.AddSingleton(mockService.Object);

    var cut = RenderComponent<DataComponent>();

    // Component should be loading
    cut.Find(".loading").ShouldNotBeNull();
    cut.FindAll(".data-content").Count.ShouldBe(0);

    // Complete initialization
    tcs.SetResult(new Data { Value = "Test" });

    // Wait for component to update
    cut.WaitForState(() => cut.FindAll(".loading").Count == 0);

    cut.Find(".data-content").TextContent.ShouldBe("Test");
}
```

## Testing Event Handlers with Async Work

```csharp
[Fact]
public async Task Button_CompletesAsyncOperation()
{
    var operationComplete = false;
    var tcs = new TaskCompletionSource();

    var cut = RenderComponent<AsyncButton>(p => p
        .Add(x => x.OnClickAsync, EventCallback.Factory.Create(this, async () =>
        {
            await tcs.Task;
            operationComplete = true;
        })));

    // Start the operation
    cut.Find("button").Click();

    // Button should be disabled while working
    cut.Find("button").HasAttribute("disabled").ShouldBeTrue();

    // Complete the operation
    tcs.SetResult();

    // Wait for completion
    cut.WaitForState(() => operationComplete);

    // Button should be enabled again
    cut.Find("button").HasAttribute("disabled").ShouldBeFalse();
}
```

## Testing Debounced Operations

```csharp
[Fact]
public void Search_DebouncesInput()
{
    var searchCount = 0;
    var mockService = new Mock<ISearchService>();
    mockService
        .Setup(s => s.SearchAsync(It.IsAny<string>()))
        .Callback(() => searchCount++)
        .ReturnsAsync(new List<Result>());

    Services.AddSingleton(mockService.Object);

    var cut = RenderComponent<SearchBox>();

    // Type quickly
    var input = cut.Find("input");
    input.Input("a");
    input.Input("ab");
    input.Input("abc");

    // Wait for debounce (component uses 300ms debounce)
    cut.WaitForState(() => searchCount > 0, TimeSpan.FromSeconds(1));

    // Should only have searched once (debounced)
    searchCount.ShouldBe(1);
    mockService.Verify(s => s.SearchAsync("abc"), Times.Once);
}
```

## Testing Timers

### Using FakeTimeProvider (.NET 8+)

```csharp
public class TimerTests : TestContext
{
    private readonly FakeTimeProvider _timeProvider = new();

    public TimerTests()
    {
        Services.AddSingleton<TimeProvider>(_timeProvider);
    }

    [Fact]
    public void AutoRefresh_RefreshesAfterInterval()
    {
        var refreshCount = 0;
        var mockService = new Mock<IDataService>();
        mockService
            .Setup(s => s.RefreshAsync())
            .Callback(() => refreshCount++)
            .Returns(Task.CompletedTask);

        Services.AddSingleton(mockService.Object);

        var cut = RenderComponent<AutoRefreshComponent>(p => p
            .Add(x => x.IntervalSeconds, 30));

        // Advance time by 30 seconds
        _timeProvider.Advance(TimeSpan.FromSeconds(30));

        cut.WaitForState(() => refreshCount == 1);

        // Advance again
        _timeProvider.Advance(TimeSpan.FromSeconds(30));

        cut.WaitForState(() => refreshCount == 2);
    }
}
```

### Without TimeProvider

```csharp
[Fact]
public async Task Countdown_UpdatesEverySecond()
{
    var cut = RenderComponent<Countdown>(p => p
        .Add(x => x.Seconds, 3));

    cut.Find(".countdown").TextContent.ShouldBe("3");

    // Wait for timer ticks
    await Task.Delay(1100); // Slightly over 1 second
    cut.Render();
    cut.Find(".countdown").TextContent.ShouldBe("2");

    await Task.Delay(1100);
    cut.Render();
    cut.Find(".countdown").TextContent.ShouldBe("1");
}
```

## Testing Cancellation

```csharp
[Fact]
public async Task Component_CancelsPendingOperation()
{
    var cancellationReceived = false;
    var tcs = new TaskCompletionSource();

    var mockService = new Mock<IDataService>();
    mockService
        .Setup(s => s.LoadAsync(It.IsAny<CancellationToken>()))
        .Returns(async (CancellationToken ct) =>
        {
            try
            {
                await Task.Delay(Timeout.Infinite, ct);
            }
            catch (OperationCanceledException)
            {
                cancellationReceived = true;
                throw;
            }
            return new Data();
        });

    Services.AddSingleton(mockService.Object);

    var cut = RenderComponent<CancellableLoader>();

    // Start loading
    cut.Find(".load-btn").Click();

    // Cancel
    cut.Find(".cancel-btn").Click();

    cut.WaitForState(() => cancellationReceived);

    cancellationReceived.ShouldBeTrue();
}
```

## Testing Error Handling

```csharp
[Fact]
public void Component_HandlesAsyncError()
{
    var mockService = new Mock<IDataService>();
    mockService
        .Setup(s => s.LoadAsync())
        .ThrowsAsync(new InvalidOperationException("Load failed"));

    Services.AddSingleton(mockService.Object);

    var cut = RenderComponent<DataLoader>();

    cut.WaitForAssertion(() =>
    {
        cut.Find(".error-message").TextContent.ShouldContain("Load failed");
    });
}
```

### Testing Error Boundaries

```csharp
[Fact]
public void ErrorBoundary_CatchesChildError()
{
    var cut = RenderComponent<ErrorBoundaryWrapper>(p => p
        .AddChildContent<ThrowingComponent>());

    // Wait for error to be caught
    cut.WaitForAssertion(() =>
    {
        cut.Find(".error-fallback").ShouldNotBeNull();
    });
}
```

## Testing Parallel Operations

```csharp
[Fact]
public async Task Component_LoadsMultipleSourcesInParallel()
{
    var source1Complete = new TaskCompletionSource<Data1>();
    var source2Complete = new TaskCompletionSource<Data2>();

    var mock1 = new Mock<IData1Service>();
    mock1.Setup(s => s.LoadAsync()).Returns(source1Complete.Task);

    var mock2 = new Mock<IData2Service>();
    mock2.Setup(s => s.LoadAsync()).Returns(source2Complete.Task);

    Services.AddSingleton(mock1.Object);
    Services.AddSingleton(mock2.Object);

    var cut = RenderComponent<ParallelLoader>();

    // Both should be loading
    cut.FindAll(".loading").Count.ShouldBe(2);

    // Complete first source
    source1Complete.SetResult(new Data1 { Value = "First" });
    cut.WaitForState(() => cut.FindAll(".loading").Count == 1);

    cut.Find(".data1").TextContent.ShouldBe("First");
    cut.Find(".data2-loading").ShouldNotBeNull();

    // Complete second source
    source2Complete.SetResult(new Data2 { Value = "Second" });
    cut.WaitForState(() => cut.FindAll(".loading").Count == 0);

    cut.Find(".data2").TextContent.ShouldBe("Second");
}
```

## Best Practices

### 1. Prefer WaitForAssertion Over Sleep

```csharp
// BAD: Using Thread.Sleep or Task.Delay
await Task.Delay(1000);
cut.Find(".element").ShouldNotBeNull();

// GOOD: Using WaitForAssertion
cut.WaitForAssertion(() =>
{
    cut.Find(".element").ShouldNotBeNull();
});
```

### 2. Use TaskCompletionSource for Control

```csharp
// Control exactly when async operations complete
var tcs = new TaskCompletionSource<Result>();
mockService.Setup(s => s.GetAsync()).Returns(tcs.Task);

var cut = RenderComponent<MyComponent>();
// Assert loading state

tcs.SetResult(new Result());
// Assert completed state
```

### 3. Set Reasonable Timeouts

```csharp
// Default timeout is 1 second; increase for slow operations
cut.WaitForState(
    () => condition,
    timeout: TimeSpan.FromSeconds(10));
```

### 4. Handle Exceptions in Async Code

```csharp
[Fact]
public async Task Test_CatchesAsyncException()
{
    var tcs = new TaskCompletionSource<Result>();

    var cut = RenderComponent<AsyncComponent>();

    // Fail the task
    tcs.SetException(new Exception("Test error"));

    await cut.WaitForAssertionAsync(() =>
    {
        cut.Find(".error").TextContent.ShouldContain("Test error");
    });
}
```
