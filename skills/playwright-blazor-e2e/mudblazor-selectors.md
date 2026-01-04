# MudBlazor Component Selectors

## Selector Strategy

MudBlazor components render standard HTML with consistent class naming. Always prefer accessibility-based locators over CSS classes.

| Priority | Approach | Stability |
|----------|----------|-----------|
| 1 | Role + accessible name | High |
| 2 | Label text | High |
| 3 | Test ID | High |
| 4 | Text content | Medium |
| 5 | MudBlazor classes | Low |

## Form Components

### MudTextField

```razor
<!-- Blazor component -->
<MudTextField @bind-Value="email" Label="Email Address" Variant="Variant.Outlined" />
```

```csharp
// By label (recommended)
var emailField = Page.GetByLabel("Email Address");
await emailField.FillAsync("test@example.com");

// By placeholder (if no label)
var searchField = Page.GetByPlaceholder("Search...");

// Clear and fill
await emailField.ClearAsync();
await emailField.FillAsync("new@example.com");

// Verify value
await Expect(emailField).ToHaveValueAsync("new@example.com");

// Check validation error
await Expect(Page.GetByText("Email is required")).ToBeVisibleAsync();
```

### MudNumericField

```razor
<MudNumericField @bind-Value="quantity" Label="Quantity" Min="1" Max="100" />
```

```csharp
var quantityField = Page.GetByLabel("Quantity");

// Type a number
await quantityField.FillAsync("50");

// Use spin buttons (if visible)
await Page.GetByRole(AriaRole.Button, new() { Name = "Increment" }).ClickAsync();
await Expect(quantityField).ToHaveValueAsync("51");
```

### MudSelect

```razor
<MudSelect @bind-Value="category" Label="Category">
    <MudSelectItem Value="@("electronics")">Electronics</MudSelectItem>
    <MudSelectItem Value="@("clothing")">Clothing</MudSelectItem>
</MudSelect>
```

```csharp
// Open dropdown
var categorySelect = Page.GetByLabel("Category");
await categorySelect.ClickAsync();

// Select option by text
await Page.GetByRole(AriaRole.Option, new() { Name = "Electronics" }).ClickAsync();

// Verify selection
await Expect(categorySelect).ToContainTextAsync("Electronics");

// For multi-select
var tagsSelect = Page.GetByLabel("Tags");
await tagsSelect.ClickAsync();
await Page.GetByRole(AriaRole.Option, new() { Name = "Featured" }).ClickAsync();
await Page.GetByRole(AriaRole.Option, new() { Name = "Sale" }).ClickAsync();
await Page.Keyboard.PressAsync("Escape"); // Close dropdown
```

### MudAutocomplete

```razor
<MudAutocomplete @bind-Value="selectedProduct" Label="Product" SearchFunc="SearchProducts" />
```

```csharp
var autocomplete = Page.GetByLabel("Product");

// Type to search
await autocomplete.FillAsync("Wid");

// Wait for options to appear
var options = Page.GetByRole(AriaRole.Option);
await Expect(options.First).ToBeVisibleAsync();

// Select from results
await Page.GetByRole(AriaRole.Option, new() { Name = "Widget Pro" }).ClickAsync();

// Verify selection
await Expect(autocomplete).ToHaveValueAsync("Widget Pro");
```

### MudDatePicker

```razor
<MudDatePicker @bind-Date="birthDate" Label="Date of Birth" />
```

```csharp
var datePicker = Page.GetByLabel("Date of Birth");

// Open picker
await datePicker.ClickAsync();

// Select specific date
await Page.GetByRole(AriaRole.Button, new() { Name = "15" }).ClickAsync(); // Day 15

// Or type directly if Editable="true"
await datePicker.FillAsync("12/25/2024");

// Navigate months
await Page.GetByRole(AriaRole.Button, new() { Name = "Previous month" }).ClickAsync();

// Verify
await Expect(datePicker).ToHaveValueAsync("12/25/2024");
```

### MudTimePicker

```razor
<MudTimePicker @bind-Time="appointmentTime" Label="Appointment Time" />
```

```csharp
var timePicker = Page.GetByLabel("Appointment Time");
await timePicker.ClickAsync();

// Select hour and minute
await Page.GetByRole(AriaRole.Button, new() { Name = "09" }).ClickAsync(); // Hour
await Page.GetByRole(AriaRole.Button, new() { Name = "30" }).ClickAsync(); // Minute
await Page.GetByRole(AriaRole.Button, new() { Name = "AM" }).ClickAsync();

// Confirm
await Page.GetByRole(AriaRole.Button, new() { Name = "OK" }).ClickAsync();
```

