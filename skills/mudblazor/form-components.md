# MudBlazor Form Components

## MudForm vs EditForm

### When to Use MudForm

Use `MudForm` when:
- You want MudBlazor's built-in validation system
- You need validation functions (custom or data annotations)
- You want `form.Validate()` and `form.ResetAsync()` methods
- You prefer programmatic form control

**CRITICAL: Do NOT use `ButtonType="ButtonType.Submit"` with MudForm.**

```razor
<MudForm @ref="form" @bind-IsValid="isValid" @bind-Errors="errors">
    <MudTextField @bind-Value="model.Name"
                  Label="Name"
                  Required="true"
                  RequiredError="Name is required"
                  Validation="@(new Func<string, string>(ValidateName))" />

    <MudButton Color="Color.Primary"
               Disabled="@(!isValid)"
               OnClick="Submit">
        Submit
    </MudButton>
</MudForm>

@code {
    private MudForm form;
    private bool isValid;
    private string[] errors = { };

    private string ValidateName(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
            return "Name is required";
        if (value.Length < 2)
            return "Name must be at least 2 characters";
        return null; // Valid
    }

    private async Task Submit()
    {
        await form.Validate();
        if (isValid)
        {
            // Process form
        }
    }
}
```

### When to Use EditForm

Use `EditForm` when:
- Using ASP.NET Core's built-in validation
- You have data annotation attributes on your model
- You want standard form submission behavior

```razor
<EditForm Model="model" OnValidSubmit="HandleValidSubmit">
    <DataAnnotationsValidator />
    <MudCard>
        <MudCardContent>
            <MudTextField @bind-Value="model.Name"
                          For="@(() => model.Name)"
                          Label="Name"
                          Variant="Variant.Outlined" />

            <MudTextField @bind-Value="model.Email"
                          For="@(() => model.Email)"
                          Label="Email"
                          Variant="Variant.Outlined"
                          Class="mt-3" />
        </MudCardContent>
        <MudCardActions>
            <MudButton ButtonType="ButtonType.Submit"
                       Color="Color.Primary"
                       Variant="Variant.Filled">
                Submit
            </MudButton>
        </MudCardActions>
    </MudCard>
</EditForm>
```

---

## MudTextField

### Basic Usage

```razor
<MudTextField @bind-Value="model.Name"
              Label="Full Name"
              Variant="Variant.Outlined"
              Required="true"
              RequiredError="Name is required"
              HelperText="Enter your legal name"
              Counter="100"
              MaxLength="100"
              Immediate="true" />
```

### Key Properties

| Property | Type | Description |
|----------|------|-------------|
| `@bind-Value` | T | Two-way data binding |
| `Label` | string | Field label |
| `Variant` | Variant | Text, Filled, or Outlined |
| `Required` | bool | Marks field as required |
| `RequiredError` | string | Error when required and empty |
| `HelperText` | string | Helper text below field |
| `HelperTextOnFocus` | bool | Show helper only on focus |
| `Counter` | int? | Show character count |
| `MaxLength` | int | Maximum characters |
| `Immediate` | bool | Update on every keystroke |
| `DebounceInterval` | int | Delay updates (ms) |
| `Clearable` | bool | Show clear button |
| `Disabled` | bool | Disable input |
| `ReadOnly` | bool | Read-only mode |
| `InputType` | InputType | Text, Password, Email, etc. |
| `Lines` | int | Multiline rows |
| `AutoGrow` | bool | Auto-expand multiline |
| `MaxLines` | int | Maximum rows for auto-grow |

### Adornments

```razor
@* Icon at start *@
<MudTextField @bind-Value="model.Email"
              Label="Email"
              Adornment="Adornment.Start"
              AdornmentIcon="@Icons.Material.Filled.Email" />

@* Text at end *@
<MudTextField @bind-Value="model.Weight"
              Label="Weight"
              Adornment="Adornment.End"
              AdornmentText="kg" />

@* Password with toggle *@
<MudTextField @bind-Value="model.Password"
              Label="Password"
              InputType="@(showPassword ? InputType.Text : InputType.Password)"
              Adornment="Adornment.End"
              AdornmentIcon="@(showPassword ? Icons.Material.Filled.Visibility : Icons.Material.Filled.VisibilityOff)"
              OnAdornmentClick="() => showPassword = !showPassword" />
```

