# Common Patterns and Examples

## Pattern 1: Marker Attribute with Partial Class Augmentation

The most common pattern - add functionality to classes marked with an attribute.

### Use Case

User writes:
```csharp
[AutoToString]
public partial class Person
{
    public string FirstName { get; set; }
    public string LastName { get; set; }
}
```

Generator produces:
```csharp
partial class Person
{
    public override string ToString() => $"Person {{ FirstName = {FirstName}, LastName = {LastName} }}";
}
```

### Complete Implementation

```csharp
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using System.Collections.Immutable;
using System.Text;

namespace AutoToString;

[Generator]
public class AutoToStringGenerator : IIncrementalGenerator
{
    public void Initialize(IncrementalGeneratorInitializationContext context)
    {
        // Register the marker attribute
        context.RegisterPostInitializationOutput(static ctx =>
        {
            ctx.AddSource("AutoToStringAttribute.g.cs", """
                namespace AutoToString
                {
                    [System.AttributeUsage(System.AttributeTargets.Class | System.AttributeTargets.Struct)]
                    public sealed class AutoToStringAttribute : System.Attribute { }
                }
                """);
        });

        // Build pipeline
        var pipeline = context.SyntaxProvider.ForAttributeWithMetadataName(
            fullyQualifiedMetadataName: "AutoToString.AutoToStringAttribute",
            predicate: static (node, _) => node is ClassDeclarationSyntax or RecordDeclarationSyntax,
            transform: static (ctx, ct) => GetClassModel(ctx, ct)
        ).Where(static m => m is not null);

        // Generate output
        context.RegisterSourceOutput(pipeline, static (spc, model) =>
        {
            if (model is null) return;
            spc.AddSource($"{model.Value.ClassName}.ToString.g.cs", GenerateCode(model.Value));
        });
    }

    private static ClassModel? GetClassModel(GeneratorAttributeSyntaxContext ctx, CancellationToken ct)
    {
        if (ctx.TargetSymbol is not INamedTypeSymbol typeSymbol)
            return null;

        // Check if partial
        if (!ctx.TargetNode.Modifiers.Any(SyntaxKind.PartialKeyword))
        {
            // Could report diagnostic here
            return null;
        }

        var properties = typeSymbol.GetMembers()
            .OfType<IPropertySymbol>()
            .Where(p => p.DeclaredAccessibility == Accessibility.Public)
            .Where(p => !p.IsStatic)
            .Select(p => p.Name)
            .ToImmutableArray();

        return new ClassModel(
            Namespace: typeSymbol.ContainingNamespace.IsGlobalNamespace
                ? null : typeSymbol.ContainingNamespace.ToDisplayString(),
            ClassName: typeSymbol.Name,
            Properties: new EquatableArray<string>(properties)
        );
    }

    private static string GenerateCode(ClassModel model)
    {
        var sb = new StringBuilder();

        if (model.Namespace is not null)
        {
            sb.AppendLine($"namespace {model.Namespace}");
            sb.AppendLine("{");
        }

        sb.AppendLine($"    partial class {model.ClassName}");
        sb.AppendLine("    {");
        sb.Append("        public override string ToString() => $\"");
        sb.Append(model.ClassName);
        sb.Append(" {{ ");

        var first = true;
        foreach (var prop in model.Properties)
        {
            if (!first) sb.Append(", ");
            sb.Append($"{prop} = {{{prop}}}");
            first = false;
        }

        sb.AppendLine(" }}\";");
        sb.AppendLine("    }");

        if (model.Namespace is not null)
            sb.AppendLine("}");

        return sb.ToString();
    }
}

internal readonly record struct ClassModel(
    string? Namespace,
    string ClassName,
    EquatableArray<string> Properties
);
```

## Pattern 2: Enum Extension Methods

Generate fast ToString and parsing methods for enums.

### Use Case

User writes:
```csharp
[EnumExtensions]
public enum Color { Red, Green, Blue }
```

