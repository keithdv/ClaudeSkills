# MudBlazor Theming

## Theme Provider

The `MudThemeProvider` component manages themes and must be in your layout:

```razor
<MudThemeProvider />
```

### Dark Mode Support

```razor
<MudThemeProvider @ref="@_mudThemeProvider" @bind-IsDarkMode="@_isDarkMode" />

@code {
    private bool _isDarkMode;
    private MudThemeProvider _mudThemeProvider;

    protected override async Task OnAfterRenderAsync(bool firstRender)
    {
        if (firstRender)
        {
            // Detect system preference
            _isDarkMode = await _mudThemeProvider.GetSystemPreference();
            StateHasChanged();
        }
    }
}
```

### Dark Mode Toggle

```razor
<MudSwitch @bind-Value="@_isDarkMode"
           Color="Color.Primary"
           Label="@(_isDarkMode ? "Dark Mode" : "Light Mode")" />

<MudIconButton Icon="@(_isDarkMode ? Icons.Material.Filled.LightMode : Icons.Material.Filled.DarkMode)"
               Color="Color.Inherit"
               OnClick="@(() => _isDarkMode = !_isDarkMode)" />
```

---

## Custom Theme Definition

### Basic Custom Theme

```razor
<MudThemeProvider Theme="@CustomTheme" @bind-IsDarkMode="@_isDarkMode" />

@code {
    private MudTheme CustomTheme = new MudTheme
    {
        PaletteLight = new PaletteLight
        {
            Primary = "#1976D2",
            PrimaryContrastText = "#FFFFFF",
            Secondary = "#FF9800",
            Tertiary = "#4CAF50",
            AppbarBackground = "#1976D2",
            AppbarText = "#FFFFFF",
            Background = "#F5F5F5",
            Surface = "#FFFFFF",
            DrawerBackground = "#FFFFFF",
            DrawerText = "#424242",
            Success = "#4CAF50",
            Warning = "#FF9800",
            Error = "#F44336",
            Info = "#2196F3"
        },
        PaletteDark = new PaletteDark
        {
            Primary = "#90CAF9",
            PrimaryContrastText = "#000000",
            Secondary = "#FFB74D",
            Background = "#121212",
            Surface = "#1E1E1E",
            AppbarBackground = "#1E1E1E",
            DrawerBackground = "#1E1E1E"
        }
    };
}
```

### Full Theme with Typography

```razor
@code {
    private MudTheme CustomTheme = new MudTheme
    {
        PaletteLight = new PaletteLight
        {
            Primary = "#5A4AE2",
            PrimaryContrastText = "#FFFFFF",
            Secondary = "#00BFA5",
            SecondaryContrastText = "#FFFFFF",
            Tertiary = "#7C4DFF",
            TertiaryContrastText = "#FFFFFF",

            // Status colors
            Info = "#2196F3",
            InfoContrastText = "#FFFFFF",
            Success = "#4CAF50",
            SuccessContrastText = "#FFFFFF",
            Warning = "#FF9800",
            WarningContrastText = "#000000",
            Error = "#F44336",
            ErrorContrastText = "#FFFFFF",

            // Backgrounds
            Background = "#F5F5F5",
            BackgroundGray = "#EEEEEE",
            Surface = "#FFFFFF",

            // AppBar
            AppbarBackground = "#5A4AE2",
            AppbarText = "#FFFFFF",

            // Drawer
            DrawerBackground = "#FFFFFF",
            DrawerText = "#424242",
            DrawerIcon = "#757575",

            // Text
            TextPrimary = "#212121",
            TextSecondary = "#757575",
            TextDisabled = "#BDBDBD",

            // Actions
            ActionDefault = "#757575",
            ActionDisabled = "#BDBDBD",
            ActionDisabledBackground = "#E0E0E0",

            // Lines
            Divider = "#E0E0E0",
            DividerLight = "#F5F5F5",

            // Dark tones
            Dark = "#424242",
            DarkContrastText = "#FFFFFF"
        },

        PaletteDark = new PaletteDark
        {
            Primary = "#90CAF9",
            PrimaryContrastText = "#000000",
            Secondary = "#00E5FF",
            SecondaryContrastText = "#000000",

            Background = "#121212",
            BackgroundGray = "#1E1E1E",
            Surface = "#1E1E1E",

            AppbarBackground = "#1E1E1E",
            AppbarText = "#FFFFFF",

            DrawerBackground = "#1E1E1E",
            DrawerText = "#FFFFFF",
            DrawerIcon = "#BDBDBD",

            TextPrimary = "#FFFFFF",
            TextSecondary = "#BDBDBD",
            TextDisabled = "#757575",

            Divider = "#424242",
            DividerLight = "#2D2D2D"
        },

        Typography = new Typography
        {
            Default = new Default
            {
                FontFamily = new[] { "Roboto", "Helvetica", "Arial", "sans-serif" }
            },
            H1 = new H1
            {
                FontSize = "2.5rem",
                FontWeight = 500,
                LineHeight = 1.2
            },
            H2 = new H2
            {
                FontSize = "2rem",
                FontWeight = 500,
                LineHeight = 1.3
            },
            H3 = new H3
            {
                FontSize = "1.75rem",
                FontWeight = 500,
                LineHeight = 1.4
            },
            H4 = new H4
            {
                FontSize = "1.5rem",
                FontWeight = 500,
                LineHeight = 1.4
            },
            H5 = new H5
            {
                FontSize = "1.25rem",
                FontWeight = 500,
                LineHeight = 1.5
            },
            H6 = new H6
            {
                FontSize = "1rem",
                FontWeight = 500,
                LineHeight = 1.6
            },
            Button = new Button
            {
                FontWeight = 600,
                TextTransform = "none"  // Disable uppercase
            }
        },

        LayoutProperties = new LayoutProperties
        {
            DefaultBorderRadius = "4px",
            DrawerWidthLeft = "260px",
            DrawerMiniWidthLeft = "56px"
        }
    };
}
```

