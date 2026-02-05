---
name: csharp-docs
description: This skill should be used when the user asks to "create documentation", "write docs", "update documentation", "add code samples", "sync snippets", "create README", "document this framework", "run docs-architect", "run docs-code-samples", "create reference application", "add region markers", or mentions MarkdownSnippets, documentation samples, keeping docs in sync with code, or the two-agent documentation pipeline. Provides comprehensive guidance for documenting C# open source frameworks using a production-quality reference application and MarkdownSnippets for code synchronization.
version: 0.5.0
---

# C# Framework Documentation

Comprehensive documentation system for C# open source frameworks using a reference application and MarkdownSnippets for code synchronization.

## Core Philosophy

**Documentation snippets come from a real, working application—not isolated test samples.**

The reference application is a production-quality, multi-layered Employee Management system that demonstrates the framework being documented. Snippets are extracted from actual application code, ensuring they compile, run, and represent realistic usage patterns.

## How to Use This Skill

### Creating New Documentation

1. **Invoke `docs-architect`** with your documentation request
2. Review the created markdown files and the structured handoff
3. **Invoke `docs-code-samples`** to implement the code in the reference application
4. Run `mdsnippets` to sync code into documentation
5. Commit both documentation and reference application changes

### Updating Existing Documentation

| Task | Agent to Use |
|------|--------------|
| Add/restructure documentation files | `docs-architect` |
| Add new snippet placeholders | `docs-architect` |
| Implement code for existing placeholders | `docs-code-samples` |
| Update code samples after API changes | `docs-code-samples` |
| Verify samples still compile | `docs-code-samples` |

### Quick Commands

- **Full documentation creation:** Run `docs-architect`, then `docs-code-samples`
- **Code samples only:** Run `docs-code-samples` directly
- **Sync snippets:** Run `mdsnippets` after code changes

## Two-Agent Pipeline

Documentation follows a two-agent pipeline with structured handoffs:

| Agent | Responsibility | Output |
|-------|---------------|--------|
| **docs-architect** | Creates documentation structure with snippet placeholders | Markdown files + structured handoff |
| **docs-code-samples** | Builds reference application with `#region` markers | Compilable C# code + completion report |

**Always run docs-architect first when creating new documentation.**

## Agent Coordination

### Handoff Format

When `docs-architect` completes, it outputs a structured handoff that `docs-code-samples` parses:

```
=== HANDOFF TO docs-code-samples ===
Reference App Path: src/docs/reference-app/

Snippets by Layer:
  Domain:
    - name: employee-aggregate-create
      file: docs/getting-started.md
      purpose: Employee entity with static factory method
      dependencies: [email-value-object]
  Application:
    - name: employee-service-create
      file: docs/guides/services.md
      purpose: Application service for employee creation
      dependencies: [employee-aggregate-create]

Platform Requirements:
  - Blazor: No
  - Console: No

=== END HANDOFF ===
```

### Completion Report

When `docs-code-samples` completes, it outputs a completion report:

```
=== IMPLEMENTATION COMPLETE ===
Reference App: src/docs/reference-app/ReferenceApp.sln

Implemented Snippets:
  Domain:
    - employee-aggregate-create: Domain/Employees/Employee.cs (lines 15-45)
  Application:
    - employee-service-create: Application/Employees/EmployeeService.cs (lines 20-35)

Build Status: SUCCESS
Test Status: 12 passed, 0 failed
Ready for mdsnippets sync: YES
=== END IMPLEMENTATION ===
```

## Reference Application Overview

The reference application lives in `src/docs/reference-app/` with a standard multi-layered architecture:

