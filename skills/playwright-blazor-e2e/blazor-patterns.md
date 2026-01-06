# Blazor-Specific Testing Patterns

## Blazor Loading States

### WebAssembly Initialization

Blazor WebAssembly apps have a loading phase where the .NET runtime and app DLLs download. Tests must wait for this to complete.

```csharp
/// <summary>
/// Waits for Blazor WebAssembly runtime to initialize.
/// </summary>
protected async Task WaitForBlazorAsync(int timeoutMs = 30000)
{
    // Wait for Blazor object to exist
    await Page.WaitForFunctionAsync(
        "window.Blazor !== undefined",
        new() { Timeout = timeoutMs }
    );
}

/// <summary>
/// Waits for Blazor and ensures no loading overlays are present.
/// </summary>
protected async Task WaitForAppReadyAsync(int timeoutMs = 30000)
{
    await WaitForBlazorAsync(timeoutMs);

    // Common loading indicator patterns
    var loaders = Page.Locator(@"
        [data-testid='app-loading'],
        .loading-overlay,
        .mud-progress-linear,
        .loading-spinner,
        #blazor-loading
    ".Trim());

    try
    {
        await Expect(loaders.First).ToBeHiddenAsync(new() { Timeout = timeoutMs });
    }
    catch (TimeoutException)
    {
        // No loader found, app is ready
    }
}
```

### Component Loading States

Many Blazor components load data asynchronously. Wait for loading indicators:

```csharp
[TestMethod]
public async Task ProductList_LoadsData()
{
    await Page.GotoAsync("/products");
    await WaitForBlazorAsync();

    // Wait for loading indicator to appear then disappear
    var loadingIndicator = Page.GetByTestId("products-loading");

    // First, ensure loading started (optional, for slow connections)
    // await Expect(loadingIndicator).ToBeVisibleAsync(new() { Timeout = 1000 });

    // Then wait for it to finish
    await Expect(loadingIndicator).ToBeHiddenAsync(new() { Timeout = 15000 });

    // Now verify data loaded
    await Expect(Page.GetByRole(AriaRole.Row)).ToHaveCountAsync(11); // header + 10 rows
}
```

### Skeleton Loaders

MudBlazor uses skeleton loaders. Wait for them to be replaced:

```csharp
[TestMethod]
public async Task Dashboard_LoadsAllCards()
{
    await Page.GotoAsync("/dashboard");
    await WaitForBlazorAsync();

    // Wait for all skeletons to be replaced with real content
    var skeletons = Page.Locator(".mud-skeleton");
    await Expect(skeletons).ToHaveCountAsync(0, new() { Timeout = 10000 });

    // Verify actual content
    await Expect(Page.GetByText("Total Revenue")).ToBeVisibleAsync();
}
```

## Form Testing Patterns

### Basic Form Submission

```csharp
[TestMethod]
public async Task CustomerForm_CreatesNewCustomer()
{
    await NavigateAndWaitAsync("/customers/new");

    // Fill form fields
    await Page.GetByLabel("First Name").FillAsync("John");
    await Page.GetByLabel("Last Name").FillAsync("Doe");
    await Page.GetByLabel("Email").FillAsync("john.doe@example.com");
    await Page.GetByLabel("Phone").FillAsync("555-123-4567");

    // Select from dropdown
    await Page.GetByLabel("Category").ClickAsync();
    await Page.GetByRole(AriaRole.Option, new() { Name = "Premium" }).ClickAsync();

    // Check checkbox
    await Page.GetByLabel("Subscribe to newsletter").CheckAsync();

    // Submit
    await Page.GetByRole(AriaRole.Button, new() { Name = "Create Customer" }).ClickAsync();

    // Verify success
    await Expect(Page).ToHaveURLAsync(new Regex("/customers$"));
    await Expect(Page.GetByRole(AriaRole.Alert)).ToContainTextAsync("created successfully");
}
```

### Validation Error Testing