### Input Masking

```razor
@* Credit card *@
<MudTextField @bind-Value="model.CardNumber"
              Label="Credit Card"
              Mask="@(new PatternMask("0000 0000 0000 0000"))" />

@* Phone number *@
<MudTextField @bind-Value="model.Phone"
              Label="Phone"
              Mask="@(new PatternMask("(000) 000-0000"))" />

@* Date mask *@
<MudTextField @bind-Value="model.Date"
              Label="Date"
              Mask="@(new DateMask("MM/dd/yyyy"))" />
```

### Debounced Search

```razor
<MudTextField @bind-Value="searchText"
              Label="Search"
              Adornment="Adornment.Start"
              AdornmentIcon="@Icons.Material.Filled.Search"
              Immediate="true"
              DebounceInterval="300"
              Clearable="true" />
```

---

## MudNumericField

### Basic Usage

```razor
<MudNumericField @bind-Value="model.Quantity"
                 Label="Quantity"
                 Variant="Variant.Outlined"
                 Min="1"
                 Max="100"
                 Step="1" />
```

### Currency Input

```razor
<MudNumericField @bind-Value="model.Price"
                 Label="Price"
                 Variant="Variant.Outlined"
                 Format="N2"
                 Culture="@CultureInfo.GetCultureInfo("en-US")"
                 Adornment="Adornment.Start"
                 AdornmentText="$"
                 Min="0"
                 HideSpinButtons="true" />
```

### Nullable Numeric (Empty Initial State)

```razor
<MudNumericField @bind-Value="model.OptionalAmount"
                 T="decimal?"
                 Label="Optional Amount"
                 Variant="Variant.Outlined"
                 Clearable="true" />
```

**Note:** Use nullable types (`int?`, `decimal?`) when you want an empty initial state instead of 0.

---

## MudSelect

### Single Selection

```razor
<MudSelect @bind-Value="model.Category"
           Label="Category"
           Variant="Variant.Outlined"
           Required="true"
           RequiredError="Please select a category">
    <MudSelectItem Value="@("electronics")">Electronics</MudSelectItem>
    <MudSelectItem Value="@("clothing")">Clothing</MudSelectItem>
    <MudSelectItem Value="@("home")">Home & Garden</MudSelectItem>
</MudSelect>
```

### Multiple Selection

```razor
<MudSelect @bind-SelectedValues="selectedTags"
           T="string"
           Label="Tags"
           Variant="Variant.Outlined"
           MultiSelection="true"
           SelectAll="true"
           SelectAllText="Select All Tags"
           MultiSelectionTextFunc="@(x => $"{x.Count()} tag(s) selected")">
    @foreach (var tag in availableTags)
    {
        <MudSelectItem Value="@tag">@tag</MudSelectItem>
    }
</MudSelect>

@code {
    private IEnumerable<string> selectedTags = new HashSet<string>();
    private List<string> availableTags = new() { "Featured", "Sale", "New", "Popular" };
}
```

### Complex Object Selection

```razor
<MudSelect @bind-Value="selectedCustomer"
           T="Customer"
           Label="Customer"
           Variant="Variant.Outlined"
           Comparer="@(new CustomerComparer())"
           ToStringFunc="@(c => c?.Name ?? string.Empty)">
    @foreach (var customer in customers)
    {
        <MudSelectItem Value="@customer">@customer.Name (@customer.AccountNumber)</MudSelectItem>
    }
</MudSelect>

@code {
    private class CustomerComparer : IEqualityComparer<Customer>
    {
        public bool Equals(Customer x, Customer y) => x?.Id == y?.Id;
        public int GetHashCode(Customer obj) => obj?.Id.GetHashCode() ?? 0;
    }
}
```

---

## MudAutocomplete

### Basic Autocomplete

```razor
<MudAutocomplete @bind-Value="model.Country"
                 Label="Country"
                 Variant="Variant.Outlined"
                 SearchFunc="SearchCountries"
                 ShowProgressIndicator="true"
                 ProgressIndicatorColor="Color.Primary"
                 ResetValueOnEmptyText="true"
                 CoerceText="true" />

@code {
    private async Task<IEnumerable<string>> SearchCountries(string value, CancellationToken token)
    {
        if (string.IsNullOrWhiteSpace(value))
            return countries;

        return countries.Where(c => c.Contains(value, StringComparison.OrdinalIgnoreCase));
    }
}
```

