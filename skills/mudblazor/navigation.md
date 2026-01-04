# MudBlazor Navigation Components

## MudNavMenu

The primary navigation component for sidebar menus.

### Basic Navigation

```razor
<MudNavMenu>
    <MudNavLink Href="/" Match="NavLinkMatch.All" Icon="@Icons.Material.Filled.Home">
        Home
    </MudNavLink>
    <MudNavLink Href="/customers" Icon="@Icons.Material.Filled.People">
        Customers
    </MudNavLink>
    <MudNavLink Href="/products" Icon="@Icons.Material.Filled.Inventory">
        Products
    </MudNavLink>
    <MudNavLink Href="/reports" Icon="@Icons.Material.Filled.Assessment">
        Reports
    </MudNavLink>
</MudNavMenu>
```

### NavLink Matching

| Match | Behavior |
|-------|----------|
| `NavLinkMatch.All` | Exact URL match only |
| `NavLinkMatch.Prefix` | Matches URL and child routes |

```razor
@* Home - only active at "/" *@
<MudNavLink Href="/" Match="NavLinkMatch.All">Home</MudNavLink>

@* Customers - active at "/customers", "/customers/1", "/customers/new" *@
<MudNavLink Href="/customers" Match="NavLinkMatch.Prefix">Customers</MudNavLink>
```

### Grouped Navigation

```razor
<MudNavMenu>
    <MudNavLink Href="/" Match="NavLinkMatch.All" Icon="@Icons.Material.Filled.Home">
        Dashboard
    </MudNavLink>

    <MudNavGroup Title="Sales" Icon="@Icons.Material.Filled.ShoppingCart" Expanded="true">
        <MudNavLink Href="/orders">Orders</MudNavLink>
        <MudNavLink Href="/customers">Customers</MudNavLink>
        <MudNavLink Href="/products">Products</MudNavLink>
    </MudNavGroup>

    <MudNavGroup Title="Reports" Icon="@Icons.Material.Filled.Assessment">
        <MudNavLink Href="/reports/sales">Sales Report</MudNavLink>
        <MudNavLink Href="/reports/inventory">Inventory Report</MudNavLink>
    </MudNavGroup>

    <MudNavGroup Title="Settings" Icon="@Icons.Material.Filled.Settings">
        <MudNavLink Href="/settings/users">Users</MudNavLink>
        <MudNavLink Href="/settings/preferences">Preferences</MudNavLink>
    </MudNavGroup>
</MudNavMenu>
```

### Two-Way Binding for Expanded State

```razor
<MudNavGroup Title="Sales" @bind-Expanded="_salesExpanded">
    @* ... *@
</MudNavGroup>

@code {
    private bool _salesExpanded = true;
}
```

### Styling Options

```razor
<MudNavMenu Bordered="true"    @* Add borders *@
            Rounded="true"     @* Rounded corners *@
            Dense="true"       @* Compact layout *@
            Color="Color.Primary" @* Active link color *@
            Margin="Margin.Dense"> @* Reduced margins *@
```

### Icons and Colors

```razor
<MudNavLink Href="/users"
            Icon="@Icons.Material.Filled.People"
            IconColor="Color.Success">
    Users
</MudNavLink>

<MudNavLink Href="/alerts"
            Icon="@Icons.Material.Filled.Warning"
            IconColor="Color.Warning">
    Alerts
</MudNavLink>
```

### Disabled Links

```razor
<MudNavLink Href="/premium" Disabled="true" Icon="@Icons.Material.Filled.Lock">
    Premium Features
</MudNavLink>
```

### Custom Click Handler

```razor
<MudNavLink Icon="@Icons.Material.Filled.ExitToApp"
            OnClick="HandleLogout">
    Logout
</MudNavLink>

@code {
    private async Task HandleLogout()
    {
        await AuthService.LogoutAsync();
        NavigationManager.NavigateTo("/login");
    }
}
```

---

## MudTabs

Tab-based navigation for content sections.

### Basic Tabs

```razor
<MudTabs Elevation="2" Rounded="true" ApplyEffectsToContainer="true" PanelClass="pa-6">
    <MudTabPanel Text="Overview">
        <MudText>Overview content</MudText>
    </MudTabPanel>
    <MudTabPanel Text="Details">
        <MudText>Details content</MudText>
    </MudTabPanel>
    <MudTabPanel Text="History">
        <MudText>History content</MudText>
    </MudTabPanel>
</MudTabs>
```

### Tabs with Icons

```razor
<MudTabs>
    <MudTabPanel Text="Profile" Icon="@Icons.Material.Filled.Person">
        @* Content *@
    </MudTabPanel>
    <MudTabPanel Text="Security" Icon="@Icons.Material.Filled.Security">
        @* Content *@
    </MudTabPanel>
    <MudTabPanel Text="Notifications" Icon="@Icons.Material.Filled.Notifications">
        @* Content *@
    </MudTabPanel>
</MudTabs>
```

### Tab Position

