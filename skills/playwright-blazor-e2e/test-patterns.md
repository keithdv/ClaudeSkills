# Common Blazor Test Patterns

## Form Submission

```csharp
[TestMethod]
public async Task LoginForm_SubmitsSuccessfully()
{
    await Page.GotoAsync("/login");
    await WaitForBlazorAsync();

    // Fill form
    await Page.GetByLabel("Email").FillAsync("user@example.com");
    await Page.GetByLabel("Password").FillAsync("password123");

    // Submit
    await Page.GetByRole(AriaRole.Button, new() { Name = "Sign In" }).ClickAsync();

    // Wait for navigation
    await Expect(Page).ToHaveURLAsync("/dashboard");
}
```

## Async Validation

```csharp
[TestMethod]
public async Task EmailField_ShowsValidationError_WhenEmailTaken()
{
    await Page.GotoAsync("/register");
    await WaitForBlazorAsync();

    // Enter duplicate email
    await Page.GetByLabel("Email").FillAsync("existing@example.com");
    await Page.GetByLabel("Email").BlurAsync(); // Trigger validation

    // Wait for async validation (uses IsBusy indicator)
    await Expect(Page.GetByTestId("email-validating")).ToBeHiddenAsync();

    // Check error message
    await Expect(Page.GetByText("Email already in use")).ToBeVisibleAsync();
}
```

## DataGrid Interaction

```csharp
[TestMethod]
public async Task ProductGrid_FiltersAndSorts()
{
    await Page.GotoAsync("/products");
    await WaitForBlazorAsync();

    // Wait for data to load
    await Expect(Page.GetByRole(AriaRole.Row)).ToHaveCountAsync(11); // 10 + header

    // Search
    await Page.GetByPlaceholder("Search").FillAsync("Widget");
    await Expect(Page.GetByRole(AriaRole.Row)).ToHaveCountAsync(4);

    // Sort by clicking header
    await Page.GetByRole(AriaRole.Columnheader, new() { Name = "Price" }).ClickAsync();

    // Verify first row after sort
    var firstDataRow = Page.GetByRole(AriaRole.Row).Nth(1);
    await Expect(firstDataRow).ToContainTextAsync("$9.99");
}
```

## Dialog Handling

```csharp
[TestMethod]
public async Task DeleteButton_ShowsConfirmation_ThenDeletes()
{
    await Page.GotoAsync("/products");
    await WaitForBlazorAsync();

    // Click delete on specific row
    var productRow = Page.GetByRole(AriaRole.Row).Filter(new() { HasText = "Widget Pro" });
    await productRow.GetByRole(AriaRole.Button, new() { Name = "Delete" }).ClickAsync();

    // Wait for dialog
    var dialog = Page.GetByRole(AriaRole.Dialog);
    await Expect(dialog).ToBeVisibleAsync();
    await Expect(dialog).ToContainTextAsync("Are you sure");

    // Confirm deletion
    await dialog.GetByRole(AriaRole.Button, new() { Name = "Delete" }).ClickAsync();

    // Verify dialog closed and item removed
    await Expect(dialog).ToBeHiddenAsync();
    await Expect(Page.GetByText("Widget Pro")).ToBeHiddenAsync();

    // Verify snackbar
    await Expect(Page.GetByRole(AriaRole.Alert)).ToContainTextAsync("deleted successfully");
}
```

## Navigation and Routing

```csharp
[TestMethod]
public async Task Navigation_BreadcrumbsWork()
{
    await Page.GotoAsync("/products/123");
    await WaitForBlazorAsync();

    // Click breadcrumb
    await Page.GetByRole(AriaRole.Link, new() { Name = "Products" }).ClickAsync();

    // Verify navigation
    await Expect(Page).ToHaveURLAsync("/products");
}

[TestMethod]
public async Task Navigation_BackButtonPreservesState()
{
    await Page.GotoAsync("/products");
    await WaitForBlazorAsync();

    // Apply filter
    await Page.GetByPlaceholder("Search").FillAsync("Widget");
    await Expect(Page.GetByRole(AriaRole.Row)).ToHaveCountAsync(4);

    // Navigate to detail
    await Page.GetByRole(AriaRole.Link, new() { Name = "Widget Pro" }).ClickAsync();
    await Expect(Page).ToHaveURLAsync(new Regex(@"/products/\d+"));

    // Go back
    await Page.GoBackAsync();

    // Verify filter preserved
    await Expect(Page.GetByPlaceholder("Search")).ToHaveValueAsync("Widget");
}
```

