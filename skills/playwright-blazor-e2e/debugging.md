# Debugging Playwright Tests

## Trace Viewer

The trace viewer is Playwright's most powerful debugging tool. It captures DOM snapshots, screenshots, network requests, and console logs for each action.

### Enabling Tracing

```csharp
// In test setup
[TestInitialize]
public async Task SetupTracing()
{
    await Context.Tracing.StartAsync(new()
    {
        Title = TestContext.TestName,
        Screenshots = true,   // Capture screenshots on each action
        Snapshots = true,     // Capture DOM snapshots
        Sources = true        // Include source code in trace
    });
}

[TestCleanup]
public async Task SaveTraceOnFailure()
{
    var failed = TestContext.CurrentTestOutcome == UnitTestOutcome.Failed;
    var tracePath = failed
        ? Path.Combine("TestResults", "traces", $"{TestContext.TestName}.zip")
        : null;

    if (tracePath != null)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(tracePath)!);
    }

    await Context.Tracing.StopAsync(new() { Path = tracePath });
}
```

### Viewing Traces

```bash
# Local trace file
pwsh bin/Debug/net8.0/playwright.ps1 show-trace TestResults/traces/LoginTest.zip

# From URL
pwsh bin/Debug/net8.0/playwright.ps1 show-trace https://example.com/traces/test.zip

# Or drag & drop to https://trace.playwright.dev
```

### What Traces Show

| Panel | Information |
|-------|-------------|
| Actions | Timeline of all test actions |
| Before/After | DOM state before and after each action |
| Console | Browser console logs |
| Network | All HTTP requests and responses |
| Source | Test source code location |
| Errors | Any errors that occurred |

## Headed Mode (Visual Debugging)

Run tests with a visible browser:

```bash
# Single test, headed
dotnet test --filter "LoginTest" -- Playwright.LaunchOptions.Headless=false

# With slow motion (500ms delay between actions)
dotnet test -- Playwright.LaunchOptions.Headless=false Playwright.LaunchOptions.SlowMo=500

# Specific browser
dotnet test -- Playwright.BrowserName=firefox Playwright.LaunchOptions.Headless=false
```

### Debug Mode with Pause

Add breakpoints in your test:

```csharp
[TestMethod]
public async Task DebugTest()
{
    await Page.GotoAsync("/login");

    // Pause execution - opens Playwright Inspector
    await Page.PauseAsync();

    // Continue with test...
    await Page.GetByLabel("Email").FillAsync("test@example.com");
}
```

Run with `PWDEBUG=1`:
```bash
$env:PWDEBUG="1"; dotnet test --filter "DebugTest"
```

## Playwright Inspector

The Inspector provides:

| Feature | Usage |
|---------|-------|
| Pick locator | Click elements to get suggested locators |
| Step through | Execute one action at a time |
| View locator | See all elements matching current locator |
| Record | Record new actions as code |

### Launch Inspector

```bash
# Windows PowerShell
$env:PWDEBUG="1"
dotnet test --filter "TestName"

# Or use Console mode
$env:PWDEBUG="console"
dotnet test --filter "TestName"
```

## Console Debugging

### Capture Console Output

```csharp
[TestMethod]
public async Task TestWithConsoleCapture()
{
    var consoleLogs = new List<string>();

    Page.Console += (_, msg) =>
    {
        consoleLogs.Add($"[{msg.Type}] {msg.Text}");
    };

    await Page.GotoAsync("/");

    // At end, log all console messages
    foreach (var log in consoleLogs)
    {
        TestContext.WriteLine(log);
    }
}
```

### Capture Page Errors

```csharp
[TestMethod]
public async Task TestWithErrorCapture()
{
    var pageErrors = new List<string>();

    Page.PageError += (_, error) =>
    {
        pageErrors.Add(error);
    };

    await Page.GotoAsync("/buggy-page");

    // Assert no JS errors
    Assert.AreEqual(0, pageErrors.Count, $"Page errors: {string.Join("\n", pageErrors)}");
}
```

## Screenshot Debugging

### On Failure