Generator produces:
```csharp
public static class ColorExtensions
{
    public static string ToStringFast(this Color value) => value switch
    {
        Color.Red => nameof(Color.Red),
        Color.Green => nameof(Color.Green),
        Color.Blue => nameof(Color.Blue),
        _ => value.ToString()
    };

    public static bool TryParse(string value, out Color result) { ... }
}
```

### Implementation

```csharp
[Generator]
public class EnumExtensionsGenerator : IIncrementalGenerator
{
    public void Initialize(IncrementalGeneratorInitializationContext context)
    {
        context.RegisterPostInitializationOutput(static ctx =>
        {
            ctx.AddSource("EnumExtensionsAttribute.g.cs", """
                namespace EnumExtensions
                {
                    [System.AttributeUsage(System.AttributeTargets.Enum)]
                    public sealed class EnumExtensionsAttribute : System.Attribute { }
                }
                """);
        });

        var pipeline = context.SyntaxProvider.ForAttributeWithMetadataName(
            "EnumExtensions.EnumExtensionsAttribute",
            predicate: static (node, _) => node is EnumDeclarationSyntax,
            transform: static (ctx, _) => GetEnumModel(ctx)
        ).Where(static m => m is not null);

        context.RegisterSourceOutput(pipeline, static (spc, model) =>
        {
            if (model is null) return;
            spc.AddSource($"{model.Value.Name}Extensions.g.cs", GenerateEnumExtensions(model.Value));
        });
    }

    private static EnumModel? GetEnumModel(GeneratorAttributeSyntaxContext ctx)
    {
        if (ctx.TargetSymbol is not INamedTypeSymbol enumSymbol)
            return null;

        var members = enumSymbol.GetMembers()
            .OfType<IFieldSymbol>()
            .Where(f => f.ConstantValue is not null)
            .Select(f => f.Name)
            .ToImmutableArray();

        return new EnumModel(
            Namespace: enumSymbol.ContainingNamespace.IsGlobalNamespace
                ? null : enumSymbol.ContainingNamespace.ToDisplayString(),
            Name: enumSymbol.Name,
            Members: new EquatableArray<string>(members)
        );
    }

    private static string GenerateEnumExtensions(EnumModel model)
    {
        var sb = new StringBuilder();

        if (model.Namespace is not null)
        {
            sb.AppendLine($"namespace {model.Namespace}");
            sb.AppendLine("{");
        }

        sb.AppendLine($"    public static class {model.Name}Extensions");
        sb.AppendLine("    {");

        // ToStringFast
        sb.AppendLine($"        public static string ToStringFast(this {model.Name} value) => value switch");
        sb.AppendLine("        {");
        foreach (var member in model.Members)
            sb.AppendLine($"            {model.Name}.{member} => nameof({model.Name}.{member}),");
        sb.AppendLine("            _ => value.ToString()");
        sb.AppendLine("        };");

        // TryParse
        sb.AppendLine();
        sb.AppendLine($"        public static bool TryParse(string value, out {model.Name} result)");
        sb.AppendLine("        {");
        sb.AppendLine("            result = default;");
        sb.AppendLine("            return value switch");
        sb.AppendLine("            {");
        foreach (var member in model.Members)
            sb.AppendLine($"                nameof({model.Name}.{member}) => (result = {model.Name}.{member}) == result,");
        sb.AppendLine("                _ => false");
        sb.AppendLine("            };");
        sb.AppendLine("        }");

        sb.AppendLine("    }");

        if (model.Namespace is not null)
            sb.AppendLine("}");

        return sb.ToString();
    }
}

internal readonly record struct EnumModel(
    string? Namespace,
    string Name,
    EquatableArray<string> Members
);
```

## Pattern 3: Interface Implementation Discovery

Find all implementations of an interface and generate a registry.

### Use Case

```csharp
// User defines interface
public interface IMessageHandler { void Handle(); }

// Various implementations
[RegisterHandler]
public class OrderHandler : IMessageHandler { ... }

[RegisterHandler]
public class PaymentHandler : IMessageHandler { ... }
```

