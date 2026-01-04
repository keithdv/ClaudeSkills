# Incremental Source Generator Deep Dive

## Why Incremental Generators?

The old `ISourceGenerator` API suffered critical performance issues:
- Created new `ISyntaxReceiver` on **every keystroke**
- Processed **every syntax node** in the compilation repeatedly
- Caused IDE hangs of "up to several seconds between characters"

Microsoft deprecated `ISourceGenerator` and created `IIncrementalGenerator` with explicit caching semantics.

## The IIncrementalGenerator Interface

```csharp
public interface IIncrementalGenerator
{
    void Initialize(IncrementalGeneratorInitializationContext context);
}
```

The single `Initialize` method receives `IncrementalGeneratorInitializationContext` which provides:

| Member | Purpose |
|--------|---------|
| `SyntaxProvider` | Access to syntax trees for filtering/transformation |
| `AdditionalTextsProvider` | Access to non-C# files |
| `AnalyzerConfigOptionsProvider` | Access to `.editorconfig` settings |
| `CompilationProvider` | Access to the full compilation |
| `RegisterPostInitializationOutput` | Add sources before pipeline runs |
| `RegisterSourceOutput` | Final stage - generate source files |
| `RegisterImplementationSourceOutput` | Generate sources that affect IDE |

## Pipeline Architecture

The generator builds a **declarative pipeline** that the compiler can cache:

```
Input Source → Predicate Filter → Transform → Cache → Output
                   ↑                  ↑          ↑
              (fast syntax)    (semantic model)  (value equality)
```

### Stage 1: Input Providers

```csharp
// Syntax-based input
context.SyntaxProvider.CreateSyntaxProvider(predicate, transform)
context.SyntaxProvider.ForAttributeWithMetadataName(name, predicate, transform)

// Other inputs
context.AdditionalTextsProvider  // Non-C# files
context.AnalyzerConfigOptionsProvider  // .editorconfig
context.CompilationProvider  // Full compilation (use sparingly)
```

### Stage 2: Pipeline Transformations

```csharp
var pipeline = context.SyntaxProvider
    .ForAttributeWithMetadataName("MyAttribute",
        predicate: (node, _) => true,
        transform: (ctx, _) => GetModel(ctx))
    .Where(m => m is not null)           // Filter nulls
    .Select((m, _) => Process(m))        // Transform
    .Collect();                          // Batch into array
```

### Stage 3: Output Registration

```csharp
// Single item output
context.RegisterSourceOutput(singleItemPipeline, (spc, model) => {
    spc.AddSource("File.g.cs", GenerateCode(model));
});

// Batched output (after .Collect())
context.RegisterSourceOutput(batchedPipeline, (spc, models) => {
    foreach (var model in models)
        spc.AddSource($"{model.Name}.g.cs", GenerateCode(model));
});
```

## ForAttributeWithMetadataName - The Recommended API

**This is 99x more efficient than CreateSyntaxProvider** for attribute-based generators.

```csharp
context.SyntaxProvider.ForAttributeWithMetadataName(
    fullyQualifiedMetadataName: "MyNamespace.MyAttribute",
    predicate: static (node, cancellationToken) => node is ClassDeclarationSyntax,
    transform: static (context, cancellationToken) => ExtractModel(context)
);
```

### Parameters

**`fullyQualifiedMetadataName`**: The full metadata name of the attribute, including namespace.

**`predicate`**: Fast syntactic filter. Should:
- Use only syntax analysis (no semantic model)
- Execute in microseconds
- Be as restrictive as possible

**`transform`**: Semantic transformation. Receives `GeneratorAttributeSyntaxContext`:

```csharp
public struct GeneratorAttributeSyntaxContext
{
    public SyntaxNode TargetNode { get; }        // The syntax node
    public ISymbol TargetSymbol { get; }         // The symbol
    public SemanticModel SemanticModel { get; }  // Full semantic access
    public ImmutableArray<AttributeData> Attributes { get; }  // Matching attributes
}
```

### Why It's So Fast

The compiler already tracks which types have which attributes during binding. `ForAttributeWithMetadataName` hooks into this tracking rather than scanning all syntax nodes.

## CreateSyntaxProvider - The General Purpose API

Use when you need to match patterns that aren't attribute-based:

```csharp
context.SyntaxProvider.CreateSyntaxProvider(
    predicate: static (node, ct) => IsSyntaxMatch(node),
    transform: static (ctx, ct) => GetSemanticInfo(ctx)
);
```

### Predicate Design

The predicate runs on **every syntax node** during each generation cycle. It must be:

1. **Extremely fast** - Only use syntax analysis
2. **Conservative** - Filter out as much as possible early
3. **Static** - No captured state

```csharp
// GOOD: Fast syntax-only check
static bool IsSyntaxMatch(SyntaxNode node)
    => node is ClassDeclarationSyntax { AttributeLists.Count: > 0 };

// BAD: Semantic analysis in predicate
static bool IsSyntaxMatch(SyntaxNode node, CancellationToken ct)
{
    if (node is ClassDeclarationSyntax cds)
    {
        var model = compilation.GetSemanticModel(node.SyntaxTree); // SLOW!
        return model.GetDeclaredSymbol(cds) is INamedTypeSymbol nts
            && nts.GetAttributes().Any(...);
    }
    return false;
}
```

