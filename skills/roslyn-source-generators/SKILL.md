---
name: roslyn-source-generators
description: Create and maintain Roslyn source generators for compile-time code generation. Use when building incremental generators, designing pipelines with ForAttributeWithMetadataName, creating marker attributes, implementing equatable models, testing generators, or debugging generator performance issues.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(dotnet:*), WebFetch
---

# Roslyn Source Generators Skill

## Overview

Source generators enable **compile-time metaprogramming** in C# - code that generates additional C# source files during compilation. Generated code becomes part of the compilation and is available for use like any other code.

### Key Capabilities

- Generate C# source at compile time
- Introspect user code via Roslyn syntax/semantic models
- Access additional files (XML, JSON, etc.)
- Report diagnostics when generation fails
- **Additive only** - cannot modify existing user code

## CRITICAL: Old vs New API

| Aspect | ISourceGenerator (DEPRECATED) | IIncrementalGenerator (CURRENT) |
|--------|-------------------------------|----------------------------------|
| Status | **Deprecated** | **Recommended** |
| Performance | Poor - runs on every keystroke | Excellent - caches pipeline stages |
| Interface | `Initialize()` + `Execute()` | Single `Initialize()` with pipeline |
| Filtering | `ISyntaxReceiver` | `ForAttributeWithMetadataName()` |
| Memory | Creates new receiver each cycle | Memoized/cached transforms |

**Always use `IIncrementalGenerator`** - the old API causes IDE hangs and performance degradation.

## Quick Start

### 1. Create Generator Project

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>netstandard2.0</TargetFramework>
    <IncludeBuildOutput>false</IncludeBuildOutput>
    <Nullable>enable</Nullable>
    <LangVersion>Latest</LangVersion>
    <EnforceExtendedAnalyzerRules>true</EnforceExtendedAnalyzerRules>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.CodeAnalysis.CSharp" Version="4.3.0" PrivateAssets="all" />
    <PackageReference Include="Microsoft.CodeAnalysis.Analyzers" Version="3.3.4" PrivateAssets="all" />
  </ItemGroup>

  <ItemGroup>
    <None Include="$(OutputPath)\$(AssemblyName).dll" Pack="true"
          PackagePath="analyzers/dotnet/cs" Visible="false" />
  </ItemGroup>
</Project>
```

### 2. Implement IIncrementalGenerator

```csharp
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using System.Collections.Immutable;
using System.Text;

namespace MyGenerators;

[Generator]
public class MyGenerator : IIncrementalGenerator
{
    public void Initialize(IncrementalGeneratorInitializationContext context)
    {
        // Step 1: Register the marker attribute (runs once at start)
        context.RegisterPostInitializationOutput(static ctx =>
        {
            ctx.AddSource("MyAttribute.g.cs", """
                namespace MyGenerators
                {
                    [System.AttributeUsage(System.AttributeTargets.Class)]
                    internal sealed class GenerateAttribute : System.Attribute { }
                }
                """);
        });

        // Step 2: Build the pipeline using ForAttributeWithMetadataName
        var pipeline = context.SyntaxProvider.ForAttributeWithMetadataName(
            fullyQualifiedMetadataName: "MyGenerators.GenerateAttribute",
            predicate: static (node, _) => node is ClassDeclarationSyntax,
            transform: static (ctx, _) => GetModel(ctx)
        ).Where(static m => m is not null);

        // Step 3: Register output generation
        context.RegisterSourceOutput(pipeline, static (spc, model) =>
        {
            if (model is null) return;

            var code = GenerateCode(model.Value);
            spc.AddSource($"{model.Value.ClassName}.g.cs", code);
        });
    }

    private static MyModel? GetModel(GeneratorAttributeSyntaxContext ctx)
    {
        if (ctx.TargetSymbol is not INamedTypeSymbol typeSymbol)
            return null;

        return new MyModel(
            Namespace: typeSymbol.ContainingNamespace.IsGlobalNamespace
                ? null
                : typeSymbol.ContainingNamespace.ToDisplayString(),
            ClassName: typeSymbol.Name
        );
    }

    private static string GenerateCode(MyModel model)
    {
        var sb = new StringBuilder();

        if (model.Namespace is not null)
        {
            sb.AppendLine($"namespace {model.Namespace}");
            sb.AppendLine("{");
        }

        sb.AppendLine($"    partial class {model.ClassName}");
        sb.AppendLine("    {");
        sb.AppendLine("        public static string GeneratedMethod() => \"Hello from generator!\";");
        sb.AppendLine("    }");

        if (model.Namespace is not null)
            sb.AppendLine("}");

        return sb.ToString();
    }
}

// CRITICAL: Use records for automatic value equality (enables caching)
internal readonly record struct MyModel(string? Namespace, string ClassName);
```

### 3. Consume in Another Project

```xml
<ItemGroup>
  <ProjectReference Include="..\MyGenerators\MyGenerators.csproj"
                    OutputItemType="Analyzer"
                    ReferenceOutputAssembly="false" />
</ItemGroup>
```

```csharp
using MyGenerators;

[Generate]
public partial class MyClass
{
    public void UseGenerated()
    {
        var result = GeneratedMethod(); // Generated at compile time
    }
}
```

## Core Concepts

### ForAttributeWithMetadataName (99x More Efficient)

**Always prefer this over `CreateSyntaxProvider`** for attribute-based generators:

```csharp
context.SyntaxProvider.ForAttributeWithMetadataName(
    fullyQualifiedMetadataName: "MyNamespace.MyAttribute",
    predicate: static (node, ct) => node is ClassDeclarationSyntax,
    transform: static (ctx, ct) => ExtractModel(ctx)
);
```

This method:
- Uses compiler's internal attribute tracking (extremely fast)
- Skips most syntax tree processing
- Handles attribute aliases automatically
- Is the **recommended default** for any generator triggered by attributes

### Pipeline Operators

| Operator | Purpose | Example |
|----------|---------|---------|
| `Select` | Transform each item | `.Select((item, ct) => Process(item))` |
| `Where` | Filter items | `.Where(item => item.IsValid)` |
| `Collect` | Batch into collection | `.Collect()` for `ImmutableArray<T>` |
| `Combine` | Merge two pipelines | `pipeline1.Combine(pipeline2)` |

### Model Design for Caching

**Critical rules for models:**

1. **Use records** - Automatic value equality
2. **Never include ISymbol** - Prevents memory reuse
3. **Extract primitives early** - Replace syntax nodes with strings/ints
4. **Wrap arrays** - Create `EquatableArray<T>` for collections

```csharp
// GOOD: Proper equatable model
internal readonly record struct ClassModel(
    string Namespace,
    string ClassName,
    EquatableArray<string> Properties
);

// BAD: Holds references that break caching
internal class BadModel
{
    public INamedTypeSymbol Symbol { get; set; } // Never do this
    public ClassDeclarationSyntax Syntax { get; set; } // Or this
}
```

## Additional Resources

For detailed guidance, see:
- [Project Setup](project-setup.md) - Full .csproj configuration
- [Incremental Generator Guide](incremental-generator-guide.md) - Deep dive into API
- [Patterns and Examples](patterns-and-examples.md) - Common implementation patterns
- [Testing](testing.md) - Unit and snapshot testing strategies
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

## What Generators Cannot Do

Source generators are explicitly **additive only**:

- Cannot modify existing user code
- Cannot rewrite syntax trees
- Cannot perform IL weaving
- Cannot replace language features
- Cannot communicate between generators
- Cannot access other generators' output

For code rewriting, use Roslyn Analyzers with Code Fixes or IL weaving tools like Fody.
