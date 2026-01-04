# MudBlazor Data Display Components

## MudDataGrid

MudDataGrid is a comprehensive data display component with sorting, filtering, pagination, and inline editing support.

### Basic DataGrid

```razor
<MudDataGrid Items="@products"
             T="Product"
             Striped="true"
             Bordered="true"
             Dense="true"
             Hover="true">
    <Columns>
        <PropertyColumn Property="x => x.Name" Title="Product Name" />
        <PropertyColumn Property="x => x.Category" Title="Category" />
        <PropertyColumn Property="x => x.Price" Title="Price" Format="C2" />
        <PropertyColumn Property="x => x.Stock" Title="In Stock" />
    </Columns>
</MudDataGrid>
```

### Column Types

| Column Type | Use Case |
|-------------|----------|
| `PropertyColumn` | Auto-binds to property, infers type for sorting/filtering |
| `TemplateColumn` | Custom rendering, no automatic property inference |

### Sorting

```razor
<MudDataGrid Items="@products" T="Product" SortMode="SortMode.Multiple">
    <Columns>
        <PropertyColumn Property="x => x.Name" Sortable="true" />
        <PropertyColumn Property="x => x.Price" Sortable="true" InitialDirection="SortDirection.Descending" />
        <TemplateColumn Title="Actions" Sortable="false" />
    </Columns>
</MudDataGrid>
```

**Sort Modes:**
- `SortMode.Multiple` - Ctrl+Click adds columns to sort (default)
- `SortMode.Single` - Only one column can be sorted
- `SortMode.None` - Disable sorting

### Filtering

```razor
<MudDataGrid Items="@products"
             T="Product"
             Filterable="true"
             FilterMode="DataGridFilterMode.ColumnFilterRow"
             FilterCaseSensitivity="DataGridFilterCaseSensitivity.CaseInsensitive"
             QuickFilter="@QuickFilter">
    <ToolBarContent>
        <MudText Typo="Typo.h6">Products</MudText>
        <MudSpacer />
        <MudTextField @bind-Value="searchString"
                      Placeholder="Search"
                      Adornment="Adornment.Start"
                      AdornmentIcon="@Icons.Material.Filled.Search"
                      Immediate="true"
                      DebounceInterval="300" />
    </ToolBarContent>
    <Columns>
        <PropertyColumn Property="x => x.Name" Filterable="true" />
        <PropertyColumn Property="x => x.Category" Filterable="true" />
    </Columns>
</MudDataGrid>

@code {
    private string searchString = string.Empty;

    private Func<Product, bool> QuickFilter => product =>
    {
        if (string.IsNullOrWhiteSpace(searchString))
            return true;

        return product.Name.Contains(searchString, StringComparison.OrdinalIgnoreCase)
            || product.Category.Contains(searchString, StringComparison.OrdinalIgnoreCase);
    };
}
```

**Filter Modes:**
- `DataGridFilterMode.Simple` - Unified filter popover
- `DataGridFilterMode.ColumnFilterMenu` - Per-column filter popover
- `DataGridFilterMode.ColumnFilterRow` - Inline filtering row

### Server-Side Data

```razor
<MudDataGrid T="Product"
             ServerData="LoadServerData"
             Striped="true"
             Loading="@isLoading"
             RowsPerPage="25">
    <Columns>
        <PropertyColumn Property="x => x.Name" Title="Name" Sortable="true" />
        <PropertyColumn Property="x => x.Price" Title="Price" Format="C2" Sortable="true" />
    </Columns>
    <PagerContent>
        <MudDataGridPager T="Product" />
    </PagerContent>
    <LoadingContent>
        <MudProgressLinear Color="Color.Primary" Indeterminate="true" />
    </LoadingContent>
    <NoRecordsContent>
        <MudText Typo="Typo.body1">No products found.</MudText>
    </NoRecordsContent>
</MudDataGrid>

@code {
    private bool isLoading = false;

    private async Task<GridData<Product>> LoadServerData(GridState<Product> state)
    {
        isLoading = true;
        StateHasChanged();

        try
        {
            var sortColumn = state.SortDefinitions.FirstOrDefault()?.SortBy;
            var sortDescending = state.SortDefinitions.FirstOrDefault()?.Descending ?? false;

            var result = await ProductService.GetProductsAsync(
                page: state.Page,
                pageSize: state.PageSize,
                sortColumn: sortColumn,
                sortDescending: sortDescending
            );

            return new GridData<Product>
            {
                Items = result.Items,
                TotalItems = result.TotalCount
            };
        }
        finally
        {
            isLoading = false;
            StateHasChanged();
        }
    }
}
```

### Inline Editing

