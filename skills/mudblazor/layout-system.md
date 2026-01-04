# MudBlazor Layout System

## Grid System

MudBlazor uses a **12-point grid system** with 6 responsive breakpoints.

### Breakpoints Reference

| Breakpoint | Code | Range | Use Case |
|------------|------|-------|----------|
| Extra small | xs | < 600px | Mobile phones |
| Small | sm | 600px - 960px | Tablets portrait |
| Medium | md | 960px - 1280px | Tablets landscape |
| Large | lg | 1280px - 1920px | Desktops |
| Extra Large | xl | 1920px - 2560px | Large monitors |
| Extra Extra Large | xxl | >= 2560px | Ultra-wide displays |

### Basic Grid

```razor
<MudGrid>
    <MudItem xs="12" sm="6" md="4">
        <MudPaper Class="pa-4">Column 1</MudPaper>
    </MudItem>
    <MudItem xs="12" sm="6" md="4">
        <MudPaper Class="pa-4">Column 2</MudPaper>
    </MudItem>
    <MudItem xs="12" sm="12" md="4">
        <MudPaper Class="pa-4">Column 3</MudPaper>
    </MudItem>
</MudGrid>
```

**Behavior:**
- Mobile (xs): All columns stack (12/12 each)
- Tablet (sm): First two side-by-side (6/6), third full width
- Desktop (md): All three in one row (4/4/4)

### Grid Spacing

Control gaps between items:

```razor
<MudGrid Spacing="0">  @* No gap *@
<MudGrid Spacing="3">  @* Small gap *@
<MudGrid Spacing="6">  @* Medium gap (default) *@
<MudGrid Spacing="10"> @* Large gap *@
```

### Grid Alignment

```razor
@* Horizontal alignment *@
<MudGrid Justify="Justify.FlexStart">    @* Left aligned *@
<MudGrid Justify="Justify.Center">        @* Center aligned *@
<MudGrid Justify="Justify.FlexEnd">       @* Right aligned *@
<MudGrid Justify="Justify.SpaceBetween">  @* Space between *@
<MudGrid Justify="Justify.SpaceAround">   @* Space around *@
<MudGrid Justify="Justify.SpaceEvenly">   @* Space evenly *@
```

### Forcing Line Breaks

```razor
<MudGrid>
    <MudItem xs="6"><MudPaper>Item 1</MudPaper></MudItem>
    <MudItem xs="6"><MudPaper>Item 2</MudPaper></MudItem>
    <MudFlexBreak />  @* Force items below to next line *@
    <MudItem xs="6"><MudPaper>Item 3</MudPaper></MudItem>
</MudGrid>
```

---

## Container

MudContainer provides responsive horizontal margins:

```razor
<MudContainer MaxWidth="MaxWidth.Small">      @* 600px max *@
<MudContainer MaxWidth="MaxWidth.Medium">     @* 960px max *@
<MudContainer MaxWidth="MaxWidth.Large">      @* 1280px max *@
<MudContainer MaxWidth="MaxWidth.ExtraLarge"> @* 1920px max *@
<MudContainer MaxWidth="MaxWidth.ExtraExtraLarge"> @* 2560px max *@
<MudContainer MaxWidth="MaxWidth.False">      @* No max width *@
```

### Page Container Pattern

```razor
<MudContainer MaxWidth="MaxWidth.ExtraLarge" Class="mt-4">
    <MudText Typo="Typo.h4" Class="mb-4">Page Title</MudText>
    @* Page content *@
</MudContainer>
```

---

## MudStack

Simplified flexbox layout component:

### Vertical Stack (Default)

```razor
<MudStack Spacing="3">
    <MudPaper Class="pa-4">Item 1</MudPaper>
    <MudPaper Class="pa-4">Item 2</MudPaper>
    <MudPaper Class="pa-4">Item 3</MudPaper>
</MudStack>
```

### Horizontal Stack

```razor
<MudStack Row="true" Spacing="3">
    <MudButton>Button 1</MudButton>
    <MudButton>Button 2</MudButton>
    <MudButton>Button 3</MudButton>
</MudStack>
```

### Alignment

