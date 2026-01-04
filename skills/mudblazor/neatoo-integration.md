# MudBlazor Integration with Neatoo Domain Objects

## Overview

When building forms with Neatoo domain entities, use the **Neatoo.Blazor.MudNeatoo** package instead of standard MudBlazor components. MudNeatoo components provide automatic integration with Neatoo's:

- Property change tracking
- Validation rule system (sync and async)
- Meta-properties (IsBusy, IsValid, IsModified, IsSavable)
- Error message display

## Installation

```bash
dotnet add package Neatoo.Blazor.MudNeatoo
```

## MudNeatoo Components

| MudNeatoo Component | MudBlazor Base | Use Case |
|---------------------|----------------|----------|
| `MudNeatooTextField<T>` | MudTextField | Text input |
| `MudNeatooNumericField<T>` | MudNumericField | Number input |
| `MudNeatooDatePicker` | MudDatePicker | Date selection |
| `MudNeatooTimePicker` | MudTimePicker | Time selection |
| `MudNeatooSelect<T>` | MudSelect | Dropdown selection |
| `MudNeatooCheckBox` | MudCheckBox | Boolean checkbox |
| `MudNeatooSwitch` | MudSwitch | Boolean toggle |
| `MudNeatooRadioGroup<T>` | MudRadioGroup | Radio button group |
| `MudNeatooAutocomplete<T>` | MudAutocomplete | Autocomplete input |
| `NeatooValidationSummary` | MudAlert | Validation message list |

---

## Basic Usage

### CORRECT: Using MudNeatoo Components

```razor
@inject IPersonFactory PersonFactory

<MudNeatooTextField T="string" EntityProperty="@person[nameof(IPerson.FirstName)]" />
<MudNeatooTextField T="string" EntityProperty="@person[nameof(IPerson.LastName)]" />
<MudNeatooTextField T="string" EntityProperty="@person[nameof(IPerson.Email)]" />

<NeatooValidationSummary Entity="@person" />

<MudButton Disabled="@(!person.IsSavable)" OnClick="Save">
    @if (person.IsBusy)
    {
        <MudProgressCircular Size="Size.Small" Indeterminate="true" Class="mr-2" />
    }
    Save
</MudButton>

@code {
    private IPerson person = default!;

    protected override void OnInitialized()
    {
        person = PersonFactory.Create();
    }

    private async Task Save()
    {
        await person.WaitForTasks();
        if (!person.IsSavable) return;
        person = await PersonFactory.Save(person);
    }
}
```

### WRONG: Manual Binding with Standard MudBlazor

Do NOT manually bind Neatoo entities with standard MudBlazor components:

```razor
@* WRONG - Don't do this! *@
<MudTextField @bind-Value="person.Name"
              Label="Name"
              Error="@(!person[nameof(IPerson.Name)].IsValid)"
              ErrorText="..." />
```

**Why this is wrong:**
- Doesn't integrate with Neatoo's property change tracking
- Doesn't handle async validation states (`IsBusy`)
- Loses error message aggregation
- Won't trigger Neatoo rules properly

---

## Property Binding Pattern

### The EntityProperty Indexer

MudNeatoo components use the `EntityProperty` parameter which takes a property accessor from Neatoo's indexer:

```razor
EntityProperty="@person[nameof(IPerson.Email)]"
```

This provides the component access to:
- Current value
- Validation state
- Busy state (for async rules)
- Error messages
- Display name (from `[DisplayName]` attribute)

### Key Differences from Standard MudBlazor

| Aspect | MudBlazor | MudNeatoo |
|--------|-----------|-----------|
| Binding | `@bind-Value="model.Property"` | `EntityProperty="@entity[nameof(IEntity.Property)]"` |
| Validation | Manual `Error`/`ErrorText` | Automatic from rules |
| Async state | Manual implementation | Automatic `IsBusy` |
| Labels | Manual `Label="..."` | Automatic from `[DisplayName]` |

---

## Form Components

### Text Fields

```razor
@* Basic text field *@
<MudNeatooTextField T="string"
                    EntityProperty="@person[nameof(IPerson.FirstName)]"
                    Variant="Variant.Outlined" />

@* Multiline *@
<MudNeatooTextField T="string"
                    EntityProperty="@person[nameof(IPerson.Notes)]"
                    Variant="Variant.Outlined"
                    Lines="4" />

@* With adornment *@
<MudNeatooTextField T="string"
                    EntityProperty="@person[nameof(IPerson.Email)]"
                    Variant="Variant.Outlined"
                    Adornment="Adornment.Start"
                    AdornmentIcon="@Icons.Material.Filled.Email" />
```

