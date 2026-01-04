# MudBlazor Feedback Components

## MudDialog

### Dialog Service Setup

The `IDialogService` requires `MudDialogProvider` in your layout:

```razor
@* MainLayout.razor *@
<MudDialogProvider />
```

### Creating a Dialog Component

```razor
@* ConfirmDialog.razor *@
<MudDialog>
    <DialogContent>
        <MudText Typo="Typo.body1">@ContentText</MudText>
    </DialogContent>
    <DialogActions>
        <MudButton OnClick="Cancel">Cancel</MudButton>
        <MudButton Color="@ButtonColor" Variant="Variant.Filled" OnClick="Confirm">
            @ButtonText
        </MudButton>
    </DialogActions>
</MudDialog>

@code {
    [CascadingParameter] private IMudDialogInstance MudDialog { get; set; }

    [Parameter] public string ContentText { get; set; }
    [Parameter] public string ButtonText { get; set; } = "Confirm";
    [Parameter] public Color ButtonColor { get; set; } = Color.Primary;

    private void Cancel() => MudDialog.Cancel();
    private void Confirm() => MudDialog.Close(DialogResult.Ok(true));
}
```

### Opening Dialogs

```csharp
@inject IDialogService DialogService

private async Task ShowConfirmation()
{
    var parameters = new DialogParameters<ConfirmDialog>
    {
        { x => x.ContentText, "Are you sure you want to delete this item?" },
        { x => x.ButtonText, "Delete" },
        { x => x.ButtonColor, Color.Error }
    };

    var options = new DialogOptions
    {
        CloseButton = true,
        MaxWidth = MaxWidth.Small,
        FullWidth = true
    };

    var dialog = await DialogService.ShowAsync<ConfirmDialog>("Confirm Delete", parameters, options);
    var result = await dialog.Result;

    if (!result.Canceled)
    {
        // User confirmed
        await DeleteItem();
    }
}
```

### Dialog Options

| Option | Description |
|--------|-------------|
| `CloseButton` | Show close button in header |
| `MaxWidth` | Maximum width (ExtraSmall to ExtraExtraLarge) |
| `FullWidth` | Expand to MaxWidth |
| `Position` | DialogPosition (Center, TopCenter, etc.) |
| `NoHeader` | Hide dialog header |
| `BackdropClick` | Close on backdrop click |
| `CloseOnEscapeKey` | Close on Escape key |

### Form Dialog

```razor
@* EditCustomerDialog.razor *@
<MudDialog>
    <TitleContent>
        <MudText Typo="Typo.h6">
            <MudIcon Icon="@Icons.Material.Filled.Edit" Class="mr-2" />
            Edit Customer
        </MudText>
    </TitleContent>
    <DialogContent>
        <MudForm @ref="form" @bind-IsValid="isValid">
            <MudGrid Spacing="3">
                <MudItem xs="12" sm="6">
                    <MudTextField @bind-Value="Customer.FirstName"
                                  Label="First Name"
                                  Required="true"
                                  RequiredError="First name is required"
                                  Variant="Variant.Outlined" />
                </MudItem>
                <MudItem xs="12" sm="6">
                    <MudTextField @bind-Value="Customer.LastName"
                                  Label="Last Name"
                                  Required="true"
                                  RequiredError="Last name is required"
                                  Variant="Variant.Outlined" />
                </MudItem>
                <MudItem xs="12">
                    <MudTextField @bind-Value="Customer.Email"
                                  Label="Email"
                                  Required="true"
                                  Validation="@(new EmailAddressAttribute())"
                                  Variant="Variant.Outlined" />
                </MudItem>
            </MudGrid>
        </MudForm>
    </DialogContent>
    <DialogActions>
        <MudButton OnClick="Cancel">Cancel</MudButton>
        <MudButton Color="Color.Primary"
                   Variant="Variant.Filled"
                   Disabled="@(!isValid || isSaving)"
                   OnClick="Save">
            @if (isSaving)
            {
                <MudProgressCircular Size="Size.Small" Indeterminate="true" Class="mr-2" />
            }
            Save
        </MudButton>
    </DialogActions>
</MudDialog>

@code {
    [CascadingParameter] private IMudDialogInstance MudDialog { get; set; }
    [Parameter] public Customer Customer { get; set; }

    private MudForm form;
    private bool isValid;
    private bool isSaving;

    private void Cancel() => MudDialog.Cancel();

    private async Task Save()
    {
        await form.Validate();
        if (!isValid) return;

        isSaving = true;
        StateHasChanged();

        try
        {
            // Save logic
            MudDialog.Close(DialogResult.Ok(Customer));
        }
        finally
        {
            isSaving = false;
        }
    }
}
```

