# Layout Components

## Quick Reference

### Layout Fundamentals

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| **Column** | Vertical stacking | `.Spacing()`, `.Item()` |
| **Row** | Horizontal layout | `.ConstantItem()`, `.RelativeItem()`, `.AutoItem()` |
| **Table** | Grid layout with headers/footers | `.ColumnsDefinition()`, `.Cell()` |
| **Inlined** | Flowing/wrapping elements | `.Spacing()`, `.AlignCenter()` |
| **Layers** | Stacked content (watermarks) | `.Layer()`, `.PrimaryLayer()` |
| **Decoration** | Repeating section headers | `.Before()`, `.Content()`, `.After()` |

### Text Fundamentals

```csharp
// Simple styled text
container.Text("Title").FontSize(24).Bold().FontColor(Colors.Blue.Darken2);

// Multi-style text block
container.Text(text =>
{
    text.Span("Normal, ");
    text.Span("bold, ").Bold();
    text.Span("colored.").FontColor(Colors.Red.Medium);

    text.EmptyLine();

    text.Span("Page ");
    text.CurrentPageNumber();
    text.Span(" of ");
    text.TotalPages();
});
```

### Common Styling

```csharp
container
    .Background(Colors.Blue.Lighten4)
    .Border(1).BorderColor(Colors.Grey.Medium)
    .Padding(10)
    .Width(200).Height(100)
    .AlignCenter().AlignMiddle()
    .Text("Styled box");
```

## Page Component

The Page is the foundational container for document structure.

### Page Configuration

```csharp
container.Page(page =>
{
    // Page size
    page.Size(PageSizes.A4);              // Predefined size
    page.Size(PageSizes.Letter);          // US Letter
    page.Size(PageSizes.A4.Landscape());  // Landscape orientation
    page.Size(new PageSize(612, 792));    // Custom (in points: 72 = 1 inch)

    // Continuous height (single scrolling page, max ~5 meters)
    page.ContinuousSize(PageSizes.A4.Width);

    // Margins
    page.Margin(50);                      // All sides
    page.MarginHorizontal(50);            // Left/right
    page.MarginVertical(30);              // Top/bottom
    page.MarginTop(40);                   // Individual sides
    page.MarginBottom(40);
    page.MarginLeft(60);
    page.MarginRight(40);

    // Content direction (for RTL languages)
    page.ContentFromLeftToRight();        // Default
    page.ContentFromRightToLeft();        // Arabic, Hebrew, etc.

    // Default text styling for all content
    page.DefaultTextStyle(x => x.FontSize(11).FontFamily("Arial"));

    // Content slots
    page.Header().Text("Repeats on every page");
    page.Content().Column(/* main content */);
    page.Footer().Text("Repeats on every page");

    // Overlay slots
    page.Background().Image("watermark.png");    // Behind content
    page.Foreground().Text("DRAFT");             // In front of content
});
```

### Common Page Sizes

| Size | Dimensions (points) | Dimensions (inches) |
|------|---------------------|---------------------|
| A4 | 595 x 842 | 8.27 x 11.69 |
| Letter | 612 x 792 | 8.5 x 11 |
| Legal | 612 x 1008 | 8.5 x 14 |
| A3 | 842 x 1191 | 11.69 x 16.54 |
| A5 | 420 x 595 | 5.83 x 8.27 |

## Column (Vertical Layout)

Stacks items vertically with optional spacing.

```csharp
container.Column(column =>
{
    column.Spacing(10);  // Gap between all items

    column.Item().Text("First item");
    column.Item().Text("Second item");
    column.Item().Background(Colors.Grey.Lighten2).Height(50).Text("Third item");
});
```

### Column with Different Item Styles

```csharp
container.Column(column =>
{
    column.Spacing(15);

    // Header
    column.Item()
        .BorderBottom(2)
        .BorderColor(Colors.Blue.Medium)
        .PaddingBottom(10)
        .Text("Section Title").FontSize(18).Bold();

    // Content items
    foreach (var item in items)
    {
        column.Item()
            .Background(Colors.Grey.Lighten4)
            .Padding(10)
            .Text(item.Name);
    }

    // Footer
    column.Item()
        .PaddingTop(20)
        .Text($"Total: {items.Count} items");
});
```

## Row (Horizontal Layout)

Arranges items horizontally with three sizing modes.