### Numeric Fields

```razor
<MudNeatooNumericField T="decimal"
                       EntityProperty="@product[nameof(IProduct.Price)]"
                       Variant="Variant.Outlined"
                       Format="N2"
                       Adornment="Adornment.Start"
                       AdornmentText="$" />

<MudNeatooNumericField T="int"
                       EntityProperty="@product[nameof(IProduct.Quantity)]"
                       Variant="Variant.Outlined"
                       Min="0"
                       Max="1000" />
```

### Select Dropdowns

```razor
<MudNeatooSelect T="string"
                 EntityProperty="@person[nameof(IPerson.State)]"
                 Variant="Variant.Outlined">
    @foreach (var state in states)
    {
        <MudSelectItem Value="@state.Code">@state.Name</MudSelectItem>
    }
</MudNeatooSelect>

@* Enum select *@
<MudNeatooSelect T="PhoneType?"
                 EntityProperty="@phone[nameof(IPersonPhone.PhoneType)]"
                 Variant="Variant.Outlined">
    @foreach (var type in Enum.GetValues<PhoneType>())
    {
        <MudSelectItem Value="@((PhoneType?)type)">@type</MudSelectItem>
    }
</MudNeatooSelect>
```

### Date Picker

```razor
<MudNeatooDatePicker EntityProperty="@person[nameof(IPerson.BirthDate)]"
                     Variant="Variant.Outlined"
                     DateFormat="MM/dd/yyyy"
                     MaxDate="DateTime.Today" />
```

### Checkbox and Switch

```razor
<MudNeatooCheckBox EntityProperty="@person[nameof(IPerson.IsActive)]"
                   Label="Active"
                   Color="Color.Primary" />

<MudNeatooSwitch EntityProperty="@settings[nameof(ISettings.DarkMode)]"
                 Label="Dark Mode"
                 Color="Color.Primary" />
```

### Autocomplete

```razor
<MudNeatooAutocomplete T="Customer"
                       EntityProperty="@order[nameof(IOrder.Customer)]"
                       SearchFunc="SearchCustomers"
                       ToStringFunc="@(c => c?.Name ?? string.Empty)"
                       Variant="Variant.Outlined" />
```

---

## Validation Display

### Validation Summary

Display all validation errors for an entity:

```razor
@if (!person.IsValid)
{
    <NeatooValidationSummary Entity="@person" />
}
```

### Per-Field Validation

MudNeatoo components automatically display validation errors inline. The error state and message come from:

1. Data annotation attributes (`[Required]`, `[EmailAddress]`, etc.)
2. Synchronous rules (`RuleBase<T>`)
3. Asynchronous rules (`AsyncRuleBase<T>`)

---

## Meta-Properties for UI State

### IsSavable for Save Button

```razor
<MudButton Disabled="@(!entity.IsSavable)"
           Color="Color.Primary"
           OnClick="Save">
    Save
</MudButton>
```

`IsSavable` is `true` when:
- `IsModified = true` (has changes)
- `IsValid = true` (all rules pass)
- `IsBusy = false` (no async operations)
- `IsChild = false` (is aggregate root)

### IsBusy for Loading State

```razor
@if (entity.IsBusy)
{
    <MudProgressLinear Indeterminate="true" Color="Color.Primary" />
}

<MudButton Disabled="@(!entity.IsSavable)" OnClick="Save">
    @if (entity.IsBusy)
    {
        <MudProgressCircular Size="Size.Small" Indeterminate="true" Class="mr-2" />
    }
    Save
</MudButton>
```

### Debug State Display

Useful during development:

```razor
<MudPaper Class="pa-4 mt-4" Outlined="true">
    <MudText Typo="Typo.caption">Entity State:</MudText>
    <MudStack Row="true" Spacing="4">
        <MudChip Size="Size.Small" Color="@(entity.IsModified ? Color.Warning : Color.Default)">
            Modified: @entity.IsModified
        </MudChip>
        <MudChip Size="Size.Small" Color="@(entity.IsValid ? Color.Success : Color.Error)">
            Valid: @entity.IsValid
        </MudChip>
        <MudChip Size="Size.Small" Color="@(entity.IsBusy ? Color.Info : Color.Default)">
            Busy: @entity.IsBusy
        </MudChip>
        <MudChip Size="Size.Small" Color="@(entity.IsSavable ? Color.Success : Color.Default)">
            Savable: @entity.IsSavable
        </MudChip>
    </MudStack>
</MudPaper>
```

