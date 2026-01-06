# Playwright Configuration

## Test Project Structure

```
MyApp.E2E/
├── MyApp.E2E.csproj
├── GlobalUsings.cs
├── .runsettings
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

## .runsettings File

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

## Running Tests

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

# Run by category
dotnet test --filter "TestCategory=Smoke"
```

## Base Test Class

```csharp
using Microsoft.Playwright;
using Microsoft.Playwright.MSTest;

namespace MyApp.E2E.Infrastructure;

[TestClass]
public class BlazorTestBase : PageTest
{
    public override BrowserNewContextOptions ContextOptions => new()
    {
        BaseURL = TestConfig.BaseUrl,
        IgnoreHTTPSErrors = true,
        ViewportSize = new ViewportSize { Width = 1920, Height = 1080 }
    };

    protected async Task WaitForBlazorAsync()
    {
        // Wait for Blazor WebAssembly to finish loading
        await Page.WaitForFunctionAsync("window.Blazor !== undefined");

        // Wait for any initial loading indicators to disappear
        var loader = Page.GetByTestId("app-loading");
        await Expect(loader).ToBeHiddenAsync(new() { Timeout = 30000 });
    }

    protected async Task LoginAsAsync(string email, string password)
    {
        await Page.GotoAsync("/login");
        await WaitForBlazorAsync();

        await Page.GetByLabel("Email").FillAsync(email);
        await Page.GetByLabel("Password").FillAsync(password);
        await Page.GetByRole(AriaRole.Button, new() { Name = "Sign In" }).ClickAsync();

        await Expect(Page).ToHaveURLAsync("/dashboard");
    }
}
```

## Test Configuration

```csharp
namespace MyApp.E2E.Infrastructure;

public static class TestConfig
{
    public static string BaseUrl =>
        Environment.GetEnvironmentVariable("E2E_BASE_URL")
        ?? "https://localhost:5001";

    public static string AdminEmail =>
        Environment.GetEnvironmentVariable("E2E_ADMIN_EMAIL")
        ?? "admin@test.com";

    public static string AdminPassword =>
        Environment.GetEnvironmentVariable("E2E_ADMIN_PASSWORD")
        ?? "Test123!";
}
```

## Global Usings

```csharp
// GlobalUsings.cs
global using Microsoft.Playwright;
global using Microsoft.Playwright.MSTest;
global using Microsoft.VisualStudio.TestTools.UnitTesting;
global using MyApp.E2E.Infrastructure;
```

## Browser Installation

```bash
# After adding Playwright package
dotnet build

# Install browsers (required once per machine)
pwsh bin/Debug/net8.0/playwright.ps1 install

# Install specific browser only
pwsh bin/Debug/net8.0/playwright.ps1 install chromium
```

## CI/CD Integration

### GitHub Actions

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'

      - name: Install dependencies
        run: dotnet restore

      - name: Build
        run: dotnet build --no-restore

      - name: Install Playwright browsers
        run: pwsh MyApp.E2E/bin/Debug/net8.0/playwright.ps1 install --with-deps

      - name: Start application
        run: |
          dotnet run --project MyApp.Server &
          sleep 10

      - name: Run E2E tests
        run: dotnet test MyApp.E2E --no-build --logger "trx;LogFileName=results.trx"
        env:
          E2E_BASE_URL: https://localhost:5001

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: "**/results.trx"

      - name: Upload traces
        uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-traces
          path: "**/traces/*.zip"
```

### Azure DevOps

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: UseDotNet@2
    inputs:
      version: '8.0.x'

  - script: dotnet build
    displayName: 'Build'

  - script: pwsh MyApp.E2E/bin/Debug/net8.0/playwright.ps1 install --with-deps
    displayName: 'Install Playwright browsers'

  - script: |
      dotnet run --project MyApp.Server &
      sleep 10
    displayName: 'Start application'

  - task: DotNetCoreCLI@2
    displayName: 'Run E2E tests'
    inputs:
      command: test
      projects: 'MyApp.E2E/*.csproj'
      arguments: '--logger trx'
    env:
      E2E_BASE_URL: https://localhost:5001

  - task: PublishTestResults@2
    inputs:
      testResultsFormat: VSTest
      testResultsFiles: '**/*.trx'
```

## Environment-Specific Configuration

```csharp
public static class TestConfig
{
    public static string BaseUrl
    {
        get
        {
            var env = Environment.GetEnvironmentVariable("TEST_ENVIRONMENT") ?? "local";
            return env switch
            {
                "local" => "https://localhost:5001",
                "dev" => "https://dev.myapp.com",
                "staging" => "https://staging.myapp.com",
                _ => throw new ArgumentException($"Unknown environment: {env}")
            };
        }
    }
}
```
