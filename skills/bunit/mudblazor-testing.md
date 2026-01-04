# Testing MudBlazor Components

## Setup Requirements

### Required Configuration

MudBlazor components require specific providers and services. Create a base test class:

```csharp
public abstract class MudBlazorTestContext : TestContext
{
    protected MudBlazorTestContext()
    {
        // Add MudBlazor services
        Services.AddMudServices(options =>
        {
            options.SnackbarConfiguration.ShowTransitionDuration = 0;
            options.SnackbarConfiguration.HideTransitionDuration = 0;
        });

        // Configure JSInterop for MudBlazor
        JSInterop.Mode = JSRuntimeMode.Loose;

        // Add required JS setup for common MudBlazor calls
        SetupMudBlazorJs();
    }

    private void SetupMudBlazorJs()
    {
        // Common MudBlazor JS interop calls
        JSInterop.SetupVoid("mudPopover.initialize", _ => true);
        JSInterop.SetupVoid("mudKeyInterceptor.connect", _ => true);
        JSInterop.SetupVoid("mudElementReference.saveFocus", _ => true);
        JSInterop.SetupVoid("mudScrollManager.lockScroll", _ => true);
        JSInterop.SetupVoid("mudScrollManager.unlockScroll", _ => true);
    }

    /// <summary>
    /// Render component wrapped with MudBlazor providers
    /// </summary>
    protected IRenderedComponent<TComponent> RenderMudComponent<TComponent>(
        Action<ComponentParameterCollectionBuilder<TComponent>>? parameterBuilder = null)
        where TComponent : IComponent
    {
        var wrapper = RenderComponent<MudPopoverProvider>();

        return RenderComponent<TComponent>(parameterBuilder ?? (_ => { }));
    }
}
```

### Package References

```xml
<ItemGroup>
    <PackageReference Include="bunit" Version="1.31.3" />
    <PackageReference Include="MudBlazor" Version="7.11.0" />
    <PackageReference Include="MudBlazor.ThemeManager" Version="2.1.0" />
</ItemGroup>
```

## Testing MudTextField

### Basic Text Input

```csharp
public class MudTextFieldTests : MudBlazorTestContext
{
    [Fact]
    public void TextField_DisplaysLabel()
    {
        var cut = RenderComponent<MudTextField<string>>(p => p
            .Add(x => x.Label, "Username")
            .Add(x => x.Value, "")
            .Add(x => x.ValueChanged, EventCallback.Factory.Create<string>(this, _ => { })));

        cut.Find("label").TextContent.ShouldContain("Username");
    }

    [Fact]
    public void TextField_BindsValue()
    {
        string boundValue = "";

        var cut = RenderComponent<MudTextField<string>>(p => p
            .Add(x => x.Value, boundValue)
            .Add(x => x.ValueChanged, EventCallback.Factory.Create<string>(
                this, v => boundValue = v)));

        var input = cut.Find("input");
        input.Change("new value");

        boundValue.ShouldBe("new value");
    }

    [Fact]
    public void TextField_ShowsValidationError()
    {
        var cut = RenderComponent<MudTextField<string>>(p => p
            .Add(x => x.Label, "Email")
            .Add(x => x.Value, "invalid")
            .Add(x => x.Validation, new EmailAddressAttribute())
            .Add(x => x.ValueChanged, EventCallback.Factory.Create<string>(this, _ => { })));

        // Trigger validation
        cut.Find("input").Blur();

        cut.WaitForAssertion(() =>
        {
            cut.Find(".mud-input-error").ShouldNotBeNull();
        });
    }
}
```

### Testing with Immediate Mode

```csharp
[Fact]
public void TextField_ImmediateMode_UpdatesOnInput()
{
    string boundValue = "";

    var cut = RenderComponent<MudTextField<string>>(p => p
        .Add(x => x.Immediate, true)
        .Add(x => x.Value, boundValue)
        .Add(x => x.ValueChanged, EventCallback.Factory.Create<string>(
            this, v => boundValue = v)));

    // Use Input event instead of Change for immediate mode
    cut.Find("input").Input("typing");

    boundValue.ShouldBe("typing");
}
```

## Testing MudSelect

### Basic Select