### MudCheckBox

```razor
<MudCheckBox @bind-Value="acceptTerms" Label="I accept the terms" />
```

```csharp
var checkbox = Page.GetByLabel("I accept the terms");

// Check
await checkbox.CheckAsync();
await Expect(checkbox).ToBeCheckedAsync();

// Uncheck
await checkbox.UncheckAsync();
await Expect(checkbox).Not.ToBeCheckedAsync();

// For tri-state checkbox
await Expect(checkbox).ToHaveAttributeAsync("aria-checked", "mixed");
```

### MudSwitch

```razor
<MudSwitch @bind-Value="isEnabled" Label="Enable notifications" />
```

```csharp
var toggle = Page.GetByLabel("Enable notifications");

// Toggle on
await toggle.CheckAsync();
await Expect(toggle).ToBeCheckedAsync();

// Toggle off
await toggle.UncheckAsync();
```

### MudRadioGroup

```razor
<MudRadioGroup @bind-Value="priority">
    <MudRadio Value="@("high")">High</MudRadio>
    <MudRadio Value="@("medium")">Medium</MudRadio>
    <MudRadio Value="@("low")">Low</MudRadio>
</MudRadioGroup>
```

```csharp
// Select by label
await Page.GetByLabel("High").CheckAsync();

// Verify selection
await Expect(Page.GetByLabel("High")).ToBeCheckedAsync();
await Expect(Page.GetByLabel("Medium")).Not.ToBeCheckedAsync();
```

## Buttons

### MudButton

```razor
<MudButton Variant="Variant.Filled" Color="Color.Primary">Save Changes</MudButton>
<MudButton Variant="Variant.Outlined" OnClick="Cancel">Cancel</MudButton>
<MudButton Disabled="@(!isValid)">Submit</MudButton>
```

```csharp
// By accessible name (button text)
await Page.GetByRole(AriaRole.Button, new() { Name = "Save Changes" }).ClickAsync();

// Check disabled state
await Expect(Page.GetByRole(AriaRole.Button, new() { Name = "Submit" }))
    .ToBeDisabledAsync();

// With icon - use exact text
await Page.GetByRole(AriaRole.Button, new() { Name = "Add Item" }).ClickAsync();
```

### MudIconButton

```razor
<MudIconButton Icon="@Icons.Material.Filled.Delete" Title="Delete item" />
<MudIconButton Icon="@Icons.Material.Filled.Edit" aria-label="Edit" />
```

```csharp
// By title or aria-label
await Page.GetByRole(AriaRole.Button, new() { Name = "Delete item" }).ClickAsync();
await Page.GetByRole(AriaRole.Button, new() { Name = "Edit" }).ClickAsync();

// Within a row
var row = Page.GetByRole(AriaRole.Row).Filter(new() { HasText = "Product A" });
await row.GetByRole(AriaRole.Button, new() { Name = "Edit" }).ClickAsync();
```

### MudFab

```razor
<MudFab Icon="@Icons.Material.Filled.Add" aria-label="Add new item" />
```

```csharp
await Page.GetByRole(AriaRole.Button, new() { Name = "Add new item" }).ClickAsync();
```

## Data Display

### MudDataGrid / MudTable

```razor
<MudDataGrid Items="@products">
    <Columns>
        <PropertyColumn Property="x => x.Name" Title="Product Name" />
        <PropertyColumn Property="x => x.Price" Title="Price" />
    </Columns>
</MudDataGrid>
```

```csharp
// Count rows (including header)
await Expect(Page.GetByRole(AriaRole.Row)).ToHaveCountAsync(11);

// Find specific row by content
var row = Page.GetByRole(AriaRole.Row).Filter(new() { HasText = "Widget Pro" });
await Expect(row).ToBeVisibleAsync();

// Get cell value
var priceCell = row.GetByRole(AriaRole.Cell).Nth(1); // Price column
await Expect(priceCell).ToContainTextAsync("$99.99");

// Click column header to sort
await Page.GetByRole(AriaRole.Columnheader, new() { Name = "Price" }).ClickAsync();

// Interact with row actions
await row.GetByRole(AriaRole.Button, new() { Name = "Edit" }).ClickAsync();

// Select row (if selectable)
await row.GetByRole(AriaRole.Checkbox).CheckAsync();

// Filter
var filterInput = Page.GetByPlaceholder("Search");
await filterInput.FillAsync("Widget");

// Pagination
await Page.GetByRole(AriaRole.Button, new() { Name = "Next page" }).ClickAsync();
await Page.GetByRole(AriaRole.Combobox, new() { Name = "Rows per page" }).ClickAsync();
await Page.GetByRole(AriaRole.Option, new() { Name = "25" }).ClickAsync();
```