### Transform Function

Receives `GeneratorSyntaxContext`:

```csharp
public struct GeneratorSyntaxContext
{
    public SyntaxNode Node { get; }              // The matched syntax node
    public SemanticModel SemanticModel { get; }  // Semantic model for analysis
}
```

Transform functions should:
1. Extract all needed information into a **value-equatable model**
2. **Never store ISymbol** in the model
3. Return `null` if the node shouldn't generate code

## Pipeline Operators in Detail

### Select - Transform Each Item

```csharp
pipeline.Select(static (item, cancellationToken) => {
    return new TransformedModel(
        Name: item.Name.ToUpperInvariant(),
        Properties: item.Properties.Select(p => p.Name).ToArray()
    );
});
```

### Where - Filter Items

```csharp
pipeline.Where(static item => item is not null && item.IsPublic);
```

### Collect - Batch Into Collection

Converts `IncrementalValuesProvider<T>` to `IncrementalValueProvider<ImmutableArray<T>>`:

```csharp
var batched = pipeline.Collect();

context.RegisterSourceOutput(batched, (spc, items) => {
    // items is ImmutableArray<T>
    foreach (var item in items)
        spc.AddSource($"{item.Name}.g.cs", Generate(item));
});
```

### Combine - Merge Pipelines

Combine two pipelines when output depends on both:

```csharp
var combined = pipeline1.Combine(pipeline2);

context.RegisterSourceOutput(combined, (spc, pair) => {
    var (left, right) = pair;
    // Use both values
});
```

Combine with compilation for accessing type information:

```csharp
var withCompilation = pipeline.Combine(context.CompilationProvider);

context.RegisterSourceOutput(withCompilation, (spc, pair) => {
    var (model, compilation) = pair;
    var specialType = compilation.GetTypeByMetadataName("System.String");
    // ...
});
```

## RegisterPostInitializationOutput

Adds source files **before** the main pipeline runs. Use for:
- Marker attributes
- Base classes generators depend on
- Interfaces for generated code

```csharp
context.RegisterPostInitializationOutput(static ctx => {
    ctx.AddSource("MarkerAttribute.g.cs", """
        namespace MyGenerator
        {
            [System.AttributeUsage(System.AttributeTargets.Class)]
            internal sealed class GenerateAttribute : System.Attribute { }
        }
        """);
});
```

These sources become available to subsequent compilation stages, so user code can reference the generated attribute.

## Caching and Incrementality

### How Caching Works

Each pipeline stage caches its output based on **value equality** of inputs:

```
Edit code → Pipeline stage runs → Compares output to cached output
                                          ↓
                     If equal: Skip downstream stages
                     If different: Continue pipeline
```

### Making Models Equatable

**Use records with value types:**

```csharp
internal readonly record struct ClassModel(
    string Namespace,
    string ClassName,
    bool IsPublic
);
```

**For collections, wrap in EquatableArray:**

```csharp
internal readonly record struct ClassModel(
    string Namespace,
    string ClassName,
    EquatableArray<string> Properties
);

// EquatableArray implementation
public readonly struct EquatableArray<T> : IEquatable<EquatableArray<T>>
    where T : IEquatable<T>
{
    private readonly T[] _array;

    public EquatableArray(T[] array) => _array = array;

    public bool Equals(EquatableArray<T> other)
        => _array.AsSpan().SequenceEqual(other._array.AsSpan());

    public override int GetHashCode()
    {
        var hash = new HashCode();
        foreach (var item in _array)
            hash.Add(item);
        return hash.ToHashCode();
    }
}
```

### What Breaks Caching

1. **ISymbol in models** - Symbols are reference types, always compare as different
2. **SyntaxNode in models** - Same issue
3. **Location objects** - Include line/column, change on any edit
4. **Non-equatable collections** - List<T>, arrays without wrapper

## Performance Best Practices

### Do

- Use `ForAttributeWithMetadataName` whenever possible
- Extract primitives (strings, ints) from symbols early
- Make all models value-equatable records
- Use `static` lambdas to avoid allocations
- Filter aggressively in predicate stage

### Don't

- Store `ISymbol` or `SyntaxNode` in models
- Use `CompilationProvider` unless absolutely necessary
- Perform semantic analysis in predicates
- Use non-equatable types in models
- Generate SyntaxNodes (use StringBuilder instead)

## Text Generation

**Avoid Roslyn SyntaxNode generation** - it's expensive and requires `NormalizeWhitespace()`.

**Use StringBuilder or IndentedTextWriter:**

```csharp
private static string GenerateCode(ClassModel model)
{
    var sb = new StringBuilder();

    sb.AppendLine($"namespace {model.Namespace}");
    sb.AppendLine("{");
    sb.AppendLine($"    partial class {model.ClassName}");
    sb.AppendLine("    {");

    foreach (var prop in model.Properties)
    {
        sb.AppendLine($"        public string Get{prop}() => {prop};");
    }

    sb.AppendLine("    }");
    sb.AppendLine("}");

    return sb.ToString();
}
```

**For complex generation, use raw string literals (C# 11+):**

```csharp
var code = $$"""
    namespace {{model.Namespace}}
    {
        partial class {{model.ClassName}}
        {
            public static string Version => "1.0.0";
        }
    }
    """;
```
