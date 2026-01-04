# Tables

## Basic Table Structure

```csharp
container.Table(table =>
{
    // Step 1: Define columns
    table.ColumnsDefinition(columns =>
    {
        columns.ConstantColumn(50);       // Fixed width (points)
        columns.RelativeColumn(2);         // 2 parts of remaining space
        columns.RelativeColumn(1);         // 1 part of remaining space
        columns.ConstantColumn(80);
    });

    // Step 2: Add cells (fill left-to-right, top-to-bottom)
    table.Cell().Text("ID");
    table.Cell().Text("Name");
    table.Cell().Text("Category");
    table.Cell().Text("Price");

    // More rows...
    table.Cell().Text("1");
    table.Cell().Text("Widget");
    table.Cell().Text("Tools");
    table.Cell().Text("$9.99");
});
```

## Table with Header, Body, and Footer

```csharp
container.Table(table =>
{
    table.ColumnsDefinition(columns =>
    {
        columns.RelativeColumn(3);  // Description
        columns.RelativeColumn(1);  // Quantity
        columns.RelativeColumn(1);  // Unit Price
        columns.RelativeColumn(1);  // Total
    });

    // Header (repeats on each page)
    table.Header(header =>
    {
        header.Cell().Text("Description").Bold();
        header.Cell().AlignRight().Text("Qty").Bold();
        header.Cell().AlignRight().Text("Unit Price").Bold();
        header.Cell().AlignRight().Text("Total").Bold();

        // Optional: border under header
        header.Cell().ColumnSpan(4).BorderBottom(1).BorderColor(Colors.Grey.Medium);
    });

    // Data rows
    foreach (var item in Model.Items)
    {
        table.Cell().Text(item.Description);
        table.Cell().AlignRight().Text(item.Quantity.ToString());
        table.Cell().AlignRight().Text($"${item.UnitPrice:F2}");
        table.Cell().AlignRight().Text($"${item.Total:F2}");
    }

    // Footer (appears after all content)
    table.Footer(footer =>
    {
        footer.Cell().ColumnSpan(3).AlignRight().Text("Total:").Bold();
        footer.Cell().AlignRight().Text($"${Model.Total:F2}").Bold();
    });
});
```

## Cell Spanning

```csharp
// Span multiple columns
table.Cell().ColumnSpan(2).Text("Spans 2 columns");

// Span multiple rows
table.Cell().RowSpan(3).Text("Spans 3 rows");

// Both directions
table.Cell().ColumnSpan(2).RowSpan(2).Text("Spans 2x2");
```

### Practical Spanning Example

```csharp
container.Table(table =>
{
    table.ColumnsDefinition(columns =>
    {
        columns.RelativeColumn();
        columns.RelativeColumn();
        columns.RelativeColumn();
        columns.RelativeColumn();
    });

    // Group header spanning all columns
    table.Cell().ColumnSpan(4)
        .Background(Colors.Blue.Lighten4)
        .Padding(8)
        .Text("Product Group A").Bold();

    // Regular data rows
    table.Cell().Padding(5).Text("Product 1");
    table.Cell().Padding(5).Text("Category");
    table.Cell().Padding(5).AlignRight().Text("10");
    table.Cell().Padding(5).AlignRight().Text("$50.00");

    // Row with description spanning 3 columns
    table.Cell().Padding(5).Text("Product 2");
    table.Cell().ColumnSpan(3).Padding(5)
        .Text("This is a detailed description that spans multiple columns.");
});
```

## Styled Table with Alternating Rows

```csharp
container.Table(table =>
{
    table.ColumnsDefinition(columns =>
    {
        columns.RelativeColumn();
        columns.RelativeColumn();
        columns.RelativeColumn();
    });

    // Styled header
    table.Header(header =>
    {
        void HeaderCell(IContainer container) => container
            .Background(Colors.Blue.Medium)
            .Padding(8)
            .DefaultTextStyle(x => x.FontColor(Colors.White).Bold());

        header.Cell().Element(HeaderCell).Text("Column 1");
        header.Cell().Element(HeaderCell).Text("Column 2");
        header.Cell().Element(HeaderCell).Text("Column 3");
    });

    // Alternating row colors
    var rowIndex = 0;
    foreach (var item in items)
    {
        var backgroundColor = rowIndex % 2 == 0
            ? Colors.White
            : Colors.Grey.Lighten4;

        void DataCell(IContainer container) => container
            .Background(backgroundColor)
            .Padding(8);

        table.Cell().Element(DataCell).Text(item.Col1);
        table.Cell().Element(DataCell).Text(item.Col2);
        table.Cell().Element(DataCell).Text(item.Col3);

        rowIndex++;
    }
});
```