### With Item Templates

```razor
<MudAutocomplete @bind-Value="selectedProduct"
                 T="Product"
                 Label="Search Products"
                 Variant="Variant.Outlined"
                 SearchFunc="SearchProducts"
                 ToStringFunc="@(p => p?.Name ?? string.Empty)"
                 ShowProgressIndicator="true"
                 Dense="true">
    <ItemTemplate Context="product">
        <MudStack Row="true" Spacing="2" AlignItems="AlignItems.Center">
            <MudAvatar Size="Size.Small" Image="@product.ImageUrl" />
            <MudStack Spacing="0">
                <MudText Typo="Typo.body2">@product.Name</MudText>
                <MudText Typo="Typo.caption" Color="Color.Secondary">
                    @product.Sku - @product.Price.ToString("C")
                </MudText>
            </MudStack>
        </MudStack>
    </ItemTemplate>
    <NoItemsTemplate>
        <MudText Typo="Typo.body2" Color="Color.Secondary" Class="pa-2">
            No products found matching your search.
        </MudText>
    </NoItemsTemplate>
</MudAutocomplete>
```

### Key Properties

| Property | Description |
|----------|-------------|
| `SearchFunc` | Async function `(string, CancellationToken) => Task<IEnumerable<T>>` |
| `ResetValueOnEmptyText` | Clear selection when text is empty |
| `CoerceText` | Force text to match selected value |
| `CoerceValue` | Accept user input as valid even if unmatched |
| `SelectValueOnTab` | Tab key confirms selection |
| `ToStringFunc` | Custom display function |

---

## MudDatePicker

### Standard Date Picker

```razor
<MudDatePicker @bind-Date="model.BirthDate"
               Label="Date of Birth"
               Variant="Variant.Outlined"
               DateFormat="MM/dd/yyyy"
               Placeholder="Select date"
               Editable="true" />
```

### With Date Constraints

```razor
<MudDatePicker @bind-Date="model.AppointmentDate"
               Label="Appointment Date"
               Variant="Variant.Outlined"
               MinDate="DateTime.Today"
               MaxDate="DateTime.Today.AddMonths(3)"
               IsDateDisabledFunc="@(date => date.DayOfWeek == DayOfWeek.Sunday)"
               HelperText="Select a date within the next 3 months (Sundays unavailable)" />
```

### Date Range Picker

```razor
<MudDateRangePicker @bind-DateRange="dateRange"
                    Label="Report Period"
                    Variant="Variant.Outlined"
                    Editable="true" />

@code {
    private DateRange dateRange = new(DateTime.Today.AddDays(-30), DateTime.Today);
}
```

### Key Properties

| Property | Description |
|----------|-------------|
| `@bind-Date` | DateTime? binding |
| `DateFormat` | Display format (e.g., "MM/dd/yyyy") |
| `MinDate` / `MaxDate` | Date constraints |
| `IsDateDisabledFunc` | Function to disable specific dates |
| `Editable` | Allow manual text input |
| `PickerVariant` | Inline, Dialog, or Static |
| `OpenTo` | Initial view (Year, Month, Date) |

---

## MudCheckBox

### Standard Checkbox

```razor
<MudCheckBox @bind-Value="model.AcceptTerms"
             Label="I accept the terms and conditions"
             Color="Color.Primary"
             Required="true"
             RequiredError="You must accept the terms" />
```

### Tri-State Checkbox

```razor
<MudCheckBox @bind-Value="selectAll"
             T="bool?"
             TriState="true"
             Label="Select All Items"
             Color="Color.Primary"
             CheckedIcon="@Icons.Material.Filled.CheckBox"
             UncheckedIcon="@Icons.Material.Filled.CheckBoxOutlineBlank"
             IndeterminateIcon="@Icons.Material.Filled.IndeterminateCheckBox" />

@code {
    private bool? selectAll = null; // null = indeterminate
}
```

---

## MudSwitch

```razor
<MudSwitch @bind-Value="model.IsActive"
           Label="Active"
           Color="Color.Primary" />

<MudSwitch @bind-Value="isDarkMode"
           Color="Color.Primary"
           Label="@(isDarkMode ? "Dark Mode" : "Light Mode")"
           LabelPosition="LabelPosition.Start" />
```

