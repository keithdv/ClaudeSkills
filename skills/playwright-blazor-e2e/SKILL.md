---
name: playwright-blazor-e2e
description: End-to-end testing for Blazor applications using Playwright for .NET. Use when writing E2E tests, creating test infrastructure, testing MudBlazor components, handling Blazor WebAssembly loading, debugging test failures, or setting up CI/CD test pipelines.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(dotnet:*), Bash(pwsh:*), WebFetch
---

# Playwright E2E Testing for Blazor

## Overview

Playwright for .NET provides cross-browser automation for testing Blazor applications. It handles Blazor's asynchronous rendering, WebAssembly loading, and SignalR connections with robust auto-waiting and retry mechanisms.

### Key Capabilities

- Cross-browser testing (Chromium, Firefox, WebKit)
- Auto-waiting for elements and network requests
- Trace viewer for debugging failed tests
- Parallel test execution
- Full support for Blazor WebAssembly and Server

## CRITICAL: Blazor-Specific Considerations

| Challenge | Solution |
|-----------|----------|
| WASM loading delay | Wait for Blazor to initialize before interacting |
| Component re-renders | Use auto-retrying assertions, not `Thread.Sleep` |
| MudBlazor components | Use role/label locators, not CSS selectors |
| Async operations | Wait for loading indicators to disappear |
| SignalR reconnection | Handle connection state changes gracefully |

## Quick Start

### 1. Create Test Project

```bash
# MSTest (recommended for .NET projects)
dotnet new mstest -n MyApp.E2E
cd MyApp.E2E

# Add Playwright
dotnet add package Microsoft.Playwright.MSTest

# Build to generate playwright.ps1
dotnet build

# Install browsers
pwsh bin/Debug/net8.0/playwright.ps1 install
```

### 2. Basic Blazor Test

```csharp
using Microsoft.Playwright;
using Microsoft.Playwright.MSTest;

namespace MyApp.E2E;

[TestClass]
public class HomePageTests : PageTest
{
    [TestMethod]
    public async Task HomePage_DisplaysWelcomeMessage()
    {
        // Navigate and wait for Blazor to load
        await Page.GotoAsync("https://localhost:5001/");
        await WaitForBlazorAsync();

        // Use role-based locator (accessibility-first)
        var heading = Page.GetByRole(AriaRole.Heading, new() { Name = "Welcome" });
        await Expect(heading).ToBeVisibleAsync();
    }

    private async Task WaitForBlazorAsync()
    {
        // Wait for Blazor WebAssembly to finish loading
        await Page.WaitForFunctionAsync("window.Blazor !== undefined");

        // Wait for any initial loading indicators to disappear
        var loader = Page.GetByTestId("app-loading");
        await Expect(loader).ToBeHiddenAsync(new() { Timeout = 30000 });
    }
}
```

### 3. Configure Base URL

Override `ContextOptions` to set a base URL:

```csharp
[TestClass]
public class BlazorTestBase : PageTest
{
    public override BrowserNewContextOptions ContextOptions => new()
    {
        BaseURL = "https://localhost:5001",
        IgnoreHTTPSErrors = true // For dev certificates
    };
}
```

## Locator Strategy (Priority Order)

Always prefer user-facing locators for resilient tests:

| Priority | Method | Example | Use When |
|----------|--------|---------|----------|
| 1 | `GetByRole()` | `GetByRole(AriaRole.Button, new() { Name = "Submit" })` | Interactive elements |
| 2 | `GetByLabel()` | `GetByLabel("Email")` | Form inputs |
| 3 | `GetByPlaceholder()` | `GetByPlaceholder("Search...")` | Inputs with placeholder |
| 4 | `GetByText()` | `GetByText("Welcome")` | Static text content |
| 5 | `GetByTestId()` | `GetByTestId("submit-button")` | When other locators fail |
| 6 | `Locator()` | `Locator(".mud-button")` | Last resort only |

### MudBlazor Component Locators

```csharp
// MudButton - use role and accessible name
var saveButton = Page.GetByRole(AriaRole.Button, new() { Name = "Save" });

// MudTextField - use label
var emailField = Page.GetByLabel("Email");

// MudSelect - use label then interact
var categorySelect = Page.GetByLabel("Category");
await categorySelect.ClickAsync();
await Page.GetByRole(AriaRole.Option, new() { Name = "Electronics" }).ClickAsync();

// MudDataGrid row - use text content
var row = Page.GetByRole(AriaRole.Row).Filter(new() { HasText = "Product ABC" });

// MudDialog - use role
var dialog = Page.GetByRole(AriaRole.Dialog);
await Expect(dialog).ToBeVisibleAsync();
```