```razor
<MudTabs Position="Position.Top">     @* Default *@
<MudTabs Position="Position.Bottom">
<MudTabs Position="Position.Start">   @* Left side *@
<MudTabs Position="Position.End">     @* Right side *@
```

### Centered Tabs

```razor
<MudTabs Centered="true">
    @* Tab panels *@
</MudTabs>
```

### Binding Active Tab

```razor
<MudTabs @bind-ActivePanelIndex="activeTab">
    <MudTabPanel Text="Tab 1">Content 1</MudTabPanel>
    <MudTabPanel Text="Tab 2">Content 2</MudTabPanel>
</MudTabs>

@code {
    private int activeTab = 0;
}
```

### Tabs with Badges

```razor
<MudTabPanel Text="Messages" BadgeData="@unreadCount" BadgeColor="Color.Error">
    @* Content *@
</MudTabPanel>

<MudTabPanel Text="Alerts" BadgeDot="true" BadgeColor="Color.Warning">
    @* Content *@
</MudTabPanel>
```

### Disabled Tab

```razor
<MudTabPanel Text="Premium" Disabled="true" ToolTip="Upgrade to access">
    @* Content *@
</MudTabPanel>
```

### Dynamic Tabs

```razor
<MudDynamicTabs @bind-ActivePanelIndex="activeIndex"
                AddTab="AddTab"
                CloseTab="CloseTab"
                PanelClass="pa-4">
    @foreach (var tab in tabs)
    {
        <MudTabPanel ID="@tab.Id" Text="@tab.Title" ShowCloseIcon="true">
            @tab.Content
        </MudTabPanel>
    }
</MudDynamicTabs>

@code {
    private int activeIndex = 0;
    private List<TabInfo> tabs = new();

    private void AddTab()
    {
        tabs.Add(new TabInfo { Id = Guid.NewGuid(), Title = $"Tab {tabs.Count + 1}" });
    }

    private void CloseTab(MudTabPanel panel)
    {
        tabs.RemoveAll(t => t.Id.Equals(panel.ID));
    }
}
```

---

## MudBreadcrumbs

Navigation breadcrumb trail.

### Basic Breadcrumbs

```razor
<MudBreadcrumbs Items="_items" />

@code {
    private List<BreadcrumbItem> _items = new()
    {
        new BreadcrumbItem("Home", href: "/"),
        new BreadcrumbItem("Products", href: "/products"),
        new BreadcrumbItem("Electronics", href: "/products/electronics"),
        new BreadcrumbItem("Laptops", href: null, disabled: true)
    };
}
```

### With Icons

```razor
<MudBreadcrumbs Items="_items">
    <ItemTemplate Context="item">
        <MudLink Href="@item.Href" Class="d-flex align-center">
            @if (!string.IsNullOrEmpty(item.Icon))
            {
                <MudIcon Icon="@item.Icon" Size="Size.Small" Class="mr-1" />
            }
            @item.Text
        </MudLink>
    </ItemTemplate>
</MudBreadcrumbs>

@code {
    private List<BreadcrumbItem> _items = new()
    {
        new BreadcrumbItem("Home", href: "/", icon: Icons.Material.Filled.Home),
        new BreadcrumbItem("Products", href: "/products", icon: Icons.Material.Filled.Inventory),
        new BreadcrumbItem("Item", href: null, disabled: true)
    };
}
```

### Custom Separator

```razor
<MudBreadcrumbs Items="_items" Separator=">" />

@* Or with custom template *@
<MudBreadcrumbs Items="_items">
    <SeparatorTemplate>
        <MudIcon Icon="@Icons.Material.Filled.ChevronRight" Size="Size.Small" />
    </SeparatorTemplate>
</MudBreadcrumbs>
```

---

## MudLink

Simple navigation link component.

```razor
<MudLink Href="/about">About Us</MudLink>

<MudLink Href="/terms" Target="_blank">Terms of Service</MudLink>

<MudLink Href="mailto:support@example.com" Color="Color.Primary">
    Contact Support
</MudLink>
```

---

## MudMenu

Dropdown menu component.

### Basic Menu

```razor
<MudMenu Icon="@Icons.Material.Filled.MoreVert">
    <MudMenuItem OnClick="@(() => Edit())">Edit</MudMenuItem>
    <MudMenuItem OnClick="@(() => Duplicate())">Duplicate</MudMenuItem>
    <MudMenuItem OnClick="@(() => Delete())">Delete</MudMenuItem>
</MudMenu>
```

### Menu with Label

```razor
<MudMenu Label="Actions" Variant="Variant.Filled" Color="Color.Primary">
    <MudMenuItem>Export</MudMenuItem>
    <MudMenuItem>Print</MudMenuItem>
    <MudMenuItem>Share</MudMenuItem>
</MudMenu>
```

### Menu with Icons