```csharp
[TestMethod]
public async Task CustomerForm_ShowsValidationErrors()
{
    await NavigateAndWaitAsync("/customers/new");

    // Submit empty form
    await Page.GetByRole(AriaRole.Button, new() { Name = "Create" }).ClickAsync();

    // Verify validation messages appear
    await Expect(Page.GetByText("First name is required")).ToBeVisibleAsync();
    await Expect(Page.GetByText("Email is required")).ToBeVisibleAsync();

    // Verify button remains enabled but form doesn't submit
    await Expect(Page).ToHaveURLAsync(new Regex("/customers/new$"));
}

[TestMethod]
public async Task EmailField_ValidatesFormat()
{
    await NavigateAndWaitAsync("/customers/new");

    var emailField = Page.GetByLabel("Email");
    await emailField.FillAsync("not-an-email");
    await emailField.BlurAsync(); // Trigger validation

    await Expect(Page.GetByText("Invalid email format")).ToBeVisibleAsync();

    // Fix the error
    await emailField.ClearAsync();
    await emailField.FillAsync("valid@email.com");
    await emailField.BlurAsync();

    await Expect(Page.GetByText("Invalid email format")).ToBeHiddenAsync();
}
```

### Async Validation (Neatoo Pattern)

For Neatoo domain objects with async validation rules:

```csharp
[TestMethod]
public async Task UniqueEmailRule_ShowsError_WhenEmailTaken()
{
    await NavigateAndWaitAsync("/users/new");

    // Enter email that triggers async validation
    var emailField = Page.GetByLabel("Email");
    await emailField.FillAsync("existing@example.com");
    await emailField.BlurAsync();

    // Wait for validation to run (look for IsBusy indicator)
    var busyIndicator = Page.GetByTestId("email-validating");
    await Expect(busyIndicator).ToBeHiddenAsync(new() { Timeout = 10000 });

    // Check for validation message
    await Expect(Page.GetByText("Email already in use")).ToBeVisibleAsync();

    // Verify Save button is disabled (IsSavable = false)
    await Expect(Page.GetByRole(AriaRole.Button, new() { Name = "Save" }))
        .ToBeDisabledAsync();
}
```

### Form with Multiple Sections

```csharp
[TestMethod]
public async Task OrderForm_FillsMultipleSections()
{
    await NavigateAndWaitAsync("/orders/new");

    // Section 1: Customer Info
    await Page.GetByRole(AriaRole.Tab, new() { Name = "Customer" }).ClickAsync();
    await Page.GetByLabel("Customer").ClickAsync();
    await Page.GetByRole(AriaRole.Option, new() { Name = "Acme Corp" }).ClickAsync();

    // Section 2: Line Items
    await Page.GetByRole(AriaRole.Tab, new() { Name = "Items" }).ClickAsync();
    await Page.GetByRole(AriaRole.Button, new() { Name = "Add Item" }).ClickAsync();

    var row = Page.GetByRole(AriaRole.Row).Last;
    await row.GetByLabel("Product").ClickAsync();
    await Page.GetByRole(AriaRole.Option, new() { Name = "Widget Pro" }).ClickAsync();
    await row.GetByLabel("Quantity").FillAsync("5");

    // Section 3: Review
    await Page.GetByRole(AriaRole.Tab, new() { Name = "Review" }).ClickAsync();
    await Expect(Page.GetByText("$499.95")).ToBeVisibleAsync(); // Total

    // Submit
    await Page.GetByRole(AriaRole.Button, new() { Name = "Place Order" }).ClickAsync();
    await Expect(Page.GetByRole(AriaRole.Alert)).ToContainTextAsync("Order placed");
}
```

## Navigation Patterns

### SPA Navigation

Blazor uses client-side routing. Wait for route changes:

```csharp
[TestMethod]
public async Task Navigation_WorksCorrectly()
{
    await NavigateAndWaitAsync("/");

    // Click nav link
    await Page.GetByRole(AriaRole.Link, new() { Name = "Products" }).ClickAsync();

    // Wait for URL change (no full page reload)
    await Expect(Page).ToHaveURLAsync("/products");

    // Verify content loaded
    await Expect(Page.GetByRole(AriaRole.Heading, new() { Name = "Products" }))
        .ToBeVisibleAsync();
}
```