```csharp
public class MudSelectTests : MudBlazorTestContext
{
    [Fact]
    public void Select_DisplaysOptions()
    {
        var cut = RenderComponent<MudSelect<string>>(p => p
            .Add(x => x.Label, "Country")
            .Add(x => x.Value, "")
            .Add(x => x.ValueChanged, EventCallback.Factory.Create<string>(this, _ => { }))
            .AddChildContent<MudSelectItem<string>>(item => item.Add(x => x.Value, "US").AddChildContent("United States"))
            .AddChildContent<MudSelectItem<string>>(item => item.Add(x => x.Value, "UK").AddChildContent("United Kingdom")));

        // Click to open dropdown
        cut.Find(".mud-select").Click();

        cut.WaitForAssertion(() =>
        {
            var items = cut.FindAll(".mud-list-item");
            items.Count.ShouldBe(2);
        });
    }

    [Fact]
    public void Select_SelectsValue()
    {
        string selectedValue = "";

        var cut = RenderComponent<MudSelect<string>>(p => p
            .Add(x => x.Value, selectedValue)
            .Add(x => x.ValueChanged, EventCallback.Factory.Create<string>(
                this, v => selectedValue = v))
            .AddChildContent<MudSelectItem<string>>(item => item
                .Add(x => x.Value, "option1")
                .AddChildContent("Option 1")));

        // Open and select
        cut.Find(".mud-select").Click();

        cut.WaitForAssertion(() =>
        {
            cut.Find(".mud-list-item").Click();
        });

        selectedValue.ShouldBe("option1");
    }
}
```

### Multi-Select

```csharp
[Fact]
public void MultiSelect_SelectsMultipleValues()
{
    IEnumerable<string> selectedValues = new List<string>();

    var cut = RenderComponent<MudSelect<string>>(p => p
        .Add(x => x.MultiSelection, true)
        .Add(x => x.SelectedValues, selectedValues)
        .Add(x => x.SelectedValuesChanged, EventCallback.Factory.Create<IEnumerable<string>>(
            this, v => selectedValues = v))
        .AddChildContent<MudSelectItem<string>>(item => item.Add(x => x.Value, "A"))
        .AddChildContent<MudSelectItem<string>>(item => item.Add(x => x.Value, "B"))
        .AddChildContent<MudSelectItem<string>>(item => item.Add(x => x.Value, "C")));

    cut.Find(".mud-select").Click();

    cut.WaitForAssertion(() =>
    {
        var items = cut.FindAll(".mud-list-item");
        items[0].Click();
        items[1].Click();
    });

    selectedValues.ShouldContain("A");
    selectedValues.ShouldContain("B");
}
```

## Testing MudButton

### Button Click

```csharp
public class MudButtonTests : MudBlazorTestContext
{
    [Fact]
    public void Button_InvokesOnClick()
    {
        var clicked = false;

        var cut = RenderComponent<MudButton>(p => p
            .Add(x => x.OnClick, EventCallback.Factory.Create<MouseEventArgs>(
                this, _ => clicked = true))
            .AddChildContent("Click Me"));

        cut.Find("button").Click();

        clicked.ShouldBeTrue();
    }

    [Fact]
    public void Button_DisabledDoesNotClick()
    {
        var clicked = false;

        var cut = RenderComponent<MudButton>(p => p
            .Add(x => x.Disabled, true)
            .Add(x => x.OnClick, EventCallback.Factory.Create<MouseEventArgs>(
                this, _ => clicked = true)));

        // Disabled button shouldn't respond to click
        // Note: bUnit will still fire the event, so check the disabled attribute
        cut.Find("button").HasAttribute("disabled").ShouldBeTrue();
    }

    [Fact]
    public void Button_ShowsLoadingState()
    {
        var cut = RenderComponent<MudButton>(p => p
            .Add(x => x.Disabled, true)
            .AddChildContent(builder =>
            {
                builder.OpenComponent<MudProgressCircular>(0);
                builder.AddAttribute(1, "Size", Size.Small);
                builder.AddAttribute(2, "Indeterminate", true);
                builder.CloseComponent();
                builder.AddContent(3, " Loading...");
            }));

        cut.FindComponent<MudProgressCircular>().ShouldNotBeNull();
    }
}
```

## Testing MudDataGrid

### Basic DataGrid