## Assertions (Auto-Retrying)

Playwright assertions automatically retry until the condition is met or timeout:

```csharp
// Element visibility
await Expect(Page.GetByRole(AriaRole.Alert)).ToBeVisibleAsync();
await Expect(Page.GetByTestId("loading")).ToBeHiddenAsync();

// Text content
await Expect(Page.GetByRole(AriaRole.Heading)).ToHaveTextAsync("Dashboard");
await Expect(Page.GetByTestId("count")).ToContainTextAsync("5");

// Form state
await Expect(Page.GetByLabel("Email")).ToBeEditableAsync();
await Expect(Page.GetByRole(AriaRole.Button, new() { Name = "Save" })).ToBeDisabledAsync();

// Page state
await Expect(Page).ToHaveTitleAsync("My App - Dashboard");
await Expect(Page).ToHaveURLAsync(new Regex("/dashboard$"));

// Count
await Expect(Page.GetByRole(AriaRole.Row)).ToHaveCountAsync(10);

// Custom timeout
await Expect(Page.GetByText("Processing complete"))
    .ToBeVisibleAsync(new() { Timeout = 30000 });
```

## Actionability (Auto-Waiting)

Playwright automatically waits for elements to be actionable before performing actions:

| Action | Waits For |
|--------|-----------|
| `ClickAsync()` | Visible, Stable, Receives Events, Enabled |
| `FillAsync()` | Visible, Enabled, Editable |
| `CheckAsync()` | Visible, Stable, Receives Events, Enabled |
| `SelectOptionAsync()` | Visible, Enabled |

```csharp
// No manual waiting needed - Playwright handles it
await Page.GetByLabel("Email").FillAsync("test@example.com");
await Page.GetByRole(AriaRole.Button, new() { Name = "Submit" }).ClickAsync();
```

## Common Blazor Test Patterns

### Form Submission

```csharp
[TestMethod]
public async Task LoginForm_SubmitsSuccessfully()
{
    await Page.GotoAsync("/login");
    await WaitForBlazorAsync();

    // Fill form
    await Page.GetByLabel("Email").FillAsync("user@example.com");
    await Page.GetByLabel("Password").FillAsync("password123");

    // Submit
    await Page.GetByRole(AriaRole.Button, new() { Name = "Sign In" }).ClickAsync();

    // Wait for navigation
    await Expect(Page).ToHaveURLAsync("/dashboard");
}
```

### Async Validation

```csharp
[TestMethod]
public async Task EmailField_ShowsValidationError_WhenEmailTaken()
{
    await Page.GotoAsync("/register");
    await WaitForBlazorAsync();

    // Enter duplicate email
    await Page.GetByLabel("Email").FillAsync("existing@example.com");
    await Page.GetByLabel("Email").BlurAsync(); // Trigger validation

    // Wait for async validation (uses IsBusy indicator)
    await Expect(Page.GetByTestId("email-validating")).ToBeHiddenAsync();

    // Check error message
    await Expect(Page.GetByText("Email already in use")).ToBeVisibleAsync();
}
```

### DataGrid Interaction

```csharp
[TestMethod]
public async Task ProductGrid_FiltersAndSorts()
{
    await Page.GotoAsync("/products");
    await WaitForBlazorAsync();

    // Wait for data to load
    await Expect(Page.GetByRole(AriaRole.Row)).ToHaveCountAsync(11); // 10 + header

    // Search
    await Page.GetByPlaceholder("Search").FillAsync("Widget");
    await Expect(Page.GetByRole(AriaRole.Row)).ToHaveCountAsync(4);

    // Sort by clicking header
    await Page.GetByRole(AriaRole.Columnheader, new() { Name = "Price" }).ClickAsync();

    // Verify first row after sort
    var firstDataRow = Page.GetByRole(AriaRole.Row).Nth(1);
    await Expect(firstDataRow).ToContainTextAsync("$9.99");
}
```

### Dialog Handling