## File Upload

```csharp
[TestMethod]
public async Task ProfileForm_UploadsAvatar()
{
    await Page.GotoAsync("/profile");
    await WaitForBlazorAsync();

    // Upload file
    var fileInput = Page.GetByLabel("Avatar");
    await fileInput.SetInputFilesAsync("test-data/avatar.png");

    // Verify preview
    await Expect(Page.GetByAltText("Avatar preview")).ToBeVisibleAsync();

    // Save
    await Page.GetByRole(AriaRole.Button, new() { Name = "Save" }).ClickAsync();

    // Verify success
    await Expect(Page.GetByRole(AriaRole.Alert)).ToContainTextAsync("saved");
}
```

## Tabs and Accordions

```csharp
[TestMethod]
public async Task ProductDetails_TabsSwitch()
{
    await Page.GotoAsync("/products/123");
    await WaitForBlazorAsync();

    // Verify default tab
    await Expect(Page.GetByRole(AriaRole.Tab, new() { Name = "Details" }))
        .ToHaveAttributeAsync("aria-selected", "true");

    // Switch tab
    await Page.GetByRole(AriaRole.Tab, new() { Name = "Reviews" }).ClickAsync();

    // Verify new tab selected and content visible
    await Expect(Page.GetByRole(AriaRole.Tab, new() { Name = "Reviews" }))
        .ToHaveAttributeAsync("aria-selected", "true");
    await Expect(Page.GetByTestId("reviews-panel")).ToBeVisibleAsync();
}
```

## Infinite Scroll / Virtualization

```csharp
[TestMethod]
public async Task ProductList_LoadsMoreOnScroll()
{
    await Page.GotoAsync("/products");
    await WaitForBlazorAsync();

    // Initial load
    await Expect(Page.GetByRole(AriaRole.Row)).ToHaveCountAsync(21); // 20 + header

    // Scroll to bottom
    await Page.GetByRole(AriaRole.Row).Last.ScrollIntoViewIfNeededAsync();

    // Wait for more items
    await Expect(Page.GetByRole(AriaRole.Row)).ToHaveCountAsync(41);
}
```

## Error States

```csharp
[TestMethod]
public async Task ProductList_ShowsErrorOnApiFailure()
{
    // Intercept API to return error
    await Page.RouteAsync("**/api/products", route =>
        route.FulfillAsync(new() { Status = 500 }));

    await Page.GotoAsync("/products");
    await WaitForBlazorAsync();

    // Verify error displayed
    await Expect(Page.GetByRole(AriaRole.Alert)).ToContainTextAsync("Failed to load");
    await Expect(Page.GetByRole(AriaRole.Button, new() { Name = "Retry" })).ToBeVisibleAsync();
}
```

## Authentication Flows

```csharp
[TestMethod]
public async Task ProtectedPage_RedirectsToLogin()
{
    await Page.GotoAsync("/admin/settings");

    // Should redirect to login
    await Expect(Page).ToHaveURLAsync(new Regex(@"/login\?returnUrl="));
}

[TestMethod]
public async Task Login_RedirectsToReturnUrl()
{
    await Page.GotoAsync("/login?returnUrl=/admin/settings");
    await WaitForBlazorAsync();

    // Login
    await Page.GetByLabel("Email").FillAsync("admin@example.com");
    await Page.GetByLabel("Password").FillAsync("password");
    await Page.GetByRole(AriaRole.Button, new() { Name = "Sign In" }).ClickAsync();

    // Should redirect to original destination
    await Expect(Page).ToHaveURLAsync("/admin/settings");
}
```

## Real-time Updates (SignalR)

```csharp
[TestMethod]
public async Task Dashboard_ReceivesRealTimeUpdates()
{
    await Page.GotoAsync("/dashboard");
    await WaitForBlazorAsync();

    var initialValue = await Page.GetByTestId("active-users").TextContentAsync();

    // Trigger server event (via API or another browser context)
    await TriggerServerEvent("user-connected");

    // Verify update
    await Expect(Page.GetByTestId("active-users")).Not.ToHaveTextAsync(initialValue);
}
```
