# 01 - Snippet Regions

How to mark code in source files for extraction into documentation using MarkdownSnippets.

---

## Code Block Categories

Documentation contains different types of code:

| Term | Marker | Description |
|------|--------|-------------|
| **Inline code** | None | Mid-sentence backticks like `EntityBase<T>` |
| **Compiled snippet** | `snippet: {id}` | Working code extracted from samples via MarkdownSnippets |
| **Pseudo-code** | `pseudo:{id}` | Illustrative code, not compiled |
| **Invalid example** | `invalid:{id}` | Intentionally wrong code (anti-patterns) |

**Inline code** names things within sentences - class names, method names, property names. These are not tracked.

**All fenced C# code blocks must have a snippet marker.** This ensures every code example has been consciously evaluated.

---

## Compiled Snippets

### Defining in C# Files

Use `#region` with a unique name:

```csharp
#region age-validation-rule
public class AgeValidationRule : RuleBase<IPerson>
{
    public AgeValidationRule() : base(p => p.Age) { }

    protected override IRuleMessages Execute(IPerson target)
    {
        if (target.Age < 0)
            return (nameof(target.Age), "Age cannot be negative").AsRuleMessages();
        return None;
    }
}
#endregion
```

**Alternative syntax** (also supported):
```csharp
// begin-snippet: age-validation-rule
public class AgeValidationRule : RuleBase<IPerson>
{
    // ...
}
// end-snippet
```

### Referencing in Markdown

Simply add a line with `snippet: {id}`:

```markdown
## Age Validation

snippet: age-validation-rule

The rule validates that age is not negative.
```

### What MarkdownSnippets Generates

After running `dotnet mdsnippets`, the markdown becomes:

```markdown
## Age Validation

<!-- snippet: age-validation-rule -->
<a id='snippet-age-validation-rule'></a>
```csharp
public class AgeValidationRule : RuleBase<IPerson>
{
    public AgeValidationRule() : base(p => p.Age) { }

    protected override IRuleMessages Execute(IPerson target)
    {
        if (target.Age < 0)
            return (nameof(target.Age), "Age cannot be negative").AsRuleMessages();
        return None;
    }
}
```
<sup><a href='/docs/samples/Rules/AgeValidationRule.cs#L5-L16' title='Snippet source file'>snippet source</a> | <a href='#snippet-age-validation-rule' title='Start of snippet'>anchor</a></sup>
<!-- endSnippet -->

The rule validates that age is not negative.
```

---

## Pseudo-code (`pseudo:`)

Illustrative code that shows conceptual patterns but isn't compiled:
- **API signatures** - Interface definitions, method signatures
- **Hypothetical examples** - Features that don't exist yet
- **Partial fragments** - Incomplete code highlighting a concept (e.g., just a property name)

```markdown
<!-- pseudo:waitfortasks-signature -->
```csharp
Task WaitForTasks(CancellationToken? token = null);
```
<!-- /snippet -->
```

**Note:** MarkdownSnippets ignores `pseudo:` markers - they're just HTML comments. Your `verify-code-blocks.ps1` script checks these.

---

## Invalid Examples (`invalid:`)

Intentionally wrong code showing what NOT to do:
- **Anti-patterns** - WRONG/CORRECT comparisons
- **Common mistakes** - Code that compiles but is incorrect
- **Breaking changes** - Old patterns that no longer work

```markdown
<!-- snippet: invalid:wrong-save-pattern -->
```csharp
// WRONG - discards the updated entity
await personFactory.Save(person);

// CORRECT
person = await personFactory.Save(person);
```
<!-- /snippet -->
```

**Tip:** If both wrong and correct code can compile, put them in the same compiled snippet:

```csharp
#region save-pattern-comparison
// WRONG - discards the updated entity
await personFactory.Save(person);

// CORRECT - captures the new instance
person = await personFactory.Save(person);
#endregion
```

This way MarkdownSnippets keeps both in sync with API changes.

---

## Why Every Block Needs a Marker

Without markers, there's no way to verify that a code block was intentionally left uncompiled vs. accidentally forgotten. The verification script ensures:
- Every `snippet: {id}` has a matching `#region {id}` in code
- Every `<!-- snippet: pseudo:{id} -->` has a matching `<!-- /snippet -->`
- Every `<!-- snippet: invalid:{id} -->` has a matching `<!-- /snippet -->`
- No unmarked C# code blocks exist

---

## Region Naming Convention

Snippet IDs must be **globally unique** across the entire project.

### Good Names

```csharp
#region person-entity
#region age-validation-rule
#region factory-create-pattern
#region server-di-setup
#region blazor-form-binding
```