| Layer | Purpose | Snippet Examples |
|-------|---------|------------------|
| **Domain/** | Core domain model (no dependencies) | `employee-aggregate`, `email-value-object` |
| **Application/** | Application services, commands, DTOs | `employee-service`, `create-employee-command` |
| **Infrastructure/** | Data access, external services | `employee-repository`, `ef-configuration` |
| **Server.WebApi/** | ASP.NET Core Web API (always created) | `api-controller`, `startup-di` |
| **Client.Blazor/** | Blazor WebAssembly (when needed) | `blazor-employee-form` |
| **Client.Console/** | Console client (when needed) | `console-main` |
| **Tests/** | Unit and integration tests | `test-domain-employee` |

Platform-specific projects (Blazor, Console, MAUI) are created **only when documentation requires them**.

See the agent files for complete structure details.

## Documentation Structure

```
README.md                    # Project overview, quick start, evaluation guide
docs/
├── index.md                 # Top-level documentation index (no breadcrumbs)
├── getting-started.md       # Installation, first usage
├── guides/                  # Feature-specific guides
│   ├── index.md
│   └── feature-a.md
├── reference/               # API reference
│   ├── index.md
│   └── api.md
└── migration/               # Migration guides
    ├── index.md
    └── from-other-lib.md
```

**Excluded from MarkdownSnippets:** `docs/todos/`, `docs/plans/`, `docs/release-notes/`

### Navigation Requirements

- **Index files**: Every folder has an `index.md` listing subfolders and files alphabetically
- **Breadcrumbs**: All non-index files have `[← Previous] | [↑ Up] | [Next →]` at top
- **Update tracking**: All files have `**UPDATED:** YYYY-MM-DD` at bottom

See [references/documentation-patterns.md](references/documentation-patterns.md) for templates.

## MarkdownSnippets Integration

### In Markdown (placeholder)

```markdown
<!-- snippet: snippet-name -->
<!-- endSnippet -->
```

### In C# (source)

```csharp
#region snippet-name
public class Employee
{
    public EmployeeId Id { get; private set; }
    // Production code
}
#endregion
```

MarkdownSnippets extracts code between `#region` and `#endregion` markers and injects into placeholders.

See [references/markdownsnippets-setup.md](references/markdownsnippets-setup.md) for installation and configuration.

## Critical Rules

### Never Comment Out Code That Doesn't Compile

**STOP and ASK the user if code doesn't compile.** Do NOT:

- Comment out code samples to avoid compilation errors
- Convert compilable code to pseudo-code or "example" comments
- Use workarounds like `[SuppressFactory]` to avoid conflicts
- Write code that demonstrates a feature incorrectly just to make it compile

If a code sample cannot compile in its intended location:

1. **STOP** - Do not proceed with workarounds
2. **REPORT** - Explain what doesn't compile and why
3. **ASK** - "Should I (1) move this to a project where it can compile, (2) restructure the sample differently, or (3) skip this sample?"

**Why:** Commented-out or pseudo-code samples are worse than no samples. They mislead readers and cannot be verified by the build system.

### Verify Samples Match Documentation Claims

Before writing a code sample for a documentation section:

1. **Read the section heading and description** - Understand what feature is being demonstrated
2. **Verify the code actually demonstrates that feature** - Don't write code that just compiles but doesn't match the claim
3. **Check the actual framework code** if unsure what a feature does

**Example of what NOT to do:**
- Section: "Create methods support multiple return types"
- Bad sample: Constructors (constructors don't have return types)
- The sample compiles but doesn't demonstrate the documented feature

## Writing Guidelines

### Target Audience

Documentation targets **expert .NET and C# developers**:

- No explanations of basic C# concepts
- No hand-holding or verbose tutorials
- Direct, technical language
- Focus on API usage and patterns

### Content Progression

1. **README** - Quick evaluation: What does it do? Why use it?
2. **Getting Started** - Minimal setup to first working code
3. **Guides** - Feature deep-dives with examples
4. **Reference** - Complete API documentation

### Placeholder Requirements

Placeholders must have **two parts**:

1. **Prose context** specifying the application layer
2. **Layer-prefixed name** for the snippet

```markdown
In the domain layer, the Employee aggregate validates business rules:

<!-- snippet: employee-aggregate-create -->
<!-- endSnippet -->
```

See [references/documentation-patterns.md](references/documentation-patterns.md) for naming conventions.

## Troubleshooting

### Snippet Not Found After Running mdsnippets

- Verify the `#region` name matches the placeholder exactly (case-sensitive)
- Check that the source file is not in an excluded directory
- Ensure the reference application builds successfully

### docs-code-samples Cannot Find Placeholders

- Ensure `docs-architect` was run first
- Check placeholder syntax: `<!-- snippet: name -->` (note the space after `snippet:`)
- Verify markdown files are in the `docs/` or `skills/*/` directory

### Build Failures in Reference Application

- Check for missing dependencies between layers
- Verify the solution file includes all projects
- Run `dotnet build` manually to see detailed errors

### Handoff Not Parsed Correctly

- Ensure `docs-architect` completed successfully
- Look for the `=== HANDOFF TO docs-code-samples ===` block
- Check that snippet names use lowercase-with-hyphens format

## Additional Resources

### Reference Files

- **[references/complete-example.md](references/complete-example.md)** - Consult when creating new documentation folders to see exact index.md and breadcrumb formatting

- **[references/markdownsnippets-setup.md](references/markdownsnippets-setup.md)** - Consult when setting up MarkdownSnippets for the first time or troubleshooting sync issues

- **[references/documentation-patterns.md](references/documentation-patterns.md)** - Consult for templates when creating README, getting-started, or feature guides; also contains the authoritative snippet naming conventions

### Related Commands

- **`/sequential-doc-create`** - Create comprehensive documentation with architect-led planning
- **`/sequential-review`** - Review all documentation files and update markdown snippets

## Getting Started

To create documentation for a C# framework:

1. Ensure the framework codebase is accessible
2. Invoke `docs-architect` with your documentation goals
3. Review the generated markdown structure and handoff
4. Invoke `docs-code-samples` to implement code samples
5. Run `mdsnippets` to synchronize code into documentation
6. Commit all changes (docs + reference application)
