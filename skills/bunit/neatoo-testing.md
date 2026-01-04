# Testing with Neatoo Domain Objects

## Overview

When testing Blazor components that use Neatoo domain objects, you need to:
1. Mock or create Neatoo factories
2. Create test instances of domain objects
3. Handle the `IsSavable`, `IsModified`, `IsValid`, and `IsBusy` properties
4. Test validation rules and error states
5. Properly handle PropertyChanged events

## Setting Up Neatoo Services

### Test Context Setup

```csharp
public abstract class NeatooTestContext : TestContext
{
    protected NeatooTestContext()
    {
        // Add Neatoo services for testing
        Services.AddNeatooServices(NeatooFactory.Local, typeof(IPatient).Assembly);

        // Add MudBlazor services if using MudNeatoo components
        Services.AddMudServices();

        JSInterop.Mode = JSRuntimeMode.Loose;
    }
}
```

### Mocking Neatoo Factories

```csharp
public class PatientFormTests : NeatooTestContext
{
    private readonly Mock<IPatientFactory> _patientFactoryMock;

    public PatientFormTests()
    {
        _patientFactoryMock = new Mock<IPatientFactory>();
        Services.AddSingleton(_patientFactoryMock.Object);
    }

    [Fact]
    public async Task Form_LoadsPatient()
    {
        var patient = CreateMockPatient();

        _patientFactoryMock
            .Setup(f => f.Fetch(It.IsAny<int>()))
            .ReturnsAsync(patient);

        var cut = RenderComponent<PatientForm>(p => p
            .Add(x => x.PatientId, 1));

        await cut.WaitForStateAsync(() =>
            cut.Find("input#firstName").GetAttribute("value") == "John");
    }
}
```

## Creating Test Domain Objects

### Using Real Neatoo Objects

When you can create real Neatoo objects in tests:

```csharp
public class PatientFormTests : NeatooTestContext
{
    [Fact]
    public async Task Form_CreatesNewPatient()
    {
        // Use real factory to create instance
        var patientFactory = Services.GetRequiredService<IPatientFactory>();
        var patient = await patientFactory.Create();

        var cut = RenderComponent<PatientForm>(p => p
            .Add(x => x.Patient, patient));

        // Verify empty form
        cut.Find("input#firstName").GetAttribute("value").ShouldBeEmpty();
        cut.Instance.Patient.IsModified.ShouldBeFalse();
    }
}
```

### Creating Mock Domain Objects

When you need to mock domain objects:

```csharp
private IPatient CreateMockPatient()
{
    var mock = new Mock<IPatient>();

    mock.Setup(p => p.FirstName).Returns("John");
    mock.Setup(p => p.LastName).Returns("Doe");
    mock.Setup(p => p.IsValid).Returns(true);
    mock.Setup(p => p.IsModified).Returns(false);
    mock.Setup(p => p.IsSavable).Returns(true);
    mock.Setup(p => p.IsBusy).Returns(false);

    // Setup property indexer for MudNeatoo components
    var firstNameProperty = new Mock<IPropertyInfo>();
    firstNameProperty.Setup(p => p.IsValid).Returns(true);
    firstNameProperty.Setup(p => p.ErrorMessages).Returns(Array.Empty<string>());

    mock.Setup(p => p[nameof(IPatient.FirstName)]).Returns(firstNameProperty.Object);

    return mock.Object;
}
```

## Testing Form Binding

### With MudNeatoo Components

```csharp
[Fact]
public void Form_BindsToNeatooEntity()
{
    var patient = await CreateTestPatient();

    var cut = RenderComponent<PatientForm>(p => p
        .Add(x => x.Patient, patient));

    // Find MudNeatooTextField
    var firstNameField = cut.Find("input#firstName");
    firstNameField.Change("Jane");

    // Verify entity was updated
    patient.FirstName.ShouldBe("Jane");
    patient.IsModified.ShouldBeTrue();
}
```

### Testing Two-Way Binding

```csharp
[Fact]
public async Task Form_UpdatesWhenEntityChanges()
{
    var patient = await CreateTestPatient();
    patient.FirstName = "John";

    var cut = RenderComponent<PatientForm>(p => p
        .Add(x => x.Patient, patient));

    // Change entity programmatically
    patient.FirstName = "Jane";

    // Trigger PropertyChanged (component should subscribe)
    await cut.InvokeAsync(() => cut.Render());

    cut.Find("input#firstName").GetAttribute("value").ShouldBe("Jane");
}
```

## Testing Validation

### Testing IsValid State

