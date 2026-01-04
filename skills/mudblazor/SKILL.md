---
name: mudblazor
description: Build enterprise Blazor applications with MudBlazor component library. Use when creating forms, data grids, dialogs, navigation, theming, layout systems, or integrating with Neatoo domain objects. Covers installation, components, validation, data display, and enterprise patterns.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(dotnet:*), WebFetch
---

# MudBlazor - Enterprise Blazor UI Development

## Overview

MudBlazor is a comprehensive Material Design component library for Blazor that provides production-ready UI components for building enterprise web applications. It emphasizes customizable theming, extensive component options, and developer-friendly APIs.

### Key Capabilities

| Category | Components |
|----------|------------|
| **Forms** | TextField, NumericField, Select, Autocomplete, DatePicker, CheckBox, Switch, RadioGroup |
| **Data Display** | DataGrid, Table, Card, List, TreeView, Tabs |
| **Feedback** | Dialog, Snackbar, Alert, Progress indicators |
| **Navigation** | NavMenu, Breadcrumbs, Tabs, Links |
| **Layout** | Grid, Container, Paper, Stack, Drawer, AppBar |

### When to Use This Skill

Use this skill when:
- Building forms with validation and user feedback
- Creating data tables and grids with sorting, filtering, and paging
- Implementing dialog-based workflows
- Setting up application layouts and navigation
- Theming and styling Blazor applications
- Integrating MudBlazor with Neatoo domain objects

## Quick Start

### Installation

```bash
dotnet add package MudBlazor
```

### Required Configuration

**Program.cs:**
```csharp
using MudBlazor.Services;

builder.Services.AddMudServices();
```

**_Imports.razor:**
```razor
@using MudBlazor
```

**MainLayout.razor - Required Providers:**
```razor
<MudThemeProvider />
<MudPopoverProvider />
<MudDialogProvider />
<MudSnackbarProvider />

<MudLayout>
    @Body
</MudLayout>
```

**App.razor or index.html - Required Assets:**
```html
<link href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" rel="stylesheet" />
<link href="_content/MudBlazor/MudBlazor.min.css" rel="stylesheet" />
<script src="_content/MudBlazor/MudBlazor.min.js"></script>
```

## Core Concepts

### Component Variants

Most MudBlazor form components support three visual variants:

| Variant | Appearance | Best For |
|---------|------------|----------|
| `Variant.Text` | Standard underline | Default, minimal visual weight |
| `Variant.Filled` | Filled background | Dialogs, short forms, emphasis |
| `Variant.Outlined` | Border outline | Long forms, reduced visual clutter |

### Spacing Utilities

MudBlazor provides utility classes for consistent spacing:

- **Padding**: `pa-0` to `pa-16` (all), `px-*` (horizontal), `py-*` (vertical), `pt-*`, `pb-*`, `ps-*`, `pe-*`
- **Margin**: `ma-0` to `ma-16`, `mx-*`, `my-*`, `mt-*`, `mb-*`, `ms-*`, `me-*`

Example: `Class="pa-4 mb-3"` = padding all sides 4 units, margin bottom 3 units

### Color System

MudBlazor uses a `Color` enum for consistent theming:

| Color | Use Case |
|-------|----------|
| `Color.Primary` | Primary actions, brand color |
| `Color.Secondary` | Secondary actions |
| `Color.Tertiary` | Tertiary actions |
| `Color.Success` | Positive outcomes |
| `Color.Warning` | Cautionary states |
| `Color.Error` | Error states, destructive actions |
| `Color.Info` | Informational content |
| `Color.Default` | Neutral states |

## Additional Resources

For detailed guidance, see:
- [Installation & Setup](installation.md) - Full setup guide, providers, assets
- [Form Components](form-components.md) - TextField, Select, DatePicker, validation
- [Data Display](data-display.md) - DataGrid, Table, Cards
- [Feedback Components](feedback-components.md) - Dialog, Snackbar, Alert
- [Layout System](layout-system.md) - Grid, Container, responsive patterns
- [Navigation](navigation.md) - NavMenu, Tabs, Breadcrumbs
- [Theming](theming.md) - Custom themes, dark mode, CSS variables
- [Neatoo Integration](neatoo-integration.md) - MudNeatoo components for domain objects
- [Best Practices](best-practices.md) - Patterns, anti-patterns, performance

## Critical Rules

### MudForm vs EditForm

| Scenario | Use |
|----------|-----|
| MudBlazor's validation system | `MudForm` with `OnClick` handlers |
| ASP.NET Core validation | `EditForm` with `ButtonType.Submit` |

**NEVER use `ButtonType="ButtonType.Submit"` with MudForm.**

### Four Required Providers

All four providers must be in MainLayout for MudBlazor to function:
```razor
<MudThemeProvider />
<MudPopoverProvider />
<MudDialogProvider />
<MudSnackbarProvider />
```

### Complex Object Selection

When using `MudSelect` or `MudDataGrid` with complex objects, implement `IEquatable<T>` or provide a `Comparer`:

```csharp
<MudSelect T="Customer" Comparer="@(new CustomerComparer())">

public class CustomerComparer : IEqualityComparer<Customer>
{
    public bool Equals(Customer x, Customer y) => x?.Id == y?.Id;
    public int GetHashCode(Customer obj) => obj?.Id.GetHashCode() ?? 0;
}
```

### Dialog Result Handling

Always check if dialog was canceled before accessing result data:

```csharp
var result = await dialog.Result;
if (!result.Canceled)
{
    var data = result.Data;
}
```

## Official Documentation

- [MudBlazor Documentation](https://mudblazor.com/docs/overview)
- [MudBlazor GitHub](https://github.com/MudBlazor/MudBlazor)
- [MudBlazor Examples](https://try.mudblazor.com/)
