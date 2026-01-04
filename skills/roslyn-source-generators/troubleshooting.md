# Troubleshooting Source Generators

## Common Issues

### Generator Not Running

**Symptoms:**
- No generated files appear
- Generated code not available in IDE
- Build succeeds but generated methods not found

**Solutions:**

1. **Check [Generator] attribute**
   ```csharp
   [Generator]  // Must be present
   public class MyGenerator : IIncrementalGenerator
   ```

2. **Verify project references**
   ```xml
   <!-- Must have OutputItemType="Analyzer" -->
   <ProjectReference Include="..\MyGenerator\MyGenerator.csproj"
                     OutputItemType="Analyzer"
                     ReferenceOutputAssembly="false" />
   ```

3. **Check target framework**
   ```xml
   <!-- Generator MUST target netstandard2.0 -->
   <TargetFramework>netstandard2.0</TargetFramework>
   ```

4. **Clean and rebuild**
   ```bash
   dotnet clean
   dotnet build
   ```

5. **Restart IDE** - Sometimes required after generator changes

---

### Generated Files Not Visible in IDE

**Enable output to disk:**
```xml
<PropertyGroup>
  <EmitCompilerGeneratedFiles>true</EmitCompilerGeneratedFiles>
  <CompilerGeneratedFilesOutputPath>$(BaseIntermediateOutputPath)Generated</CompilerGeneratedFilesOutputPath>
</PropertyGroup>
```

**Check location:**
- Visual Studio: Dependencies > Analyzers > [Generator Name]
- Rider: Dependencies > Source Generators
- On disk: `obj/Debug/net8.0/Generated/`

---

### ForAttributeWithMetadataName Not Finding Types

**Common causes:**

1. **Wrong metadata name format**
   ```csharp
   // WRONG - missing namespace
   "MyAttribute"

   // WRONG - includes Attribute suffix incorrectly
   "MyNamespace.MyAttributeAttribute"

   // CORRECT - full metadata name without 'Attribute' suffix
   "MyNamespace.MyAttribute"

   // CORRECT - if the class is actually named MyAttributeAttribute
   "MyNamespace.MyAttributeAttribute"
   ```

2. **Attribute not registered yet**
   ```csharp
   // Ensure attribute is added via RegisterPostInitializationOutput
   context.RegisterPostInitializationOutput(static ctx =>
   {
       ctx.AddSource("MyAttribute.g.cs", attributeSource);
   });

   // Then use ForAttributeWithMetadataName
   var pipeline = context.SyntaxProvider.ForAttributeWithMetadataName(...);
   ```

3. **Wrong predicate**
   ```csharp
   // Make sure predicate matches the syntax node type
   predicate: static (node, _) => node is ClassDeclarationSyntax  // For classes
   predicate: static (node, _) => node is MethodDeclarationSyntax  // For methods
   ```

---

### IDE Performance Issues

**Symptoms:**
- Typing lag
- IDE freezing
- High CPU usage

**Causes and fixes:**

1. **Using old ISourceGenerator**
   ```csharp
   // DEPRECATED - causes performance issues
   public class MyGenerator : ISourceGenerator

   // CORRECT - use incremental
   public class MyGenerator : IIncrementalGenerator
   ```

2. **Storing ISymbol in models**
   ```csharp
   // BAD - breaks caching, causes re-runs
   record Model(INamedTypeSymbol Symbol);

   // GOOD - extract primitives
   record Model(string Name, string Namespace);
   ```

3. **Semantic analysis in predicate**
   ```csharp
   // BAD - runs on every syntax node
   predicate: (node, _) => {
       var model = compilation.GetSemanticModel(node.SyntaxTree);
       // ...
   }

   // GOOD - syntax-only in predicate
   predicate: (node, _) => node is ClassDeclarationSyntax { AttributeLists.Count: > 0 }
   ```

4. **Not using ForAttributeWithMetadataName**
   ```csharp
   // SLOW - scans all syntax
   context.SyntaxProvider.CreateSyntaxProvider(...)

   // FAST - uses compiler's attribute tracking
   context.SyntaxProvider.ForAttributeWithMetadataName(...)
   ```

---

### Compilation Errors in Generated Code

**Debugging steps:**

1. **View generated source**
   ```xml
   <EmitCompilerGeneratedFiles>true</EmitCompilerGeneratedFiles>
   ```
   Then check `obj/Generated/` folder

2. **Add diagnostic output**
   ```csharp
   context.RegisterSourceOutput(pipeline, (spc, model) =>
   {
       // Debug diagnostic
       spc.ReportDiagnostic(Diagnostic.Create(
           new DiagnosticDescriptor("GEN_DEBUG", "Debug", $"Model: {model}", "Debug", DiagnosticSeverity.Warning, true),
           Location.None));

       // Generate code...
   });
   ```

3. **Common generation errors:**

   **Missing namespace imports**
   ```csharp
   // Always include necessary usings
   var code = """
       using System;
       using System.Collections.Generic;

       namespace MyNamespace { ... }
       """;
   ```

   **Unescaped special characters**
   ```csharp
   // In interpolated strings, escape braces
   $"Value: {{{value}}}"  // Outputs: Value: {actualValue}
   ```

   **Partial class mismatch**
   ```csharp
   // Generated code must match original declaration
   // If original is: public partial class Foo
   // Generated must be: public partial class Foo (not internal, not without partial)
   ```

---

### Caching Not Working

**Symptoms:**
- Generator runs on every keystroke
- High CPU during editing
- Slow IDE response