```razor
<MudDataGrid T="Product"
             Items="@products"
             EditMode="DataGridEditMode.Form"
             EditTrigger="DataGridEditTrigger.OnRowClick"
             ReadOnly="false"
             CommittedItemChanges="OnCommittedItemChanges">
    <Columns>
        <PropertyColumn Property="x => x.Name" Title="Name" IsEditable="true" />
        <PropertyColumn Property="x => x.Price" Title="Price" Format="C2" IsEditable="true" />
        <PropertyColumn Property="x => x.Stock" Title="Stock" IsEditable="true" />
    </Columns>
</MudDataGrid>

@code {
    private async Task OnCommittedItemChanges(Product item)
    {
        await ProductService.UpdateAsync(item);
        Snackbar.Add("Product updated successfully", Severity.Success);
    }
}
```

**Edit Modes:**
- `DataGridEditMode.Form` - Popup editing interface
- `DataGridEditMode.Cell` - Excel-style inline editing

### Selection

```razor
<MudDataGrid T="Product"
             Items="@products"
             MultiSelection="true"
             @bind-SelectedItems="selectedProducts">
    <Columns>
        <SelectColumn T="Product" />
        <PropertyColumn Property="x => x.Name" />
    </Columns>
</MudDataGrid>

@code {
    private HashSet<Product> selectedProducts = new();
}
```

### Custom Cell Template

```razor
<MudDataGrid Items="@orders" T="Order">
    <Columns>
        <PropertyColumn Property="x => x.OrderNumber" />
        <TemplateColumn Title="Status">
            <CellTemplate>
                <MudChip Size="Size.Small" Color="@GetStatusColor(context.Item.Status)">
                    @context.Item.Status
                </MudChip>
            </CellTemplate>
        </TemplateColumn>
        <TemplateColumn Title="Actions" Sortable="false" Filterable="false">
            <CellTemplate>
                <MudStack Row="true" Spacing="1">
                    <MudIconButton Icon="@Icons.Material.Filled.Edit"
                                   Size="Size.Small"
                                   OnClick="@(() => EditOrder(context.Item))" />
                    <MudIconButton Icon="@Icons.Material.Filled.Delete"
                                   Size="Size.Small"
                                   Color="Color.Error"
                                   OnClick="@(() => DeleteOrder(context.Item))" />
                </MudStack>
            </CellTemplate>
        </TemplateColumn>
    </Columns>
</MudDataGrid>
```

### Grouping

```razor
<MudDataGrid Items="@products" T="Product" Groupable="true">
    <Columns>
        <PropertyColumn Property="x => x.Category" Title="Category" Groupable="true" />
        <PropertyColumn Property="x => x.Name" Title="Name" />
    </Columns>
</MudDataGrid>
```

### Aggregations

```razor
<MudDataGrid Items="@products" T="Product">
    <Columns>
        <PropertyColumn Property="x => x.Name" />
        <PropertyColumn Property="x => x.Price" Format="C2"
                        AggregateDefinition="@(new AggregateDefinition<Product>
                        {
                            Type = AggregateType.Sum,
                            DisplayFormat = "Total: {0:C2}"
                        })" />
    </Columns>
</MudDataGrid>
```

---

## MudTable

MudTable is an alternative data display component with similar features but different API.

### Basic Table

```razor
<MudTable Items="@orders"
          T="Order"
          Hover="true"
          Striped="true"
          Dense="true">
    <HeaderContent>
        <MudTh>Order #</MudTh>
        <MudTh>Customer</MudTh>
        <MudTh>Total</MudTh>
        <MudTh>Status</MudTh>
    </HeaderContent>
    <RowTemplate>
        <MudTd DataLabel="Order #">@context.OrderNumber</MudTd>
        <MudTd DataLabel="Customer">@context.Customer</MudTd>
        <MudTd DataLabel="Total">@context.Total.ToString("C")</MudTd>
        <MudTd DataLabel="Status">@context.Status</MudTd>
    </RowTemplate>
</MudTable>
```

### With Sorting

```razor
<MudTable Items="@orders" T="Order">
    <HeaderContent>
        <MudTh>
            <MudTableSortLabel SortBy="new Func<Order, object>(x => x.OrderNumber)">
                Order #
            </MudTableSortLabel>
        </MudTh>
        <MudTh>
            <MudTableSortLabel SortBy="new Func<Order, object>(x => x.Total)">
                Total
            </MudTableSortLabel>
        </MudTh>
    </HeaderContent>
    <RowTemplate>
        <MudTd>@context.OrderNumber</MudTd>
        <MudTd>@context.Total.ToString("C")</MudTd>
    </RowTemplate>
</MudTable>
```

### Server-Side Table

