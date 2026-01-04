# Project Setup for Source Generators

## Generator Project Configuration

### Complete .csproj File

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <!-- MUST target netstandard2.0 for maximum compiler compatibility -->
    <TargetFramework>netstandard2.0</TargetFramework>

    <!-- Prevents the DLL from being referenced directly - it's an analyzer -->
    <IncludeBuildOutput>false</IncludeBuildOutput>

    <!-- Enable nullable reference types and latest C# features -->
    <Nullable>enable</Nullable>
    <LangVersion>Latest</LangVersion>
    <ImplicitUsings>enable</ImplicitUsings>

    <!-- Required for .NET 6+ SDK - enforces analyzer rules -->
    <EnforceExtendedAnalyzerRules>true</EnforceExtendedAnalyzerRules>

    <!-- Standard assembly info -->
    <RootNamespace>MyCompany.Generators</RootNamespace>
    <AssemblyName>MyCompany.Generators</AssemblyName>
  </PropertyGroup>

  <!-- Core Roslyn dependencies -->
  <ItemGroup>
    <!-- Provides IIncrementalGenerator, ISymbol, SemanticModel, etc. -->
    <PackageReference Include="Microsoft.CodeAnalysis.CSharp" Version="4.3.0" PrivateAssets="all" />

    <!-- Required analyzer for generator development -->
    <PackageReference Include="Microsoft.CodeAnalysis.Analyzers" Version="3.3.4" PrivateAssets="all" />
  </ItemGroup>

  <!-- Package the generator DLL in the analyzers folder -->
  <ItemGroup>
    <None Include="$(OutputPath)\$(AssemblyName).dll"
          Pack="true"
          PackagePath="analyzers/dotnet/cs"
          Visible="false" />
  </ItemGroup>

</Project>
```

### Key Properties Explained

| Property | Value | Purpose |
|----------|-------|---------|
| `TargetFramework` | `netstandard2.0` | Required for compiler compatibility across all .NET versions |
| `IncludeBuildOutput` | `false` | Prevents direct assembly reference - forces analyzer reference |
| `EnforceExtendedAnalyzerRules` | `true` | Enables analyzer-specific compiler diagnostics |
| `PrivateAssets="all"` | On PackageReferences | Prevents transitive dependency exposure |

### Minimum Package Versions

| Package | Minimum Version | Notes |
|---------|-----------------|-------|
| Microsoft.CodeAnalysis.CSharp | 4.0.0 | `ForAttributeWithMetadataName` requires 4.3.0+ |
| Microsoft.CodeAnalysis.Analyzers | 3.3.0 | Development-time analyzer support |

### For .NET 8+ Projects with LangVersion 12

If your **consuming** projects use C# 12 features, ensure your generator handles them:

```xml
<PackageReference Include="Microsoft.CodeAnalysis.CSharp" Version="4.8.0" PrivateAssets="all" />
```

## Consuming Project Configuration

### Project Reference (Same Solution)

```xml
<ItemGroup>
  <ProjectReference Include="..\MyCompany.Generators\MyCompany.Generators.csproj"
                    OutputItemType="Analyzer"
                    ReferenceOutputAssembly="false" />
</ItemGroup>
```

### NuGet Package Reference

```xml
<ItemGroup>
  <PackageReference Include="MyCompany.Generators" Version="1.0.0" />
</ItemGroup>
```

### Viewing Generated Files

Add to consuming project's .csproj to emit generated files to disk:

```xml
<PropertyGroup>
  <!-- Writes generated files to obj/Generated -->
  <EmitCompilerGeneratedFiles>true</EmitCompilerGeneratedFiles>

  <!-- Optional: Custom output path -->
  <CompilerGeneratedFilesOutputPath>$(BaseIntermediateOutputPath)Generated</CompilerGeneratedFilesOutputPath>
</PropertyGroup>
```

Generated files appear at:
```
obj/Debug/net8.0/Generated/MyCompany.Generators/MyCompany.Generators.MyGenerator/
```

## Multi-Project Generator Structure

For complex generators, split into multiple projects:

```
MyCompany.Generators/
├── MyCompany.Generators/              # Main generator
│   ├── MyCompany.Generators.csproj
│   ├── MyGenerator.cs
│   └── Models/
│       └── ClassModel.cs
│
├── MyCompany.Generators.Attributes/   # Runtime attributes (if needed)
│   ├── MyCompany.Generators.Attributes.csproj
│   └── GenerateAttribute.cs
│
└── MyCompany.Generators.Tests/        # Unit tests
    ├── MyCompany.Generators.Tests.csproj
    └── GeneratorTests.cs
