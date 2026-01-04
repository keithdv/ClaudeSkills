# MudBlazor Best Practices

## Form Development

### Always Provide Labels

Every form field should have a descriptive label for accessibility:

```razor
@* GOOD *@
<MudTextField @bind-Value="model.Email" Label="Email Address" />

@* BAD *@
<MudTextField @bind-Value="model.Email" Placeholder="Enter email" />
```

### Use HelperText for Constraints

Communicate field constraints proactively:

```razor
<MudTextField @bind-Value="model.Password"
              Label="Password"
              HelperText="Minimum 8 characters with uppercase, lowercase, and number"
              Counter="50"
              MaxLength="50" />
```

### Choose Appropriate Update Timing

| Scenario | Setting |
|----------|---------|
| Search/filter fields | `Immediate="true" DebounceInterval="300"` |
| Form fields with validation | `Immediate="true"` |
| Fields triggering API calls | `DebounceInterval="500"` |
| Simple forms | Default (on blur/enter) |

### Enable Real-Time Validation

```razor
<MudTextField @bind-Value="model.Email"
              Label="Email"
              Validation="@(new EmailAddressAttribute())"
              Immediate="true" />  @* Validates as user types *@
```

---

## Data Tables

### Use Server-Side for Large Datasets

For more than a few hundred rows, always use server-side data loading:

```razor
<MudDataGrid T="Product"
             ServerData="LoadServerData"
             Loading="@isLoading"
             RowsPerPage="25">
```

### Enable Virtualization for Large Lists

```razor
<MudDataGrid T="Product"
             Items="@largeDataset"
             Virtualize="true"
             Height="400px">
```

### Debounce Search Fields

```razor
<MudTextField @bind-Value="searchString"
              Immediate="true"
              DebounceInterval="300"
              OnDebounceIntervalElapsed="@(async () => await table.ReloadServerData())" />
```

### Implement Object Equality

For complex objects in selection components:

```razor
@code {
    public class Customer : IEquatable<Customer>
    {
        public int Id { get; set; }
        public string Name { get; set; }

        public bool Equals(Customer other) => Id == other?.Id;
        public override int GetHashCode() => Id.GetHashCode();
    }
}
```

Or provide a comparer:

```razor
<MudDataGrid T="Product" Comparer="@(new ProductComparer())">
```

---

## Validation

### MudForm vs EditForm

**MudForm:**
- Use `OnClick` handlers on buttons
- Call `await form.Validate()` before processing
- Never use `ButtonType.Submit`

**EditForm:**
- Use `OnValidSubmit` handler
- Use `ButtonType.Submit` on buttons

### Display Errors Inline

```razor
<MudTextField @bind-Value="model.Email"
              Error="@hasEmailError"
              ErrorText="@emailErrorMessage" />
```

### Show Form-Level Errors

```razor
@if (hasError)
{
    <MudAlert Severity="Severity.Error" Class="mb-4" ShowCloseIcon="true"
              CloseIconClicked="() => hasError = false">
        @errorMessage
    </MudAlert>
}
```

---

## Feedback & Loading States

### Always Show Loading State

```razor
@if (isLoading)
{
    <MudProgressLinear Indeterminate="true" Color="Color.Primary" />
}
else if (hasError)
{
    <MudAlert Severity="Severity.Error">@errorMessage</MudAlert>
}
else
{
    @* Main content *@
}
```

### Button Loading Indicator

```razor
<MudButton Disabled="@(isSaving || !isValid)" OnClick="Save">
    @if (isSaving)
    {
        <MudProgressCircular Size="Size.Small" Indeterminate="true" Class="mr-2" />
    }
    Save
</MudButton>
```

### Immediate User Feedback

Every user action should provide visible feedback:

```csharp
try
{
    await Service.SaveAsync(model);
    Snackbar.Add("Saved successfully!", Severity.Success);
}
catch (Exception)
{
    Snackbar.Add("Save failed. Please try again.", Severity.Error);
}
```

---

## Dialog Handling

### Always Check Dialog Result

```csharp
var result = await dialog.Result;
if (!result.Canceled)  // IMPORTANT: Always check!
{
    var data = (MyType)result.Data;
    // Process data
}
```

### Use Typed Parameters

```csharp
var parameters = new DialogParameters<MyDialog>
{
    { x => x.Item, myItem },          // Type-safe
    { x => x.Title, "Edit Item" }
};
```

### Standard Dialog Options

```csharp
var options = new DialogOptions
{
    CloseButton = true,
    MaxWidth = MaxWidth.Medium,
    FullWidth = true,
    CloseOnEscapeKey = true
};
```

---

## Layout & Styling

### Use MudBlazor Utilities Before Custom CSS

```razor
@* GOOD - Use built-in classes *@
<MudPaper Class="pa-4 mb-3">

@* AVOID - Custom CSS for standard spacing *@
<MudPaper Style="padding: 16px; margin-bottom: 12px;">
```

### Responsive Grid Patterns