```razor
<MudStack Row="true" Justify="Justify.SpaceBetween" AlignItems="AlignItems.Center">
    <MudText Typo="Typo.h6">Title</MudText>
    <MudButton>Action</MudButton>
</MudStack>
```

### Common Stack Patterns

```razor
@* Form actions - right aligned *@
<MudStack Row="true" Justify="Justify.FlexEnd" Spacing="2">
    <MudButton Variant="Variant.Text">Cancel</MudButton>
    <MudButton Variant="Variant.Filled" Color="Color.Primary">Save</MudButton>
</MudStack>

@* Header with spacer *@
<MudStack Row="true" AlignItems="AlignItems.Center">
    <MudText Typo="Typo.h5">Products</MudText>
    <MudSpacer />
    <MudButton StartIcon="@Icons.Material.Filled.Add">Add Product</MudButton>
</MudStack>
```

---

## MudPaper

Container component with elevation and styling:

```razor
<MudPaper Elevation="0">  @* No shadow *@
<MudPaper Elevation="2">  @* Subtle shadow *@
<MudPaper Elevation="4">  @* Medium shadow *@
<MudPaper Elevation="8">  @* Prominent shadow *@

<MudPaper Outlined="true">  @* Border instead of shadow *@
<MudPaper Square="true">    @* No border radius *@
```

### Card-Like Paper

```razor
<MudPaper Elevation="2" Class="pa-4">
    <MudText Typo="Typo.h6" Class="mb-4">Section Title</MudText>
    <MudText>Content goes here</MudText>
</MudPaper>
```

---

## Application Layout

### MudLayout Components

| Component | Purpose |
|-----------|---------|
| `MudLayout` | Root container |
| `MudAppBar` | Top navigation bar |
| `MudDrawer` | Side navigation panel |
| `MudMainContent` | Main content area |

### Basic Application Layout

```razor
<MudLayout>
    <MudAppBar Elevation="1">
        <MudIconButton Icon="@Icons.Material.Filled.Menu"
                       Color="Color.Inherit"
                       Edge="Edge.Start"
                       OnClick="@ToggleDrawer" />
        <MudText Typo="Typo.h5" Class="ml-3">My Application</MudText>
        <MudSpacer />
        <MudIconButton Icon="@Icons.Material.Filled.Person" Color="Color.Inherit" />
    </MudAppBar>

    <MudDrawer @bind-Open="_drawerOpen" Elevation="2">
        <MudDrawerHeader>
            <MudText Typo="Typo.h6">Navigation</MudText>
        </MudDrawerHeader>
        <MudNavMenu>
            <MudNavLink Href="/" Icon="@Icons.Material.Filled.Home">Home</MudNavLink>
            <MudNavLink Href="/products" Icon="@Icons.Material.Filled.Inventory">Products</MudNavLink>
        </MudNavMenu>
    </MudDrawer>

    <MudMainContent>
        @Body
    </MudMainContent>
</MudLayout>

@code {
    private bool _drawerOpen = true;
    private void ToggleDrawer() => _drawerOpen = !_drawerOpen;
}
```

### Drawer Variants

```razor
@* Responsive drawer (mini on small screens) *@
<MudDrawer @bind-Open="_drawerOpen"
           Variant="@DrawerVariant.Mini"
           OpenMiniOnHover="true">

@* Persistent drawer (always visible) *@
<MudDrawer @bind-Open="_drawerOpen"
           Variant="DrawerVariant.Persistent">

@* Temporary drawer (overlay) *@
<MudDrawer @bind-Open="_drawerOpen"
           Variant="DrawerVariant.Temporary">
```

### Drawer Clipping

```razor
@* Drawer starts below AppBar *@
<MudDrawer ClipMode="DrawerClipMode.Always">

@* Drawer extends behind AppBar *@
<MudDrawer ClipMode="DrawerClipMode.Never">
```

---

## Common Layout Patterns

### Dashboard Layout