### Programmatic Navigation

```csharp
[TestMethod]
public async Task FormSubmit_RedirectsToDashboard()
{
    await NavigateAndWaitAsync("/login");

    await Page.GetByLabel("Email").FillAsync("user@example.com");
    await Page.GetByLabel("Password").FillAsync("password");
    await Page.GetByRole(AriaRole.Button, new() { Name = "Sign In" }).ClickAsync();

    // Wait for NavigationManager redirect
    await Expect(Page).ToHaveURLAsync("/dashboard", new() { Timeout = 10000 });
}
```

### Browser Back/Forward

```csharp
[TestMethod]
public async Task BrowserHistory_PreservesState()
{
    await NavigateAndWaitAsync("/products");

    // Navigate to detail
    await Page.GetByRole(AriaRole.Link, new() { Name = "View Details" }).First.ClickAsync();
    await Expect(Page).ToHaveURLAsync(new Regex("/products/\\d+"));

    // Go back
    await Page.GoBackAsync();
    await Expect(Page).ToHaveURLAsync("/products");

    // Go forward
    await Page.GoForwardAsync();
    await Expect(Page).ToHaveURLAsync(new Regex("/products/\\d+"));
}
```

## DataGrid/Table Testing

### Basic Grid Operations

```csharp
[TestMethod]
public async Task ProductGrid_SupportsSearchAndSort()
{
    await NavigateAndWaitAsync("/products");

    // Wait for initial load
    await Expect(Page.GetByRole(AriaRole.Row)).ToHaveCountAsync(11);

    // Search
    await Page.GetByPlaceholder("Search").FillAsync("Widget");
    await Expect(Page.GetByRole(AriaRole.Row)).ToHaveCountAsync(4); // header + 3 results

    // Clear search
    await Page.GetByPlaceholder("Search").ClearAsync();
    await Expect(Page.GetByRole(AriaRole.Row)).ToHaveCountAsync(11);

    // Sort by price
    await Page.GetByRole(AriaRole.Columnheader, new() { Name = "Price" }).ClickAsync();

    // Verify sort order (first data row should have lowest price)
    var firstRow = Page.GetByRole(AriaRole.Row).Nth(1);
    await Expect(firstRow).ToContainTextAsync("$9.99");

    // Click again for descending
    await Page.GetByRole(AriaRole.Columnheader, new() { Name = "Price" }).ClickAsync();
    await Expect(firstRow).ToContainTextAsync("$999.99");
}
```

### Pagination

```csharp
[TestMethod]
public async Task ProductGrid_PaginatesCorrectly()
{
    await NavigateAndWaitAsync("/products");

    // Verify page 1
    await Expect(Page.GetByRole(AriaRole.Row)).ToHaveCountAsync(11);
    await Expect(Page.GetByText("Page 1 of 5")).ToBeVisibleAsync();

    // Go to next page
    await Page.GetByRole(AriaRole.Button, new() { Name = "Next page" }).ClickAsync();

    // Verify page changed
    await Expect(Page.GetByText("Page 2 of 5")).ToBeVisibleAsync();

    // Data should update
    var firstRow = Page.GetByRole(AriaRole.Row).Nth(1);
    await Expect(firstRow).Not.ToContainTextAsync("Product 1");
}
```

### Row Selection