---

## Collection Binding

### Editable Table of Child Entities

```razor
<MudTable Items="@person.PersonPhoneList" Dense="true">
    <HeaderContent>
        <MudTh>Type</MudTh>
        <MudTh>Number</MudTh>
        <MudTh></MudTh>
    </HeaderContent>
    <RowTemplate>
        <MudTd>
            <MudNeatooSelect T="PhoneType?"
                             EntityProperty="@context[nameof(IPersonPhone.PhoneType)]"
                             Variant="Variant.Text"
                             Dense="true">
                @foreach (var type in Enum.GetValues<PhoneType>())
                {
                    <MudSelectItem Value="@((PhoneType?)type)">@type</MudSelectItem>
                }
            </MudNeatooSelect>
        </MudTd>
        <MudTd>
            <MudNeatooTextField T="string"
                                EntityProperty="@context[nameof(IPersonPhone.PhoneNumber)]"
                                Variant="Variant.Text"
                                Dense="true" />
        </MudTd>
        <MudTd>
            <MudIconButton Icon="@Icons.Material.Filled.Delete"
                           Size="Size.Small"
                           Color="Color.Error"
                           OnClick="@(() => person.PersonPhoneList.Remove(context))" />
        </MudTd>
    </RowTemplate>
</MudTable>

<MudButton Variant="Variant.Outlined"
           StartIcon="@Icons.Material.Filled.Add"
           OnClick="@(() => person.PersonPhoneList.AddPhoneNumber())"
           Class="mt-2">
    Add Phone
</MudButton>
```

---

## PropertyChanged for UI Updates

Subscribe to `PropertyChanged` to update UI when entity state changes:

```razor
@implements IDisposable

@code {
    private IPerson person = default!;

    protected override void OnParametersSet()
    {
        if (person != null)
        {
            person.PropertyChanged += OnPropertyChanged;
        }
    }

    private void OnPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        InvokeAsync(StateHasChanged);
    }

    public void Dispose()
    {
        if (person != null)
        {
            person.PropertyChanged -= OnPropertyChanged;
        }
    }
}
```

---

## Complete Form Example