### Naming Strategies

| Strategy | Example |
|----------|---------|
| Feature + concept | `validation-age-rule` |
| Entity + operation | `person-create-factory` |
| Context + pattern | `server-di-setup` |

### Avoid

```csharp
// BAD - too generic, likely to collide
#region example
#region usage
#region pattern

// GOOD - specific and unique
#region validation-rule-example
#region factory-usage
#region save-pattern
```

---

## Project Structure

Documentation and skills live in the repository, both pulling from the same samples:

```
{Project}/
├── README.md                                   # Main docs (mdsnippets-processed)
├── src/
│   └── {Project}/                              # Main library
│
├── .claude/
│   └── skills/
│       └── {skill}/                            # Local skill (versioned with code)
│           ├── SKILL.md                        # mdsnippets-processed
│           └── *.md
│
├── docs/
│   ├── *.md                                    # Documentation (mdsnippets-processed)
│   ├── release-notes/                          # Version release notes
│   │
│   ├── todos/                                  # Active markdown plans
│   │   └── completed/                          # Completed plans
│   │
│   └── samples/                                # Single source for BOTH docs AND skills
│       ├── {Project}.Samples.DomainModel/      # Domain with #region snippets
│       │   ├── Entities/
│       │   │   ├── IPerson.cs
│       │   │   └── Person.cs
│       │   ├── Rules/
│       │   │   └── AgeValidationRule.cs
│       │   └── ...
│       ├── {Project}.Samples.DomainModel.Tests/# Tests (proves snippets work)
│       ├── {Project}.Samples.BlazorClient/     # Program.cs client snippets
│       ├── {Project}.Samples.Server/           # Program.cs server snippets
│       └── {Project}.Samples.Ef/               # EF Core (optional)
│
├── scripts/
│   └── verify-code-blocks.ps1                  # Verifies pseudo/invalid markers
│
├── mdsnippets.json                             # MarkdownSnippets config
└── .config/
    └── dotnet-tools.json                       # Tool manifest

~/.claude/skills/{skill}/                       # Shared copy (for use outside repo)
```

**Key insight:** The domain model IS the snippets. Entities, rules, and factories contain `#region` markers - no separate snippet library needed. Both docs and skills use the same `snippet: {id}` syntax.

---

## Infrastructure Snippets (Program.cs)

Infrastructure code lives in runnable projects. Use regions to mark the Neatoo-specific parts:

### Server Program.cs

```csharp
// In docs/samples/{Project}.Samples.Server/Program.cs

var builder = WebApplication.CreateBuilder(args);

#region server-di-setup
// Neatoo server setup
builder.Services.AddNeatooServices(NeatooFactory.Server, typeof(IPerson).Assembly);
#endregion

// App-specific services...
builder.Services.AddScoped<IPersonDbContext, PersonDbContext>();

var app = builder.Build();

#region server-endpoint
// Neatoo endpoint with cancellation support
app.MapPost("/api/neatoo", (HttpContext ctx, RemoteRequestDto request, CancellationToken ct) =>
{
    var handler = ctx.RequestServices.GetRequiredService<HandleRemoteDelegateRequest>();
    return handler(request, ct);
});
#endregion

await app.RunAsync();
```

### Blazor Client Program.cs

```csharp
// In docs/samples/{Project}.Samples.BlazorClient/Program.cs

var builder = WebAssemblyHostBuilder.CreateDefault(args);

#region client-di-setup
// Neatoo client setup
builder.Services.AddNeatooServices(NeatooFactory.Remote, typeof(IPerson).Assembly);
builder.Services.AddKeyedScoped(RemoteFactoryServices.HttpClientKey, (sp, key) =>
    new HttpClient { BaseAddress = new Uri("http://localhost:5183/") });
#endregion

await builder.Build().RunAsync();
```

---

## Nested Regions (Micro-Snippets)

For large examples, use nested regions to extract focused parts:

```csharp
[Factory]
internal partial class OrderSamples : EntityBase<OrderSamples>
{
    // Full class context for compilation...

    #region state-tracking-properties
    public partial string? Status { get; set; }     // IsModified tracked
    public partial decimal Total { get; set; }      // IsSavable updated
    #endregion

    #region inline-validation
    RuleManager.AddValidation(
        t => t.Total <= 0 ? "Total must be positive" : "",
        t => t.Total);
    #endregion
}
```

Documentation can reference either the full class OR the micro-snippets independently.

---

## File Header Convention

Include a header listing all snippets for discoverability:

