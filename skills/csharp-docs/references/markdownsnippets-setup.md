# MarkdownSnippets Setup

MarkdownSnippets is a tool by Simon Cropp that keeps code samples in documentation synchronized with actual compilable code.

## How It Works

1. Code samples live in the reference application with `#region snippet-name` markers
2. Markdown files contain `<!-- snippet: snippet-name -->` placeholders
3. MarkdownSnippets extracts code from regions and injects into markdown
4. Running the tool keeps documentation in sync with code changes

## Installation Options

### Option 1: .NET Global Tool (Recommended)

```bash
dotnet tool install -g MarkdownSnippets.Tool
```

Run manually:
```bash
mdsnippets
```

### Option 2: NuGet Package for Build Integration

Add to your reference application's Server.WebApi project (or any project that builds):

```xml
<ItemGroup>
  <PackageReference Include="MarkdownSnippets.MsBuild" Version="*" PrivateAssets="all" />
</ItemGroup>
```

This runs automatically during build.

### Option 3: GitHub Action

```yaml
- name: Run MarkdownSnippets
  uses: SimonCropp/MarkdownSnippets@master
```

## Configuration

Create `mdsnippets.json` in repository root:

```json
{
  "Convention": "InPlaceOverwrite",
  "TocLevel": 2,
  "MaxWidth": 120,
  "LinkFormat": "GitHub",
  "DocumentExtensions": [
    "md"
  ],
  "UrlsAsSnippets": [],
  "ExcludeDirectories": [
    "docs/todos",
    "docs/plans",
    "docs/release-notes"
  ],
  "ExcludeMarkdownDirectories": [
    "docs/todos",
    "docs/plans",
    "docs/release-notes"
  ]
}
```

### Configuration Options

| Option | Description | Recommended |
|--------|-------------|-------------|
| `Convention` | How to handle snippets | `InPlaceOverwrite` |
| `TocLevel` | Table of contents depth | `2` |
| `MaxWidth` | Max line width | `120` |
| `ExcludeDirectories` | Directories to skip for snippets | todos, plans, release-notes |
| `ExcludeMarkdownDirectories` | Markdown dirs to skip | Same as above |

## Reference Application Structure

The reference application is the source for all snippets:

```
src/docs/reference-app/
├── ReferenceApp.sln
├── Domain/                    # Domain layer snippets
│   ├── Employees/
│   │   └── Employee.cs        # #region employee-aggregate
│   └── Shared/
│       └── EmailAddress.cs    # #region email-value-object
├── Application/               # Application layer snippets
│   └── Employees/
│       └── EmployeeService.cs # #region employee-service-create
├── Infrastructure/            # Infrastructure layer snippets
│   └── Persistence/
│       └── Configurations/
│           └── EmployeeConfiguration.cs  # #region ef-employee-config
├── Server.WebApi/             # Server layer snippets
│   ├── Program.cs             # #region startup-di
│   └── Controllers/
│       └── EmployeesController.cs  # #region api-employees-controller
├── Client.Blazor/             # Blazor snippets (when needed)
│   └── Pages/
│       └── EmployeeForm.razor # #region blazor-employee-form
└── Tests/                     # Test snippets (for testing docs)
    └── Domain.Tests/
        └── EmployeeTests.cs   # #region test-employee-aggregate
```

## Writing Snippets

### In Reference Application Code

Wrap snippet code with `#region` markers:

```csharp
// Domain/Employees/Employee.cs

public class Employee
{
    // Code before snippet...

    #region employee-create-method
    public static Employee Create(string firstName, string lastName, EmailAddress email)
    {
        var employee = new Employee
        {
            Id = EmployeeId.New(),
            FirstName = firstName,
            LastName = lastName,
            Email = email,
            Status = EmployeeStatus.Active
        };

        employee.AddDomainEvent(new EmployeeCreatedEvent(employee.Id));
        return employee;
    }
    #endregion

    // Code after snippet...
}
```

### In Markdown Documentation

```markdown
## Creating an Employee

The Employee aggregate enforces business rules during creation:

<!-- snippet: employee-create-method -->
<!-- endSnippet -->
```

### After Running MarkdownSnippets

The markdown file becomes:

```markdown
## Creating an Employee

The Employee aggregate enforces business rules during creation:

<!-- snippet: employee-create-method -->
```cs
public static Employee Create(string firstName, string lastName, EmailAddress email)
{
    var employee = new Employee
    {
        Id = EmployeeId.New(),
        FirstName = firstName,
        LastName = lastName,
        Email = email,
        Status = EmployeeStatus.Active
    };

    employee.AddDomainEvent(new EmployeeCreatedEvent(employee.Id));
    return employee;
}
```
<!-- endSnippet -->
```

## Workflow

1. **docs-architect** creates documentation with empty snippet placeholders
2. **docs-code-samples** implements code in the reference application with `#region` markers
3. Run `mdsnippets` to sync code into documentation
4. Commit both documentation and reference application changes

## Troubleshooting

### Snippet Not Found

Error: `Snippet 'name' not found`

- Verify `#region name` exists in the reference application
- Check spelling matches exactly (case-sensitive)
- Ensure the file is in a scanned directory (not excluded)

### Snippet Not Updated

- Run `mdsnippets` manually to force update
- Check `ExcludeDirectories` doesn't exclude your source
- Verify the snippet markers are formatted correctly

### Build Integration Not Running

- Ensure `MarkdownSnippets.MsBuild` package is installed
- Check it has `PrivateAssets="all"` attribute
- Verify build output for MarkdownSnippets messages

## Snippet Naming by Layer

| Layer | Pattern | Examples |
|-------|---------|----------|
| Domain | `{aggregate}-{concept}` | `employee-aggregate`, `email-value-object` |
| Application | `{feature}-service-{action}` | `employee-service-create`, `employee-service-update` |
| Infrastructure | `{feature}-repository`, `ef-{config}` | `employee-repository`, `ef-employee-config` |
| Server | `api-{feature}-{action}`, `startup-{config}` | `api-employees-get`, `startup-di` |
| Client | `blazor-{component}`, `console-{feature}` | `blazor-employee-form`, `console-main` |
| Tests | `test-{layer}-{feature}` | `test-domain-employee`, `test-api-integration` |