### MudCard

```razor
<MudCard>
    <MudCardHeader>
        <CardHeaderContent>
            <MudText Typo="Typo.h6">Card Title</MudText>
        </CardHeaderContent>
    </MudCardHeader>
    <MudCardContent>Content here</MudCardContent>
    <MudCardActions>
        <MudButton>Action</MudButton>
    </MudCardActions>
</MudCard>
```

```csharp
// Find card by heading
var card = Page.Locator("article").Filter(new() { Has = Page.GetByText("Card Title") });

// Or use test ID
var card = Page.GetByTestId("product-card");

// Interact with card actions
await card.GetByRole(AriaRole.Button, new() { Name = "Action" }).ClickAsync();
```

### MudChip

```razor
<MudChip Color="Color.Success">Active</MudChip>
<MudChip OnClose="RemoveTag">Tag Name</MudChip>
```

```csharp
// Verify chip exists
await Expect(Page.GetByText("Active")).ToBeVisibleAsync();

// Click removable chip
await Page.GetByRole(AriaRole.Button, new() { Name = "Tag Name" }).ClickAsync();

// Or remove via close button
var chip = Page.Locator(".mud-chip").Filter(new() { HasText = "Tag Name" });
await chip.GetByRole(AriaRole.Button, new() { Name = "Close" }).ClickAsync();
```

## Dialogs and Overlays

### MudDialog

```razor
<MudDialog>
    <DialogContent>Dialog content here</DialogContent>
    <DialogActions>
        <MudButton OnClick="Cancel">Cancel</MudButton>
        <MudButton OnClick="Submit">Submit</MudButton>
    </DialogActions>
</MudDialog>
```

```csharp
// Wait for dialog to appear
var dialog = Page.GetByRole(AriaRole.Dialog);
await Expect(dialog).ToBeVisibleAsync();

// Get dialog by title (if title is rendered as heading)
var dialog = Page.GetByRole(AriaRole.Dialog)
    .Filter(new() { Has = Page.GetByRole(AriaRole.Heading, new() { Name = "Confirm Delete" }) });

// Interact with dialog content
await dialog.GetByLabel("Reason").FillAsync("No longer needed");

// Click dialog buttons
await dialog.GetByRole(AriaRole.Button, new() { Name = "Cancel" }).ClickAsync();
await Expect(dialog).ToBeHiddenAsync();

// Submit
await dialog.GetByRole(AriaRole.Button, new() { Name = "Submit" }).ClickAsync();
```

### MudDrawer

```csharp
// Open drawer via menu button
await Page.GetByRole(AriaRole.Button, new() { Name = "Menu" }).ClickAsync();

// Wait for drawer
var drawer = Page.Locator(".mud-drawer");
await Expect(drawer).ToBeVisibleAsync();

// Navigate via drawer
await drawer.GetByRole(AriaRole.Link, new() { Name = "Settings" }).ClickAsync();
```

### MudMenu

```razor
<MudMenu Label="Options">
    <MudMenuItem>Edit</MudMenuItem>
    <MudMenuItem>Delete</MudMenuItem>
</MudMenu>
```

```csharp
// Open menu
await Page.GetByRole(AriaRole.Button, new() { Name = "Options" }).ClickAsync();

// Select item
await Page.GetByRole(AriaRole.Menuitem, new() { Name = "Edit" }).ClickAsync();

// Wait for menu to close
await Expect(Page.GetByRole(AriaRole.Menu)).ToBeHiddenAsync();
```

### MudPopover / MudTooltip

```csharp
// Hover to show tooltip
await Page.GetByRole(AriaRole.Button, new() { Name = "Info" }).HoverAsync();

// Verify tooltip text
await Expect(Page.GetByRole(AriaRole.Tooltip)).ToContainTextAsync("More information");

// Or for popover
var popover = Page.Locator(".mud-popover");
await Expect(popover).ToBeVisibleAsync();
```

## Feedback Components

### MudSnackbar

```csharp
// Wait for snackbar
var snackbar = Page.GetByRole(AriaRole.Alert);
await Expect(snackbar).ToBeVisibleAsync();
await Expect(snackbar).ToContainTextAsync("Saved successfully");

// Click snackbar action
await snackbar.GetByRole(AriaRole.Button, new() { Name = "Undo" }).ClickAsync();

// Wait for snackbar to disappear
await Expect(snackbar).ToBeHiddenAsync(new() { Timeout = 10000 });
```