Generator produces:
```csharp
public static class HandlerRegistry
{
    public static IEnumerable<Type> GetHandlerTypes()
    {
        yield return typeof(OrderHandler);
        yield return typeof(PaymentHandler);
    }
}
```

### Implementation

```csharp
[Generator]
public class HandlerRegistryGenerator : IIncrementalGenerator
{
    public void Initialize(IncrementalGeneratorInitializationContext context)
    {
        context.RegisterPostInitializationOutput(static ctx =>
        {
            ctx.AddSource("RegisterHandlerAttribute.g.cs", """
                namespace Handlers
                {
                    [System.AttributeUsage(System.AttributeTargets.Class)]
                    public sealed class RegisterHandlerAttribute : System.Attribute { }
                }
                """);
        });

        // Collect ALL matching handlers
        var pipeline = context.SyntaxProvider.ForAttributeWithMetadataName(
            "Handlers.RegisterHandlerAttribute",
            predicate: static (node, _) => node is ClassDeclarationSyntax,
            transform: static (ctx, _) => GetHandlerInfo(ctx)
        )
        .Where(static h => h is not null)
        .Collect();  // Batch all handlers together

        // Generate single registry file
        context.RegisterSourceOutput(pipeline, static (spc, handlers) =>
        {
            if (handlers.IsDefaultOrEmpty) return;
            spc.AddSource("HandlerRegistry.g.cs", GenerateRegistry(handlers!));
        });
    }

    private static HandlerInfo? GetHandlerInfo(GeneratorAttributeSyntaxContext ctx)
    {
        if (ctx.TargetSymbol is not INamedTypeSymbol typeSymbol)
            return null;

        return new HandlerInfo(typeSymbol.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat));
    }

    private static string GenerateRegistry(ImmutableArray<HandlerInfo?> handlers)
    {
        var sb = new StringBuilder();

        sb.AppendLine("namespace Handlers");
        sb.AppendLine("{");
        sb.AppendLine("    public static class HandlerRegistry");
        sb.AppendLine("    {");
        sb.AppendLine("        public static System.Collections.Generic.IEnumerable<System.Type> GetHandlerTypes()");
        sb.AppendLine("        {");

        foreach (var handler in handlers)
        {
            if (handler is null) continue;
            sb.AppendLine($"            yield return typeof({handler.Value.FullyQualifiedName});");
        }

        sb.AppendLine("        }");
        sb.AppendLine("    }");
        sb.AppendLine("}");

        return sb.ToString();
    }
}

internal readonly record struct HandlerInfo(string FullyQualifiedName);
```

## Pattern 4: Additional Files Processing

Generate code from non-C# files (JSON, XML, etc.).

### Use Case

`appsettings.schema.json`:
```json
{
  "ConnectionString": "string",
  "MaxRetries": "int",
  "Timeout": "TimeSpan"
}
```

Generator produces:
```csharp
public class AppSettings
{
    public string ConnectionString { get; set; }
    public int MaxRetries { get; set; }
    public TimeSpan Timeout { get; set; }
}
```

### Implementation

```csharp
[Generator]
public class SettingsGenerator : IIncrementalGenerator
{
    public void Initialize(IncrementalGeneratorInitializationContext context)
    {
        var pipeline = context.AdditionalTextsProvider
            .Where(static file => file.Path.EndsWith(".schema.json"))
            .Select(static (file, ct) =>
            {
                var content = file.GetText(ct)?.ToString();
                if (content is null) return null;

                var name = Path.GetFileNameWithoutExtension(
                    Path.GetFileNameWithoutExtension(file.Path)); // Remove .schema.json

                return new SchemaFile(name, content);
            })
            .Where(static f => f is not null);

        context.RegisterSourceOutput(pipeline, static (spc, schema) =>
        {
            if (schema is null) return;
            spc.AddSource($"{schema.Value.Name}.g.cs", GenerateSettings(schema.Value));
        });
    }

    private static string GenerateSettings(SchemaFile schema)
    {
        // Parse JSON and generate class
        // Simplified example - use System.Text.Json in real implementation
        var sb = new StringBuilder();
        sb.AppendLine($"public class {schema.Name}");
        sb.AppendLine("{");
        // Parse schema.Content and generate properties
        sb.AppendLine("}");
        return sb.ToString();
    }
}

internal readonly record struct SchemaFile(string Name, string Content);
```

