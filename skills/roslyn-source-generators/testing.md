# Testing Source Generators

## Testing Approaches

| Approach | Best For | Tools |
|----------|----------|-------|
| Unit Testing | Model extraction, code generation logic | xUnit/NUnit |
| Snapshot Testing | Output validation, regression detection | Verify + VerifySourceGenerators |
| Integration Testing | End-to-end validation | In-memory compilation |
| Diagnostic Testing | Error/warning validation | Roslyn test infrastructure |

## Project Setup for Tests

### Test Project .csproj

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
  </PropertyGroup>

  <ItemGroup>
    <!-- Test framework -->
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.8.0" />
    <PackageReference Include="xunit" Version="2.6.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.5.4" PrivateAssets="all" />

    <!-- Roslyn testing infrastructure -->
    <PackageReference Include="Microsoft.CodeAnalysis.CSharp" Version="4.8.0" />
    <PackageReference Include="Microsoft.CodeAnalysis.CSharp.Workspaces" Version="4.8.0" />

    <!-- Snapshot testing (optional but recommended) -->
    <PackageReference Include="Verify.Xunit" Version="22.7.0" />
    <PackageReference Include="Verify.SourceGenerators" Version="2.2.0" />
  </ItemGroup>

  <ItemGroup>
    <!-- Reference the generator project directly -->
    <ProjectReference Include="..\MyGenerator\MyGenerator.csproj" />
  </ItemGroup>
</Project>
```

## Test Helper Class

```csharp
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using System.Collections.Immutable;

namespace MyGenerator.Tests;

public static class TestHelper
{
    /// <summary>
    /// Runs a source generator against the provided source code.
    /// </summary>
    public static GeneratorDriverRunResult RunGenerator<TGenerator>(string source)
        where TGenerator : IIncrementalGenerator, new()
    {
        var syntaxTree = CSharpSyntaxTree.ParseText(source);

        var references = AppDomain.CurrentDomain.GetAssemblies()
            .Where(a => !a.IsDynamic && !string.IsNullOrEmpty(a.Location))
            .Select(a => MetadataReference.CreateFromFile(a.Location))
            .Cast<MetadataReference>()
            .ToList();

        var compilation = CSharpCompilation.Create(
            assemblyName: "TestAssembly",
            syntaxTrees: new[] { syntaxTree },
            references: references,
            options: new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary));

        var generator = new TGenerator();

        GeneratorDriver driver = CSharpGeneratorDriver.Create(generator);
        driver = driver.RunGeneratorsAndUpdateCompilation(
            compilation,
            out var outputCompilation,
            out var diagnostics);

        return driver.GetRunResult();
    }

    /// <summary>
    /// Runs a generator and returns the output compilation for further testing.
    /// </summary>
    public static (Compilation OutputCompilation, ImmutableArray<Diagnostic> Diagnostics)
        RunGeneratorWithCompilation<TGenerator>(string source)
        where TGenerator : IIncrementalGenerator, new()
    {
        var syntaxTree = CSharpSyntaxTree.ParseText(source);

        var references = GetDefaultReferences();

        var compilation = CSharpCompilation.Create(
            assemblyName: "TestAssembly",
            syntaxTrees: new[] { syntaxTree },
            references: references,
            options: new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary));

        var generator = new TGenerator();

        GeneratorDriver driver = CSharpGeneratorDriver.Create(generator);
        driver = driver.RunGeneratorsAndUpdateCompilation(
            compilation,
            out var outputCompilation,
            out var diagnostics);

        return (outputCompilation, diagnostics);
    }

    private static IEnumerable<MetadataReference> GetDefaultReferences()
    {
        // Core runtime references
        var assemblies = new[]
        {
            typeof(object).Assembly,
            typeof(Console).Assembly,
            typeof(Enumerable).Assembly,
        };

        foreach (var assembly in assemblies)
        {
            yield return MetadataReference.CreateFromFile(assembly.Location);
        }

        // Add reference to System.Runtime
        var runtimePath = Path.GetDirectoryName(typeof(object).Assembly.Location)!;
        yield return MetadataReference.CreateFromFile(Path.Combine(runtimePath, "System.Runtime.dll"));
    }
}
```

## Unit Testing Examples

### Testing Model Extraction

```csharp
using Xunit;

namespace MyGenerator.Tests;

public class ModelExtractionTests
{
    [Fact]
    public void ExtractsClassName()
    {
        var source = """
            using MyGenerator;

            [Generate]
            public partial class TestClass { }
            """;

        var result = TestHelper.RunGenerator<MyGenerator>(source);

        var generatedSource = result.GeneratedTrees
            .FirstOrDefault(t => t.FilePath.Contains("TestClass"));

        Assert.NotNull(generatedSource);
        Assert.Contains("partial class TestClass", generatedSource.GetText().ToString());
    }

