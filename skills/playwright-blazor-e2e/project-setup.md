# Playwright Blazor E2E - Project Setup

## Project Structure

```
Solution/
├── src/
│   └── MyApp.Blazor/           # Blazor application
│       └── MyApp.Blazor.csproj
└── tests/
    └── MyApp.E2E/              # E2E test project
        ├── MyApp.E2E.csproj
        ├── .runsettings
        ├── GlobalUsings.cs
        ├── Infrastructure/
        │   ├── BlazorTestBase.cs
        │   ├── TestServerFactory.cs
        │   └── AuthenticationHelper.cs
        └── Tests/
            └── ...
```

## Project File (.csproj)

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
    <!-- MSTest -->
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.11.1" />
    <PackageReference Include="MSTest.TestAdapter" Version="3.6.3" />
    <PackageReference Include="MSTest.TestFramework" Version="3.6.3" />

    <!-- Playwright -->
    <PackageReference Include="Microsoft.Playwright.MSTest" Version="1.49.0" />

    <!-- Optional: For testing with WebApplicationFactory -->
    <PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="8.0.11" />
  </ItemGroup>

  <!-- Reference Blazor app for integration testing -->
  <ItemGroup>
    <ProjectReference Include="..\..\src\MyApp.Blazor\MyApp.Blazor.csproj" />
  </ItemGroup>

</Project>
```

## Global Usings

```csharp
// GlobalUsings.cs
global using Microsoft.Playwright;
global using Microsoft.Playwright.MSTest;
global using Microsoft.VisualStudio.TestTools.UnitTesting;
global using System.Text.RegularExpressions;
```

## Base Test Class

```csharp
// Infrastructure/BlazorTestBase.cs
using System.Diagnostics;

namespace MyApp.E2E.Infrastructure;

[TestClass]
public class BlazorTestBase : PageTest
{
    private static Process? _blazorProcess;
    private static readonly object _lock = new();

    protected string BaseUrl => "https://localhost:5001";

    public override BrowserNewContextOptions ContextOptions => new()
    {
        BaseURL = BaseUrl,
        IgnoreHTTPSErrors = true,
        ViewportSize = new ViewportSize { Width = 1920, Height = 1080 }
    };

    [AssemblyInitialize]
    public static void AssemblyInit(TestContext context)
    {
        // Start Blazor app if not running
        StartBlazorAppIfNeeded();
    }

    [AssemblyCleanup]
    public static void AssemblyCleanup()
    {
        StopBlazorApp();
    }

    [TestInitialize]
    public async Task TestInit()
    {
        // Start tracing for each test
        await Context.Tracing.StartAsync(new()
        {
            Title = TestContext.TestName,
            Screenshots = true,
            Snapshots = true,
            Sources = true
        });
    }

