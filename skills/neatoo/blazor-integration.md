# Neatoo Blazor Integration Reference

## Overview

Neatoo entities implement `INotifyPropertyChanged`, enabling automatic UI updates in Blazor. The `Neatoo.Blazor.MudNeatoo` package provides MudBlazor-integrated components for seamless entity binding.

## Automatic UI Binding

All Neatoo entities inherit from `ValidateBase<T>` which implements `INotifyPropertyChanged`:

```razor
@page "/person/edit/{Id:guid}"
@inject IPersonFactory PersonFactory

<h1>Edit Person</h1>

<EditForm Model="@_person">
    <div class="form-group">
        <label>First Name</label>
        <InputText @bind-Value="_person.FirstName" class="form-control" />
    </div>

    <div class="form-group">
        <label>Last Name</label>
        <InputText @bind-Value="_person.LastName" class="form-control" />
    </div>

    <button type="button" @onclick="Save" disabled="@(!_person.IsSavable)">
        Save
    </button>
</EditForm>

@code {
    [Parameter] public Guid Id { get; set; }

    private IPerson _person = default!;

    protected override async Task OnInitializedAsync()
    {
        _person = await PersonFactory.Fetch(Id);
    }

    private async Task Save()
    {
        await _person.WaitForTasks();
        if (_person.IsSavable)
        {
            _person = await PersonFactory.Save(_person);
        }
    }
}
```

## MudNeatoo Components

### Installation

```bash
dotnet add package Neatoo.Blazor.MudNeatoo
```

### Namespaces

Add these to your `_Imports.razor`:

```razor
@using Neatoo.Blazor.MudNeatoo.Components
@using Neatoo.Blazor.MudNeatoo.Validation
```

### MudNeatooTextField

**IMPORTANT**: MudNeatoo components use `EntityProperty` parameter with the entity indexer, not a `For` expression.

```razor
@* Access property via entity indexer *@
<MudNeatooTextField T="string?"
                    EntityProperty="@(_person[nameof(_person.FirstName)])"
                    Placeholder="First Name" />

<MudNeatooTextField T="string?"
                    EntityProperty="@(_person[nameof(_person.Email)])"
                    Placeholder="Email" />
```

**Parameters:**
- `EntityProperty` - The entity property from indexer (required)
- `T` - Type parameter for the value type
- `Placeholder` - Placeholder text
- `HelperText` - Helper text below the field
- `Variant` - MudBlazor variant styling
- `Margin` - MudBlazor margin setting
- `Lines` - For multiline text
- `Adornment`, `AdornmentIcon`, `AdornmentColor` - Icon adornments
- `Class` - CSS class

**Features:**
- Automatic two-way binding via entity property
- Displays validation messages from PropertyMessages
- Shows busy indicator during async validation
- Applies error styling when invalid

### MudNeatooNumericField

```razor
<MudNeatooNumericField T="int"
                       EntityProperty="@(_orderLine[nameof(_orderLine.Quantity)])"
                       Placeholder="Quantity" />

<MudNeatooNumericField T="decimal"
                       EntityProperty="@(_orderLine[nameof(_orderLine.UnitPrice)])"
                       Placeholder="Unit Price"
                       Adornment="Adornment.Start"
                       AdornmentIcon="@Icons.Material.Filled.AttachMoney" />
```

### MudNeatooDatePicker

```razor
<MudNeatooDatePicker EntityProperty="@(_order[nameof(_order.OrderDate)])"
                     Placeholder="Order Date" />

<MudNeatooDatePicker EntityProperty="@(_order[nameof(_order.ShipDate)])"
                     Placeholder="Ship Date" />
```

### MudNeatooSelect