```razor
<MudContainer MaxWidth="MaxWidth.ExtraLarge" Class="mt-4">
    @* Stats row *@
    <MudGrid Spacing="3" Class="mb-4">
        <MudItem xs="12" sm="6" md="3">
            <MudPaper Elevation="2" Class="pa-4">
                <MudText Typo="Typo.subtitle2" Color="Color.Secondary">Total Orders</MudText>
                <MudText Typo="Typo.h4">1,234</MudText>
            </MudPaper>
        </MudItem>
        @* More stat cards... *@
    </MudGrid>

    @* Main content area *@
    <MudGrid Spacing="3">
        <MudItem xs="12" lg="8">
            <MudPaper Elevation="2" Class="pa-4">
                <MudText Typo="Typo.h6" Class="mb-4">Recent Activity</MudText>
                @* Content *@
            </MudPaper>
        </MudItem>

        <MudItem xs="12" lg="4">
            <MudPaper Elevation="2" Class="pa-4">
                <MudText Typo="Typo.h6" Class="mb-4">Quick Actions</MudText>
                @* Sidebar *@
            </MudPaper>
        </MudItem>
    </MudGrid>
</MudContainer>
```

### Form Page Layout

```razor
<MudContainer MaxWidth="MaxWidth.Medium" Class="mt-4">
    <MudPaper Elevation="2" Class="pa-6">
        <MudStack Row="true" AlignItems="AlignItems.Center" Class="mb-4">
            <MudIconButton Icon="@Icons.Material.Filled.ArrowBack" OnClick="GoBack" />
            <MudText Typo="Typo.h5">Edit Customer</MudText>
        </MudStack>

        @* Form content *@

        <MudStack Row="true" Justify="Justify.FlexEnd" Class="mt-6">
            <MudButton Variant="Variant.Text" OnClick="Cancel">Cancel</MudButton>
            <MudButton Variant="Variant.Filled" Color="Color.Primary">Save</MudButton>
        </MudStack>
    </MudPaper>
</MudContainer>
```

### Master-Detail Layout

```razor
<MudGrid Spacing="3">
    @* List panel *@
    <MudItem xs="12" md="4">
        <MudPaper Elevation="2" Class="pa-4" Style="height: calc(100vh - 100px); overflow-y: auto;">
            <MudList T="Item" @bind-SelectedValue="selectedItem" Clickable="true">
                @foreach (var item in items)
                {
                    <MudListItem Value="@item">@item.Name</MudListItem>
                }
            </MudList>
        </MudPaper>
    </MudItem>

    @* Detail panel *@
    <MudItem xs="12" md="8">
        <MudPaper Elevation="2" Class="pa-4">
            @if (selectedItem != null)
            {
                <MudText Typo="Typo.h5">@selectedItem.Name</MudText>
                @* Detail content *@
            }
            else
            {
                <MudText Color="Color.Secondary">Select an item to view details</MudText>
            }
        </MudPaper>
    </MudItem>
</MudGrid>
```

---

## Spacing Utilities

### Padding Classes

| Pattern | Description |
|---------|-------------|
| `pa-{0-16}` | Padding all sides |
| `px-{0-16}` | Padding horizontal (left + right) |
| `py-{0-16}` | Padding vertical (top + bottom) |
| `pt-{0-16}` | Padding top |
| `pb-{0-16}` | Padding bottom |
| `ps-{0-16}` | Padding start (left in LTR) |
| `pe-{0-16}` | Padding end (right in LTR) |

### Margin Classes

| Pattern | Description |
|---------|-------------|
| `ma-{0-16}` | Margin all sides |
| `mx-{0-16}` | Margin horizontal |
| `my-{0-16}` | Margin vertical |
| `mt-{0-16}` | Margin top |
| `mb-{0-16}` | Margin bottom |
| `ms-{0-16}` | Margin start |
| `me-{0-16}` | Margin end |
| `mt-n{1-16}` | Negative margin top |

### Common Spacing Examples

```razor
<MudPaper Class="pa-4">           @* Padding 16px all sides *@
<MudPaper Class="pa-4 mb-3">      @* Padding 16px, margin-bottom 12px *@
<MudText Class="mt-4 mb-2">       @* Margin top 16px, bottom 8px *@
<MudButton Class="mx-2">          @* Horizontal margin 8px *@
```

### Spacing Scale

| Value | Pixels |
|-------|--------|
| 0 | 0px |
| 1 | 4px |
| 2 | 8px |
| 3 | 12px |
| 4 | 16px |
| 5 | 20px |
| 6 | 24px |
| 8 | 32px |
| 10 | 40px |
| 12 | 48px |
| 16 | 64px |