### Inline Dialog

For dialogs embedded in a component rather than opened via service:

```razor
<MudButton OnClick="@(() => _visible = true)">Open Dialog</MudButton>

<MudDialog @bind-Visible="_visible" Options="_dialogOptions">
    <DialogContent>
        <MudText>This is an inline dialog</MudText>
    </DialogContent>
    <DialogActions>
        <MudButton OnClick="@(() => _visible = false)">Close</MudButton>
    </DialogActions>
</MudDialog>

@code {
    private bool _visible;
    private DialogOptions _dialogOptions = new() { FullWidth = true };
}
```

---

## MudSnackbar

### Basic Usage

```csharp
@inject ISnackbar Snackbar

// Success message
Snackbar.Add("Record saved successfully!", Severity.Success);

// Error message
Snackbar.Add("Failed to save record. Please try again.", Severity.Error);

// Warning message
Snackbar.Add("Your session will expire in 5 minutes.", Severity.Warning);

// Info message
Snackbar.Add("New updates are available.", Severity.Info);
```

### Severity Levels

| Severity | Use Case |
|----------|----------|
| `Severity.Normal` | Default notifications |
| `Severity.Info` | Informational messages |
| `Severity.Success` | Positive confirmations |
| `Severity.Warning` | Cautionary alerts |
| `Severity.Error` | Error notifications |

### With Actions

```csharp
Snackbar.Add("Record deleted.", Severity.Normal, config =>
{
    config.Action = "Undo";
    config.ActionColor = Color.Primary;
    config.Onclick = snackbar =>
    {
        // Undo logic
        return Task.CompletedTask;
    };
    config.RequireInteraction = true;
});
```

### Custom Configuration

```csharp
Snackbar.Add("Processing complete!", Severity.Success, config =>
{
    config.ShowCloseIcon = true;
    config.VisibleStateDuration = 10000;
    config.Icon = Icons.Material.Filled.CheckCircle;
    config.IconSize = Size.Large;
    config.IconColor = Color.Success;
});
```

### Global Configuration

**Program.cs:**
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

### Position Options

| Position | Constant |
|----------|----------|
| Top Left | `Defaults.Classes.Position.TopLeft` |
| Top Center | `Defaults.Classes.Position.TopCenter` |
| Top Right | `Defaults.Classes.Position.TopRight` |
| Bottom Left | `Defaults.Classes.Position.BottomLeft` |
| Bottom Center | `Defaults.Classes.Position.BottomCenter` |
| Bottom Right | `Defaults.Classes.Position.BottomRight` |

### Programmatic Control

```csharp
private Snackbar _snackbar;

void ShowPersistent()
{
    _snackbar = Snackbar.Add("Long running operation...", Severity.Info, config =>
    {
        config.VisibleStateDuration = int.MaxValue;
        config.RequireInteraction = true;
    });
}

void HideSnackbar()
{
    Snackbar.Remove(_snackbar);
}
```

### Close After Navigation

```csharp
Snackbar.Add("Navigating to new page...", Severity.Info, config =>
{
    config.CloseAfterNavigation = true;
});
```

---

## MudAlert

### Inline Alerts

```razor
@if (hasError)
{
    <MudAlert Severity="Severity.Error" Class="mb-4" ShowCloseIcon="true"
              CloseIconClicked="() => hasError = false">
        @errorMessage
    </MudAlert>
}

@if (hasWarning)
{
    <MudAlert Severity="Severity.Warning" Variant="Variant.Outlined" Class="mb-4">
        <MudText><strong>Warning:</strong> @warningMessage</MudText>
    </MudAlert>
}

<MudAlert Severity="Severity.Info" Variant="Variant.Filled" Dense="true" Class="mb-4">
    Tip: You can use keyboard shortcuts to navigate faster.
</MudAlert>
```

### Alert Variants

| Variant | Appearance |
|---------|------------|
| `Variant.Text` | Text with colored background |
| `Variant.Filled` | Solid colored background |
| `Variant.Outlined` | Border with subtle background |

### With Icons

