# Complete Documentation Structure Example

This example shows the complete structure with indexes, breadcrumbs, and snippet placeholders.

## docs/index.md (no breadcrumbs)

```markdown
# Documentation

Welcome to the framework documentation.

## Subfolders

- **[Guides](guides/)** - Feature guides and tutorials
- **[Reference](reference/)** - API reference documentation

## Documentation

- **[Getting Started](getting-started.md)** - Installation and first steps

---

**UPDATED:** 2026-01-24
```

## docs/getting-started.md

```markdown
[↑ Up](index.md)

# Getting Started

Installation instructions...

<!-- snippet: getting-started-install -->
<!-- endSnippet -->

---

**UPDATED:** 2026-01-24
```

## docs/guides/index.md

```markdown
[↑ Up](../index.md)

# Guides

Feature guides and tutorials.

## Documentation

- **[Feature A](feature-a.md)** - How to use Feature A
- **[Feature B](feature-b.md)** - How to use Feature B

---

**UPDATED:** 2026-01-24
```

## docs/guides/feature-a.md

```markdown
[↑ Up](index.md) | [Next →](feature-b.md)

# Feature A

Detailed guide...

<!-- snippet: feature-a-basic -->
<!-- endSnippet -->

---

**UPDATED:** 2026-01-24
```

## docs/guides/feature-b.md

```markdown
[← Previous](feature-a.md) | [↑ Up](index.md)

# Feature B

Detailed guide...

---

**UPDATED:** 2026-01-24
```