```csharp
container.Row(row =>
{
    row.Spacing(10);  // Gap between items

    // ConstantItem: Fixed width in points
    row.ConstantItem(100).Background(Colors.Blue.Lighten2).Text("100pt wide");

    // RelativeItem: Proportional width (2:1 ratio here)
    row.RelativeItem(2).Background(Colors.Green.Lighten2).Text("2 parts");
    row.RelativeItem(1).Background(Colors.Yellow.Lighten2).Text("1 part");

    // AutoItem: Width based on content
    row.AutoItem().Text("Auto width");
});
```

### Row Alignment

```csharp
container.Row(row =>
{
    row.Spacing(10);

    // Vertical alignment within cells
    row.ConstantItem(100).AlignTop().Text("Top");
    row.ConstantItem(100).AlignMiddle().Text("Middle");
    row.ConstantItem(100).AlignBottom().Text("Bottom");
});
```

### Two-Column Layout

```csharp
container.Row(row =>
{
    row.Spacing(20);

    row.RelativeItem().Column(column =>
    {
        column.Spacing(5);
        column.Item().Text("Bill To:").Bold();
        column.Item().Text(Model.BillToAddress.Name);
        column.Item().Text(Model.BillToAddress.Street);
        column.Item().Text($"{Model.BillToAddress.City}, {Model.BillToAddress.State}");
    });

    row.RelativeItem().Column(column =>
    {
        column.Spacing(5);
        column.Item().Text("Ship To:").Bold();
        column.Item().Text(Model.ShipToAddress.Name);
        column.Item().Text(Model.ShipToAddress.Street);
        column.Item().Text($"{Model.ShipToAddress.City}, {Model.ShipToAddress.State}");
    });
});
```

## Inlined (Flowing Elements)

Elements that flow horizontally and wrap to the next line when needed.

```csharp
container.Inlined(inline =>
{
    inline.Spacing(5);              // Both horizontal and vertical
    inline.VerticalSpacing(10);     // Between wrapped rows
    inline.HorizontalSpacing(5);    // Between items in a row

    // Horizontal alignment
    inline.AlignLeft();             // Default
    inline.AlignCenter();
    inline.AlignRight();
    inline.AlignJustify();          // Distribute evenly

    // Vertical alignment of items within a row
    inline.BaselineTop();
    inline.BaselineMiddle();
    inline.BaselineBottom();

    // Items
    foreach (var tag in tags)
    {
        inline.Item()
            .Border(1)
            .BorderColor(Colors.Grey.Medium)
            .Background(Colors.Grey.Lighten3)
            .Padding(5)
            .Text(tag);
    }
});
```

### Tag Cloud Example

```csharp
void ComposeTags(IContainer container)
{
    container.Column(column =>
    {
        column.Item().Text("Tags:").Bold();

        column.Item().Inlined(inline =>
        {
            inline.Spacing(8);

            foreach (var tag in Model.Tags)
            {
                inline.Item()
                    .Background(Colors.Blue.Lighten4)
                    .Border(1)
                    .BorderColor(Colors.Blue.Lighten2)
                    .Padding(horizontal: 8, vertical: 4)
                    .Text(tag)
                    .FontSize(10);
            }
        });
    });
}
```

## Layers (Stacking Content)

Stack multiple layers of content on top of each other.

```csharp
container.Layers(layers =>
{
    // Background layer (rendered first, behind everything)
    layers.Layer().Image("watermark.png").FitArea();

    // Primary layer (required - determines the size of the stack)
    layers.PrimaryLayer().Column(column =>
    {
        column.Spacing(10);
        column.Item().Text("Main Content").FontSize(18);
        column.Item().Text("This is the primary content.");
    });

    // Foreground layer (rendered last, in front of everything)
    layers.Layer()
        .AlignCenter()
        .AlignMiddle()
        .Text("DRAFT")
        .FontSize(72)
        .FontColor(Colors.Grey.Lighten2)
        .Bold();
});
```

### Watermark Pattern

```csharp
void ComposeWithWatermark(IContainer container)
{
    container.Layers(layers =>
    {
        // Main content
        layers.PrimaryLayer().Column(column =>
        {
            column.Spacing(10);
            foreach (var paragraph in Model.Paragraphs)
            {
                column.Item().Text(paragraph);
            }
        });

        // Diagonal watermark
        layers.Layer()
            .AlignCenter()
            .AlignMiddle()
            .RotateLeft()
            .Text("CONFIDENTIAL")
            .FontSize(60)
            .FontColor(Colors.Red.Lighten3)
            .Bold();
    });
}
```