```razor
@* Enum binding *@
<MudNeatooSelect T="PhoneType"
                 EntityProperty="@(_phone[nameof(_phone.PhoneType)])">
    @foreach (PhoneType type in Enum.GetValues<PhoneType>())
    {
        <MudSelectItem Value="@type">@type</MudSelectItem>
    }
</MudNeatooSelect>

@* Collection binding *@
<MudNeatooSelect T="Guid?"
                 EntityProperty="@(_order[nameof(_order.CustomerId)])">
    @foreach (var customer in _customers)
    {
        <MudSelectItem Value="@customer.Id">@customer.Name</MudSelectItem>
    }
</MudNeatooSelect>
```

### MudNeatooCheckBox

```razor
<MudNeatooCheckBox T="bool"
                   EntityProperty="@(_order[nameof(_order.IsRush)])" />

<MudNeatooCheckBox T="bool"
                   EntityProperty="@(_person[nameof(_person.IsActive)])"
                   Color="Color.Primary" />
```

### NeatooValidationSummary

```razor
<NeatooValidationSummary Entity="_person" />

@* With custom styling *@
<NeatooValidationSummary Entity="_person"
                         Class="validation-errors"
                         IncludePropertyNames="true" />
```

**Parameters:**
- `Entity` - The entity implementing IValidateMetaProperties (required)
- `ShowHeader` - Show/hide the header
- `HeaderText` - Custom header text
- `Variant` - MudBlazor variant styling
- `Dense` - Dense display mode
- `Elevation` - Paper elevation
- `Class` - CSS class
- `IncludePropertyNames` - Include property names with messages

## Manual Binding Patterns

### Property Binding

```razor
<input @bind="_person.FirstName" />
<input @bind="_person.LastName" />
```

### Accessing Property Meta-Properties

```razor
@{
    var emailProp = _person[nameof(_person.Email)];
}

<div class="form-group @(emailProp.IsValid ? "" : "has-error")">
    <label>Email</label>
    <input @bind="_person.Email"
           disabled="@emailProp.IsBusy" />

    @if (emailProp.IsBusy)
    {
        <span class="spinner">Validating...</span>
    }

    @if (!emailProp.IsValid)
    {
        @foreach (var msg in emailProp.PropertyMessages)
        {
            <span class="text-danger">@msg.Message</span>
        }
    }

    @if (emailProp.IsModified)
    {
        <span class="badge">Modified</span>
    }
</div>
```

### Property Messages Display

```razor
<div class="form-group">
    <label>Email</label>
    <input @bind="_person.Email"
           class="@(GetInputClass(nameof(_person.Email)))" />

    @foreach (var msg in GetMessagesFor(nameof(_person.Email)))
    {
        <span class="text-danger">@msg.Message</span>
    }
</div>

@code {
    private string GetInputClass(string propertyName)
    {
        return _person[propertyName].IsValid
            ? "form-control"
            : "form-control is-invalid";
    }

    private IEnumerable<IPropertyMessage> GetMessagesFor(string propertyName)
    {
        return _person.PropertyMessages
            .Where(m => m.Property.Name == propertyName);
    }
}
```

## Save Button Pattern

### Basic Save Button

```razor
<button @onclick="Save"
        disabled="@(!_person.IsSavable)"
        class="btn btn-primary">
    Save
</button>
```

### Complete Implementation

```razor
<button @onclick="HandleSave"
        disabled="@(!CanSave)"
        class="btn btn-primary">
    @if (_isSaving)
    {
        <span class="spinner-border spinner-border-sm"></span>
        <span>Saving...</span>
    }
    else if (_person.IsBusy)
    {
        <span>Validating...</span>
    }
    else
    {
        <span>Save</span>
    }
</button>

@if (!_person.IsModified && !_person.IsNew)
{
    <span class="text-muted ms-2">No changes</span>
}

@code {
    private bool _isSaving;

    private bool CanSave => !_isSaving && _person.IsSavable;

    private async Task HandleSave()
    {
        await _person.WaitForTasks();

        if (!_person.IsSavable)
        {
            StateHasChanged();
            return;
        }

        try
        {
            _isSaving = true;
            StateHasChanged();

            // CRITICAL: Reassign to capture new instance
            _person = await PersonFactory.Save(_person);

            NavigationManager.NavigateTo("/persons");
        }
        catch (Exception ex)
        {
            Snackbar.Add($"Save failed: {ex.Message}", Severity.Error);
        }
        finally
        {
            _isSaving = false;
        }
    }
}
```