```csharp
[TestCleanup]
public async Task CaptureScreenshotOnFailure()
{
    if (TestContext.CurrentTestOutcome == UnitTestOutcome.Failed)
    {
        var screenshotPath = Path.Combine(
            "TestResults", "screenshots",
            $"{TestContext.TestName}.png");

        Directory.CreateDirectory(Path.GetDirectoryName(screenshotPath)!);

        await Page.ScreenshotAsync(new()
        {
            Path = screenshotPath,
            FullPage = true
        });
    }
}
```

### Debug Screenshots

```csharp
[TestMethod]
public async Task TestWithDebugScreenshots()
{
    await Page.GotoAsync("/products");

    // Screenshot at specific point
    await Page.ScreenshotAsync(new() { Path = "debug-1-loaded.png" });

    await Page.GetByPlaceholder("Search").FillAsync("Widget");

    await Page.ScreenshotAsync(new() { Path = "debug-2-filtered.png" });

    await Page.GetByRole(AriaRole.Button, new() { Name = "Add" }).ClickAsync();

    await Page.ScreenshotAsync(new() { Path = "debug-3-dialog.png" });
}
```

## Network Debugging

### Log All Requests

```csharp
[TestMethod]
public async Task TestWithNetworkLogging()
{
    Page.Request += (_, request) =>
    {
        TestContext.WriteLine($">> {request.Method} {request.Url}");
    };

    Page.Response += (_, response) =>
    {
        TestContext.WriteLine($"<< {response.Status} {response.Url}");
    };

    await Page.GotoAsync("/products");
}
```

### Wait for Specific Request

```csharp
[TestMethod]
public async Task TestWithRequestWait()
{
    // Start waiting before triggering the request
    var responseTask = Page.WaitForResponseAsync(
        response => response.Url.Contains("/api/products") && response.Status == 200
    );

    await Page.GotoAsync("/products");

    // Get the response
    var response = await responseTask;
    var json = await response.JsonAsync();
    TestContext.WriteLine($"Products loaded: {json}");
}
```

### Mock Failed Requests

```csharp
[TestMethod]
public async Task TestErrorHandling()
{
    // Mock API to return error
    await Page.RouteAsync("**/api/products", async route =>
    {
        await route.FulfillAsync(new()
        {
            Status = 500,
            ContentType = "application/json",
            Body = "{\"error\": \"Internal Server Error\"}"
        });
    });

    await Page.GotoAsync("/products");

    // Verify error handling
    await Expect(Page.GetByText("Failed to load products")).ToBeVisibleAsync();
}
```

## Debugging Flaky Tests

### Increase Timeout

```csharp
// Per assertion
await Expect(Page.GetByText("Loaded")).ToBeVisibleAsync(new() { Timeout = 30000 });

// Global (in .runsettings)
<Playwright>
    <ExpectTimeout>15000</ExpectTimeout>
</Playwright>
```

### Add Explicit Waits

```csharp
[TestMethod]
public async Task TestWithExplicitWaits()
{
    await Page.GotoAsync("/dashboard");

    // Wait for network idle (all requests completed)
    await Page.WaitForLoadStateAsync(LoadState.NetworkIdle);

    // Wait for specific element to be stable
    await Page.GetByTestId("dashboard-content").WaitForAsync(new() { State = WaitForSelectorState.Visible });

    // Wait for function
    await Page.WaitForFunctionAsync("document.querySelectorAll('.chart').length > 0");
}
```

### Retry Flaky Actions

```csharp
private async Task RetryAsync(Func<Task> action, int maxRetries = 3)
{
    for (int i = 0; i < maxRetries; i++)
    {
        try
        {
            await action();
            return;
        }
        catch when (i < maxRetries - 1)
        {
            await Task.Delay(1000);
        }
    }
}

[TestMethod]
public async Task TestWithRetry()
{
    await RetryAsync(async () =>
    {
        await Page.GetByRole(AriaRole.Button, new() { Name = "Flaky Button" }).ClickAsync();
    });
}
```

### Video Recording