**Diagnostic:**
```csharp
// Track run count (development only)
private static int _runCount = 0;

context.RegisterSourceOutput(pipeline, (spc, model) =>
{
    _runCount++;
    spc.ReportDiagnostic(Diagnostic.Create(
        new DiagnosticDescriptor("CACHE", "Cache", $"Run #{_runCount}", "Debug", DiagnosticSeverity.Warning, true),
        Location.None));
    // ...
});
```

**Common causes:**

1. **Non-equatable models**
   ```csharp
   // BAD - class doesn't have value equality
   class Model { public string Name; }

   // GOOD - record has automatic value equality
   record struct Model(string Name);
   ```

2. **Collections without proper equality**
   ```csharp
   // BAD - arrays don't have value equality
   record Model(string[] Items);

   // GOOD - use EquatableArray
   record Model(EquatableArray<string> Items);
   ```

3. **Including Location in model**
   ```csharp
   // BAD - location changes on any edit
   record Model(string Name, Location Location);

   // GOOD - only include location when reporting diagnostics
   record Model(string Name);
   ```

---

### NuGet Package Issues

**Package not recognized as analyzer:**

```xml
<!-- Ensure proper packaging -->
<ItemGroup>
  <None Include="$(OutputPath)\$(AssemblyName).dll"
        Pack="true"
        PackagePath="analyzers/dotnet/cs"
        Visible="false" />
</ItemGroup>
```

**Dependencies exposed to consumers:**

```xml
<!-- Use PrivateAssets on all dependencies -->
<PackageReference Include="Microsoft.CodeAnalysis.CSharp"
                  Version="4.3.0"
                  PrivateAssets="all" />
```

**Missing runtime types:**

If your generator needs types at runtime (not just compile time), add a separate lib folder:

```xml
<ItemGroup>
  <!-- Generator DLL -->
  <None Include="$(OutputPath)\$(AssemblyName).dll"
        Pack="true" PackagePath="analyzers/dotnet/cs" Visible="false" />

  <!-- Runtime types DLL -->
  <None Include="$(OutputPath)\$(AssemblyName).Attributes.dll"
        Pack="true" PackagePath="lib/netstandard2.0" Visible="false" />
</ItemGroup>
```

---

### Debugging Generators

**Method 1: Debugger.Launch()**
```csharp
public void Initialize(IncrementalGeneratorInitializationContext context)
{
#if DEBUG
    if (!System.Diagnostics.Debugger.IsAttached)
    {
        System.Diagnostics.Debugger.Launch();
    }
#endif
    // ...
}
```

**Method 2: Visual Studio Roslyn Component Debugging**

1. Set generator project as startup
2. Project Properties > Debug > Launch Profile > Roslyn Component
3. Set target project
4. F5 to debug

**Method 3: Log to file**
```csharp
private static void Log(string message)
{
#if DEBUG
    File.AppendAllText(@"C:\Temp\generator.log", $"{DateTime.Now}: {message}\n");
#endif
}
```

---

### Generator Version Conflicts

**Symptom:** Build errors about missing types or methods in Microsoft.CodeAnalysis

**Solution:** Align versions across solution

```xml
<!-- In Directory.Packages.props -->
<ItemGroup>
  <PackageVersion Include="Microsoft.CodeAnalysis.CSharp" Version="4.8.0" />
  <PackageVersion Include="Microsoft.CodeAnalysis.Analyzers" Version="3.3.4" />
</ItemGroup>
```

---

### RegisterPostInitializationOutput Issues

**Attribute not found by consuming code:**

The attribute must be generated before the compilation sees user code. Use raw string with full namespace:

```csharp
context.RegisterPostInitializationOutput(static ctx =>
{
    ctx.AddSource("GenerateAttribute.g.cs", """
        // <auto-generated/>
        #nullable enable

        namespace MyGenerator
        {
            /// <summary>
            /// Marks a class for code generation.
            /// </summary>
            [global::System.AttributeUsage(global::System.AttributeTargets.Class, Inherited = false)]
            [global::System.Diagnostics.CodeAnalysis.ExcludeFromCodeCoverage]
            internal sealed class GenerateAttribute : global::System.Attribute
            {
            }
        }
        """);
});
```

---

## Error Reference

| Error | Cause | Solution |
|-------|-------|----------|
| CS0246: Type or namespace not found | Generated code not available | Rebuild, check generator runs |
| CS0111: Member already defined | Duplicate generation | Check for multiple generators or duplicate Add Source calls |
| RS1035: Symbol equality | Comparing symbols with == | Use SymbolEqualityComparer.Default |
| RS1036: Nullable value types | Nullable issues in generator | Enable nullable and fix warnings |

## Diagnostic IDs for Generators

Reserve a unique prefix for your diagnostics:

```csharp
// Convention: PROJECT + NUMBER
// Example: MYPROJ001, MYPROJ002, etc.

private static readonly DiagnosticDescriptor NotPartialError = new(
    id: "MYPROJ001",
    title: "Type must be partial",
    messageFormat: "The type '{0}' must be declared as partial",
    category: "MyProjectGenerator",
    defaultSeverity: DiagnosticSeverity.Error,
    isEnabledByDefault: true);
```

## Getting Help

1. **Enable verbose MSBuild output**
   ```bash
   dotnet build -v detailed > build.log
   ```

2. **Check Roslyn GitHub issues**
   https://github.com/dotnet/roslyn/issues

3. **Source Generator samples**
   https://github.com/dotnet/roslyn-sdk/tree/main/samples/CSharp/SourceGenerators
