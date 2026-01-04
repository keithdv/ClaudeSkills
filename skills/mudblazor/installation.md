# MudBlazor Installation & Setup

## Package Installation

### NuGet Package

```bash
dotnet add package MudBlazor
```

### Optional Templates

Install MudBlazor templates for quick project scaffolding:

```bash
dotnet new install MudBlazor.Templates
dotnet new mudblazor --interactivity Auto --name MyApplication --all-interactive
```

## Required Configuration Steps

### 1. Register Services

**Program.cs:**
```csharp
using MudBlazor.Services;

builder.Services.AddMudServices();
```

**With Snackbar Configuration:**
```csharp
builder.Services.AddMudServices(config =>
{
    config.SnackbarConfiguration.PositionClass = Defaults.Classes.Position.BottomRight;
    config.SnackbarConfiguration.PreventDuplicates = false;
    config.SnackbarConfiguration.NewestOnTop = true;
    config.SnackbarConfiguration.ShowCloseIcon = true;
    config.SnackbarConfiguration.VisibleStateDuration = 5000;
    config.SnackbarConfiguration.HideTransitionDuration = 500;
    config.SnackbarConfiguration.ShowTransitionDuration = 500;
    config.SnackbarConfiguration.SnackbarVariant = Variant.Filled;
});
```

### 2. Import Namespace

**_Imports.razor:**
```razor
@using MudBlazor
```

### 3. Add CSS and Font Assets

Add to HTML head (`index.html`, `_Layout.cshtml`, `_Host.cshtml`, or `App.razor`):

```html
<link href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" rel="stylesheet" />
<link href="_content/MudBlazor/MudBlazor.min.css" rel="stylesheet" />
```

**For .NET 9+** use asset fingerprinting:
```html
<link href="@Assets["_content/MudBlazor/MudBlazor.min.css"]" rel="stylesheet" />
```

### 4. Add JavaScript Assets

Place near the Blazor script at document end:

```html
<script src="_content/MudBlazor/MudBlazor.min.js"></script>
```

**For .NET 9+:**
```html
<script src="@Assets["_content/MudBlazor/MudBlazor.min.js"]"></script>
```

### 5. Add Required Providers

**MainLayout.razor:**
```razor
<MudThemeProvider />
<MudPopoverProvider />
<MudDialogProvider />
<MudSnackbarProvider />

<MudLayout>
    @Body
</MudLayout>
```

## Provider Functions

| Provider | Purpose |
|----------|---------|
| `MudThemeProvider` | Manages themes, dark mode, CSS variables |
| `MudPopoverProvider` | Container for dropdown menus, tooltips |
| `MudDialogProvider` | Container for dialog components |
| `MudSnackbarProvider` | Container for toast notifications |

## Render Mode Requirements

**IMPORTANT**: MudBlazor requires interactive rendering. Static rendering is NOT supported.

For .NET 8+ with interactive Auto mode:
```razor
@* App.razor *@
<Routes @rendermode="InteractiveAuto" />
```

## Complete MainLayout Example

```razor
@inherits LayoutComponentBase

<MudThemeProvider @ref="@_mudThemeProvider" @bind-IsDarkMode="@_isDarkMode" />
<MudPopoverProvider />
<MudDialogProvider />
<MudSnackbarProvider />

<MudLayout>
    <MudAppBar Elevation="1">
        <MudIconButton Icon="@Icons.Material.Filled.Menu" Color="Color.Inherit"
                       Edge="Edge.Start" OnClick="@ToggleDrawer" />
        <MudText Typo="Typo.h5" Class="ml-3">My Application</MudText>
        <MudSpacer />
        <MudIconButton Icon="@(_isDarkMode ? Icons.Material.Filled.LightMode : Icons.Material.Filled.DarkMode)"
                       Color="Color.Inherit" OnClick="@ToggleDarkMode" />
    </MudAppBar>

    <MudDrawer @bind-Open="_drawerOpen" ClipMode="DrawerClipMode.Always" Elevation="2">
        <MudNavMenu>
            <MudNavLink Href="/" Match="NavLinkMatch.All" Icon="@Icons.Material.Filled.Home">Home</MudNavLink>
            <MudNavLink Href="/customers" Icon="@Icons.Material.Filled.People">Customers</MudNavLink>
            <MudNavLink Href="/products" Icon="@Icons.Material.Filled.Inventory">Products</MudNavLink>
        </MudNavMenu>
    </MudDrawer>

    <MudMainContent>
        <MudContainer MaxWidth="MaxWidth.ExtraLarge" Class="mt-4">
            @Body
        </MudContainer>
    </MudMainContent>
</MudLayout>

@code {
    private bool _drawerOpen = true;
    private bool _isDarkMode;
    private MudThemeProvider _mudThemeProvider;

    private void ToggleDrawer() => _drawerOpen = !_drawerOpen;
    private void ToggleDarkMode() => _isDarkMode = !_isDarkMode;

    protected override async Task OnAfterRenderAsync(bool firstRender)
    {
        if (firstRender)
        {
            _isDarkMode = await _mudThemeProvider.GetSystemPreference();
            StateHasChanged();
        }
    }
}
```

## Removing Bootstrap

If using the default Blazor template, you can remove Bootstrap since MudBlazor replaces it:

1. Remove Bootstrap CSS link from `index.html` or `App.razor`
2. Remove Bootstrap JS if included
3. Update any custom CSS that depended on Bootstrap utilities

## Troubleshooting

### Components Not Rendering

1. Verify all four providers are in MainLayout
2. Check that `AddMudServices()` is called in Program.cs
3. Ensure CSS and JS assets are properly linked

### Dialogs/Snackbars Not Appearing

1. Verify `MudDialogProvider` and `MudSnackbarProvider` are present
2. Check that providers are at root level, not nested inside other components

### Styles Not Applied

1. Verify MudBlazor.min.css is loaded (check browser dev tools)
2. For .NET 9+, ensure `app.MapStaticAssets()` middleware is enabled
3. Implement cache-busting for production deployments