```csharp
public class MudDataGridTests : MudBlazorTestContext
{
    private readonly List<Product> _products = new()
    {
        new() { Id = 1, Name = "Widget", Price = 9.99m },
        new() { Id = 2, Name = "Gadget", Price = 19.99m },
        new() { Id = 3, Name = "Gizmo", Price = 29.99m }
    };

    [Fact]
    public void DataGrid_RendersAllRows()
    {
        var cut = RenderComponent<MudDataGrid<Product>>(p => p
            .Add(x => x.Items, _products)
            .AddChildContent<Columns<Product>>(cols => cols
                .AddChildContent<PropertyColumn<Product, string>>(col => col
                    .Add(x => x.Property, x => x.Name)
                    .Add(x => x.Title, "Name"))
                .AddChildContent<PropertyColumn<Product, decimal>>(col => col
                    .Add(x => x.Property, x => x.Price)
                    .Add(x => x.Title, "Price"))));

        var rows = cut.FindAll("tr.mud-table-row");
        rows.Count.ShouldBe(3);
    }

    [Fact]
    public void DataGrid_SortsOnColumnClick()
    {
        var cut = RenderComponent<MudDataGrid<Product>>(p => p
            .Add(x => x.Items, _products)
            .AddChildContent<Columns<Product>>(cols => cols
                .AddChildContent<PropertyColumn<Product, string>>(col => col
                    .Add(x => x.Property, x => x.Name)
                    .Add(x => x.Sortable, true))));

        // Click header to sort
        cut.Find("th").Click();

        cut.WaitForAssertion(() =>
        {
            var firstRow = cut.Find("tr.mud-table-row td");
            firstRow.TextContent.ShouldBe("Gadget"); // Alphabetically first
        });
    }
}
```

### Testing Row Selection

```csharp
[Fact]
public void DataGrid_SelectsRow()
{
    Product? selectedItem = null;

    var cut = RenderComponent<MudDataGrid<Product>>(p => p
        .Add(x => x.Items, _products)
        .Add(x => x.SelectedItem, selectedItem)
        .Add(x => x.SelectedItemChanged, EventCallback.Factory.Create<Product>(
            this, item => selectedItem = item)));

    // Click a row
    cut.FindAll("tr.mud-table-row")[1].Click();

    selectedItem.ShouldNotBeNull();
    selectedItem!.Name.ShouldBe("Gadget");
}
```

## Testing MudDialog

### Dialog Service Integration

```csharp
public class DialogTests : MudBlazorTestContext
{
    private IDialogService DialogService => Services.GetRequiredService<IDialogService>();

    [Fact]
    public async Task Dialog_ShowsContent()
    {
        // Render a host component that will show the dialog
        var cut = RenderComponent<MudDialogProvider>();

        // Show dialog
        var dialogRef = await cut.InvokeAsync(() =>
            DialogService.ShowAsync<TestDialog>("Test Title"));

        cut.WaitForAssertion(() =>
        {
            cut.Find(".mud-dialog-title").TextContent.ShouldContain("Test Title");
        });
    }

    [Fact]
    public async Task Dialog_ReturnsResult()
    {
        var cut = RenderComponent<MudDialogProvider>();

        var dialogRef = await cut.InvokeAsync(() =>
            DialogService.ShowAsync<ConfirmDialog>("Confirm"));

        // Click the confirm button
        cut.WaitForAssertion(() =>
        {
            cut.Find(".btn-confirm").Click();
        });

        var result = await dialogRef.Result;
        result.Canceled.ShouldBeFalse();
    }
}

// Test dialog component
public class TestDialog : ComponentBase
{
    [CascadingParameter] private IMudDialogInstance MudDialog { get; set; } = default!;

    protected override void BuildRenderTree(RenderTreeBuilder builder)
    {
        builder.OpenComponent<MudDialog>(0);
        builder.AddAttribute(1, "TitleContent", (RenderFragment)(b => b.AddContent(0, "Dialog Content")));
        builder.CloseComponent();
    }
}
```

### Testing Dialog with Parameters

```csharp
[Fact]
public async Task Dialog_ReceivesParameters()
{
    var cut = RenderComponent<MudDialogProvider>();

    var parameters = new DialogParameters<ConfirmDialog>
    {
        { x => x.ContentText, "Are you sure?" },
        { x => x.ButtonText, "Yes, Delete" },
        { x => x.Color, Color.Error }
    };

    await cut.InvokeAsync(() =>
        DialogService.ShowAsync<ConfirmDialog>("Confirm", parameters));

    cut.WaitForAssertion(() =>
    {
        cut.Find(".dialog-content").TextContent.ShouldContain("Are you sure?");
        cut.Find(".btn-confirm").TextContent.ShouldBe("Yes, Delete");
    });
}
```

## Testing MudForm

### Form Validation

```csharp
public class MudFormTests : MudBlazorTestContext
{
    [Fact]
    public void Form_ValidatesOnSubmit()
    {
        var cut = RenderComponent<TestFormComponent>();

        // Submit without filling required fields
        cut.Find("button[type='button']").Click(); // MudForm uses button, not submit

        cut.WaitForAssertion(() =>
        {
            cut.FindAll(".mud-input-error").Count.ShouldBeGreaterThan(0);
        });
    }

    [Fact]
    public void Form_IsValidWhenFilled()
    {
        var cut = RenderComponent<TestFormComponent>();

        // Fill required fields
        cut.Find("input#name").Change("John Doe");
        cut.Find("input#email").Change("john@example.com");

        // Blur to trigger validation
        cut.Find("input#email").Blur();

        cut.WaitForAssertion(() =>
        {
            cut.FindAll(".mud-input-error").Count.ShouldBe(0);
        });
    }
}
```