```razor
@page "/person/{Id:guid?}"
@inject IPersonFactory PersonFactory
@inject NavigationManager NavigationManager
@inject ISnackbar Snackbar
@implements IDisposable

<MudContainer MaxWidth="MaxWidth.Medium" Class="mt-4">
    @if (isLoading)
    {
        <MudProgressLinear Indeterminate="true" Color="Color.Primary" />
    }
    else if (person != null)
    {
        <MudPaper Elevation="2" Class="pa-6">
            <MudStack Row="true" AlignItems="AlignItems.Center" Class="mb-4">
                <MudIconButton Icon="@Icons.Material.Filled.ArrowBack" OnClick="GoBack" />
                <MudText Typo="Typo.h5">@(IsNew ? "New Person" : "Edit Person")</MudText>
            </MudStack>

            @if (person.IsBusy)
            {
                <MudProgressLinear Indeterminate="true" Color="Color.Info" Class="mb-4" />
            }

            @if (!person.IsValid)
            {
                <NeatooValidationSummary Entity="@person" Class="mb-4" />
            }

            <MudGrid Spacing="3">
                <MudItem xs="12" sm="6">
                    <MudNeatooTextField T="string"
                                        EntityProperty="@person[nameof(IPerson.FirstName)]"
                                        Variant="Variant.Outlined" />
                </MudItem>
                <MudItem xs="12" sm="6">
                    <MudNeatooTextField T="string"
                                        EntityProperty="@person[nameof(IPerson.LastName)]"
                                        Variant="Variant.Outlined" />
                </MudItem>
                <MudItem xs="12">
                    <MudNeatooTextField T="string"
                                        EntityProperty="@person[nameof(IPerson.Email)]"
                                        Variant="Variant.Outlined"
                                        Adornment="Adornment.Start"
                                        AdornmentIcon="@Icons.Material.Filled.Email" />
                </MudItem>
            </MudGrid>

            <MudDivider Class="my-6" />

            <MudText Typo="Typo.h6" Class="mb-4">Phone Numbers</MudText>

            <MudTable Items="@person.PersonPhoneList" Dense="true">
                <HeaderContent>
                    <MudTh>Type</MudTh>
                    <MudTh>Number</MudTh>
                    <MudTh Style="width: 50px;"></MudTh>
                </HeaderContent>
                <RowTemplate>
                    <MudTd>
                        <MudNeatooSelect T="PhoneType?"
                                         EntityProperty="@context[nameof(IPersonPhone.PhoneType)]"
                                         Variant="Variant.Text">
                            @foreach (var type in Enum.GetValues<PhoneType>())
                            {
                                <MudSelectItem Value="@((PhoneType?)type)">@type</MudSelectItem>
                            }
                        </MudNeatooSelect>
                    </MudTd>
                    <MudTd>
                        <MudNeatooTextField T="string"
                                            EntityProperty="@context[nameof(IPersonPhone.PhoneNumber)]"
                                            Variant="Variant.Text" />
                    </MudTd>
                    <MudTd>
                        <MudIconButton Icon="@Icons.Material.Filled.Delete"
                                       Size="Size.Small"
                                       Color="Color.Error"
                                       OnClick="@(() => person.PersonPhoneList.Remove(context))" />
                    </MudTd>
                </RowTemplate>
            </MudTable>

            <MudButton Variant="Variant.Text"
                       StartIcon="@Icons.Material.Filled.Add"
                       OnClick="AddPhone"
                       Class="mt-2">
                Add Phone Number
            </MudButton>

            <MudStack Row="true" Justify="Justify.FlexEnd" Class="mt-6">
                <MudButton Variant="Variant.Text" OnClick="GoBack">Cancel</MudButton>
                <MudButton Variant="Variant.Filled"
                           Color="Color.Primary"
                           Disabled="@(!person.IsSavable)"
                           OnClick="Save">
                    @if (isSaving)
                    {
                        <MudProgressCircular Size="Size.Small" Indeterminate="true" Class="mr-2" />
                    }
                    Save
                </MudButton>
            </MudStack>
        </MudPaper>
    }
</MudContainer>

@code {
    [Parameter] public Guid? Id { get; set; }

    private bool IsNew => !Id.HasValue;
    private IPerson? person;
    private bool isLoading = true;
    private bool isSaving;

    protected override async Task OnInitializedAsync()
    {
        if (IsNew)
        {
            person = PersonFactory.Create();
        }
        else
        {
            person = await PersonFactory.Fetch(Id.Value);
        }

        if (person != null)
        {
            person.PropertyChanged += OnPropertyChanged;
        }

        isLoading = false;
    }

    private void OnPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        InvokeAsync(StateHasChanged);
    }

    private void AddPhone()
    {
        person?.PersonPhoneList.AddPhoneNumber();
    }

    private async Task Save()
    {
        if (person == null) return;

        await person.WaitForTasks();
        if (!person.IsSavable) return;

        isSaving = true;
        StateHasChanged();

        try
        {
            person = await PersonFactory.Save(person);
            person.PropertyChanged += OnPropertyChanged;

            Snackbar.Add("Person saved successfully!", Severity.Success);
            NavigationManager.NavigateTo("/persons");
        }
        catch (Exception ex)
        {
            Snackbar.Add("Failed to save person.", Severity.Error);
        }
        finally
        {
            isSaving = false;
        }
    }

    private void GoBack() => NavigationManager.NavigateTo("/persons");

    public void Dispose()
    {
        if (person != null)
        {
            person.PropertyChanged -= OnPropertyChanged;
        }
    }
}
```

---

## Key Reminders

1. **Always use MudNeatoo components** with Neatoo entities, not standard MudBlazor
2. **Use `EntityProperty` indexer** syntax: `entity[nameof(IEntity.Property)]`
3. **Check `IsSavable`** for Save button state
4. **Call `WaitForTasks()`** before checking validity at save time
5. **Reassign after Save()**: `entity = await factory.Save(entity);`
6. **Subscribe to PropertyChanged** if you need UI updates from entity changes
7. **Unsubscribe in Dispose** to prevent memory leaks