```csharp
[Fact]
public async Task Form_ShowsValidationErrors()
{
    var patient = await CreateTestPatient();

    var cut = RenderComponent<PatientForm>(p => p
        .Add(x => x.Patient, patient));

    // Trigger validation by leaving required field empty
    var firstNameInput = cut.Find("input#firstName");
    firstNameInput.Change("");
    firstNameInput.Blur();

    // Wait for async validation
    await patient.WaitForTasks();

    cut.WaitForAssertion(() =>
    {
        cut.Find(".validation-error").ShouldNotBeNull();
        patient.IsValid.ShouldBeFalse();
    });
}
```

### Testing Neatoo Rules

```csharp
[Fact]
public async Task Form_ExecutesBusinessRules()
{
    var visit = await CreateTestVisit();

    var cut = RenderComponent<VisitDateEditor>(p => p
        .Add(x => x.Visit, visit));

    // Set future date (should fail validation rule)
    var dateInput = cut.Find("input#visitDate");
    dateInput.Change(DateTime.Today.AddDays(1).ToString("yyyy-MM-dd"));

    // Wait for rules to execute
    await visit.WaitForTasks();

    cut.WaitForAssertion(() =>
    {
        cut.Find(".mud-input-error").TextContent
            .ShouldContain("Date cannot be in the future");
        visit.IsSavable.ShouldBeFalse();
    });
}
```

### Testing NeatooValidationSummary

```csharp
[Fact]
public async Task ValidationSummary_ShowsAllErrors()
{
    var patient = await CreateInvalidPatient();

    var cut = RenderComponent<PatientForm>(p => p
        .Add(x => x.Patient, patient));

    // Trigger full validation
    cut.Find(".validate-btn").Click();
    await patient.WaitForTasks();

    cut.WaitForAssertion(() =>
    {
        var summary = cut.FindComponent<NeatooValidationSummary>();
        var errors = summary.FindAll(".validation-message");

        errors.Count.ShouldBeGreaterThan(0);
    });
}
```

## Testing Save Operations

### IsSavable State

```csharp
[Fact]
public async Task SaveButton_DisabledWhenNotSavable()
{
    var patient = await CreateTestPatient();

    var cut = RenderComponent<PatientForm>(p => p
        .Add(x => x.Patient, patient));

    // Initially not modified, so not savable
    var saveButton = cut.Find(".save-btn");
    saveButton.HasAttribute("disabled").ShouldBeTrue();

    // Make a change
    cut.Find("input#firstName").Change("Updated");

    // Wait for state update
    await patient.WaitForTasks();

    cut.WaitForAssertion(() =>
    {
        cut.Find(".save-btn").HasAttribute("disabled").ShouldBeFalse();
    });
}
```

### Testing Save Flow

```csharp
[Fact]
public async Task Form_SavesPatient()
{
    var patient = await CreateTestPatient();
    var savedPatient = false;

    _patientFactoryMock
        .Setup(f => f.Save(It.IsAny<IPatient>()))
        .Callback(() => savedPatient = true)
        .ReturnsAsync(patient);

    var cut = RenderComponent<PatientForm>(p => p
        .Add(x => x.Patient, patient));

    // Make changes
    cut.Find("input#firstName").Change("Updated");
    await patient.WaitForTasks();

    // Click save
    cut.Find(".save-btn").Click();

    cut.WaitForAssertion(() =>
    {
        savedPatient.ShouldBeTrue();
    });
}
```

### Testing WaitForTasks

```csharp
[Fact]
public async Task Form_WaitsForAsyncValidation()
{
    var patient = await CreateTestPatient();

    // Setup async validation rule
    var validationComplete = new TaskCompletionSource();
    // ... configure patient with async rule

    var cut = RenderComponent<PatientForm>(p => p
        .Add(x => x.Patient, patient));

    cut.Find("input#email").Change("test@example.com");

    // IsBusy should be true during async validation
    patient.IsBusy.ShouldBeTrue();

    // Complete validation
    validationComplete.SetResult();
    await patient.WaitForTasks();

    patient.IsBusy.ShouldBeFalse();
    patient.IsValid.ShouldBeTrue();
}
```

## Testing Child Collections

### Adding Items

```csharp
[Fact]
public async Task Form_AddsChildItem()
{
    var visit = await CreateTestVisit();

    var cut = RenderComponent<VisitForm>(p => p
        .Add(x => x.Visit, visit));

    var initialCount = visit.SignsAssessments.Count;

    cut.Find(".add-signs-btn").Click();

    cut.WaitForAssertion(() =>
    {
        visit.SignsAssessments.Count.ShouldBe(initialCount + 1);
    });
}
```

### Removing Items

```csharp
[Fact]
public async Task Form_RemovesChildItem()
{
    var visit = await CreateVisitWithAssessments();

    var cut = RenderComponent<VisitForm>(p => p
        .Add(x => x.Visit, visit));

    var initialCount = visit.SignsAssessments.Count;

    // Click remove on first item
    cut.Find(".signs-item:first-child .remove-btn").Click();

    cut.WaitForAssertion(() =>
    {
        visit.SignsAssessments.Count.ShouldBe(initialCount - 1);
    });
}
```