```csharp
[TestMethod]
public async Task DeleteButton_ShowsConfirmation_ThenDeletes()
{
    await Page.GotoAsync("/products");
    await WaitForBlazorAsync();

    // Click delete on specific row
    var productRow = Page.GetByRole(AriaRole.Row).Filter(new() { HasText = "Widget Pro" });
    await productRow.GetByRole(AriaRole.Button, new() { Name = "Delete" }).ClickAsync();

    // Wait for dialog
    var dialog = Page.GetByRole(AriaRole.Dialog);
    await Expect(dialog).ToBeVisibleAsync();
    await Expect(dialog).ToContainTextAsync("Are you sure");

    // Confirm deletion
    await dialog.GetByRole(AriaRole.Button, new() { Name = "Delete" }).ClickAsync();

    // Verify dialog closed and item removed
    await Expect(dialog).ToBeHiddenAsync();
    await Expect(Page.GetByText("Widget Pro")).ToBeHiddenAsync();

    // Verify snackbar
    await Expect(Page.GetByRole(AriaRole.Alert)).ToContainTextAsync("deleted successfully");
}
```

## Test Organization

```
MyApp.E2E/
├── MyApp.E2E.csproj
├── GlobalUsings.cs
├── Infrastructure/
│   ├── BlazorTestBase.cs      # Base class with WaitForBlazor
│   ├── TestDataBuilder.cs     # Test data factories
│   └── AuthenticationHelper.cs # Login helpers
├── PageObjects/               # Page Object Model (optional)
│   ├── LoginPage.cs
│   └── DashboardPage.cs
└── Tests/
    ├── Authentication/
    │   ├── LoginTests.cs
    │   └── RegistrationTests.cs
    ├── Products/
    │   ├── ProductListTests.cs
    │   └── ProductFormTests.cs
    └── Dashboard/
        └── DashboardTests.cs
```

## Configuration

### .runsettings File

```xml
<?xml version="1.0" encoding="utf-8"?>
<RunSettings>
  <MSTest>
    <Parallelize>
      <Workers>4</Workers>
      <Scope>ClassLevel</Scope>
    </Parallelize>
  </MSTest>
  <Playwright>
    <BrowserName>chromium</BrowserName>
    <LaunchOptions>
      <Headless>true</Headless>
      <SlowMo>0</SlowMo>
    </LaunchOptions>
    <ExpectTimeout>10000</ExpectTimeout>
  </Playwright>
</RunSettings>
```

### Running Tests

```bash
# Run all tests
dotnet test

# Run with settings file
dotnet test --settings:.runsettings

# Run headed (visible browser)
dotnet test -- Playwright.LaunchOptions.Headless=false

# Run specific browser
dotnet test -- Playwright.BrowserName=firefox

# Run with slow motion for debugging
dotnet test -- Playwright.LaunchOptions.SlowMo=500

# Run specific test
dotnet test --filter "FullyQualifiedName~LoginTests"
```

## Debugging Failed Tests

### Enable Tracing

```csharp
[TestClass]
public class BlazorTestBase : PageTest
{
    [TestInitialize]
    public async Task SetupTracing()
    {
        await Context.Tracing.StartAsync(new()
        {
            Title = TestContext.TestName,
            Screenshots = true,
            Snapshots = true,
            Sources = true
        });
    }

    [TestCleanup]
    public async Task SaveTrace()
    {
        var failed = TestContext.CurrentTestOutcome == UnitTestOutcome.Failed;
        await Context.Tracing.StopAsync(new()
        {
            Path = failed ? $"traces/{TestContext.TestName}.zip" : null
        });
    }
}
```

### View Trace

```bash
# Open trace viewer
pwsh bin/Debug/net8.0/playwright.ps1 show-trace traces/LoginTest.zip

# Or upload to web viewer at trace.playwright.dev
```

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| `Thread.Sleep(2000)` | Slow, flaky | Use auto-waiting assertions |
| `Locator(".css-class")` | Brittle selectors | Use role/label locators |
| Hard-coded waits | Race conditions | Use `Expect()` assertions |
| Testing implementation | Breaks on refactor | Test user-visible behavior |
| No base URL | Duplicate URLs | Configure in `ContextOptions` |
| Ignoring loading states | Flaky tests | Wait for loaders to disappear |

## Additional Resources

For detailed guidance, see:
- [Project Setup](project-setup.md) - Full project configuration
- [Blazor Patterns](blazor-patterns.md) - Blazor-specific testing patterns
- [MudBlazor Selectors](mudblazor-selectors.md) - Finding MudBlazor components
- [Debugging](debugging.md) - Trace viewer and debugging techniques

## External Documentation

- [Playwright .NET Docs](https://playwright.dev/dotnet/docs/intro)
- [Playwright Locators](https://playwright.dev/dotnet/docs/locators)
- [Playwright Assertions](https://playwright.dev/dotnet/docs/test-assertions)
- [Playwright Trace Viewer](https://playwright.dev/dotnet/docs/trace-viewer)