### Consuming Project Configuration

```xml
<ItemGroup>
  <AdditionalFiles Include="appsettings.schema.json" />
</ItemGroup>
```

## Pattern 5: Method Interception (Partial Method)

Generate method implementations for partial method declarations.

### Use Case

```csharp
public partial class Logger
{
    [LogMethod(Level = "Info")]
    public static partial void LogUserCreated(int userId, string userName);
}
```

Generator produces:
```csharp
partial class Logger
{
    public static partial void LogUserCreated(int userId, string userName)
    {
        if (IsEnabled(LogLevel.Info))
        {
            Log(LogLevel.Info, $"User created: {userId}, {userName}");
        }
    }
}
```

### Implementation

```csharp
[Generator]
public class LogMethodGenerator : IIncrementalGenerator
{
    public void Initialize(IncrementalGeneratorInitializationContext context)
    {
        context.RegisterPostInitializationOutput(static ctx =>
        {
            ctx.AddSource("LogMethodAttribute.g.cs", """
                namespace Logging
                {
                    [System.AttributeUsage(System.AttributeTargets.Method)]
                    public sealed class LogMethodAttribute : System.Attribute
                    {
                        public string Level { get; set; } = "Info";
                    }
                }
                """);
        });

        var pipeline = context.SyntaxProvider.ForAttributeWithMetadataName(
            "Logging.LogMethodAttribute",
            predicate: static (node, _) => node is MethodDeclarationSyntax,
            transform: static (ctx, _) => GetMethodModel(ctx)
        ).Where(static m => m is not null);

        context.RegisterSourceOutput(pipeline, static (spc, model) =>
        {
            if (model is null) return;
            spc.AddSource($"{model.Value.ClassName}.{model.Value.MethodName}.g.cs",
                GenerateLogMethod(model.Value));
        });
    }

    private static LogMethodModel? GetMethodModel(GeneratorAttributeSyntaxContext ctx)
    {
        if (ctx.TargetSymbol is not IMethodSymbol methodSymbol)
            return null;

        var attribute = ctx.Attributes.First();
        var level = attribute.NamedArguments
            .FirstOrDefault(a => a.Key == "Level")
            .Value.Value?.ToString() ?? "Info";

        var parameters = methodSymbol.Parameters
            .Select(p => new ParameterModel(p.Name, p.Type.ToDisplayString()))
            .ToImmutableArray();

        return new LogMethodModel(
            Namespace: methodSymbol.ContainingNamespace.IsGlobalNamespace
                ? null : methodSymbol.ContainingNamespace.ToDisplayString(),
            ClassName: methodSymbol.ContainingType.Name,
            MethodName: methodSymbol.Name,
            Level: level,
            Parameters: new EquatableArray<ParameterModel>(parameters)
        );
    }

    private static string GenerateLogMethod(LogMethodModel model)
    {
        var sb = new StringBuilder();

        if (model.Namespace is not null)
        {
            sb.AppendLine($"namespace {model.Namespace}");
            sb.AppendLine("{");
        }

        sb.AppendLine($"    partial class {model.ClassName}");
        sb.AppendLine("    {");

        // Method signature
        sb.Append($"        public static partial void {model.MethodName}(");
        sb.Append(string.Join(", ", model.Parameters.Select(p => $"{p.Type} {p.Name}")));
        sb.AppendLine(")");
        sb.AppendLine("        {");

        // Implementation
        sb.AppendLine($"            if (IsEnabled(LogLevel.{model.Level}))");
        sb.AppendLine("            {");

        var message = string.Join(", ", model.Parameters.Select(p => $"{{{p.Name}}}"));
        sb.AppendLine($"                Log(LogLevel.{model.Level}, $\"{model.MethodName}: {message}\");");

        sb.AppendLine("            }");
        sb.AppendLine("        }");
        sb.AppendLine("    }");

        if (model.Namespace is not null)
            sb.AppendLine("}");

        return sb.ToString();
    }
}

internal readonly record struct LogMethodModel(
    string? Namespace,
    string ClassName,
    string MethodName,
    string Level,
    EquatableArray<ParameterModel> Parameters
);

internal readonly record struct ParameterModel(string Name, string Type);
```