```razor
@* Mobile first: stack, then side-by-side *@
<MudGrid>
    <MudItem xs="12" sm="6" md="4">Item 1</MudItem>
    <MudItem xs="12" sm="6" md="4">Item 2</MudItem>
    <MudItem xs="12" sm="12" md="4">Item 3</MudItem>
</MudGrid>
```

### Consistent Variant Usage

Pick a variant and use it consistently:

```razor
@* Forms typically use Outlined *@
<MudTextField Variant="Variant.Outlined" />
<MudSelect Variant="Variant.Outlined" />
<MudDatePicker Variant="Variant.Outlined" />
```

---

## Performance

### Avoid Unnecessary Re-renders

Use `@key` directive for lists:

```razor
@foreach (var item in items)
{
    <ItemComponent @key="item.Id" Item="item" />
}
```

### Minimize StateHasChanged Calls

Only call when necessary:

```csharp
// Let Blazor handle binding updates automatically
// Only call StateHasChanged for external changes
```

### Lazy Load Data

```csharp
protected override async Task OnInitializedAsync()
{
    // Load initial data
    products = await ProductService.GetTopProductsAsync(10);
}

// Load more on demand
private async Task LoadMore()
{
    var more = await ProductService.GetMoreProductsAsync(skip, take);
    products.AddRange(more);
}
```

---

## Common Anti-Patterns

### 1. ButtonType.Submit with MudForm

```razor
@* WRONG *@
<MudForm>
    <MudButton ButtonType="ButtonType.Submit">Save</MudButton>
</MudForm>

@* CORRECT *@
<MudForm @ref="form">
    <MudButton OnClick="Submit">Save</MudButton>
</MudForm>
```

### 2. Missing Providers

All four providers are required:

```razor
@* All must be present in MainLayout *@
<MudThemeProvider />
<MudPopoverProvider />
<MudDialogProvider />
<MudSnackbarProvider />
```

### 3. Complex Objects Without Equality

```csharp
// WRONG - Selection won't work properly
public class Product { public int Id; public string Name; }

// CORRECT - Implement IEquatable or provide Comparer
public class Product : IEquatable<Product>
{
    public int Id { get; set; }
    public string Name { get; set; }
    public bool Equals(Product other) => Id == other?.Id;
    public override int GetHashCode() => Id.GetHashCode();
}
```

### 4. Not Handling Dialog Cancellation

```csharp
// WRONG - Will throw if canceled
var result = await dialog.Result;
var data = (MyType)result.Data;  // NullReferenceException if canceled!

// CORRECT
var result = await dialog.Result;
if (!result.Canceled)
{
    var data = (MyType)result.Data;
}
```

### 5. Non-Nullable DateTime in DatePicker

```razor
@* WRONG - Can't clear the date *@
<MudDatePicker @bind-Date="requiredDate" />  @* DateTime *@

@* CORRECT - Use nullable for optional dates *@
<MudDatePicker @bind-Date="optionalDate" />  @* DateTime? *@
```

### 6. Inline Styles Instead of Spacing Classes

```razor
@* WRONG *@
<MudPaper Style="margin-bottom: 16px; padding: 24px;">

@* CORRECT *@
<MudPaper Class="mb-4 pa-6">
```

---

## Accessibility

### Keyboard Navigation

MudBlazor components support keyboard navigation by default. Don't break it:

- Don't override `tabindex` without reason
- Ensure custom components are keyboard accessible
- Test with Tab key navigation

### Screen Reader Support

- Always use `Label` for form fields
- Provide meaningful text content
- Use ARIA attributes when needed

### Color Contrast

MudBlazor's default theme meets WCAG guidelines. When customizing:

- Ensure text contrast ratio is at least 4.5:1
- Don't rely solely on color to convey information
- Test with color blindness simulators

---

## Error Handling Pattern

```csharp
private bool isLoading;
private bool hasError;
private string errorMessage = string.Empty;

private async Task LoadData()
{
    isLoading = true;
    hasError = false;

    try
    {
        data = await Service.GetDataAsync();
    }
    catch (Exception ex)
    {
        hasError = true;
        errorMessage = "Failed to load data. Please try again.";
        Logger.LogError(ex, "Data load failed");
    }
    finally
    {
        isLoading = false;
    }
}

private async Task SaveData()
{
    try
    {
        await Service.SaveAsync(model);
        Snackbar.Add("Saved successfully!", Severity.Success);
        NavigationManager.NavigateTo("/list");
    }
    catch (ValidationException ex)
    {
        foreach (var error in ex.Errors)
        {
            Snackbar.Add(error.ErrorMessage, Severity.Warning);
        }
    }
    catch (Exception ex)
    {
        Snackbar.Add("An error occurred. Please try again.", Severity.Error);
        Logger.LogError(ex, "Save failed");
    }
}
```

---

## Checklist Before Production

- [ ] All form fields have labels
- [ ] Validation provides clear error messages
- [ ] Loading states are shown for async operations
- [ ] Error states are handled and displayed
- [ ] Complex objects implement equality
- [ ] Server-side data for large datasets
- [ ] Dialog results are checked for cancellation
- [ ] All four providers are in MainLayout
- [ ] Theme works in both light and dark modes
- [ ] Keyboard navigation works
- [ ] Performance tested with realistic data volumes
