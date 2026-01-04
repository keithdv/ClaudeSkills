# Component Testing Patterns

## Parameters

### Simple Parameters

```csharp
[Fact]
public void Button_WithLabel_DisplaysLabel()
{
    var cut = RenderComponent<Button>(parameters => parameters
        .Add(p => p.Label, "Click Me")
        .Add(p => p.Disabled, false)
        .Add(p => p.Size, ButtonSize.Large));

    cut.Find("button").TextContent.ShouldBe("Click Me");
}
```

### Complex Object Parameters

```csharp
[Fact]
public void CustomerCard_WithCustomer_DisplaysInfo()
{
    var customer = new Customer
    {
        Id = 1,
        FirstName = "John",
        LastName = "Doe",
        Email = "john@example.com"
    };

    var cut = RenderComponent<CustomerCard>(p => p
        .Add(x => x.Customer, customer));

    cut.Find(".customer-name").TextContent.ShouldBe("John Doe");
    cut.Find(".customer-email").TextContent.ShouldBe("john@example.com");
}
```

### Collection Parameters

```csharp
[Fact]
public void ProductList_WithProducts_RendersAllItems()
{
    var products = new List<Product>
    {
        new() { Id = 1, Name = "Widget" },
        new() { Id = 2, Name = "Gadget" },
        new() { Id = 3, Name = "Gizmo" }
    };

    var cut = RenderComponent<ProductList>(p => p
        .Add(x => x.Products, products));

    cut.FindAll(".product-item").Count.ShouldBe(3);
}
```

### Nullable/Optional Parameters

```csharp
[Fact]
public void Header_WithoutSubtitle_HidesSubtitleElement()
{
    var cut = RenderComponent<Header>(p => p
        .Add(x => x.Title, "Main Title")
        .Add(x => x.Subtitle, null));  // Optional parameter

    cut.FindAll(".subtitle").Count.ShouldBe(0);
}
```

## Event Callbacks

### Testing EventCallback Invocation

```csharp
[Fact]
public void DeleteButton_WhenClicked_InvokesOnDelete()
{
    var deleteWasCalled = false;
    var deletedId = 0;

    var cut = RenderComponent<DeleteButton>(p => p
        .Add(x => x.ItemId, 42)
        .Add(x => x.OnDelete, EventCallback.Factory.Create<int>(
            this, id => { deleteWasCalled = true; deletedId = id; })));

    cut.Find("button").Click();

    deleteWasCalled.ShouldBeTrue();
    deletedId.ShouldBe(42);
}
```

### Testing Async EventCallback

```csharp
[Fact]
public async Task SaveButton_WhenClicked_InvokesOnSaveAsync()
{
    var tcs = new TaskCompletionSource<bool>();

    var cut = RenderComponent<SaveButton>(p => p
        .Add(x => x.OnSave, EventCallback.Factory.Create(
            this, async () =>
            {
                await Task.Delay(10);
                tcs.SetResult(true);
            })));

    cut.Find("button").Click();

    var result = await tcs.Task;
    result.ShouldBeTrue();
}
```

### Multiple Event Callbacks

```csharp
[Fact]
public void Dialog_InvokesCorrectCallback()
{
    var confirmCalled = false;
    var cancelCalled = false;

    var cut = RenderComponent<ConfirmDialog>(p => p
        .Add(x => x.OnConfirm, EventCallback.Factory.Create(this, () => confirmCalled = true))
        .Add(x => x.OnCancel, EventCallback.Factory.Create(this, () => cancelCalled = true)));

    // Test confirm
    cut.Find(".btn-confirm").Click();
    confirmCalled.ShouldBeTrue();

    // Reset and test cancel
    confirmCalled = false;
    cut.Find(".btn-cancel").Click();
    cancelCalled.ShouldBeTrue();
    confirmCalled.ShouldBeFalse();
}
```

## Cascading Values

### Simple Cascading Value

```csharp
[Fact]
public void ThemedComponent_UsesCascadedTheme()
{
    var theme = new Theme { Primary = "blue", Secondary = "gray" };

    var cut = RenderComponent<ThemedButton>(p => p
        .AddCascadingValue(theme));

    cut.Find("button").ClassList.ShouldContain("theme-blue");
}
```

### Named Cascading Value

```csharp
[Fact]
public void Component_UsesNamedCascadingValue()
{
    var cut = RenderComponent<MyComponent>(p => p
        .AddCascadingValue("UserContext", new UserContext { Name = "Alice" }));

    cut.Find(".username").TextContent.ShouldBe("Alice");
}
```