```razor
<MudMenu Icon="@Icons.Material.Filled.Add" Color="Color.Primary">
    <MudMenuItem Icon="@Icons.Material.Filled.Person">Add User</MudMenuItem>
    <MudMenuItem Icon="@Icons.Material.Filled.Group">Add Team</MudMenuItem>
    <MudMenuItem Icon="@Icons.Material.Filled.Business">Add Organization</MudMenuItem>
</MudMenu>
```

### Nested Menu

```razor
<MudMenu Label="Options">
    <MudMenuItem>Option 1</MudMenuItem>
    <MudMenuItem>Option 2</MudMenuItem>
    <MudMenu ActivationEvent="MouseEvent.MouseOver" AnchorOrigin="Origin.TopRight">
        <ActivatorContent>
            <MudMenuItem>More Options</MudMenuItem>
        </ActivatorContent>
        <ChildContent>
            <MudMenuItem>Sub Option 1</MudMenuItem>
            <MudMenuItem>Sub Option 2</MudMenuItem>
        </ChildContent>
    </MudMenu>
</MudMenu>
```

---

## Complete Navigation Example

### MainLayout with Full Navigation

```razor
@inherits LayoutComponentBase

<MudThemeProvider @bind-IsDarkMode="@_isDarkMode" />
<MudPopoverProvider />
<MudDialogProvider />
<MudSnackbarProvider />

<MudLayout>
    <MudAppBar Elevation="1">
        <MudIconButton Icon="@Icons.Material.Filled.Menu"
                       Color="Color.Inherit"
                       Edge="Edge.Start"
                       OnClick="@ToggleDrawer" />
        <MudText Typo="Typo.h5" Class="ml-3">Enterprise App</MudText>
        <MudSpacer />

        <MudMenu Icon="@Icons.Material.Filled.Add" Color="Color.Inherit">
            <MudMenuItem Href="/orders/new">New Order</MudMenuItem>
            <MudMenuItem Href="/customers/new">New Customer</MudMenuItem>
            <MudMenuItem Href="/products/new">New Product</MudMenuItem>
        </MudMenu>

        <MudIconButton Icon="@Icons.Material.Filled.Notifications"
                       Color="Color.Inherit" />

        <MudIconButton Icon="@(_isDarkMode ? Icons.Material.Filled.LightMode : Icons.Material.Filled.DarkMode)"
                       Color="Color.Inherit"
                       OnClick="@ToggleDarkMode" />

        <MudMenu Icon="@Icons.Material.Filled.AccountCircle" Color="Color.Inherit">
            <MudMenuItem Href="/profile">Profile</MudMenuItem>
            <MudMenuItem Href="/settings">Settings</MudMenuItem>
            <MudDivider />
            <MudMenuItem OnClick="Logout">Logout</MudMenuItem>
        </MudMenu>
    </MudAppBar>

    <MudDrawer @bind-Open="_drawerOpen" ClipMode="DrawerClipMode.Always" Elevation="2">
        <MudDrawerHeader>
            <MudText Typo="Typo.h6">Navigation</MudText>
        </MudDrawerHeader>

        <MudNavMenu Bordered="true" Margin="Margin.Dense">
            <MudNavLink Href="/" Match="NavLinkMatch.All"
                        Icon="@Icons.Material.Filled.Dashboard">
                Dashboard
            </MudNavLink>

            <MudNavGroup Title="Sales" Icon="@Icons.Material.Filled.ShoppingCart"
                         @bind-Expanded="_salesExpanded">
                <MudNavLink Href="/orders" Match="NavLinkMatch.Prefix">Orders</MudNavLink>
                <MudNavLink Href="/customers" Match="NavLinkMatch.Prefix">Customers</MudNavLink>
                <MudNavLink Href="/quotes">Quotes</MudNavLink>
            </MudNavGroup>

            <MudNavGroup Title="Inventory" Icon="@Icons.Material.Filled.Inventory">
                <MudNavLink Href="/products" Match="NavLinkMatch.Prefix">Products</MudNavLink>
                <MudNavLink Href="/categories">Categories</MudNavLink>
                <MudNavLink Href="/suppliers">Suppliers</MudNavLink>
            </MudNavGroup>

            <MudNavGroup Title="Reports" Icon="@Icons.Material.Filled.Assessment">
                <MudNavLink Href="/reports/sales">Sales Report</MudNavLink>
                <MudNavLink Href="/reports/inventory">Inventory Report</MudNavLink>
                <MudNavLink Href="/reports/customers">Customer Report</MudNavLink>
            </MudNavGroup>

            <MudDivider Class="my-2" />

            <MudNavLink Href="/settings" Icon="@Icons.Material.Filled.Settings">
                Settings
            </MudNavLink>
            <MudNavLink Href="/help" Icon="@Icons.Material.Filled.Help">
                Help
            </MudNavLink>
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
    private bool _salesExpanded = true;

    private void ToggleDrawer() => _drawerOpen = !_drawerOpen;
    private void ToggleDarkMode() => _isDarkMode = !_isDarkMode;
    private void Logout() { /* Logout logic */ }
}
```
