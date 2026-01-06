# bUnit Core Concepts

## TestContext

`TestContext` is the base class for bUnit tests. It provides:

| Property/Method | Purpose |
|-----------------|---------|
| `RenderComponent<T>()` | Render a component and return `IRenderedComponent<T>` |
| `Services` | `IServiceCollection` for DI registration |
| `JSInterop` | Mock JavaScript interop calls |
| `ComponentFactories` | Register component doubles/stubs |
| `Renderer` | Access to the test renderer |
| `DisposeComponents()` | Dispose all rendered components |

```csharp
public class MyTests : TestContext
{
    public MyTests()
    {
        // Register services in constructor
        Services.AddSingleton<IMyService, MockMyService>();

        // Configure JSInterop
        JSInterop.Mode = JSRuntimeMode.Loose;
    }
}
```

## IRenderedComponent<T>

The object returned from `RenderComponent<T>()`:

| Property/Method | Purpose |
|-----------------|---------|
| `Instance` | Access the component instance directly |
| `Markup` | Get rendered HTML as string |
| `Find(selector)` | Find single element by CSS selector |
| `FindAll(selector)` | Find all matching elements |
| `FindComponent<T>()` | Find child component |
| `FindComponents<T>()` | Find all child components |
| `InvokeAsync(action)` | Invoke action on component's sync context |
| `Render()` | Force re-render |
| `SetParametersAndRender()` | Update parameters and re-render |
| `WaitForState(predicate)` | Wait for condition to be true |
| `WaitForAssertion(assertion)` | Wait for assertion to pass |

## Finding Elements

```csharp
// By CSS selector
var button = cut.Find("button");
var submitBtn = cut.Find("button[type='submit']");
var primaryBtn = cut.Find(".btn-primary");
var namedInput = cut.Find("input#username");

// Find all matching
var allButtons = cut.FindAll("button");
var listItems = cut.FindAll("li.item");

// Find child components
var childComponent = cut.FindComponent<ChildComponent>();
var allCards = cut.FindComponents<Card>();
```

## DOM Assertions

```csharp
// Markup matching (flexible whitespace)
element.MarkupMatches("<p>Expected content</p>");

// Text content
element.TextContent.ShouldBe("Expected text");
element.TextContent.ShouldContain("partial");

// Attributes
element.GetAttribute("class").ShouldContain("active");
element.HasAttribute("disabled").ShouldBeTrue();
element.Id.ShouldBe("my-element");

// Element existence
cut.FindAll(".item").Count.ShouldBe(5);
cut.Find(".error").ShouldNotBeNull();

// Semantic HTML diff (ignores insignificant differences)
element.MarkupMatches(@"
    <div class=""container"">
        <span>Content</span>
    </div>");
```

## User Interactions

```csharp
// Click events
cut.Find("button").Click();
cut.Find("button").DoubleClick();

// Input events
cut.Find("input").Change("new value");
cut.Find("input").Input("typing...");

// Form submission
cut.Find("form").Submit();

// Keyboard events
cut.Find("input").KeyDown(Key.Enter);
cut.Find("input").KeyUp(Key.Escape);
cut.Find("input").KeyPress("a");

// Focus events
cut.Find("input").Focus();
cut.Find("input").Blur();

// Mouse events
cut.Find("div").MouseOver();
cut.Find("div").MouseOut();

// Checkbox/radio
cut.Find("input[type='checkbox']").Change(true);

// Select dropdown
cut.Find("select").Change("option-value");
```