## Decoration (Repeating Section Headers/Footers)

Create headers/footers that repeat when content spans multiple pages within a section.

```csharp
container.Decoration(decoration =>
{
    // Before: appears at the top of the decorated content on each page
    decoration.Before()
        .BorderBottom(1)
        .BorderColor(Colors.Grey.Medium)
        .PaddingBottom(5)
        .Text("Section: Customer Orders").Bold();

    // Content: the main content that may span multiple pages
    decoration.Content().Column(column =>
    {
        column.Spacing(10);

        foreach (var order in Model.Orders)
        {
            column.Item()
                .Border(1)
                .BorderColor(Colors.Grey.Lighten2)
                .Padding(10)
                .Text($"Order #{order.Number}: {order.Total:C}");
        }
    });

    // After: appears at the bottom of the decorated content on each page
    decoration.After()
        .PaddingTop(5)
        .Text("-- Continued --")
        .FontSize(9)
        .FontColor(Colors.Grey.Medium);
});
```

### Section with Table Headers

```csharp
container.Decoration(decoration =>
{
    decoration.Before().Table(table =>
    {
        table.ColumnsDefinition(columns =>
        {
            columns.RelativeColumn(2);
            columns.RelativeColumn(1);
            columns.RelativeColumn(1);
        });

        table.Header(header =>
        {
            header.Cell().Background(Colors.Grey.Darken2)
                .Padding(5).Text("Product").FontColor(Colors.White).Bold();
            header.Cell().Background(Colors.Grey.Darken2)
                .Padding(5).AlignRight().Text("Qty").FontColor(Colors.White).Bold();
            header.Cell().Background(Colors.Grey.Darken2)
                .Padding(5).AlignRight().Text("Price").FontColor(Colors.White).Bold();
        });
    });

    decoration.Content().Column(column =>
    {
        foreach (var item in items)
        {
            column.Item().Row(row =>
            {
                row.RelativeItem(2).Padding(5).Text(item.Name);
                row.RelativeItem(1).Padding(5).AlignRight().Text(item.Quantity.ToString());
                row.RelativeItem(1).Padding(5).AlignRight().Text($"{item.Price:C}");
            });
        }
    });
});
```

## Styling and Alignment

### Container Styling Methods

```csharp
container
    // Background
    .Background(Colors.Blue.Lighten4)
    .Background("#E3F2FD")

    // Border
    .Border(2).BorderColor(Colors.Blue.Medium)
    .BorderLeft(1).BorderRight(1)
    .BorderTop(1).BorderBottom(1)
    .BorderHorizontal(1)  // Top and bottom
    .BorderVertical(1)    // Left and right

    // Border alignment
    .BorderAlignmentInside()
    .BorderAlignmentMiddle()   // Default
    .BorderAlignmentOutside()

    // Padding
    .Padding(20)
    .PaddingTop(10).PaddingBottom(10)
    .PaddingLeft(15).PaddingRight(15)
    .PaddingHorizontal(20).PaddingVertical(10)

    // Size constraints
    .Width(200).Height(100)
    .MinWidth(100).MaxWidth(300)
    .MinHeight(50).MaxHeight(200)
    .AspectRatio(16f / 9f)

    // Alignment
    .AlignLeft().AlignCenter().AlignRight()
    .AlignTop().AlignMiddle().AlignBottom()
    .Content();
```

### Reusable Style Functions

```csharp
static class Styles
{
    public static IContainer Card(IContainer container) =>
        container
            .Background(Colors.White)
            .Border(1)
            .BorderColor(Colors.Grey.Lighten2)
            .Padding(15);

    public static IContainer HeaderCell(IContainer container) =>
        container
            .Background(Colors.Blue.Darken2)
            .Padding(8)
            .DefaultTextStyle(x => x.FontColor(Colors.White).Bold());

    public static IContainer DataCell(IContainer container) =>
        container
            .BorderBottom(0.5f)
            .BorderColor(Colors.Grey.Lighten2)
            .Padding(8);
}

// Usage
column.Item().Element(Styles.Card).Column(inner =>
{
    inner.Item().Text("Card Title").Bold();
    inner.Item().Text("Card content goes here.");
});

table.Cell().Element(Styles.HeaderCell).Text("Column Header");
table.Cell().Element(Styles.DataCell).Text("Data value");
```