```csharp
[TestMethod]
public async Task ProductGrid_SupportsMultiSelect()
{
    await NavigateAndWaitAsync("/products");

    // Select first row checkbox
    var selectAll = Page.GetByRole(AriaRole.Checkbox).First;
    var row1Checkbox = Page.GetByRole(AriaRole.Row).Nth(1).GetByRole(AriaRole.Checkbox);
    var row2Checkbox = Page.GetByRole(AriaRole.Row).Nth(2).GetByRole(AriaRole.Checkbox);

    await row1Checkbox.CheckAsync();
    await row2Checkbox.CheckAsync();

    // Verify bulk action becomes available
    await Expect(Page.GetByRole(AriaRole.Button, new() { Name = "Delete Selected (2)" }))
        .ToBeVisibleAsync();

    // Select all
    await selectAll.CheckAsync();
    await Expect(Page.GetByRole(AriaRole.Button, new() { Name = "Delete Selected (10)" }))
        .ToBeVisibleAsync();
}
```

### Inline Editing

```csharp
[TestMethod]
public async Task ProductGrid_SupportsInlineEdit()
{
    await NavigateAndWaitAsync("/products");

    // Find specific row and click to edit
    var row = Page.GetByRole(AriaRole.Row).Filter(new() { HasText = "Widget Pro" });
    await row.ClickAsync();

    // Edit inline
    var nameCell = row.GetByRole(AriaRole.Textbox).First;
    await nameCell.ClearAsync();
    await nameCell.FillAsync("Widget Pro v2");

    // Save (press Enter or click save button)
    await nameCell.PressAsync("Enter");

    // Verify saved
    await Expect(Page.GetByRole(AriaRole.Alert)).ToContainTextAsync("saved");
    await Expect(row).ToContainTextAsync("Widget Pro v2");
}
```

## Dialog Testing

### Confirmation Dialog

```csharp
[TestMethod]
public async Task DeleteButton_RequiresConfirmation()
{
    await NavigateAndWaitAsync("/products");

    // Click delete button
    var row = Page.GetByRole(AriaRole.Row).Filter(new() { HasText = "Widget Pro" });
    await row.GetByRole(AriaRole.Button, new() { Name = "Delete" }).ClickAsync();

    // Verify dialog appears
    var dialog = Page.GetByRole(AriaRole.Dialog);
    await Expect(dialog).ToBeVisibleAsync();
    await Expect(dialog).ToContainTextAsync("Are you sure");
    await Expect(dialog).ToContainTextAsync("Widget Pro");

    // Cancel
    await dialog.GetByRole(AriaRole.Button, new() { Name = "Cancel" }).ClickAsync();
    await Expect(dialog).ToBeHiddenAsync();

    // Item still exists
    await Expect(row).ToBeVisibleAsync();
}

[TestMethod]
public async Task DeleteConfirmation_DeletesItem()
{
    await NavigateAndWaitAsync("/products");

    var row = Page.GetByRole(AriaRole.Row).Filter(new() { HasText = "Widget Pro" });
    await row.GetByRole(AriaRole.Button, new() { Name = "Delete" }).ClickAsync();

    var dialog = Page.GetByRole(AriaRole.Dialog);
    await dialog.GetByRole(AriaRole.Button, new() { Name = "Delete" }).ClickAsync();

    // Dialog closes
    await Expect(dialog).ToBeHiddenAsync();

    // Item removed
    await Expect(Page.GetByText("Widget Pro")).ToBeHiddenAsync();

    // Success message
    await Expect(Page.GetByRole(AriaRole.Alert)).ToContainTextAsync("deleted");
}
```

### Form Dialog

```csharp
[TestMethod]
public async Task EditDialog_UpdatesItem()
{
    await NavigateAndWaitAsync("/products");

    // Open edit dialog
    var row = Page.GetByRole(AriaRole.Row).Filter(new() { HasText = "Widget Pro" });
    await row.GetByRole(AriaRole.Button, new() { Name = "Edit" }).ClickAsync();

    var dialog = Page.GetByRole(AriaRole.Dialog);
    await Expect(dialog).ToBeVisibleAsync();

    // Modify fields
    var nameField = dialog.GetByLabel("Name");
    await nameField.ClearAsync();
    await nameField.FillAsync("Widget Pro v2");

    var priceField = dialog.GetByLabel("Price");
    await priceField.ClearAsync();
    await priceField.FillAsync("149.99");

    // Save
    await dialog.GetByRole(AriaRole.Button, new() { Name = "Save" }).ClickAsync();

    // Dialog closes
    await Expect(dialog).ToBeHiddenAsync();

    // Verify updates in grid
    await Expect(row).ToContainTextAsync("Widget Pro v2");
    await Expect(row).ToContainTextAsync("$149.99");
}
```