### MudAlert

```razor
<MudAlert Severity="Severity.Error">Error message here</MudAlert>
```

```csharp
// Verify alert
var errorAlert = Page.GetByRole(AriaRole.Alert);
await Expect(errorAlert).ToContainTextAsync("Error message here");

// Close dismissible alert
await errorAlert.GetByRole(AriaRole.Button, new() { Name = "Close" }).ClickAsync();
await Expect(errorAlert).ToBeHiddenAsync();
```

### MudProgressLinear / MudProgressCircular

```csharp
// Wait for loading to start
await Expect(Page.Locator(".mud-progress-linear")).ToBeVisibleAsync();

// Wait for loading to complete
await Expect(Page.Locator(".mud-progress-linear")).ToBeHiddenAsync(new() { Timeout = 30000 });

// Or use test ID
await Expect(Page.GetByTestId("loading-indicator")).ToBeHiddenAsync();
```

## Navigation Components

### MudNavMenu

```csharp
// Click nav item
await Page.GetByRole(AriaRole.Link, new() { Name = "Dashboard" }).ClickAsync();

// Expand nav group
await Page.GetByRole(AriaRole.Button, new() { Name = "Settings" }).ClickAsync();
await Page.GetByRole(AriaRole.Link, new() { Name = "User Settings" }).ClickAsync();
```

### MudTabs

```razor
<MudTabs>
    <MudTabPanel Text="General">...</MudTabPanel>
    <MudTabPanel Text="Advanced">...</MudTabPanel>
</MudTabs>
```

```csharp
// Click tab
await Page.GetByRole(AriaRole.Tab, new() { Name = "Advanced" }).ClickAsync();

// Verify tab is selected
await Expect(Page.GetByRole(AriaRole.Tab, new() { Name = "Advanced" }))
    .ToHaveAttributeAsync("aria-selected", "true");

// Verify tab panel content
await Expect(Page.GetByRole(AriaRole.Tabpanel)).ToContainTextAsync("Advanced settings");
```

### MudBreadcrumbs

```csharp
// Click breadcrumb
await Page.GetByRole(AriaRole.Link, new() { Name = "Products" }).ClickAsync();

// Verify current page (last breadcrumb, usually not a link)
await Expect(Page.GetByText("Product Details")).ToBeVisibleAsync();
```

## Layout Components

### MudAppBar

```csharp
// Interact with app bar elements
var appBar = Page.Locator("header");
await appBar.GetByRole(AriaRole.Button, new() { Name = "Menu" }).ClickAsync();
await appBar.GetByRole(AriaRole.Button, new() { Name = "Account" }).ClickAsync();
```

### MudContainer / MudPaper

These are structural components. Use test IDs or find by content:

```csharp
var section = Page.GetByTestId("customer-info-section");
// Or
var section = Page.Locator("section").Filter(new() { HasText = "Customer Information" });
```

## Common Patterns

### Finding Elements in Loading State

```csharp
// Wait for skeleton loader to be replaced
await Expect(Page.Locator(".mud-skeleton")).ToHaveCountAsync(0);

// Wait for specific content
await Expect(Page.GetByText("Total: $123.45")).ToBeVisibleAsync();
```

### Handling Dynamic IDs

MudBlazor generates dynamic IDs. Never use them directly:

```csharp
// BAD - ID changes on each render
Page.Locator("#mud-input-123");

// GOOD - Use label association
Page.GetByLabel("Email");

// GOOD - Use test ID
Page.GetByTestId("email-field");
```

### Adding Test IDs to MudBlazor Components

In your Blazor components, add UserAttributes:

```razor
<MudTextField @bind-Value="email"
              Label="Email"
              UserAttributes="@(new Dictionary<string, object> { ["data-testid"] = "email-field" })" />

<MudButton data-testid="submit-button">Submit</MudButton>
```

Then locate:
```csharp
await Page.GetByTestId("email-field").FillAsync("test@example.com");
await Page.GetByTestId("submit-button").ClickAsync();
```

### Waiting for MudBlazor Animations

MudBlazor uses CSS transitions. Usually Playwright's auto-waiting handles this, but for complex animations:

```csharp
// Wait for drawer animation
await Task.Delay(300);

// Or wait for specific state
await Expect(drawer).ToHaveClassAsync(new Regex("mud-drawer--open"));
```