```csharp
/// <summary>
/// Code samples for validation documentation.
///
/// Snippets in this file:
/// - required-attribute
/// - age-validation-rule
/// - async-database-rule
///
/// Corresponding tests: RuleBaseSamplesTests.cs
/// </summary>

namespace Neatoo.Samples.DomainModel.Rules;
```

---

## Snippet Size Guidelines

| Lines | Status | Recommendation |
|-------|--------|----------------|
| 1-15 | Good | Focused, easy to understand |
| 16-30 | Acceptable | Consider splitting if possible |
| 30+ | Too large | Use nested micro-snippets |

---

## Testing Snippets

Every snippet should have corresponding test coverage:

```csharp
// In Tests/ValidationAndRules/RuleBaseSamplesTests.cs

public class RuleBaseSamplesTests : SamplesTestBase
{
    [Fact]
    public async Task AgeValidationRule_NegativeAge_ReturnsError()
    {
        // Test that the documented rule actually works
        var person = CreatePerson();
        person.Age = -5;

        await person.WaitForTasks();

        Assert.False(person.IsValid);
        Assert.Contains("Age cannot be negative", person.PropertyMessages);
    }
}
```

**Benefits:**
- Proves the documented code actually works
- Catches API changes that break examples
- Documents expected behavior

---

## Common Mistakes

### Missing #endregion

```csharp
// BAD - MarkdownSnippets will fail
#region example-snippet
// code
// forgot #endregion
```

### Duplicate IDs

```csharp
// BAD - same ID in two files causes unpredictable behavior
// File1.cs: #region save-pattern
// File2.cs: #region save-pattern

// GOOD - unique IDs
// File1.cs: #region person-save-pattern
// File2.cs: #region order-save-pattern
```

### Generic Region Names

```csharp
// BAD - collides with standard VS regions
#region Properties
#region Methods

// GOOD - specific snippet names
#region person-properties
#region factory-methods
```

---

## Setting Up From Scratch

If your repository doesn't have a `docs/samples/` structure yet, follow these steps:

### Step 1: Create Folder Structure

```powershell
# From your project root
mkdir docs
mkdir docs/samples
```

### Step 2: Create Sample Projects

```powershell
cd docs/samples

# Domain model project (where snippets live)
dotnet new classlib -n {Project}.Samples.DomainModel
cd {Project}.Samples.DomainModel

# Add reference to your main library
dotnet add reference ../../../src/{Project}/{Project}.csproj
cd ..

# Test project
dotnet new xunit -n {Project}.Samples.DomainModel.Tests
cd {Project}.Samples.DomainModel.Tests
dotnet add reference ../{Project}.Samples.DomainModel/{Project}.Samples.DomainModel.csproj
cd ../..
```

### Step 3: Install MarkdownSnippets

```powershell
# From project root
dotnet new tool-manifest  # if .config/dotnet-tools.json doesn't exist
dotnet tool install MarkdownSnippets.Tool
```

### Step 4: Create Configuration

Create `mdsnippets.json` in project root:

```json
{
  "Convention": "InPlaceOverwrite",
  "LinkFormat": "GitHub",
  "OmitSnippetLinks": true,
  "ExcludeDirectories": ["node_modules", "bin", "obj", ".git"]
}
```

### Step 5: Add Your First Snippet

1. Create a class in `docs/samples/{Project}.Samples.DomainModel/`:

```csharp
#region hello-world
public class HelloWorld
{
    public string Greet() => "Hello, World!";
}
#endregion
```

2. Create a markdown file in `docs/`:

```markdown
# Getting Started

snippet: hello-world
```

3. Run MarkdownSnippets:

```powershell
dotnet mdsnippets
```

4. Check the result - your markdown now contains the code.

---

## Sample Project Setup

These are the recommended project file configurations:

### Domain Model Project (Contains Snippets)

```xml
<!-- docs/samples/{Project}.Samples.DomainModel/{Project}.Samples.DomainModel.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <!-- Reference the main library -->
    <ProjectReference Include="..\..\..\src\{Project}\{Project}.csproj" />
  </ItemGroup>
</Project>
```

### Test Project

```xml
<!-- docs/samples/{Project}.Samples.DomainModel.Tests/{Project}.Samples.DomainModel.Tests.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <IsTestProject>true</IsTestProject>
  </PropertyGroup>

  <ItemGroup>
    <ProjectReference Include="..\{Project}.Samples.DomainModel\{Project}.Samples.DomainModel.csproj" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.*" />
    <PackageReference Include="xunit" Version="2.*" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.*" />
  </ItemGroup>
</Project>
```