## Authentication Patterns

### Login Flow

```csharp
[TestMethod]
public async Task Login_RedirectsToRequestedPage()
{
    // Try to access protected page
    await Page.GotoAsync("/admin/settings");
    await WaitForBlazorAsync();

    // Should redirect to login
    await Expect(Page).ToHaveURLAsync(new Regex("/login"));

    // Login
    await Page.GetByLabel("Email").FillAsync("admin@example.com");
    await Page.GetByLabel("Password").FillAsync("AdminPassword123!");
    await Page.GetByRole(AriaRole.Button, new() { Name = "Sign In" }).ClickAsync();

    // Should redirect back to original page
    await Expect(Page).ToHaveURLAsync("/admin/settings");
}
```

### Reusing Auth State

```csharp
[TestClass]
public class AuthenticatedTests : BlazorTestBase
{
    private static string _authStatePath = "playwright/.auth/user.json";

    [ClassInitialize]
    public static async Task SetupAuth(TestContext context)
    {
        // Create a browser context and login once
        var playwright = await Playwright.CreateAsync();
        var browser = await playwright.Chromium.LaunchAsync();
        var context = await browser.NewContextAsync(new()
        {
            BaseURL = "https://localhost:5001",
            IgnoreHTTPSErrors = true
        });
        var page = await context.NewPageAsync();

        // Perform login
        await page.GotoAsync("/login");
        await page.GetByLabel("Email").FillAsync("test@example.com");
        await page.GetByLabel("Password").FillAsync("password");
        await page.GetByRole(AriaRole.Button, new() { Name = "Sign In" }).ClickAsync();
        await page.WaitForURLAsync("/dashboard");

        // Save auth state
        Directory.CreateDirectory(Path.GetDirectoryName(_authStatePath)!);
        await context.StorageStateAsync(new() { Path = _authStatePath });

        await browser.CloseAsync();
    }

    public override BrowserNewContextOptions ContextOptions => new()
    {
        BaseURL = BaseUrl,
        IgnoreHTTPSErrors = true,
        StorageStatePath = _authStatePath // Reuse auth state
    };

    [TestMethod]
    public async Task Dashboard_LoadsForAuthenticatedUser()
    {
        // Already authenticated, no login needed
        await Page.GotoAsync("/dashboard");
        await WaitForBlazorAsync();

        await Expect(Page.GetByRole(AriaRole.Heading, new() { Name = "Dashboard" }))
            .ToBeVisibleAsync();
    }
}
```

### Role-Based Access

```csharp
[TestMethod]
public async Task AdminPage_DeniedForRegularUser()
{
    await LoginAsUser("regular@example.com", "password");

    await Page.GotoAsync("/admin");
    await WaitForBlazorAsync();

    // Should show access denied
    await Expect(Page.GetByText("Access Denied")).ToBeVisibleAsync();
    // Or redirect to home
    // await Expect(Page).ToHaveURLAsync("/");
}

[TestMethod]
public async Task AdminPage_AllowedForAdmin()
{
    await LoginAsUser("admin@example.com", "adminpassword");

    await Page.GotoAsync("/admin");
    await WaitForBlazorAsync();

    await Expect(Page.GetByRole(AriaRole.Heading, new() { Name = "Admin" }))
        .ToBeVisibleAsync();
}
```

## File Upload Testing