## EquatableArray Implementation

Required for proper caching with collection properties:

```csharp
using System.Collections;

namespace MyGenerator;

/// <summary>
/// An immutable array with value semantics for source generator caching.
/// </summary>
public readonly struct EquatableArray<T> : IEquatable<EquatableArray<T>>, IEnumerable<T>
    where T : IEquatable<T>
{
    public static readonly EquatableArray<T> Empty = new(Array.Empty<T>());

    private readonly T[]? _array;

    public EquatableArray(T[] array) => _array = array;
    public EquatableArray(ImmutableArray<T> array) => _array = array.IsDefault ? null : array.ToArray();

    public int Length => _array?.Length ?? 0;
    public T this[int index] => _array![index];

    public bool Equals(EquatableArray<T> other)
    {
        if (_array is null && other._array is null) return true;
        if (_array is null || other._array is null) return false;
        return _array.AsSpan().SequenceEqual(other._array.AsSpan());
    }

    public override bool Equals(object? obj) => obj is EquatableArray<T> other && Equals(other);

    public override int GetHashCode()
    {
        if (_array is null) return 0;
        var hash = new HashCode();
        foreach (var item in _array)
            hash.Add(item);
        return hash.ToHashCode();
    }

    public IEnumerator<T> GetEnumerator() => ((IEnumerable<T>)(_array ?? Array.Empty<T>())).GetEnumerator();
    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();

    public static bool operator ==(EquatableArray<T> left, EquatableArray<T> right) => left.Equals(right);
    public static bool operator !=(EquatableArray<T> left, EquatableArray<T> right) => !left.Equals(right);
}
```

## Anti-Patterns to Avoid

### DON'T: Store Symbols in Models

```csharp
// BAD - breaks caching
internal class BadModel
{
    public INamedTypeSymbol Symbol { get; set; }
}

// GOOD - extract what you need as primitives
internal readonly record struct GoodModel(
    string FullyQualifiedName,
    string Name,
    bool IsPublic
);
```

### DON'T: Scan All Types for Interface Implementation

```csharp
// BAD - extremely slow, runs on every keystroke
var allTypes = compilation.GetSymbolsWithName(_ => true, SymbolFilter.Type);
var implementations = allTypes.Where(t => t.AllInterfaces.Any(i => i.Name == "IHandler"));

// GOOD - use attributes instead
[RegisterHandler]
public class MyHandler : IHandler { }
```

### DON'T: Use Semantic Model in Predicate

```csharp
// BAD - predicate should be syntax-only
predicate: (node, ct) => {
    var model = compilation.GetSemanticModel(node.SyntaxTree);
    return model.GetDeclaredSymbol(node)?.GetAttributes().Any() == true;
}

// GOOD - use ForAttributeWithMetadataName instead
context.SyntaxProvider.ForAttributeWithMetadataName(
    "MyAttribute",
    predicate: (node, _) => node is ClassDeclarationSyntax,
    transform: (ctx, _) => /* semantic analysis here */
);
```

### DON'T: Generate SyntaxNodes

```csharp
// BAD - slow and memory-intensive
var classDecl = SyntaxFactory.ClassDeclaration("MyClass")
    .AddModifiers(SyntaxFactory.Token(SyntaxKind.PublicKeyword))
    .NormalizeWhitespace(); // This is expensive!

// GOOD - use string building
var code = $"public class MyClass {{ }}";
```
