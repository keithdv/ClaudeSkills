# Project Setup for MarkdownSnippets

How to set up MarkdownSnippets in a new project.

## Prerequisites

- .NET SDK installed
- Project with documentation in `docs/` or `README.md`

## Step 1: Install MarkdownSnippets

```powershell
# Create tool manifest (if not exists)
dotnet new tool-manifest

# Install the tool
dotnet tool install MarkdownSnippets.Tool

# Verify
dotnet mdsnippets --help
```

## Step 2: Create Configuration

Create `mdsnippets.json` in project root:

```json
{
  "Convention": "InPlaceOverwrite",
  "LinkFormat": "GitHub",
  "OmitSnippetLinks": true,
  "ExcludeDirectories": ["node_modules", "bin", "obj", ".git"]
}
```

**Configuration options:**

| Setting | Value | Purpose |
|---------|-------|---------|
| `Convention` | `InPlaceOverwrite` | Modifies `.md` files directly |
| `LinkFormat` | `GitHub` | GitHub-compatible source links |
| `OmitSnippetLinks` | `true` | Cleaner output (no source links) |
| `ExcludeDirectories` | array | Directories to skip |

## Step 3: Create Samples Project

```powershell
mkdir docs/samples
cd docs/samples

# Create library project
dotnet new classlib -n {Project}.Samples

# Create test project
dotnet new xunit -n {Project}.Samples.Tests
cd {Project}.Samples.Tests
dotnet add reference ../{Project}.Samples/{Project}.Samples.csproj
```

## Step 4: Add First Snippet

In `docs/samples/{Project}.Samples/Example.cs`:

```csharp
#region hello-world
public class HelloWorld
{
    public string Greet() => "Hello, World!";
}
#endregion
```

In `docs/getting-started.md`:

```markdown
# Getting Started

snippet: hello-world
```

Run:

```powershell
dotnet mdsnippets
```

The markdown now contains the compiled code.

## Step 5: Create Verification Script

Create `scripts/verify-code-blocks.ps1` (see [verification.md](verification.md)).

## Recommended Project Structure

```
{Project}/
├── README.md
├── docs/
│   ├── *.md
│   └── samples/
│       ├── {Project}.Samples/
│       │   └── *.cs (with #region markers)
│       └── {Project}.Samples.Tests/
├── scripts/
│   └── verify-code-blocks.ps1
├── mdsnippets.json
└── .config/
    └── dotnet-tools.json
```

## Sample Project Configuration

`{Project}.Samples.csproj`:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\..\..\src\{Project}\{Project}.csproj" />
  </ItemGroup>
</Project>
```

## File Header Convention

Include a header listing snippets for discoverability:

```csharp
/// <summary>
/// Code samples for documentation.
///
/// Snippets in this file:
/// - hello-world
/// - validation-example
/// </summary>
```
