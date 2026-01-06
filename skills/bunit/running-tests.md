# Running bUnit Tests

## Command Line

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

# Run tests in specific project
dotnet test MyApp.Tests/MyApp.Tests.csproj
```

## Visual Studio

- **Test Explorer**: View > Test Explorer (Ctrl+E, T)
- **Run All**: Ctrl+R, A
- **Run Selected**: Ctrl+R, T
- **Debug Selected**: Ctrl+R, Ctrl+T

## VS Code

With the C# Dev Kit extension:
- Open the Testing panel (beaker icon)
- Click run/debug icons next to tests

## Filtering Tests

```bash
# By trait/category
dotnet test --filter "Category=Unit"

# By namespace
dotnet test --filter "Namespace~MyApp.Tests.Components"

# Exclude tests
dotnet test --filter "FullyQualifiedName!~Integration"

# Combine filters
dotnet test --filter "(Category=Unit) & (FullyQualifiedName~Counter)"
```

## Test Output

```bash
# TRX format (for CI)
dotnet test --logger "trx;LogFileName=results.trx"

# JUnit format
dotnet test --logger "junit;LogFileName=results.xml"

# HTML report (with ReportGenerator)
dotnet test --collect:"XPlat Code Coverage"
reportgenerator -reports:**/coverage.cobertura.xml -targetdir:coverage-report
```

## Parallel Execution

Configure in `xunit.json`:

```json
{
  "$schema": "https://xunit.net/schema/current/xunit.runner.schema.json",
  "parallelizeAssembly": true,
  "parallelizeTestCollections": true,
  "maxParallelThreads": 0
}
```

Or disable for specific collections:

```csharp
[Collection("Sequential")]
public class DatabaseTests : TestContext
{
    // These tests run sequentially
}
```

## Continuous Integration

### GitHub Actions

```yaml
- name: Test
  run: dotnet test --configuration Release --logger "trx;LogFileName=results.trx"

- name: Upload Test Results
  uses: actions/upload-artifact@v4
  if: always()
  with:
    name: test-results
    path: "**/results.trx"
```

### Azure DevOps

```yaml
- task: DotNetCoreCLI@2
  inputs:
    command: test
    projects: '**/*.Tests.csproj'
    arguments: '--configuration Release --logger trx'

- task: PublishTestResults@2
  inputs:
    testResultsFormat: VSTest
    testResultsFiles: '**/*.trx'
```