```csharp
public override BrowserNewContextOptions ContextOptions => new()
{
    BaseURL = "https://localhost:5001",
    RecordVideoDir = "TestResults/videos",
    RecordVideoSize = new RecordVideoSize { Width = 1920, Height = 1080 }
};

[TestCleanup]
public async Task SaveVideo()
{
    var videoPath = await Page.Video?.PathAsync();
    if (videoPath != null && TestContext.CurrentTestOutcome == UnitTestOutcome.Passed)
    {
        // Delete video for passing tests
        File.Delete(videoPath);
    }
}
```

## Common Issues

### Element Not Found

```csharp
// Problem: Element not found
await Page.GetByRole(AriaRole.Button, new() { Name = "Submit" }).ClickAsync();
// TimeoutException

// Debug: Check what's on page
var html = await Page.ContentAsync();
TestContext.WriteLine(html);

// Debug: Screenshot
await Page.ScreenshotAsync(new() { Path = "debug-element-not-found.png", FullPage = true });

// Solution 1: Wrong locator - use Inspector to find correct one
await Page.PauseAsync(); // Pick locator in Inspector

// Solution 2: Element not ready yet - check loading state
await Expect(Page.GetByTestId("loading")).ToBeHiddenAsync();
await Page.GetByRole(AriaRole.Button, new() { Name = "Submit" }).ClickAsync();
```

### Element Obscured

```csharp
// Problem: Element obscured by overlay
// Error: Element is outside of the viewport or overlapped by another element

// Debug: Check what's overlapping
var boundingBox = await Page.GetByRole(AriaRole.Button).BoundingBoxAsync();
TestContext.WriteLine($"Button at: {boundingBox}");

// Solution 1: Close overlay first
await Page.GetByRole(AriaRole.Button, new() { Name = "Close" }).ClickAsync();

// Solution 2: Scroll into view
await Page.GetByRole(AriaRole.Button, new() { Name = "Submit" }).ScrollIntoViewIfNeededAsync();

// Solution 3: Force click (use sparingly)
await Page.GetByRole(AriaRole.Button, new() { Name = "Submit" }).ClickAsync(new() { Force = true });
```

### Multiple Elements Match

```csharp
// Problem: Strict mode violation - multiple elements match
await Page.GetByRole(AriaRole.Button, new() { Name = "Edit" }).ClickAsync();
// Throws because there are multiple Edit buttons

// Solution 1: Be more specific
var row = Page.GetByRole(AriaRole.Row).Filter(new() { HasText = "Product A" });
await row.GetByRole(AriaRole.Button, new() { Name = "Edit" }).ClickAsync();

// Solution 2: Use .First or .Nth
await Page.GetByRole(AriaRole.Button, new() { Name = "Edit" }).First.ClickAsync();

// Debug: Count matching elements
var count = await Page.GetByRole(AriaRole.Button, new() { Name = "Edit" }).CountAsync();
TestContext.WriteLine($"Found {count} Edit buttons");
```

### Blazor Not Ready

```csharp
// Problem: Interacting before Blazor loads
await Page.GotoAsync("/");
await Page.GetByLabel("Email").FillAsync("test@example.com");
// Fails because Blazor hasn't initialized

// Solution: Wait for Blazor
await Page.GotoAsync("/");
await Page.WaitForFunctionAsync("window.Blazor !== undefined");
await Expect(Page.GetByTestId("app-loading")).ToBeHiddenAsync();
await Page.GetByLabel("Email").FillAsync("test@example.com");
```

### SignalR Reconnection

```csharp
// Problem: SignalR disconnects during test

// Solution: Wait for reconnection
await Page.WaitForFunctionAsync(@"
    document.querySelector('.mud-alert-error') === null ||
    !document.querySelector('.mud-alert-error').textContent.includes('disconnected')
", new() { Timeout = 30000 });
```

## Debugging Checklist

When a test fails:

1. **Check trace** - Open trace.zip in trace viewer
2. **Screenshot** - Look at the page state at failure
3. **Console logs** - Check for JavaScript errors
4. **Network requests** - Did API calls succeed?
5. **Run headed** - Watch the test execute
6. **Add pause** - Step through with Inspector
7. **Check locator** - Use Inspector to verify locator finds element
8. **Check timing** - Is there a loading state being missed?
9. **Check environment** - CI vs local differences?
10. **Simplify** - Can you reproduce with smaller test?