```razor
<MudTable ServerData="LoadServerData"
          T="Customer"
          Hover="true"
          Loading="@isLoading"
          @ref="table">
    <HeaderContent>
        <MudTh><MudTableSortLabel T="Customer" SortLabel="name">Name</MudTableSortLabel></MudTh>
        <MudTh><MudTableSortLabel T="Customer" SortLabel="email">Email</MudTableSortLabel></MudTh>
    </HeaderContent>
    <RowTemplate>
        <MudTd>@context.Name</MudTd>
        <MudTd>@context.Email</MudTd>
    </RowTemplate>
    <PagerContent>
        <MudTablePager />
    </PagerContent>
</MudTable>

@code {
    private MudTable<Customer> table;
    private bool isLoading = false;

    private async Task<TableData<Customer>> LoadServerData(TableState state, CancellationToken ct)
    {
        isLoading = true;
        try
        {
            var result = await CustomerService.GetCustomersAsync(
                page: state.Page,
                pageSize: state.PageSize,
                sortLabel: state.SortLabel,
                sortDirection: state.SortDirection
            );

            return new TableData<Customer>
            {
                Items = result.Items,
                TotalItems = result.TotalCount
            };
        }
        finally
        {
            isLoading = false;
        }
    }

    private Task RefreshData() => table.ReloadServerData();
}
```

### Multi-Selection

```razor
<MudTable Items="@orders"
          T="Order"
          MultiSelection="true"
          @bind-SelectedItems="selectedOrders">
    <ToolBarContent>
        @if (selectedOrders.Count > 0)
        {
            <MudButton OnClick="ProcessSelected">
                Process @selectedOrders.Count Order(s)
            </MudButton>
        }
    </ToolBarContent>
    <HeaderContent>
        <MudTh>Order #</MudTh>
    </HeaderContent>
    <RowTemplate>
        <MudTd>@context.OrderNumber</MudTd>
    </RowTemplate>
</MudTable>

@code {
    private HashSet<Order> selectedOrders = new();
}
```

---

## MudCard

### Info Card

```razor
<MudCard Elevation="2">
    <MudCardHeader>
        <CardHeaderAvatar>
            <MudAvatar Color="Color.Primary">@customer.Name[0]</MudAvatar>
        </CardHeaderAvatar>
        <CardHeaderContent>
            <MudText Typo="Typo.h6">@customer.Name</MudText>
            <MudText Typo="Typo.body2" Color="Color.Secondary">@customer.Email</MudText>
        </CardHeaderContent>
        <CardHeaderActions>
            <MudIconButton Icon="@Icons.Material.Filled.MoreVert" />
        </CardHeaderActions>
    </MudCardHeader>
    <MudCardContent>
        <MudText Typo="Typo.body2">@customer.Bio</MudText>
    </MudCardContent>
    <MudCardActions>
        <MudButton Variant="Variant.Text" Color="Color.Primary">View Profile</MudButton>
        <MudButton Variant="Variant.Text" Color="Color.Primary">Send Message</MudButton>
    </MudCardActions>
</MudCard>
```

### Stat Card

```razor
<MudPaper Elevation="2" Class="pa-4">
    <MudStack Row="true" Justify="Justify.SpaceBetween">
        <MudStack Spacing="1">
            <MudText Typo="Typo.subtitle2" Color="Color.Secondary">Total Revenue</MudText>
            <MudText Typo="Typo.h4">$45,231</MudText>
            <MudText Typo="Typo.caption" Color="Color.Success">+20.1% from last month</MudText>
        </MudStack>
        <MudAvatar Color="Color.Primary" Variant="Variant.Filled">
            <MudIcon Icon="@Icons.Material.Filled.AttachMoney" />
        </MudAvatar>
    </MudStack>
</MudPaper>
```

---

## MudList

```razor
<MudList T="string" Dense="true">
    <MudListItem Icon="@Icons.Material.Filled.Warning" IconColor="Color.Warning">
        <MudText Typo="Typo.body2">Low stock alert: Widget Pro</MudText>
        <MudText Typo="Typo.caption" Color="Color.Secondary">2 hours ago</MudText>
    </MudListItem>
    <MudListItem Icon="@Icons.Material.Filled.CheckCircle" IconColor="Color.Success">
        <MudText Typo="Typo.body2">Order #1234 completed</MudText>
        <MudText Typo="Typo.caption" Color="Color.Secondary">5 hours ago</MudText>
    </MudListItem>
</MudList>
```

---

## DataGrid vs Table

| Feature | MudDataGrid | MudTable |
|---------|-------------|----------|
| Column definition | `PropertyColumn`, `TemplateColumn` | Manual `<MudTh>`/`<MudTd>` |
| Built-in filtering | Yes, with UI | Manual implementation |
| Inline editing | Yes | Manual with `RowEditingTemplate` |
| Grouping | Yes | No |
| Aggregations | Yes | No |
| Column resizing | Yes | No |
| Best for | Complex data with filtering/editing | Simple tables, full control |