## Critical: Reassign After Save

**IMPORTANT**: Save returns a new instance. You must reassign:

```razor
@code {
    private IPerson? _person;

    // WRONG - stale reference
    private async Task HandleSave()
    {
        await PersonFactory.Save(_person);
        // _person still has old values, wrong ID
        NavigationManager.NavigateTo($"/person/{_person.Id}");  // Bad ID!
    }

    // CORRECT - capture new instance
    private async Task HandleSave()
    {
        _person = await PersonFactory.Save(_person);
        // _person now has server-generated ID and values
        NavigationManager.NavigateTo($"/person/{_person.Id}");  // Correct!
    }
}
```

## Busy State Handling

### Entity-Level

```razor
<div class="@(_person.IsBusy ? "loading" : "")">
    <EditForm Model="@_person">
        @* Form fields *@

        <button disabled="@(_person.IsBusy || !_person.IsSavable)">
            @if (_person.IsBusy)
            {
                <span class="spinner-border spinner-border-sm"></span>
                <span>Validating...</span>
            }
            else
            {
                <span>Save</span>
            }
        </button>
    </EditForm>
</div>
```

### Property-Level

```razor
<div class="form-group">
    <label>Email</label>
    <div class="input-group">
        <input @bind="_person.Email"
               disabled="@_person[nameof(_person.Email)].IsBusy" />

        @if (_person[nameof(_person.Email)].IsBusy)
        {
            <div class="input-group-append">
                <span class="spinner-border spinner-border-sm"></span>
            </div>
        }
    </div>
    <small class="text-muted">
        @(_person[nameof(_person.Email)].IsBusy
            ? "Checking availability..."
            : "")
    </small>
</div>
```

## Collection Binding

### Basic Table

```razor
<table class="table">
    <thead>
        <tr>
            <th>Product</th>
            <th>Quantity</th>
            <th>Unit Price</th>
            <th>Total</th>
            <th></th>
        </tr>
    </thead>
    <tbody>
        @foreach (var line in _order.Lines)
        {
            <tr class="@(line.IsValid ? "" : "table-danger")">
                <td><input @bind="line.ProductName" /></td>
                <td><input type="number" @bind="line.Quantity" /></td>
                <td><input type="number" @bind="line.UnitPrice" step="0.01" /></td>
                <td>@line.Total.ToString("C")</td>
                <td>
                    <button @onclick="() => RemoveLine(line)"
                            class="btn btn-danger btn-sm">
                        Remove
                    </button>
                </td>
            </tr>
        }
    </tbody>
</table>

<button @onclick="AddLine" class="btn btn-secondary">Add Line</button>

@code {
    private async Task AddLine()
    {
        var line = await _order.Lines.AddLine();
    }

    private void RemoveLine(IOrderLine line)
    {
        _order.Lines.RemoveLine(line);
    }
}
```

### MudBlazor DataGrid

```razor
<MudDataGrid Items="@_order.Lines"
             Bordered="true"
             Dense="true"
             EditMode="DataGridEditMode.Cell">
    <Columns>
        <PropertyColumn Property="x => x.ProductName" Title="Product">
            <EditTemplate>
                <MudNeatooTextField T="string?"
                                   EntityProperty="@(context.Item[nameof(context.Item.ProductName)])" />
            </EditTemplate>
        </PropertyColumn>

        <PropertyColumn Property="x => x.Quantity" Title="Qty">
            <EditTemplate>
                <MudNeatooNumericField T="int"
                                      EntityProperty="@(context.Item[nameof(context.Item.Quantity)])" />
            </EditTemplate>
        </PropertyColumn>

        <PropertyColumn Property="x => x.UnitPrice" Title="Price" Format="C2" />
        <PropertyColumn Property="x => x.Total" Title="Total" Format="C2" />

        <TemplateColumn>
            <CellTemplate>
                <MudIconButton Icon="@Icons.Material.Filled.Delete"
                               OnClick="() => RemoveLine(context.Item)"
                               Color="Color.Error" />
            </CellTemplate>
        </TemplateColumn>
    </Columns>
</MudDataGrid>
```