```csharp
[TestMethod]
public async Task FileUpload_UploadsDocument()
{
    await NavigateAndWaitAsync("/documents/upload");

    // Create test file
    var testFilePath = Path.Combine(Path.GetTempPath(), "test-document.pdf");
    await File.WriteAllTextAsync(testFilePath, "Test PDF content");

    try
    {
        // Upload file
        var fileInput = Page.GetByLabel("Choose file");
        await fileInput.SetInputFilesAsync(testFilePath);

        // Verify file selected
        await Expect(Page.GetByText("test-document.pdf")).ToBeVisibleAsync();

        // Submit
        await Page.GetByRole(AriaRole.Button, new() { Name = "Upload" }).ClickAsync();

        // Verify success
        await Expect(Page.GetByRole(AriaRole.Alert)).ToContainTextAsync("uploaded");
    }
    finally
    {
        File.Delete(testFilePath);
    }
}
```

## Real-Time Updates (SignalR)

```csharp
[TestMethod]
public async Task Notifications_UpdateInRealTime()
{
    await NavigateAndWaitAsync("/dashboard");

    // Get initial notification count
    var badge = Page.GetByTestId("notification-badge");
    await Expect(badge).ToHaveTextAsync("3");

    // Trigger notification from another source (API call simulating another user)
    await TriggerNotificationAsync();

    // Badge should update without refresh
    await Expect(badge).ToHaveTextAsync("4", new() { Timeout = 5000 });
}

private async Task TriggerNotificationAsync()
{
    using var client = new HttpClient();
    await client.PostAsync(
        "https://localhost:5001/api/test/trigger-notification",
        new StringContent("{}", Encoding.UTF8, "application/json")
    );
}
```

## Error Handling Patterns

```csharp
[TestMethod]
public async Task NetworkError_ShowsRetryOption()
{
    await NavigateAndWaitAsync("/products");

    // Simulate offline mode
    await Context.SetOfflineAsync(true);

    // Try to load more data
    await Page.GetByRole(AriaRole.Button, new() { Name = "Load More" }).ClickAsync();

    // Should show error with retry
    await Expect(Page.GetByText("Network error")).ToBeVisibleAsync();
    var retryButton = Page.GetByRole(AriaRole.Button, new() { Name = "Retry" });
    await Expect(retryButton).ToBeVisibleAsync();

    // Go back online and retry
    await Context.SetOfflineAsync(false);
    await retryButton.ClickAsync();

    // Should succeed
    await Expect(Page.GetByText("Network error")).ToBeHiddenAsync();
}
```

## Assertions (Auto-Retrying)

Playwright assertions automatically retry until the condition is met or timeout:

```csharp
// Element visibility
await Expect(Page.GetByRole(AriaRole.Alert)).ToBeVisibleAsync();
await Expect(Page.GetByTestId("loading")).ToBeHiddenAsync();

// Text content
await Expect(Page.GetByRole(AriaRole.Heading)).ToHaveTextAsync("Dashboard");
await Expect(Page.GetByTestId("count")).ToContainTextAsync("5");

// Form state
await Expect(Page.GetByLabel("Email")).ToBeEditableAsync();
await Expect(Page.GetByRole(AriaRole.Button, new() { Name = "Save" })).ToBeDisabledAsync();

// Page state
await Expect(Page).ToHaveTitleAsync("My App - Dashboard");
await Expect(Page).ToHaveURLAsync(new Regex("/dashboard$"));

// Count
await Expect(Page.GetByRole(AriaRole.Row)).ToHaveCountAsync(10);

// Custom timeout
await Expect(Page.GetByText("Processing complete"))
    .ToBeVisibleAsync(new() { Timeout = 30000 });
```

## Actionability (Auto-Waiting)

Playwright automatically waits for elements to be actionable before performing actions:

| Action | Waits For |
|--------|-----------|
| `ClickAsync()` | Visible, Stable, Receives Events, Enabled |
| `FillAsync()` | Visible, Enabled, Editable |
| `CheckAsync()` | Visible, Stable, Receives Events, Enabled |
| `SelectOptionAsync()` | Visible, Enabled |

```csharp
// No manual waiting needed - Playwright handles it
await Page.GetByLabel("Email").FillAsync("test@example.com");
await Page.GetByRole(AriaRole.Button, new() { Name = "Submit" }).ClickAsync();
```