### Multiple Cascading Values

```csharp
[Fact]
public void Component_WithMultipleCascadingValues()
{
    var theme = new Theme { Primary = "blue" };
    var user = new UserContext { Name = "Bob", IsAdmin = true };

    var cut = RenderComponent<AdminPanel>(p => p
        .AddCascadingValue(theme)
        .AddCascadingValue(user));

    cut.Find(".admin-badge").ShouldNotBeNull();
}
```

### CascadingValue with EditContext

```csharp
[Fact]
public void FormField_WithEditContext_ShowsValidation()
{
    var model = new LoginModel();
    var editContext = new EditContext(model);

    var cut = RenderComponent<EmailField>(p => p
        .AddCascadingValue(editContext)
        .Add(x => x.Value, "")
        .Add(x => x.ValueChanged, EventCallback.Factory.Create<string>(this, _ => { })));

    // Trigger validation
    editContext.Validate();

    cut.Find(".validation-message").ShouldNotBeNull();
}
```

## Render Fragments

### ChildContent

```csharp
[Fact]
public void Card_RendersChildContent()
{
    var cut = RenderComponent<Card>(p => p
        .AddChildContent("<p>Card content here</p>"));

    cut.Find(".card-body p").TextContent.ShouldBe("Card content here");
}
```

### ChildContent with Components

```csharp
[Fact]
public void Card_RendersChildComponent()
{
    var cut = RenderComponent<Card>(p => p
        .AddChildContent<Button>(buttonParams => buttonParams
            .Add(b => b.Label, "Inner Button")));

    cut.FindComponent<Button>().ShouldNotBeNull();
}
```

### Named RenderFragment Parameters

```csharp
[Fact]
public void DataGrid_UsesCustomHeaderTemplate()
{
    var cut = RenderComponent<DataGrid<Product>>(p => p
        .Add(x => x.Items, products)
        .Add(x => x.HeaderTemplate, builder =>
        {
            builder.OpenElement(0, "th");
            builder.AddContent(1, "Custom Header");
            builder.CloseElement();
        }));

    cut.Find("th").TextContent.ShouldBe("Custom Header");
}
```

### Typed RenderFragment

```csharp
[Fact]
public void List_UsesItemTemplate()
{
    var items = new[] { "Apple", "Banana", "Cherry" };

    var cut = RenderComponent<ItemList<string>>(p => p
        .Add(x => x.Items, items)
        .Add<string>(x => x.ItemTemplate, item => builder =>
        {
            builder.OpenElement(0, "li");
            builder.AddAttribute(1, "class", "fruit");
            builder.AddContent(2, item.ToUpper());
            builder.CloseElement();
        }));

    var listItems = cut.FindAll("li.fruit");
    listItems.Count.ShouldBe(3);
    listItems[0].TextContent.ShouldBe("APPLE");
}
```

## Child Components

### Finding Child Components

```csharp
[Fact]
public void Parent_ContainsChildComponent()
{
    var cut = RenderComponent<ParentComponent>();

    // Find single child
    var child = cut.FindComponent<ChildComponent>();
    child.Instance.SomeProperty.ShouldBe(expectedValue);

    // Find all children of type
    var allChildren = cut.FindComponents<ChildComponent>();
    allChildren.Count.ShouldBe(3);
}
```

### Testing Child Component Interactions

```csharp
[Fact]
public void Parent_RespondsToChildEvent()
{
    var cut = RenderComponent<ShoppingCart>();

    // Find the first item's remove button (inside a child component)
    var firstItem = cut.FindComponent<CartItem>();
    firstItem.Find(".remove-btn").Click();

    // Parent should update
    cut.Find(".cart-count").TextContent.ShouldBe("0");
}
```

### Stubbing Child Components

```csharp
public class ParentTests : TestContext
{
    public ParentTests()
    {
        // Replace heavy component with stub
        ComponentFactories.AddStub<ExpensiveChart>("Chart Stub");
    }

    [Fact]
    public void Parent_RendersFastWithStub()
    {
        var cut = RenderComponent<Dashboard>();

        cut.Find(".stub").TextContent.ShouldBe("Chart Stub");
    }
}
```

### Custom Component Stub