### Row Validation Status

```razor
<MudDataGrid Items="@_order.Lines">
    <Columns>
        @* Data columns... *@

        <TemplateColumn Title="Status">
            <CellTemplate>
                @if (!context.Item.IsValid)
                {
                    <MudTooltip>
                        <ChildContent>
                            <MudIcon Icon="@Icons.Material.Filled.Error"
                                     Color="Color.Error" />
                        </ChildContent>
                        <TooltipContent>
                            <ul>
                                @foreach (var msg in context.Item.PropertyMessages)
                                {
                                    <li>@msg.Message</li>
                                }
                            </ul>
                        </TooltipContent>
                    </MudTooltip>
                }
                else
                {
                    <MudIcon Icon="@Icons.Material.Filled.CheckCircle"
                             Color="Color.Success" />
                }
            </CellTemplate>
        </TemplateColumn>
    </Columns>
</MudDataGrid>
```

## Authorization-Aware UI

### Hiding Unauthorized Actions

```razor
@if (PersonFactory.CanCreate().IsAuthorized)
{
    <MudButton OnClick="CreateNew" Color="Color.Primary">
        Create New Person
    </MudButton>
}

@if (PersonFactory.CanDelete().IsAuthorized && !_person.IsNew)
{
    <MudButton OnClick="Delete" Color="Color.Error">
        Delete
    </MudButton>
}
```

### Authorization Messages

```razor
@{
    var canUpdate = PersonFactory.CanUpdate();
}

@if (!canUpdate.IsAuthorized)
{
    <MudAlert Severity="Severity.Warning">
        @canUpdate.Message
    </MudAlert>

    <PersonReadOnlyView Person="_person" />
}
else
{
    <PersonEditForm Person="_person" />
}
```

## Unsaved Changes Warning

```razor
@inject NavigationManager NavigationManager

@code {
    protected override void OnInitialized()
    {
        NavigationManager.RegisterLocationChangingHandler(OnLocationChanging);
    }

    private async ValueTask OnLocationChanging(LocationChangingContext context)
    {
        if (_person?.IsModified == true)
        {
            var confirmed = await DialogService.ShowMessageBox(
                "Unsaved Changes",
                "You have unsaved changes. Leave anyway?",
                yesText: "Leave", cancelText: "Stay");

            if (confirmed != true)
            {
                context.PreventNavigation();
            }
        }
    }
}
```

## Event Subscription Cleanup

```razor
@implements IDisposable

@code {
    private IPerson _person;

    protected override async Task OnInitializedAsync()
    {
        _person = await PersonFactory.Fetch(Id);
        _person.PropertyChanged += OnPropertyChanged;
    }

    private void OnPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        InvokeAsync(StateHasChanged);
    }

    public void Dispose()
    {
        if (_person != null)
        {
            _person.PropertyChanged -= OnPropertyChanged;
        }
    }
}
```

## Complete Page Example