    [Fact]
    public void ExtractsNamespace()
    {
        var source = """
            using MyGenerator;

            namespace MyApp.Models
            {
                [Generate]
                public partial class TestClass { }
            }
            """;

        var result = TestHelper.RunGenerator<MyGenerator>(source);
        var generatedSource = result.GeneratedTrees.First().GetText().ToString();

        Assert.Contains("namespace MyApp.Models", generatedSource);
    }

    [Fact]
    public void ExtractsPublicProperties()
    {
        var source = """
            using MyGenerator;

            [AutoToString]
            public partial class Person
            {
                public string Name { get; set; }
                public int Age { get; set; }
                private string Secret { get; set; } // Should not appear
            }
            """;

        var result = TestHelper.RunGenerator<AutoToStringGenerator>(source);
        var generatedSource = result.GeneratedTrees.First().GetText().ToString();

        Assert.Contains("Name", generatedSource);
        Assert.Contains("Age", generatedSource);
        Assert.DoesNotContain("Secret", generatedSource);
    }
}
```

### Testing Generated Code Compiles

```csharp
public class CompilationTests
{
    [Fact]
    public void GeneratedCodeCompiles()
    {
        var source = """
            using MyGenerator;

            [Generate]
            public partial class TestClass { }
            """;

        var (compilation, diagnostics) = TestHelper.RunGeneratorWithCompilation<MyGenerator>(source);

        // No compilation errors
        var errors = compilation.GetDiagnostics()
            .Where(d => d.Severity == DiagnosticSeverity.Error)
            .ToList();

        Assert.Empty(errors);
    }

    [Fact]
    public void GeneratedMethodIsCallable()
    {
        var source = """
            using MyGenerator;

            [Generate]
            public partial class TestClass
            {
                public void UseGenerated()
                {
                    var result = GeneratedMethod(); // This should exist
                }
            }
            """;

        var (compilation, _) = TestHelper.RunGeneratorWithCompilation<MyGenerator>(source);

        var errors = compilation.GetDiagnostics()
            .Where(d => d.Severity == DiagnosticSeverity.Error);

        Assert.Empty(errors);
    }
}
```

## Snapshot Testing with Verify

Snapshot testing captures generator output and compares it against saved baselines.

### Basic Snapshot Test

```csharp
using VerifyXunit;

namespace MyGenerator.Tests;

[UsesVerify]
public class SnapshotTests
{
    [Fact]
    public Task GeneratesExpectedOutput()
    {
        var source = """
            using MyGenerator;

            namespace TestApp
            {
                [Generate]
                public partial class Person
                {
                    public string Name { get; set; }
                    public int Age { get; set; }
                }
            }
            """;

        var result = TestHelper.RunGenerator<MyGenerator>(source);

        return Verify(result);
    }
}
```

### Snapshot File

Verify creates/compares files like `SnapshotTests.GeneratesExpectedOutput.verified.txt`:

```
{
  GeneratedTrees: [
    {
      FilePath: TestApp.Person.g.cs,
      Source:
namespace TestApp
{
    partial class Person
    {
        public static string GeneratedMethod() => "Hello from generator!";
    }
}
    }
  ],
  Diagnostics: []
}
```

### Updating Snapshots

When generator output changes intentionally:

1. Run tests - they will fail with diff
2. Review the diff carefully
3. Accept changes: `dotnet verify accept` or use IDE integration
4. Commit updated `.verified.txt` files

## Diagnostic Testing

### Testing Error Reporting

```csharp
public class DiagnosticTests
{
    [Fact]
    public void ReportsDiagnosticForNonPartialClass()
    {
        var source = """
            using MyGenerator;

            [Generate]
            public class NotPartial { }  // Missing 'partial' keyword
            """;

        var result = TestHelper.RunGenerator<MyGenerator>(source);

        var diagnostic = result.Diagnostics.FirstOrDefault(d => d.Id == "GEN001");

        Assert.NotNull(diagnostic);
        Assert.Equal(DiagnosticSeverity.Error, diagnostic.Severity);
        Assert.Contains("must be partial", diagnostic.GetMessage());
    }