### Testing Form with Model

```csharp
// Component under test
public class CustomerFormComponent : ComponentBase
{
    private MudForm _form = default!;
    private bool _isValid;
    private CustomerModel _model = new();

    protected override void BuildRenderTree(RenderTreeBuilder builder)
    {
        builder.OpenComponent<MudForm>(0);
        builder.AddAttribute(1, "IsValid", _isValid);
        builder.AddAttribute(2, "IsValidChanged", EventCallback.Factory.Create<bool>(this, v => _isValid = v));
        builder.AddAttribute(3, "ChildContent", (RenderFragment)(formBuilder =>
        {
            formBuilder.OpenComponent<MudTextField<string>>(0);
            formBuilder.AddAttribute(1, "Label", "Name");
            formBuilder.AddAttribute(2, "Required", true);
            formBuilder.AddAttribute(3, "Value", _model.Name);
            formBuilder.AddAttribute(4, "ValueChanged", EventCallback.Factory.Create<string>(this, v => _model.Name = v));
            formBuilder.CloseComponent();
        }));
        builder.CloseComponent();
    }
}
```

## Testing MudTable

### Table with Actions

```csharp
[Fact]
public void Table_ActionButtonInRow_Works()
{
    var deletedIds = new List<int>();

    var cut = RenderComponent<ProductTable>(p => p
        .Add(x => x.Products, _products)
        .Add(x => x.OnDelete, EventCallback.Factory.Create<int>(
            this, id => deletedIds.Add(id))));

    // Click delete on first row
    cut.Find("tr.mud-table-row .delete-btn").Click();

    deletedIds.ShouldContain(1);
}
```

### Server-Side Table

```csharp
[Fact]
public async Task Table_ServerData_LoadsCorrectly()
{
    var mockService = new Mock<IProductService>();
    mockService
        .Setup(s => s.GetPagedAsync(It.IsAny<int>(), It.IsAny<int>()))
        .ReturnsAsync(new PagedResult<Product>
        {
            Items = _products,
            TotalCount = 100
        });

    Services.AddSingleton(mockService.Object);

    var cut = RenderComponent<ServerSideProductTable>();

    await cut.WaitForAssertionAsync(() =>
    {
        var rows = cut.FindAll("tr.mud-table-row");
        rows.Count.ShouldBe(3);
    });
}
```

## Testing Snackbar

```csharp
public class SnackbarTests : MudBlazorTestContext
{
    private ISnackbar Snackbar => Services.GetRequiredService<ISnackbar>();

    [Fact]
    public void Snackbar_ShowsMessage()
    {
        var cut = RenderComponent<MudSnackbarProvider>();

        cut.InvokeAsync(() => Snackbar.Add("Test message", Severity.Success));

        cut.WaitForAssertion(() =>
        {
            cut.Find(".mud-snackbar").TextContent.ShouldContain("Test message");
        });
    }

    [Fact]
    public void Snackbar_ShowsCorrectSeverity()
    {
        var cut = RenderComponent<MudSnackbarProvider>();

        cut.InvokeAsync(() => Snackbar.Add("Error!", Severity.Error));

        cut.WaitForAssertion(() =>
        {
            cut.Find(".mud-snackbar").ClassList.ShouldContain("mud-alert-error");
        });
    }
}
```

## Common Gotchas

### 1. Popover Components Need Provider

```csharp
// Select, Autocomplete, Menu, etc. render into MudPopoverProvider
// Always render the provider first or use RenderMudComponent helper
var provider = RenderComponent<MudPopoverProvider>();
var cut = RenderComponent<MudSelect<string>>(...);
```

### 2. Async Rendering

```csharp
// MudBlazor components often render asynchronously
// Use WaitForAssertion instead of immediate assertions
cut.WaitForAssertion(() =>
{
    cut.Find(".expected-element").ShouldNotBeNull();
});
```

### 3. JS Interop in Strict Mode

```csharp
// MudBlazor uses JS extensively - use Loose mode or set up all calls
JSInterop.Mode = JSRuntimeMode.Loose;

// Or explicitly mock common calls
JSInterop.SetupVoid("mudPopover.connect", _ => true);
```

### 4. Event Timing

```csharp
// Some components debounce or delay events
// Use WaitForState for state-dependent assertions
cut.WaitForState(() => cut.Instance.Value == expectedValue);
```