---

## MudRadioGroup

```razor
<MudRadioGroup @bind-Value="model.PaymentMethod">
    <MudRadio Value="@("credit")">Credit Card</MudRadio>
    <MudRadio Value="@("debit")">Debit Card</MudRadio>
    <MudRadio Value="@("paypal")">PayPal</MudRadio>
</MudRadioGroup>
```

---

## Validation Approaches

### 1. Simple Custom Validation

```razor
<MudTextField @bind-Value="model.Email"
              Validation="@(new Func<string, IEnumerable<string>>(ValidateEmail))" />

@code {
    private IEnumerable<string> ValidateEmail(string value)
    {
        if (string.IsNullOrEmpty(value))
            yield return "Email is required";
        else if (!value.Contains("@"))
            yield return "Invalid email format";
    }
}
```

### 2. Data Annotations

```razor
<MudTextField @bind-Value="model.Email"
              Validation="@(new EmailAddressAttribute() { ErrorMessage = "Invalid email" })" />
```

### 3. FluentValidation

```razor
<MudForm @ref="form" Model="model" Validation="@(validator.ValidateValue)">
    <MudTextField @bind-Value="model.Name"
                  For="@(() => model.Name)"
                  Label="Name"
                  Immediate="true" />
</MudForm>

@code {
    private MudForm form;
    private CustomerModel model = new();
    private CustomerValidator validator = new();

    public class CustomerValidator : AbstractValidator<CustomerModel>
    {
        public CustomerValidator()
        {
            RuleFor(x => x.Name)
                .NotEmpty().WithMessage("Name is required")
                .MinimumLength(2).WithMessage("Name must be at least 2 characters");
        }

        public Func<object, string, Task<IEnumerable<string>>> ValidateValue => async (model, propertyName) =>
        {
            var result = await ValidateAsync(ValidationContext<CustomerModel>
                .CreateWithOptions((CustomerModel)model, x => x.IncludeProperties(propertyName)));
            return result.IsValid
                ? Array.Empty<string>()
                : result.Errors.Select(e => e.ErrorMessage);
        };
    }
}
```

---

## Form Layout Patterns

### Sectioned Form

```razor
<MudPaper Elevation="2" Class="pa-6">
    <MudText Typo="Typo.h5" Class="mb-4">Customer Information</MudText>

    <MudGrid Spacing="3">
        <MudItem xs="12" md="6">
            <MudTextField @bind-Value="model.FirstName" Label="First Name" Variant="Variant.Outlined" />
        </MudItem>
        <MudItem xs="12" md="6">
            <MudTextField @bind-Value="model.LastName" Label="Last Name" Variant="Variant.Outlined" />
        </MudItem>
        <MudItem xs="12">
            <MudTextField @bind-Value="model.Email" Label="Email" Variant="Variant.Outlined" />
        </MudItem>
    </MudGrid>

    <MudDivider Class="my-6" />

    <MudText Typo="Typo.h6" Class="mb-4">Address</MudText>

    <MudGrid Spacing="3">
        <MudItem xs="12">
            <MudTextField @bind-Value="model.Street" Label="Street Address" Variant="Variant.Outlined" />
        </MudItem>
        <MudItem xs="12" sm="6" md="4">
            <MudTextField @bind-Value="model.City" Label="City" Variant="Variant.Outlined" />
        </MudItem>
        <MudItem xs="12" sm="6" md="4">
            <MudTextField @bind-Value="model.State" Label="State" Variant="Variant.Outlined" />
        </MudItem>
        <MudItem xs="12" sm="12" md="4">
            <MudTextField @bind-Value="model.ZipCode" Label="Zip Code" Variant="Variant.Outlined" />
        </MudItem>
    </MudGrid>
</MudPaper>
```

### Form with Actions

```razor
<MudStack Row="true" Justify="Justify.FlexEnd" Class="mt-6">
    <MudButton Variant="Variant.Text" OnClick="Cancel">Cancel</MudButton>
    <MudButton Variant="Variant.Filled"
               Color="Color.Primary"
               Disabled="@(!isValid || isSaving)"
               OnClick="Save">
        @if (isSaving)
        {
            <MudProgressCircular Size="Size.Small" Indeterminate="true" Class="mr-2" />
        }
        Save
    </MudButton>
</MudStack>
```
