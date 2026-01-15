# Documentation Structure Templates

Copy-paste templates for common documentation scenarios.

## README Template

```markdown
# {ProjectName}

{One-sentence description - what problem does this solve?}

## Features

- {Key feature 1}
- {Key feature 2}
- {Key feature 3}

## Installation

```bash
dotnet add package {PackageName}
```

## Quick Start

```csharp
// Minimal working example that demonstrates core value
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [Concepts](docs/concepts.md)
- [API Reference](docs/reference.md)

## License

{License type}
```

## Getting Started Template

```markdown
# Getting Started

## Prerequisites

- .NET {version} or later
- {Other requirements}

## Installation

```bash
dotnet add package {PackageName}
```

## First Example

{Brief context - 1 sentence}

```csharp
// Complete, working example
// Should be copy-paste ready
```

## Next Steps

- [Core Concepts](concepts.md) - Understand the fundamentals
- [Common Patterns](patterns.md) - Real-world usage
```

## How-To Guide Template

```markdown
# How to {Accomplish Task}

## Problem

{1-2 sentences describing the situation}

## Solution

```csharp
// Working code that solves the problem
```

## Explanation

{What the code does and why}

## Variations

### {Variation 1}

```csharp
// Alternative approach
```

### {Variation 2}

```csharp
// Another alternative
```

## Related

- [Related Guide 1](related1.md)
- [Related Guide 2](related2.md)
```

## Concept Documentation Template

```markdown
# {Concept Name}

{Brief overview - what is this and why does it matter?}

## How It Works

{Explanation of the concept - can include diagrams}

## Example

```csharp
// Code demonstrating the concept
```

## When to Use

- {Situation 1}
- {Situation 2}

## When NOT to Use

- {Anti-pattern 1}
- {Anti-pattern 2}

## Related Concepts

- [{Related 1}](related1.md)
- [{Related 2}](related2.md)
```

## API Reference Template

```markdown
# {ClassName}

{Brief description of the class/interface purpose}

## Properties

### {PropertyName}

```csharp
public {Type} {PropertyName} { get; set; }
```

{Description of what the property does}

## Methods

### {MethodName}

```csharp
public {ReturnType} {MethodName}({Parameters})
```

{Description of what the method does}

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| {param1} | {Type} | {Description} |

**Returns:** {Description of return value}

**Example:**

```csharp
// Usage example
```

## See Also

- [{Related Class}]({link})
```

## Migration Guide Template

```markdown
# Migrating from {OldVersion} to {NewVersion}

## Overview

{Summary of what changed and why}

## Breaking Changes

### {Change 1}

**Before:**
```csharp
// Old code
```

**After:**
```csharp
// New code
```

**Why:** {Reason for the change}

### {Change 2}

...

## New Features

### {Feature 1}

{Description}

```csharp
// Example
```

## Deprecated

| Old | New | Removal |
|-----|-----|---------|
| `OldMethod()` | `NewMethod()` | v{X} |

## Checklist

- [ ] Update package reference to {version}
- [ ] Replace {old} with {new}
- [ ] Test {critical paths}
```

## Release Notes Template

```markdown
# {Project} {Version}

**Release Date:** {YYYY-MM-DD}

## Highlights

{1-3 sentences on the most important changes}

## What's New

### {Feature Name}

{Description with example}

```csharp
// Example
```

## Bug Fixes

- Fixed {issue description} ([#123](link))
- Fixed {issue description}

## Breaking Changes

{If any - include migration guidance}

## Contributors

Thanks to {contributors} for this release.
```