## Table with Cell Borders

```csharp
void BorderedCell(IContainer container) => container
    .Border(0.5f)
    .BorderColor(Colors.Grey.Medium)
    .Padding(5);

container.Table(table =>
{
    table.ColumnsDefinition(columns =>
    {
        columns.RelativeColumn();
        columns.RelativeColumn();
        columns.RelativeColumn();
    });

    for (var row = 0; row < 5; row++)
    {
        table.Cell().Element(BorderedCell).Text($"R{row}C1");
        table.Cell().Element(BorderedCell).Text($"R{row}C2");
        table.Cell().Element(BorderedCell).Text($"R{row}C3");
    }
});
```

## Invoice-Style Data Table

```csharp
void ComposeLineItems(IContainer container)
{
    container.Table(table =>
    {
        table.ColumnsDefinition(columns =>
        {
            columns.RelativeColumn(3);    // Description
            columns.RelativeColumn(1);    // Quantity
            columns.RelativeColumn(1);    // Unit Price
            columns.RelativeColumn(1);    // Total
        });

        // Header
        table.Header(header =>
        {
            void HeaderCell(IContainer container) => container
                .Background(Colors.Grey.Darken3)
                .Padding(8)
                .DefaultTextStyle(x => x.FontColor(Colors.White).Bold());

            header.Cell().Element(HeaderCell).Text("Description");
            header.Cell().Element(HeaderCell).AlignRight().Text("Qty");
            header.Cell().Element(HeaderCell).AlignRight().Text("Unit Price");
            header.Cell().Element(HeaderCell).AlignRight().Text("Total");
        });

        // Data rows
        void DataCell(IContainer container) => container
            .BorderBottom(0.5f)
            .BorderColor(Colors.Grey.Lighten2)
            .Padding(8);

        foreach (var item in Model.Items)
        {
            table.Cell().Element(DataCell).Text(item.Description);
            table.Cell().Element(DataCell).AlignRight().Text(item.Quantity.ToString());
            table.Cell().Element(DataCell).AlignRight().Text($"${item.UnitPrice:F2}");
            table.Cell().Element(DataCell).AlignRight().Text($"${item.Total:F2}");
        }

        // Totals section
        void TotalCell(IContainer container) => container.Padding(8);

        table.Cell().ColumnSpan(3).Element(TotalCell).AlignRight().Text("Subtotal:");
        table.Cell().Element(TotalCell).AlignRight().Text($"${Model.Subtotal:F2}");

        table.Cell().ColumnSpan(3).Element(TotalCell).AlignRight().Text("Tax (8%):");
        table.Cell().Element(TotalCell).AlignRight().Text($"${Model.Tax:F2}");

        void GrandTotalCell(IContainer container) => container
            .Background(Colors.Grey.Lighten3)
            .Padding(8);

        table.Cell().ColumnSpan(3).Element(GrandTotalCell).AlignRight().Text("TOTAL:").Bold();
        table.Cell().Element(GrandTotalCell).AlignRight().Text($"${Model.Total:F2}").Bold();
    });
}
```

## Nested Tables

```csharp
container.Table(table =>
{
    table.ColumnsDefinition(columns =>
    {
        columns.RelativeColumn(1);
        columns.RelativeColumn(2);
    });

    table.Cell().Padding(10).Text("Category A").Bold();

    // Nested table in second column
    table.Cell().Padding(10).Table(nestedTable =>
    {
        nestedTable.ColumnsDefinition(columns =>
        {
            columns.RelativeColumn();
            columns.RelativeColumn();
        });

        nestedTable.Cell().Text("Item 1");
        nestedTable.Cell().Text("$10.00");
        nestedTable.Cell().Text("Item 2");
        nestedTable.Cell().Text("$20.00");
    });

    table.Cell().Padding(10).Text("Category B").Bold();

    table.Cell().Padding(10).Table(nestedTable =>
    {
        nestedTable.ColumnsDefinition(columns =>
        {
            columns.RelativeColumn();
            columns.RelativeColumn();
        });

        nestedTable.Cell().Text("Item 3");
        nestedTable.Cell().Text("$15.00");
    });
});
```