```razor
@page "/person/edit/{Id:guid}"
@inject IPersonFactory PersonFactory
@inject NavigationManager NavigationManager
@inject IDialogService DialogService
@inject ISnackbar Snackbar
@implements IDisposable

@if (_loading)
{
    <MudProgressCircular Indeterminate="true" />
}
else if (_person == null)
{
    <MudAlert Severity="Severity.Error">Person not found</MudAlert>
}
else
{
    <MudPaper Class="pa-4">
        <MudForm>
            <MudNeatooTextField T="string?"
                               EntityProperty="@(_person[nameof(_person.FirstName)])"
                               Placeholder="First Name" />
            <MudNeatooTextField T="string?"
                               EntityProperty="@(_person[nameof(_person.LastName)])"
                               Placeholder="Last Name" />
            <MudNeatooTextField T="string?"
                               EntityProperty="@(_person[nameof(_person.Email)])"
                               Placeholder="Email" />

            @if (!_person.IsValid)
            {
                <NeatooValidationSummary Entity="_person" />
            }
        </MudForm>

        <MudDivider Class="my-4" />

        <MudStack Row="true" Justify="Justify.FlexEnd">
            <MudButton OnClick="HandleSave"
                       Disabled="@(!CanSave)"
                       Color="Color.Primary"
                       Variant="Variant.Filled">
                @if (_isSaving) { <MudProgressCircular Size="Size.Small" /> }
                Save
            </MudButton>

            @if (!_person.IsNew)
            {
                <MudButton OnClick="HandleDelete"
                           Color="Color.Error"
                           Variant="Variant.Outlined">
                    Delete
                </MudButton>
            }

            <MudButton OnClick="Cancel" Variant="Variant.Text">
                Cancel
            </MudButton>
        </MudStack>
    </MudPaper>
}

@code {
    [Parameter] public Guid Id { get; set; }

    private IPerson? _person;
    private bool _loading = true;
    private bool _isSaving;

    private bool CanSave => !_isSaving && (_person?.IsSavable ?? false);

    protected override async Task OnInitializedAsync()
    {
        _person = await PersonFactory.Fetch(Id);
        _loading = false;

        NavigationManager.RegisterLocationChangingHandler(OnLocationChanging);
    }

    private async Task HandleSave()
    {
        if (_person == null) return;

        await _person.WaitForTasks();
        if (!_person.IsSavable) return;

        try
        {
            _isSaving = true;
            _person = await PersonFactory.Save(_person);
            Snackbar.Add("Saved successfully", Severity.Success);
            NavigationManager.NavigateTo("/persons");
        }
        catch (Exception ex)
        {
            Snackbar.Add($"Save failed: {ex.Message}", Severity.Error);
        }
        finally
        {
            _isSaving = false;
        }
    }

    private async Task HandleDelete()
    {
        var confirm = await DialogService.ShowMessageBox(
            "Confirm Delete",
            "Are you sure you want to delete this person?",
            yesText: "Delete", cancelText: "Cancel");

        if (confirm == true && _person != null)
        {
            _person.Delete();
            await PersonFactory.Save(_person);
            NavigationManager.NavigateTo("/persons");
        }
    }

    private void Cancel()
    {
        NavigationManager.NavigateTo("/persons");
    }

    private async ValueTask OnLocationChanging(LocationChangingContext context)
    {
        if (_person?.IsModified == true)
        {
            var confirmed = await DialogService.ShowMessageBox(
                "Unsaved Changes",
                "Discard changes?",
                yesText: "Discard", cancelText: "Stay");

            if (confirmed != true)
            {
                context.PreventNavigation();
            }
        }
    }

    public void Dispose()
    {
        // Cleanup if needed
    }
}
```

## Best Practices

### Always Wait for Tasks

```csharp
private async Task Save()
{
    await _entity.WaitForTasks();  // Never skip
    if (_entity.IsSavable)
    {
        _entity = await Factory.Save(_entity);
    }
}
```

### Check IsSavable, Not IsValid

```csharp
// IsSavable includes all necessary checks
// IsModified && IsValid && !IsBusy && !IsChild
<button disabled="@(!_person.IsSavable)">Save</button>
```

### Reassign After Save

```csharp
// ALWAYS reassign
_person = await PersonFactory.Save(_person);
```

### Use MudNeatoo Components

They handle validation display, busy states, and binding automatically.

## Common Pitfalls

1. **Not reassigning after Save** - UI shows stale data
2. **Not waiting for tasks** - Saving before validation completes
3. **Using IsValid instead of IsSavable** - Missing modification/busy checks
4. **Not disposing event handlers** - Memory leaks
5. **Missing authorization checks** - UI shows unauthorized actions