---

## Palette Properties Reference

### Core Colors

| Property | Description |
|----------|-------------|
| `Primary` | Main brand color |
| `Secondary` | Secondary accent |
| `Tertiary` | Third accent |
| `Info` | Information messages |
| `Success` | Positive states |
| `Warning` | Cautionary states |
| `Error` | Error states |
| `Dark` | Dark surfaces |

### Contrast Text Colors

Each color has a matching `ContrastText` property:
- `PrimaryContrastText`
- `SecondaryContrastText`
- etc.

### Surface Colors

| Property | Description |
|----------|-------------|
| `Background` | Page background |
| `BackgroundGray` | Secondary background |
| `Surface` | Card/Paper background |

### Component Colors

| Property | Description |
|----------|-------------|
| `AppbarBackground` | AppBar background |
| `AppbarText` | AppBar text |
| `DrawerBackground` | Drawer background |
| `DrawerText` | Drawer text |
| `DrawerIcon` | Drawer icon color |

### Text Colors

| Property | Description |
|----------|-------------|
| `TextPrimary` | Primary text |
| `TextSecondary` | Secondary/muted text |
| `TextDisabled` | Disabled text |

### Action Colors

| Property | Description |
|----------|-------------|
| `ActionDefault` | Default icon/action color |
| `ActionDisabled` | Disabled action color |
| `ActionDisabledBackground` | Disabled button background |

### Lines

| Property | Description |
|----------|-------------|
| `Divider` | Standard divider |
| `DividerLight` | Lighter divider |

---

## CSS Variables

MudBlazor exposes theme values as CSS variables:

### Using Theme Variables in Custom CSS

```css
.custom-element {
    background-color: var(--mud-palette-primary);
    color: var(--mud-palette-primary-text);
    border-radius: var(--mud-default-borderradius);
}

.custom-surface {
    background-color: var(--mud-palette-surface);
    box-shadow: var(--mud-elevation-2);
}

.custom-text {
    color: var(--mud-palette-text-primary);
    font-family: var(--mud-typography-default-family);
}
```

### Common CSS Variables

| Variable | Description |
|----------|-------------|
| `--mud-palette-primary` | Primary color |
| `--mud-palette-secondary` | Secondary color |
| `--mud-palette-background` | Background color |
| `--mud-palette-surface` | Surface color |
| `--mud-palette-text-primary` | Primary text |
| `--mud-palette-text-secondary` | Secondary text |
| `--mud-elevation-{0-25}` | Shadow definitions |
| `--mud-default-borderradius` | Default border radius |
| `--mud-typography-default-family` | Font family |

