# MudBlazor Core Concepts

## Component Variants

Most MudBlazor form components support three visual variants:

| Variant | Appearance | Best For |
|---------|------------|----------|
| `Variant.Text` | Standard underline | Default, minimal visual weight |
| `Variant.Filled` | Filled background | Dialogs, short forms, emphasis |
| `Variant.Outlined` | Border outline | Long forms, reduced visual clutter |

Choose a variant and use it consistently across your forms for a cohesive look.

---

## Spacing Utilities

MudBlazor provides utility classes for consistent spacing:

- **Padding**: `pa-0` to `pa-16` (all), `px-*` (horizontal), `py-*` (vertical), `pt-*`, `pb-*`, `ps-*`, `pe-*`
- **Margin**: `ma-0` to `ma-16`, `mx-*`, `my-*`, `mt-*`, `mb-*`, `ms-*`, `me-*`

Example: `Class="pa-4 mb-3"` = padding all sides 4 units, margin bottom 3 units

**Prefer spacing classes over inline styles:**

```razor
@* GOOD *@
<MudPaper Class="pa-4 mb-3">

@* AVOID *@
<MudPaper Style="padding: 16px; margin-bottom: 12px;">
```

---

## Color System

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

```razor
<MudButton Color="Color.Primary">Save</MudButton>
<MudAlert Severity="Severity.Success">Saved!</MudAlert>
<MudChip Color="Color.Warning">Pending</MudChip>
```