    [Fact]
    public void NoDiagnosticsForValidInput()
    {
        var source = """
            using MyGenerator;

            [Generate]
            public partial class ValidClass { }
            """;

        var result = TestHelper.RunGenerator<MyGenerator>(source);

        var errors = result.Diagnostics
            .Where(d => d.Severity == DiagnosticSeverity.Error);

        Assert.Empty(errors);
    }
}
```

### Reporting Diagnostics from Generator

```csharp
// In your generator
private static readonly DiagnosticDescriptor NotPartialError = new(
    id: "GEN001",
    title: "Type must be partial",
    messageFormat: "The type '{0}' must be declared as partial to use [Generate]",
    category: "Generation",
    defaultSeverity: DiagnosticSeverity.Error,
    isEnabledByDefault: true);

// In RegisterSourceOutput
context.RegisterSourceOutput(pipeline, (spc, model) =>
{
    if (!model.IsPartial)
    {
        spc.ReportDiagnostic(Diagnostic.Create(
            NotPartialError,
            model.Location,
            model.ClassName));
        return;
    }

    // Generate code...
});
```

## Incremental Caching Tests

Verify that the generator properly caches between runs:

```csharp
public class CachingTests
{
    [Fact]
    public void CachesOutputWhenInputUnchanged()
    {
        var source = """
            using MyGenerator;

            [Generate]
            public partial class TestClass { }
            """;

        var syntaxTree = CSharpSyntaxTree.ParseText(source);
        var compilation = CreateCompilation(syntaxTree);

        var generator = new MyGenerator();
        GeneratorDriver driver = CSharpGeneratorDriver.Create(generator);

        // First run
        driver = driver.RunGeneratorsAndUpdateCompilation(
            compilation, out _, out _);
        var result1 = driver.GetRunResult();

        // Second run (same input)
        driver = driver.RunGeneratorsAndUpdateCompilation(
            compilation, out _, out _);
        var result2 = driver.GetRunResult();

        // Verify caching
        var runResult = result2.Results[0];

        // IncrementalGeneratorRunStep.OutputSteps shows caching behavior
        // Cached items have Reason = IncrementalStepRunReason.Cached
    }

    [Fact]
    public void RegeneratesWhenInputChanges()
    {
        var source1 = """
            using MyGenerator;

            [Generate]
            public partial class TestClass { }
            """;

        var source2 = """
            using MyGenerator;

            [Generate]
            public partial class TestClass
            {
                public string Name { get; set; }  // Added property
            }
            """;

        // Run with source1, then source2
        // Verify different output
    }
}
```

## Testing Additional Files

```csharp
public class AdditionalFilesTests
{
    [Fact]
    public void ProcessesJsonSchemaFile()
    {
        var source = "// Empty C# file";
        var jsonContent = """
            {
                "Name": "string",
                "Age": "int"
            }
            """;

        var syntaxTree = CSharpSyntaxTree.ParseText(source);
        var compilation = CreateCompilation(syntaxTree);

        // Create additional text
        var additionalText = new TestAdditionalText(
            path: "settings.schema.json",
            content: jsonContent);

        var generator = new SettingsGenerator();
        GeneratorDriver driver = CSharpGeneratorDriver.Create(
            generators: new[] { generator.AsSourceGenerator() },
            additionalTexts: new[] { additionalText });

        driver = driver.RunGeneratorsAndUpdateCompilation(
            compilation, out _, out _);

        var result = driver.GetRunResult();
        var generated = result.GeneratedTrees.First().GetText().ToString();

        Assert.Contains("public string Name", generated);
        Assert.Contains("public int Age", generated);
    }
}

// Test helper for additional files
public class TestAdditionalText : AdditionalText
{
    private readonly string _path;
    private readonly string _content;

    public TestAdditionalText(string path, string content)
    {
        _path = path;
        _content = content;
    }

    public override string Path => _path;

    public override SourceText? GetText(CancellationToken cancellationToken = default)
        => SourceText.From(_content);
}
```

## Test Organization

```
MyGenerator.Tests/
├── Unit/
│   ├── ModelExtractionTests.cs
│   ├── CodeGenerationTests.cs
│   └── EquatableArrayTests.cs
├── Integration/
│   ├── CompilationTests.cs
│   └── CachingTests.cs
├── Snapshots/
│   ├── SnapshotTests.cs
│   └── *.verified.txt
├── Diagnostics/
│   └── DiagnosticTests.cs
├── Helpers/
│   ├── TestHelper.cs
│   └── TestAdditionalText.cs
└── TestData/
    └── *.json
```

## Best Practices

1. **Test happy path first** - Ensure basic generation works
2. **Test edge cases** - Global namespace, nested classes, generics
3. **Test error conditions** - Missing partial, invalid attributes
4. **Use snapshot testing** - Catches unintended output changes
5. **Test caching behavior** - Verify incremental generator performance
6. **Keep test sources minimal** - Only include what's needed for the test