```csharp
public class ParentTests : TestContext
{
    public ParentTests()
    {
        // Stub with custom rendering
        ComponentFactories.AddStub<DataChart>(parameters =>
            $"<div class='chart-stub' data-items='{parameters.Get(x => x.DataPoints)?.Count}'></div>");
    }

    [Fact]
    public void Parent_PassesDataToChart()
    {
        var cut = RenderComponent<Dashboard>(p => p
            .Add(x => x.ChartData, new List<DataPoint> { new(), new(), new() }));

        cut.Find(".chart-stub").GetAttribute("data-items").ShouldBe("3");
    }
}
```

## Updating Parameters

### SetParametersAndRender

```csharp
[Fact]
public void Counter_UpdatesWhenInitialCountChanges()
{
    var cut = RenderComponent<Counter>(p => p
        .Add(x => x.InitialCount, 0));

    cut.Find(".count").TextContent.ShouldBe("0");

    // Update parameter and re-render
    cut.SetParametersAndRender(p => p
        .Add(x => x.InitialCount, 10));

    cut.Find(".count").TextContent.ShouldBe("10");
}
```

### Instance Property Changes

```csharp
[Fact]
public void Component_ReactsToInstancePropertyChange()
{
    var cut = RenderComponent<StatefulComponent>();

    // Access instance and modify
    cut.Instance.Count = 5;

    // Force re-render
    cut.Render();

    cut.Find(".count").TextContent.ShouldBe("5");
}
```

### InvokeAsync for StateHasChanged

```csharp
[Fact]
public async Task Component_UpdatesAfterAsyncOperation()
{
    var cut = RenderComponent<AsyncComponent>();

    // Invoke method that calls StateHasChanged
    await cut.InvokeAsync(() => cut.Instance.LoadDataAsync());

    cut.Find(".data").TextContent.ShouldNotBeEmpty();
}
```

## Two-Way Binding

### Testing @bind

```csharp
[Fact]
public void Input_TwoWayBinding_UpdatesParent()
{
    var boundValue = "initial";

    var cut = RenderComponent<TextInput>(p => p
        .Add(x => x.Value, boundValue)
        .Add(x => x.ValueChanged, EventCallback.Factory.Create<string>(
            this, newValue => boundValue = newValue)));

    cut.Find("input").Change("updated");

    boundValue.ShouldBe("updated");
}
```

### Complex Two-Way Binding

```csharp
[Fact]
public void DatePicker_TwoWayBinding()
{
    DateTime? selectedDate = null;

    var cut = RenderComponent<DatePicker>(p => p
        .Add(x => x.Date, selectedDate)
        .Add(x => x.DateChanged, EventCallback.Factory.Create<DateTime?>(
            this, date => selectedDate = date)));

    cut.Find("input").Change("2024-12-25");

    selectedDate.ShouldBe(new DateTime(2024, 12, 25));
}
```

## Component Lifecycle

### Testing OnInitialized

```csharp
[Fact]
public void Component_LoadsDataOnInit()
{
    Services.AddSingleton<IDataService>(new MockDataService());

    var cut = RenderComponent<DataLoader>();

    // OnInitialized should have fetched data
    cut.FindAll(".item").Count.ShouldBeGreaterThan(0);
}
```

### Testing OnParametersSet

```csharp
[Fact]
public void Component_ReactsToParameterChanges()
{
    var cut = RenderComponent<FilteredList>(p => p
        .Add(x => x.Filter, ""));

    cut.FindAll(".item").Count.ShouldBe(10);

    cut.SetParametersAndRender(p => p
        .Add(x => x.Filter, "active"));

    cut.FindAll(".item").Count.ShouldBe(3);
}
```

### Testing OnAfterRender

```csharp
[Fact]
public void Component_InitializesJsOnAfterRender()
{
    JSInterop.SetupVoid("initChart", _ => true);

    var cut = RenderComponent<ChartComponent>();

    JSInterop.VerifyInvoke("initChart", calledTimes: 1);
}
```

### Testing IDisposable

```csharp
[Fact]
public void Component_DisposesResources()
{
    var disposed = false;
    var mockService = new Mock<IDisposableService>();
    mockService.Setup(s => s.Dispose()).Callback(() => disposed = true);

    Services.AddSingleton(mockService.Object);

    var cut = RenderComponent<ResourceComponent>();

    // Dispose the component
    cut.Dispose();

    // Verify cleanup
    mockService.Verify(s => s.Dispose(), Times.Once);
}
```