    [TestCleanup]
    public async Task TestCleanup()
    {
        // Save trace only on failure
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

    /// <summary>
    /// Waits for Blazor WebAssembly to fully initialize.
    /// Call after navigation to ensure the app is ready for interaction.
    /// </summary>
    protected async Task WaitForBlazorAsync(int timeoutMs = 30000)
    {
        // Wait for Blazor runtime
        await Page.WaitForFunctionAsync(
            "window.Blazor !== undefined",
            new() { Timeout = timeoutMs }
        );

        // Wait for any loading overlay to disappear
        var loader = Page.Locator("[data-testid='app-loading'], .loading-overlay, #blazor-loading");
        try
        {
            await Expect(loader).ToBeHiddenAsync(new() { Timeout = timeoutMs });
        }
        catch (TimeoutException)
        {
            // Loader might not exist if already loaded
        }
    }

    /// <summary>
    /// Navigates to a path and waits for Blazor to be ready.
    /// </summary>
    protected async Task NavigateAndWaitAsync(string path)
    {
        await Page.GotoAsync(path);
        await WaitForBlazorAsync();
    }

    private static void StartBlazorAppIfNeeded()
    {
        lock (_lock)
        {
            if (_blazorProcess != null) return;

            // Check if already running
            using var client = new HttpClient();
            try
            {
                var response = client.GetAsync("https://localhost:5001").Result;
                return; // Already running
            }
            catch
            {
                // Not running, start it
            }

            var projectPath = Path.GetFullPath(
                Path.Combine(Directory.GetCurrentDirectory(),
                "..", "..", "..", "..", "..", "src", "MyApp.Blazor"));

            _blazorProcess = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = "dotnet",
                    Arguments = "run --no-build",
                    WorkingDirectory = projectPath,
                    UseShellExecute = false,
                    CreateNoWindow = true
                }
            };
            _blazorProcess.Start();

            // Wait for app to be ready
            WaitForAppReady("https://localhost:5001", TimeSpan.FromSeconds(60));
        }
    }

    private static void WaitForAppReady(string url, TimeSpan timeout)
    {
        using var client = new HttpClient(new HttpClientHandler
        {
            ServerCertificateCustomValidationCallback = (_, _, _, _) => true
        });

        var deadline = DateTime.UtcNow + timeout;
        while (DateTime.UtcNow < deadline)
        {
            try
            {
                var response = client.GetAsync(url).Result;
                if (response.IsSuccessStatusCode)
                    return;
            }
            catch { }
            Thread.Sleep(500);
        }

        throw new TimeoutException($"App at {url} did not start within {timeout.TotalSeconds}s");
    }

    private static void StopBlazorApp()
    {
        lock (_lock)
        {
            if (_blazorProcess == null) return;

            try
            {
                _blazorProcess.Kill(entireProcessTree: true);
                _blazorProcess.WaitForExit(5000);
            }
            catch { }
            finally
            {
                _blazorProcess.Dispose();
                _blazorProcess = null;
            }
        }
    }
}
```

## Alternative: WebApplicationFactory Integration

For tighter integration, use ASP.NET Core's test server:

```csharp
// Infrastructure/TestServerFactory.cs
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Hosting;

namespace MyApp.E2E.Infrastructure;

public class BlazorAppFactory : WebApplicationFactory<Program>
{
    private readonly int _port;

    public BlazorAppFactory(int port = 5001)
    {
        _port = port;
    }

    public string BaseUrl => $"https://localhost:{_port}";

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.UseEnvironment("Testing");
        builder.UseUrls(BaseUrl);

        // Configure test services
        builder.ConfigureServices(services =>
        {
            // Replace database with in-memory
            // services.RemoveAll<DbContext>();
            // services.AddDbContext<AppDbContext>(options =>
            //     options.UseInMemoryDatabase("E2ETests"));
        });
    }

    protected override IHost CreateHost(IHostBuilder builder)
    {
        // Create the host that listens on localhost
        var host = base.CreateHost(builder);
        return host;
    }
}
```

## .runsettings Configuration

```xml
<?xml version="1.0" encoding="utf-8"?>
<RunSettings>
  <!-- MSTest configuration -->
  <MSTest>
    <Parallelize>
      <Workers>4</Workers>
      <Scope>ClassLevel</Scope>
    </Parallelize>
    <CaptureTraceOutput>false</CaptureTraceOutput>
  </MSTest>

  <!-- Playwright configuration -->
  <Playwright>
    <!-- Browser: chromium, firefox, webkit -->
    <BrowserName>chromium</BrowserName>

    <LaunchOptions>
      <!-- Run headless in CI, headed locally for debugging -->
      <Headless>true</Headless>

      <!-- Slow down actions for debugging (ms) -->
      <SlowMo>0</SlowMo>

      <!-- Browser args -->
      <Args>--disable-gpu</Args>
    </LaunchOptions>

    <!-- Default assertion timeout (ms) -->
    <ExpectTimeout>10000</ExpectTimeout>
  </Playwright>

  <!-- Test results directory -->
  <RunConfiguration>
    <ResultsDirectory>.\TestResults</ResultsDirectory>
  </RunConfiguration>
</RunSettings>
```

## Authentication Helper

```csharp
// Infrastructure/AuthenticationHelper.cs
namespace MyApp.E2E.Infrastructure;

public static class AuthenticationHelper
{
    public static async Task LoginAsync(
        IPage page,
        string email = "test@example.com",
        string password = "TestPassword123!")
    {
        await page.GotoAsync("/login");

        await page.GetByLabel("Email").FillAsync(email);
        await page.GetByLabel("Password").FillAsync(password);
        await page.GetByRole(AriaRole.Button, new() { Name = "Sign In" }).ClickAsync();

        // Wait for redirect after login
        await Expect(page).Not.ToHaveURLAsync(new Regex("/login"));
    }