## Dynamic Column Widths

```csharp
void ComposeDynamicTable(IContainer container, List<ColumnDef> columnDefs, List<DataRow> rows)
{
    container.Table(table =>
    {
        table.ColumnsDefinition(columns =>
        {
            foreach (var col in columnDefs)
            {
                if (col.FixedWidth.HasValue)
                    columns.ConstantColumn(col.FixedWidth.Value);
                else
                    columns.RelativeColumn(col.RelativeWidth);
            }
        });

        // Header
        table.Header(header =>
        {
            foreach (var col in columnDefs)
            {
                var cell = header.Cell().Background(Colors.Grey.Darken2).Padding(5);

                if (col.Alignment == ColumnAlignment.Right)
                    cell = cell.AlignRight();
                else if (col.Alignment == ColumnAlignment.Center)
                    cell = cell.AlignCenter();

                cell.Text(col.Header).FontColor(Colors.White).Bold();
            }
        });

        // Data
        foreach (var row in rows)
        {
            for (var i = 0; i < columnDefs.Count; i++)
            {
                var col = columnDefs[i];
                var cell = table.Cell().Padding(5);

                if (col.Alignment == ColumnAlignment.Right)
                    cell = cell.AlignRight();
                else if (col.Alignment == ColumnAlignment.Center)
                    cell = cell.AlignCenter();

                cell.Text(row.Values[i]);
            }
        }
    });
}
```

## Table with Images

```csharp
container.Table(table =>
{
    table.ColumnsDefinition(columns =>
    {
        columns.ConstantColumn(50);   // Image
        columns.RelativeColumn(2);     // Name
        columns.RelativeColumn(1);     // Price
    });

    foreach (var product in products)
    {
        table.Cell().Padding(5).Height(40).Image(product.ImageBytes).FitArea();
        table.Cell().Padding(5).AlignMiddle().Text(product.Name);
        table.Cell().Padding(5).AlignMiddle().AlignRight().Text($"${product.Price:F2}");
    }
});
```

## Report Summary Table

```csharp
void ComposeSummaryTable(IContainer container)
{
    container.Table(table =>
    {
        table.ColumnsDefinition(columns =>
        {
            columns.RelativeColumn();
            columns.RelativeColumn();
        });

        void LabelCell(IContainer container) => container
            .Background(Colors.Grey.Lighten3)
            .Padding(8);

        void ValueCell(IContainer container) => container
            .Background(Colors.White)
            .Padding(8);

        // Label-Value pairs
        table.Cell().Element(LabelCell).Text("Report Date:");
        table.Cell().Element(ValueCell).Text(Model.ReportDate.ToString("d"));

        table.Cell().Element(LabelCell).Text("Period:");
        table.Cell().Element(ValueCell).Text($"{Model.StartDate:d} - {Model.EndDate:d}");

        table.Cell().Element(LabelCell).Text("Total Records:");
        table.Cell().Element(ValueCell).Text(Model.TotalRecords.ToString("N0"));

        table.Cell().Element(LabelCell).Text("Total Amount:");
        table.Cell().Element(ValueCell).Text(Model.TotalAmount.ToString("C")).Bold();
    });
}
```

## Best Practices

### Column Width Guidelines

| Type | Use When |
|------|----------|
| `ConstantColumn(n)` | Fixed content like IDs, dates, icons |
| `RelativeColumn()` | Variable content like names, descriptions |
| `RelativeColumn(n)` | Proportional sizing (2:1, 3:1 ratios) |

### Cell Styling Tips

1. **Use helper functions** for consistent styling
2. **Apply padding to cells**, not content
3. **Use `AlignRight()` for numbers** (currency, quantities)
4. **Apply borders sparingly** - they add visual noise
5. **Use alternating row colors** for data readability

### Performance

- For large tables (1000+ rows), consider pagination
- Avoid complex nested layouts within cells
- Use `.ShowEntire()` only when necessary (prevents row splitting)
