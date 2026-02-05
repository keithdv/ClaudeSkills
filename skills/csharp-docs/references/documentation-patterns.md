# Documentation Patterns

Common patterns and templates for C# framework documentation.

## README Structure

A compelling README for framework evaluation:

```markdown
# Framework Name

Brief tagline describing what the framework does.

## Why Framework Name?

2-3 sentences on the core value proposition. What problem does it solve better than alternatives?

## Quick Example

The Employee aggregate demonstrates core framework concepts:

<!-- snippet: readme-teaser -->
<!-- endSnippet -->

## Installation

<!-- snippet: readme-install -->
<!-- endSnippet -->

## Documentation

- [Getting Started](docs/getting-started.md)
- [Guides](docs/guides/)
- [API Reference](docs/reference/)
- [Migration from X](docs/migration/from-x.md)

## License

[License type]
```

## Getting Started Template

```markdown
# Getting Started

## Installation

<!-- snippet: getting-started-install -->
<!-- endSnippet -->

## Your First [Thing]

Create a domain entity using the framework:

<!-- snippet: getting-started-domain -->
<!-- endSnippet -->

## Registering Services

Configure dependency injection in your ASP.NET Core application:

<!-- snippet: getting-started-startup -->
<!-- endSnippet -->

## Next Steps

- [Feature A Guide](guides/feature-a.md) - Deep dive into Feature A
- [Feature B Guide](guides/feature-b.md) - Learn about Feature B
- [API Reference](reference/api.md) - Complete API documentation
```

## Feature Guide Template

```markdown
# Feature Name

Brief description of what this feature does.

## Basic Usage

The domain model demonstrates basic feature usage:

<!-- snippet: feature-domain-basic -->
<!-- endSnippet -->

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `OptionA` | `string` | `null` | Description |
| `OptionB` | `bool` | `false` | Description |

## Common Patterns

### Pattern 1: [Name]

In the application layer, configure the pattern:

<!-- snippet: feature-app-pattern-1 -->
<!-- endSnippet -->

### Pattern 2: [Name]

The infrastructure implementation:

<!-- snippet: feature-infra-pattern-2 -->
<!-- endSnippet -->

## Advanced Usage

### [Advanced Topic]

For complex scenarios, extend the server configuration:

<!-- snippet: feature-server-advanced -->
<!-- endSnippet -->

## Troubleshooting

### Issue: [Common Problem]

**Symptom:** Description of what goes wrong

**Solution:** How to fix it

<!-- snippet: feature-troubleshoot -->
<!-- endSnippet -->
```

## API Reference Template

```markdown
# API Reference

## Core Types

### `ClassName`

Description of the class purpose.

#### Constructor

<!-- snippet: api-classname-ctor -->
<!-- endSnippet -->

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `PropA` | `string` | Description |
| `PropB` | `int` | Description |

#### Methods

##### `MethodName(params)`

Description of what the method does.

**Parameters:**
- `param1` (`Type`) - Description
- `param2` (`Type`) - Description

**Returns:** `ReturnType` - Description

<!-- snippet: api-classname-methodname -->
<!-- endSnippet -->
```

## Migration Guide Template

```markdown
# Migrating from [Other Library]

## Overview

Key differences between [Other Library] and [This Framework]:

| Aspect | [Other Library] | [This Framework] |
|--------|-----------------|------------------|
| Approach | Description | Description |
| Performance | Description | Description |
| API Style | Description | Description |

## Step-by-Step Migration

### Step 1: Installation

Remove [Other Library]:
```bash
dotnet remove package OtherLibrary
```

Add [This Framework]:
<!-- snippet: migration-install -->
<!-- endSnippet -->

### Step 2: Update Domain Model

**Before ([Other Library]):**
<!-- snippet: migration-before-domain -->
<!-- endSnippet -->

**After ([This Framework]):**
<!-- snippet: migration-after-domain -->
<!-- endSnippet -->

### Step 3: Update Service Registration

**Before:**
<!-- snippet: migration-before-startup -->
<!-- endSnippet -->

**After:**
<!-- snippet: migration-after-startup -->
<!-- endSnippet -->

## Common Migration Issues

### Issue: [Problem]

**Solution:** Description and example
```

## Snippet Naming by Layer

Use layer-prefixed naming to clarify where code belongs:

| Layer | Pattern | Examples |
|-------|---------|----------|
| Domain | `{aggregate}-{concept}` | `employee-aggregate`, `employee-created-event`, `email-value-object` |
| Application | `{feature}-service-{action}` | `employee-service-create`, `employee-service-update` |
| Infrastructure | `{feature}-repository`, `ef-{config}` | `employee-repository`, `ef-employee-config` |
| Server | `api-{feature}-{action}`, `startup-{config}` | `api-employees-get`, `startup-di` |
| Client | `blazor-{component}`, `console-{feature}` | `blazor-employee-form`, `console-main` |
| Tests | `test-{layer}-{feature}` | `test-domain-employee`, `test-api-integration` |
| README | `readme-{section}` | `readme-teaser`, `readme-install` |
| Getting Started | `getting-started-{topic}` | `getting-started-domain`, `getting-started-startup` |
| Migration | `migration-{before\|after}-{layer}` | `migration-before-domain`, `migration-after-startup` |

### Naming Rules

1. Use lowercase with hyphens
2. Be descriptive but concise
3. Include layer context in the name
4. Number sequences when order matters

## Content Guidelines

### For Expert Developers

**Do:**
- Jump straight to code
- Use technical terminology
- Show realistic examples from the reference application
- Include edge cases

**Don't:**
- Explain basic C# concepts
- Over-explain obvious things
- Use verbose introductions
- Include placeholder comments like "// Your code here"

### Code Sample Quality

Every snippet should:
- Come from the reference application
- Compile without errors
- Run as verified by tests
- Demonstrate one concept clearly
- Use realistic (not toy) examples

### Progressive Detail

1. **README**: Just enough to evaluate
2. **Getting Started**: Minimal viable usage
3. **Guides**: Complete feature coverage
4. **Reference**: Every option and method

## Placeholder Context Requirements

When docs-architect creates placeholders, include layer context for docs-code-samples:

**Good placeholder context:**
```markdown
The Employee aggregate validates business rules during creation:

<!-- snippet: employee-create -->
<!-- endSnippet -->
```

**Better placeholder context (explicit layer):**
```markdown
In the domain layer, the Employee aggregate validates business rules during creation:

<!-- snippet: employee-aggregate-create -->
<!-- endSnippet -->
```

**Bad placeholder context:**
```markdown
<!-- snippet: methods-example -->
<!-- endSnippet -->
```

The description above the snippet tells docs-code-samples:
1. Which layer of the reference application to implement the code
2. What functionality the code should demonstrate
3. What context to include in the snippet