---

## Typography System

### Using Typography

```razor
<MudText Typo="Typo.h1">Heading 1</MudText>
<MudText Typo="Typo.h2">Heading 2</MudText>
<MudText Typo="Typo.h3">Heading 3</MudText>
<MudText Typo="Typo.h4">Heading 4</MudText>
<MudText Typo="Typo.h5">Heading 5</MudText>
<MudText Typo="Typo.h6">Heading 6</MudText>
<MudText Typo="Typo.subtitle1">Subtitle 1</MudText>
<MudText Typo="Typo.subtitle2">Subtitle 2</MudText>
<MudText Typo="Typo.body1">Body 1 (default)</MudText>
<MudText Typo="Typo.body2">Body 2</MudText>
<MudText Typo="Typo.caption">Caption</MudText>
<MudText Typo="Typo.overline">OVERLINE</MudText>
```

### Text Colors

```razor
<MudText Color="Color.Primary">Primary colored text</MudText>
<MudText Color="Color.Secondary">Secondary colored text</MudText>
<MudText Color="Color.Success">Success colored text</MudText>
<MudText Color="Color.Error">Error colored text</MudText>
```

---

## Elevation (Shadows)

MudBlazor provides elevation levels 0-25:

```razor
<MudPaper Elevation="0">  @* No shadow *@
<MudPaper Elevation="1">  @* Minimal shadow *@
<MudPaper Elevation="2">  @* Subtle shadow *@
<MudPaper Elevation="4">  @* Medium shadow *@
<MudPaper Elevation="8">  @* Prominent shadow *@
<MudPaper Elevation="16"> @* Strong shadow *@
```

---

## Z-Index Layers

MudBlazor uses consistent z-index values:

| Component | Z-Index |
|-----------|---------|
| Drawer | 1100 |
| Popover | 1200 |
| AppBar | 1300 |
| Dialog | 1400 |
| Snackbar | 1500 |

---

## Applying Theme to Components

### Setting Theme Colors

```razor
<MudButton Color="Color.Primary">Primary</MudButton>
<MudButton Color="Color.Secondary">Secondary</MudButton>
<MudAlert Severity="Severity.Success">Success alert</MudAlert>
<MudChip Color="Color.Warning">Warning chip</MudChip>
```

### Component Variants

```razor
@* Text variant - no background *@
<MudButton Variant="Variant.Text" Color="Color.Primary">Text</MudButton>

@* Filled variant - solid background *@
<MudButton Variant="Variant.Filled" Color="Color.Primary">Filled</MudButton>

@* Outlined variant - border only *@
<MudButton Variant="Variant.Outlined" Color="Color.Primary">Outlined</MudButton>
```

---

## Theme Service for Dynamic Changes

```csharp
@inject IThemeService ThemeService

// Access current theme
var currentTheme = ThemeService.CurrentTheme;

// Runtime palette modification
ThemeService.CurrentTheme.PaletteLight.Primary = "#FF5722";
StateHasChanged();
```

---

## Best Practices

### 1. Define Theme Once

Create a single `MudTheme` instance and use it throughout the application:

```csharp
// Services/AppTheme.cs
public static class AppTheme
{
    public static MudTheme Theme => new MudTheme
    {
        // Theme definition
    };
}

// MainLayout.razor
<MudThemeProvider Theme="@AppTheme.Theme" />
```

### 2. Use Theme Colors Consistently

Instead of hardcoding colors:

```razor
@* GOOD *@
<MudButton Color="Color.Primary">Save</MudButton>

@* AVOID *@
<MudButton Style="background-color: #1976D2;">Save</MudButton>
```

### 3. Respect Dark Mode

Ensure custom components work in both light and dark modes:

```razor
<MudPaper Class="@(_isDarkMode ? "dark-custom" : "light-custom")">
```

Or better, use CSS variables:

```css
.custom-component {
    background-color: var(--mud-palette-surface);
    color: var(--mud-palette-text-primary);
}
```

### 4. Test Both Modes

Always test your UI in both light and dark modes to ensure readability and visual consistency.