    public static async Task LogoutAsync(IPage page)
    {
        await page.GetByRole(AriaRole.Button, new() { Name = "Account" }).ClickAsync();
        await page.GetByRole(AriaRole.Menuitem, new() { Name = "Logout" }).ClickAsync();

        await Expect(page).ToHaveURLAsync("/login");
    }

    /// <summary>
    /// Saves authentication state to a file for reuse across tests.
    /// Call once in test setup, then load in individual tests.
    /// </summary>
    public static async Task SaveAuthStateAsync(IBrowserContext context, string path = "auth.json")
    {
        await context.StorageStateAsync(new() { Path = path });
    }

    /// <summary>
    /// Creates a context with saved authentication state.
    /// </summary>
    public static BrowserNewContextOptions WithAuthState(
        this BrowserNewContextOptions options,
        string path = "auth.json")
    {
        options.StorageStatePath = path;
        return options;
    }
}
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'

      - name: Restore dependencies
        run: dotnet restore

      - name: Build
        run: dotnet build --no-restore

      - name: Install Playwright Browsers
        run: pwsh tests/MyApp.E2E/bin/Debug/net8.0/playwright.ps1 install --with-deps

      - name: Run E2E Tests
        run: dotnet test tests/MyApp.E2E --no-build --settings:tests/MyApp.E2E/.runsettings
        env:
          CI: true

      - name: Upload Test Results
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-traces
          path: tests/MyApp.E2E/TestResults/traces/
          retention-days: 7
```

### Azure DevOps

```yaml
# azure-pipelines.yml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: UseDotNet@2
    inputs:
      version: '8.0.x'

  - script: dotnet restore
    displayName: 'Restore'

  - script: dotnet build --no-restore
    displayName: 'Build'

  - script: pwsh tests/MyApp.E2E/bin/Debug/net8.0/playwright.ps1 install --with-deps
    displayName: 'Install Browsers'

  - script: dotnet test tests/MyApp.E2E --no-build --settings:tests/MyApp.E2E/.runsettings --logger trx
    displayName: 'Run E2E Tests'
    continueOnError: true

  - task: PublishTestResults@2
    inputs:
      testResultsFormat: 'VSTest'
      testResultsFiles: '**/TestResults/*.trx'
    condition: always()

  - publish: tests/MyApp.E2E/TestResults/traces
    artifact: playwright-traces
    condition: failed()
```

## Environment-Specific Configuration

```csharp
// Infrastructure/TestConfiguration.cs
namespace MyApp.E2E.Infrastructure;

public static class TestConfiguration
{
    public static string BaseUrl =>
        Environment.GetEnvironmentVariable("E2E_BASE_URL")
        ?? "https://localhost:5001";

    public static bool IsCI =>
        Environment.GetEnvironmentVariable("CI") == "true";

    public static string TestUserEmail =>
        Environment.GetEnvironmentVariable("E2E_TEST_USER_EMAIL")
        ?? "e2e-test@example.com";

    public static string TestUserPassword =>
        Environment.GetEnvironmentVariable("E2E_TEST_USER_PASSWORD")
        ?? "TestPassword123!";
}
```

## Database Seeding

```csharp
// Infrastructure/TestDataSeeder.cs
namespace MyApp.E2E.Infrastructure;

public static class TestDataSeeder
{
    private static readonly HttpClient _client = new(new HttpClientHandler
    {
        ServerCertificateCustomValidationCallback = (_, _, _, _) => true
    });

    /// <summary>
    /// Seeds test data via API endpoint (requires /api/test-data endpoint in Testing environment)
    /// </summary>
    public static async Task SeedDataAsync(string baseUrl, object data)
    {
        var response = await _client.PostAsJsonAsync($"{baseUrl}/api/test-data/seed", data);
        response.EnsureSuccessStatusCode();
    }

    /// <summary>
    /// Resets database to clean state
    /// </summary>
    public static async Task ResetDatabaseAsync(string baseUrl)
    {
        var response = await _client.PostAsync($"{baseUrl}/api/test-data/reset", null);
        response.EnsureSuccessStatusCode();
    }
}
```
