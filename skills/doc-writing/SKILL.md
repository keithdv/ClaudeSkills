---
name: doc-writing
description: This skill should be used when "writing documentation", "creating README", "documenting code", "explaining features", "writing technical docs", "improving docs clarity", "adding doc comments", or asking how to document something. Provides guidance for clear, effective technical documentation.
---

# Technical Documentation Writing

Effective documentation helps users accomplish their goals. This skill provides guidance for writing clear, useful technical documentation.

## Core Principle

**Write for the reader, not the writer.** Documentation exists to help someone accomplish a task, not to show what you built.

## Documentation Types

| Type | Purpose | Structure |
|------|---------|-----------|
| **README** | First impression, quick start | What → Why → How to start |
| **Getting Started** | First successful use | Prerequisites → Install → First example |
| **Tutorials** | Learning by doing | Step-by-step with explanations |
| **How-To Guides** | Solve specific problems | Problem → Solution → Variations |
| **Reference** | Complete API coverage | Organized by feature/namespace |
| **Concepts** | Deep understanding | Explain the "why" and architecture |

## Writing Principles

### Show, Don't Tell

**Weak:** "The validation system is flexible and powerful."

**Strong:**
```csharp
// Validate age with a custom rule
RuleManager.AddValidation(
    t => t.Age < 0 ? "Age cannot be negative" : "",
    t => t.Age);
```

### Progressive Disclosure

Lead with the common case, then expand:

1. **Quick example** - Copy-paste and it works
2. **Explanation** - What it does and why
3. **Options** - Variations and configuration
4. **Edge cases** - Special situations

### Examples First

Don't explain, then show. Show, then explain:

```markdown
## Email Validation

```csharp
if (!email.Contains("@"))
    return "Invalid email format";
```

The validator checks for the @ symbol. For more complex validation,
see [Advanced Patterns](advanced.md).
```

### Scannable Structure

Readers scan before reading. Help them find what they need:

- **Headers** - Clear, specific (not "Overview" or "Introduction")
- **Code blocks** - Break up text, provide examples
- **Tables** - Compare options, list parameters
- **Lists** - Steps, options, requirements

## Structure Patterns

### What/Why/How

For feature documentation:

```markdown
## Validation Rules

**What:** Custom rules that validate entity properties.

**Why:** Built-in attributes handle simple cases. Rules handle:
- Cross-property validation
- Async validation (database checks)
- Complex business logic

**How:**
```csharp
// Example code
```
```

### Problem/Solution

For how-to guides:

```markdown
## Validating Related Entities

**Problem:** Need to validate that a parent entity exists before saving.

**Solution:** Use an async validation rule:
```csharp
// Example code
```

**Variations:**
- Check multiple parents
- Custom error messages
```

### Before/After

For migration or comparison:

```markdown
## Migrating to v2.0

**Before (v1.x):**
```csharp
await factory.Save(entity);
```

**After (v2.0):**
```csharp
entity = await factory.Save(entity);  // Must reassign
```
```

## Code Example Guidelines

### When to Include Code

- **Always** for API usage examples
- **Always** for configuration
- **Usually** for concepts that have code implications
- **Rarely** for purely conceptual explanations

### How Much Context

**Too little:**
```csharp
person.Age = 25;
```

**Too much:**
```csharp
using Microsoft.Extensions.DependencyInjection;
using MyApp.Domain;
using MyApp.Domain.Entities;

namespace MyApp.Tests;

public class PersonTests
{
    private readonly IServiceProvider _services;

    public PersonTests()
    {
        var services = new ServiceCollection();
        // ... 20 more lines of setup
    }

    [Fact]
    public void SetAge()
    {
        var person = CreatePerson();
        person.Age = 25;  // <-- The actual point
    }
}
```

**Just right:**
```csharp
var person = await personFactory.Create();
person.Age = 25;  // Triggers validation
await person.WaitForTasks();
Assert.True(person.IsValid);
```

### Naming in Examples

Use realistic names that convey intent:

| Avoid | Prefer |
|-------|--------|
| `Foo`, `Bar`, `Baz` | `Person`, `Order`, `Invoice` |
| `DoSomething()` | `ValidateEmail()`, `SaveOrder()` |
| `MyClass` | `EmailValidator`, `OrderService` |
| `x`, `y`, `z` | `email`, `total`, `userId` |

## README Structure

A good README answers these questions in order:

1. **What is this?** - One sentence
2. **Why would I use it?** - Key benefits
3. **How do I get started?** - Install and first example
4. **Where do I learn more?** - Links to docs

```markdown
# ProjectName

One-sentence description of what this does.

## Features

- Bullet point benefits
- What makes this useful
- Key capabilities

## Quick Start

```bash
dotnet add package ProjectName
```

```csharp
// Minimal working example
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [API Reference](docs/api-reference.md)
```

## Common Mistakes

### Wall of Text

**Problem:** Long paragraphs without breaks.

**Fix:** Add headers, code blocks, lists. If a section is more than 3 paragraphs, split it.

### Missing Examples

**Problem:** "Use the validation API to add custom rules."

**Fix:** Show the code. Every feature needs at least one example.

### Outdated Information

**Problem:** Documentation references old APIs or patterns.

**Fix:** Use compiled code snippets (see docs-snippets skill). Code that compiles can't be wrong.

### Burying the Lead

**Problem:** Three paragraphs of background before showing how to use it.

**Fix:** Example first, explanation second.

## Additional Resources

- **[references/patterns.md](references/patterns.md)** - Documentation structure templates