```

### Separate Attributes Package (Optional)

If consumers need runtime access to attributes:

```xml
<!-- MyCompany.Generators.Attributes.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>netstandard2.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
```

```csharp
// GenerateAttribute.cs
namespace MyCompany.Generators
{
    [AttributeUsage(AttributeTargets.Class)]
    public sealed class GenerateAttribute : Attribute { }
}
```

Main generator references the attributes:

```xml
<!-- MyCompany.Generators.csproj -->
<ItemGroup>
  <ProjectReference Include="..\MyCompany.Generators.Attributes\MyCompany.Generators.Attributes.csproj"
                    PrivateAssets="all" />
</ItemGroup>

<!-- Include both DLLs in package -->
<ItemGroup>
  <None Include="$(OutputPath)\$(AssemblyName).dll"
        Pack="true" PackagePath="analyzers/dotnet/cs" Visible="false" />
  <None Include="$(OutputPath)\MyCompany.Generators.Attributes.dll"
        Pack="true" PackagePath="lib/netstandard2.0" Visible="false" />
</ItemGroup>
```

## NuGet Package Configuration

### Full Package Setup

```xml
<PropertyGroup>
  <!-- Package metadata -->
  <PackageId>MyCompany.Generators</PackageId>
  <Version>1.0.0</Version>
  <Authors>Your Name</Authors>
  <Description>Source generator for automatic code generation</Description>

  <!-- Package settings -->
  <GeneratePackageOnBuild>true</GeneratePackageOnBuild>
  <IncludeSymbols>true</IncludeSymbols>
  <SymbolPackageFormat>snupkg</SymbolPackageFormat>

  <!-- Prevent direct library reference -->
  <IncludeBuildOutput>false</IncludeBuildOutput>
  <DevelopmentDependency>true</DevelopmentDependency>

  <!-- Suppress NU5128 warning about no lib folder -->
  <NoWarn>$(NoWarn);NU5128</NoWarn>
</PropertyGroup>
```

### Package Structure

The resulting .nupkg should contain:

```
MyCompany.Generators.1.0.0.nupkg
├── analyzers/
│   └── dotnet/
│       └── cs/
│           └── MyCompany.Generators.dll
├── lib/
│   └── netstandard2.0/
│       └── MyCompany.Generators.Attributes.dll  (if separate)
└── MyCompany.Generators.nuspec
```

## Debugging Setup

### Enable Source Generator Debugging

Add to generator project:

```xml
<PropertyGroup>
  <IsRoslynComponent>true</IsRoslynComponent>
</PropertyGroup>
```

### Attach Debugger Programmatically

```csharp
[Generator]
public class MyGenerator : IIncrementalGenerator
{
    public void Initialize(IncrementalGeneratorInitializationContext context)
    {
#if DEBUG
        if (!System.Diagnostics.Debugger.IsAttached)
        {
            System.Diagnostics.Debugger.Launch();
        }
#endif
        // ... rest of initialization
    }
}
```

### Visual Studio Debugging

1. Set generator project as startup project
2. Go to Project Properties > Debug
3. Select "Roslyn Component" launch profile
4. Set consuming project as the "Target Project"
5. F5 to debug

### Logging During Development

```csharp
context.RegisterSourceOutput(pipeline, (spc, model) =>
{
    // Add diagnostic for debugging
    spc.ReportDiagnostic(Diagnostic.Create(
        new DiagnosticDescriptor(
            "GEN001",
            "Generator Debug",
            $"Processing: {model.ClassName}",
            "Debug",
            DiagnosticSeverity.Warning,
            isEnabledByDefault: true),
        Location.None));

    // Generate actual code...
});
```

## Directory.Build.props for Solution-Wide Settings

Place at solution root:

```xml
<!-- Directory.Build.props -->
<Project>
  <PropertyGroup>
    <LangVersion>Latest</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
</Project>
```

## IDE Support

### Visual Studio

- Generated files visible under Dependencies > Analyzers > [Generator Name]
- Ctrl+Click on generated members navigates to generated source
- IntelliSense works for generated code after build

### Rider

- Generated files under Dependencies > Source Generators
- May require "Reload Project" after generator changes

### VS Code + OmniSharp

- Requires `omnisharp.enableRoslynAnalyzers: true` in settings
- Generated files in obj/Generated after build