### Testing Child Validation

```csharp
[Fact]
public async Task ParentInvalid_WhenChildInvalid()
{
    var visit = await CreateVisitWithAssessments();

    var cut = RenderComponent<VisitForm>(p => p
        .Add(x => x.Visit, visit));

    // Make child item invalid
    var firstAssessment = visit.SignsAssessments[0];
    cut.Find(".signs-item:first-child input#severity").Change("");

    await visit.WaitForTasks();

    // Parent should reflect child validity
    visit.IsValid.ShouldBeFalse();
    visit.IsSavable.ShouldBeFalse();
}
```

## Testing PropertyChanged

### Subscribing to Changes

```csharp
[Fact]
public void Component_UpdatesOnPropertyChanged()
{
    var patient = await CreateTestPatient();
    var propertyChangedCalled = false;

    patient.PropertyChanged += (s, e) =>
    {
        if (e.PropertyName == nameof(IPatient.FirstName))
            propertyChangedCalled = true;
    };

    var cut = RenderComponent<PatientDisplay>(p => p
        .Add(x => x.Patient, patient));

    patient.FirstName = "Updated";

    propertyChangedCalled.ShouldBeTrue();

    // Component should re-render
    cut.WaitForAssertion(() =>
    {
        cut.Find(".first-name").TextContent.ShouldBe("Updated");
    });
}
```

## Testing IsBusy State

```csharp
[Fact]
public async Task Form_ShowsLoadingDuringAsyncValidation()
{
    var patient = await CreateTestPatient();

    // Make validation slow
    var validationDelay = new TaskCompletionSource();
    // Configure patient with delayed async validation

    var cut = RenderComponent<PatientForm>(p => p
        .Add(x => x.Patient, patient));

    // Trigger async validation
    cut.Find("input#email").Change("new@email.com");

    // Should show loading indicator
    cut.WaitForAssertion(() =>
    {
        cut.Find(".validation-loading").ShouldNotBeNull();
    });

    // Complete validation
    validationDelay.SetResult();

    // Loading should disappear
    cut.WaitForAssertion(() =>
    {
        cut.FindAll(".validation-loading").Count.ShouldBe(0);
    });
}
```

## Complete Example

```csharp
public class PatientFormTests : NeatooTestContext
{
    private readonly Mock<IPatientFactory> _factoryMock;

    public PatientFormTests()
    {
        _factoryMock = new Mock<IPatientFactory>();
        Services.AddSingleton(_factoryMock.Object);
    }

    [Fact]
    public async Task CompleteEditFlow()
    {
        // Arrange
        var patient = await CreateTestPatient();
        patient.FirstName = "John";
        patient.LastName = "Doe";

        _factoryMock.Setup(f => f.Fetch(1)).ReturnsAsync(patient);
        _factoryMock.Setup(f => f.Save(It.IsAny<IPatient>())).ReturnsAsync(patient);

        var cut = RenderComponent<PatientEditPage>(p => p
            .Add(x => x.PatientId, 1));

        // Wait for load
        await cut.WaitForStateAsync(() => !cut.Instance.IsLoading);

        // Verify initial state
        cut.Find("input#firstName").GetAttribute("value").ShouldBe("John");
        cut.Find(".save-btn").HasAttribute("disabled").ShouldBeTrue();

        // Act - make changes
        cut.Find("input#firstName").Change("Jane");
        await patient.WaitForTasks();

        // Assert - save enabled
        cut.Find(".save-btn").HasAttribute("disabled").ShouldBeFalse();

        // Act - save
        cut.Find(".save-btn").Click();

        // Assert - save was called
        _factoryMock.Verify(f => f.Save(
            It.Is<IPatient>(p => p.FirstName == "Jane")),
            Times.Once);
    }
}
```

## Best Practices

### 1. Always Wait for Tasks

```csharp
// After any change that might trigger validation
cut.Find("input").Change("value");
await entity.WaitForTasks();
```

### 2. Use Real Factories When Possible

```csharp
// Real factories catch integration issues early
Services.AddNeatooServices(NeatooFactory.Local, typeof(IPatient).Assembly);
var factory = Services.GetRequiredService<IPatientFactory>();
var patient = await factory.Create();
```

### 3. Test State Transitions

```csharp
// Test the full lifecycle: clean -> modified -> valid -> saved
entity.IsModified.ShouldBeFalse();
// Make change
entity.IsModified.ShouldBeTrue();
// Validate
entity.IsValid.ShouldBeTrue();
entity.IsSavable.ShouldBeTrue();
```

### 4. Mock at Factory Level

```csharp
// Mock the factory, not the entity
_factoryMock.Setup(f => f.Fetch(It.IsAny<int>()))
    .ReturnsAsync(CreateTestPatient());
```