```razor
<MudAlert Severity="Severity.Success" Icon="@Icons.Material.Filled.CheckCircle">
    Operation completed successfully!
</MudAlert>

<MudAlert Severity="Severity.Error" NoIcon="true">
    Error without icon.
</MudAlert>
```

---

## MudProgressLinear

### Basic Progress

```razor
@* Indeterminate *@
<MudProgressLinear Color="Color.Primary" Indeterminate="true" />

@* Determinate *@
<MudProgressLinear Color="Color.Primary" Value="@progress" />
```

### With Buffer

```razor
<MudProgressLinear Color="Color.Primary" Value="@progress" Buffer="true" BufferValue="@bufferProgress" />
```

### Page Loading Pattern

```razor
@if (isLoading)
{
    <MudProgressLinear Color="Color.Primary" Indeterminate="true" Class="my-4" />
}
else
{
    @* Content *@
}
```

---

## MudProgressCircular

### Basic Usage

```razor
@* Indeterminate *@
<MudProgressCircular Color="Color.Primary" Indeterminate="true" />

@* Determinate *@
<MudProgressCircular Color="Color.Primary" Value="@progress" />
```

### In Button

```razor
<MudButton Variant="Variant.Filled"
           Color="Color.Primary"
           Disabled="@isSaving"
           OnClick="Save">
    @if (isSaving)
    {
        <MudProgressCircular Size="Size.Small" Indeterminate="true" Class="mr-2" />
    }
    Save
</MudButton>
```

### Sizes

```razor
<MudProgressCircular Size="Size.Small" Indeterminate="true" />
<MudProgressCircular Size="Size.Medium" Indeterminate="true" />
<MudProgressCircular Size="Size.Large" Indeterminate="true" />
```

---

## MudOverlay

### Loading Overlay

```razor
<MudOverlay Visible="@isLoading" DarkBackground="true" Absolute="true">
    <MudProgressCircular Color="Color.Primary" Indeterminate="true" />
</MudOverlay>
```

### Blocking Overlay

```razor
<MudPaper Class="position-relative pa-4" Style="height: 200px;">
    <MudText>Content behind overlay</MudText>

    <MudOverlay Visible="@isBlocked" DarkBackground="true" Absolute="true">
        <MudStack AlignItems="AlignItems.Center">
            <MudProgressCircular Color="Color.Secondary" Indeterminate="true" />
            <MudText Color="Color.Secondary">Processing...</MudText>
        </MudStack>
    </MudOverlay>
</MudPaper>
```

---

## MudSkeleton

### Loading Placeholder

```razor
@if (isLoading)
{
    <MudCard>
        <MudCardHeader>
            <CardHeaderAvatar>
                <MudSkeleton SkeletonType="SkeletonType.Circle" Width="40px" Height="40px" />
            </CardHeaderAvatar>
            <CardHeaderContent>
                <MudSkeleton Width="60%" />
                <MudSkeleton Width="40%" />
            </CardHeaderContent>
        </MudCardHeader>
        <MudCardContent>
            <MudSkeleton SkeletonType="SkeletonType.Rectangle" Height="200px" />
        </MudCardContent>
    </MudCard>
}
else
{
    @* Actual content *@
}
```

### Skeleton Types

```razor
<MudSkeleton SkeletonType="SkeletonType.Text" />
<MudSkeleton SkeletonType="SkeletonType.Circle" Width="40px" Height="40px" />
<MudSkeleton SkeletonType="SkeletonType.Rectangle" Height="200px" />
```

---

## Common Patterns

### Error Handling with Snackbar

```csharp
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
    Logger.LogError(ex, "Save operation failed");
}
```

### Loading State Pattern

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

### Delete Confirmation Pattern

```csharp
private async Task ConfirmDelete(Item item)
{
    var parameters = new DialogParameters<ConfirmDialog>
    {
        { x => x.ContentText, $"Are you sure you want to delete '{item.Name}'?" },
        { x => x.ButtonText, "Delete" },
        { x => x.ButtonColor, Color.Error }
    };

    var dialog = await DialogService.ShowAsync<ConfirmDialog>("Confirm Delete", parameters);
    var result = await dialog.Result;

    if (!result.Canceled)
    {
        try
        {
            await ItemService.DeleteAsync(item.Id);
            Snackbar.Add("Item deleted successfully!", Severity.Success);
            await RefreshData();
        }
        catch (Exception)
        {
            Snackbar.Add("Failed to delete item.", Severity.Error);
        }
    }
}
```
