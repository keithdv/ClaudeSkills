# Report Patterns

## Invoice Template

### Complete Invoice Document

```csharp
public class InvoiceDocument : IDocument
{
    public InvoiceModel Model { get; }
    private readonly Image _logo;

    public InvoiceDocument(InvoiceModel model)
    {
        Model = model;
        _logo = Image.FromFile("logo.png");
    }

    public DocumentMetadata GetMetadata() => new DocumentMetadata
    {
        Title = $"Invoice #{Model.InvoiceNumber}",
        Author = "Acme Corp",
        CreationDate = DateTimeOffset.Now
    };

    public DocumentSettings GetSettings() => DocumentSettings.Default;

    public void Compose(IDocumentContainer container)
    {
        container.Page(page =>
        {
            page.Size(PageSizes.A4);
            page.Margin(50);
            page.DefaultTextStyle(x => x.FontSize(10));

            page.Header().Element(ComposeHeader);
            page.Content().Element(ComposeContent);
            page.Footer().Element(ComposeFooter);
        });
    }

    void ComposeHeader(IContainer container)
    {
        container.Row(row =>
        {
            row.RelativeItem().Column(column =>
            {
                column.Item().Height(50).Image(_logo).FitArea();
                column.Item().Text("ACME CORPORATION")
                    .FontSize(16).Bold().FontColor(Colors.Blue.Darken2);
                column.Item().Text("123 Business Street");
                column.Item().Text("City, State 12345");
                column.Item().Text("(555) 123-4567");
            });

            row.ConstantItem(150).Column(column =>
            {
                column.Item().AlignRight().Text("INVOICE")
                    .FontSize(28).Bold().FontColor(Colors.Grey.Darken3);
                column.Item().AlignRight().Text($"#{Model.InvoiceNumber}").FontSize(12);
                column.Item().Height(20);
                column.Item().AlignRight().Text($"Date: {Model.Date:d}");
                column.Item().AlignRight().Text($"Due: {Model.DueDate:d}");
            });
        });
    }

    void ComposeContent(IContainer container)
    {
        container.PaddingTop(30).Column(column =>
        {
            column.Spacing(20);

            // Addresses
            column.Item().Row(row =>
            {
                row.Spacing(30);

                row.RelativeItem().Component(
                    new AddressComponent("BILL TO", Model.BillToAddress));
                row.RelativeItem().Component(
                    new AddressComponent("SHIP TO", Model.ShipToAddress));
            });

            // Line items table
            column.Item().Element(ComposeLineItems);

            // Totals
            column.Item().Element(ComposeTotals);

            // Notes
            if (!string.IsNullOrEmpty(Model.Notes))
            {
                column.Item().Element(ComposeNotes);
            }
        });
    }

    void ComposeLineItems(IContainer container)
    {
        container.Table(table =>
        {
            table.ColumnsDefinition(columns =>
            {
                columns.RelativeColumn(3);
                columns.RelativeColumn(1);
                columns.RelativeColumn(1);
                columns.RelativeColumn(1);
            });

            table.Header(header =>
            {
                void HeaderCell(IContainer c) => c
                    .Background(Colors.Grey.Darken3)
                    .Padding(8)
                    .DefaultTextStyle(x => x.FontColor(Colors.White).Bold());

                header.Cell().Element(HeaderCell).Text("Description");
                header.Cell().Element(HeaderCell).AlignRight().Text("Qty");
                header.Cell().Element(HeaderCell).AlignRight().Text("Unit Price");
                header.Cell().Element(HeaderCell).AlignRight().Text("Amount");
            });

            foreach (var item in Model.Items)
            {
                void DataCell(IContainer c) => c
                    .BorderBottom(0.5f)
                    .BorderColor(Colors.Grey.Lighten2)
                    .Padding(8);

                table.Cell().Element(DataCell).Text(item.Description);
                table.Cell().Element(DataCell).AlignRight().Text(item.Quantity.ToString());
                table.Cell().Element(DataCell).AlignRight().Text($"${item.UnitPrice:F2}");
                table.Cell().Element(DataCell).AlignRight().Text($"${item.Total:F2}");
            }
        });
    }

    void ComposeTotals(IContainer container)
    {
        container.AlignRight().Width(200).Column(column =>
        {
            void TotalRow(IContainer c) => c.Padding(5);

            column.Item().Row(row =>
            {
                row.RelativeItem().Element(TotalRow).AlignRight().Text("Subtotal:");
                row.ConstantItem(80).Element(TotalRow).AlignRight().Text($"${Model.Subtotal:F2}");
            });

            column.Item().Row(row =>
            {
                row.RelativeItem().Element(TotalRow).AlignRight().Text($"Tax ({Model.TaxRate}%):");
                row.ConstantItem(80).Element(TotalRow).AlignRight().Text($"${Model.Tax:F2}");
            });

            column.Item()
                .BorderTop(2)
                .BorderColor(Colors.Grey.Darken3)
                .Row(row =>
                {
                    row.RelativeItem().Padding(8).AlignRight().Text("TOTAL:").Bold();
                    row.ConstantItem(80).Padding(8).AlignRight()
                        .Text($"${Model.Total:F2}").Bold().FontSize(14);
                });
        });
    }

    void ComposeNotes(IContainer container)
    {
        container
            .Background(Colors.Grey.Lighten4)
            .Padding(15)
            .Column(column =>
            {
                column.Item().Text("Notes").Bold();
                column.Item().PaddingTop(5).Text(Model.Notes);
            });
    }

    void ComposeFooter(IContainer container)
    {
        container.Row(row =>
        {
            row.RelativeItem().Text("Thank you for your business!").FontSize(9);
            row.RelativeItem().AlignRight().Text(text =>
            {
                text.Span("Page ").FontSize(9);
                text.CurrentPageNumber().FontSize(9);
            });
        });
    }
}
```

## Reusable Components

### Address Component

```csharp
public class AddressComponent : IComponent
{
    public string Title { get; }
    public Address Address { get; }

    public AddressComponent(string title, Address address)
    {
        Title = title;
        Address = address;
    }

    public void Compose(IContainer container)
    {
        container.Column(column =>
        {
            column.Spacing(2);
            column.Item().Text(Title).Bold().FontSize(9).FontColor(Colors.Grey.Darken1);
            column.Item().Text(Address.Name).SemiBold();
            column.Item().Text(Address.Line1);
            if (!string.IsNullOrEmpty(Address.Line2))
                column.Item().Text(Address.Line2);
            column.Item().Text($"{Address.City}, {Address.State} {Address.PostalCode}");
        });
    }
}

// Usage
container.Component(new AddressComponent("Bill To:", invoice.BillToAddress));
```

### Info Box Component

```csharp
public class InfoBoxComponent : IComponent
{
    public string Title { get; }
    public IReadOnlyList<(string Label, string Value)> Items { get; }
    public string BackgroundColor { get; }

    public InfoBoxComponent(
        string title,
        IReadOnlyList<(string Label, string Value)> items,
        string backgroundColor = null)
    {
        Title = title;
        Items = items;
        BackgroundColor = backgroundColor ?? Colors.Grey.Lighten4;
    }

    public void Compose(IContainer container)
    {
        container
            .Background(BackgroundColor)
            .Padding(15)
            .Column(column =>
            {
                column.Spacing(5);

                if (!string.IsNullOrEmpty(Title))
                {
                    column.Item()
                        .BorderBottom(1)
                        .BorderColor(Colors.Grey.Medium)
                        .PaddingBottom(5)
                        .Text(Title).Bold();
                }

                foreach (var (label, value) in Items)
                {
                    column.Item().Row(row =>
                    {
                        row.ConstantItem(100).Text($"{label}:").SemiBold();
                        row.RelativeItem().Text(value);
                    });
                }
            });
    }
}
```

### Signature Line Component

```csharp
public class SignatureComponent : IComponent
{
    public string Label { get; }
    public string Name { get; }
    public DateTime? Date { get; }

    public SignatureComponent(string label, string name = null, DateTime? date = null)
    {
        Label = label;
        Name = name;
        Date = date;
    }

    public void Compose(IContainer container)
    {
        container.Row(row =>
        {
            row.RelativeItem().Column(column =>
            {
                column.Item().Height(40);  // Space for signature
                column.Item().BorderTop(1).BorderColor(Colors.Grey.Darken1);
                column.Item().Text(Label).FontSize(9);
                if (!string.IsNullOrEmpty(Name))
                    column.Item().Text(Name).FontSize(10).Bold();
            });

            row.ConstantItem(30);

            row.ConstantItem(120).Column(column =>
            {
                column.Item().Height(40);
                column.Item().BorderTop(1).BorderColor(Colors.Grey.Darken1);
                column.Item().Text("Date").FontSize(9);
                if (Date.HasValue)
                    column.Item().Text(Date.Value.ToString("d")).FontSize(10);
            });
        });
    }
}
```

## Data Report Pattern

### Tabular Data Report

```csharp
public class DataReportDocument : IDocument
{
    public DataReportModel Model { get; }

    public DataReportDocument(DataReportModel model) => Model = model;

    public void Compose(IDocumentContainer container)
    {
        container.Page(page =>
        {
            page.Size(PageSizes.A4.Landscape());  // Wide for tables
            page.Margin(40);
            page.DefaultTextStyle(x => x.FontSize(9));

            page.Header().Element(ComposeHeader);
            page.Content().Element(ComposeContent);
            page.Footer().Element(ComposeFooter);
        });
    }

    void ComposeHeader(IContainer container)
    {
        container.Column(column =>
        {
            column.Item().Row(row =>
            {
                row.RelativeItem().Text(Model.Title).FontSize(18).Bold();
                row.AutoItem().Text($"Generated: {DateTime.Now:g}").FontSize(9);
            });

            column.Item().PaddingTop(5).Row(row =>
            {
                row.RelativeItem().Text($"Period: {Model.StartDate:d} - {Model.EndDate:d}");
                row.AutoItem().Text($"Total Records: {Model.TotalRecords:N0}");
            });

            column.Item().Height(10);
            column.Item().BorderBottom(2).BorderColor(Colors.Blue.Medium);
        });
    }

    void ComposeContent(IContainer container)
    {
        container.PaddingTop(15).Table(table =>
        {
            table.ColumnsDefinition(columns =>
            {
                foreach (var col in Model.Columns)
                {
                    if (col.Width.HasValue)
                        columns.ConstantColumn(col.Width.Value);
                    else
                        columns.RelativeColumn();
                }
            });

            // Header row
            table.Header(header =>
            {
                foreach (var col in Model.Columns)
                {
                    var cell = header.Cell()
                        .Background(Colors.Blue.Darken2)
                        .Padding(6)
                        .DefaultTextStyle(x => x.FontColor(Colors.White).Bold());

                    if (col.Alignment == Alignment.Right)
                        cell = cell.AlignRight();
                    else if (col.Alignment == Alignment.Center)
                        cell = cell.AlignCenter();

                    cell.Text(col.Header);
                }
            });

            // Data rows with alternating colors
            var rowIndex = 0;
            foreach (var row in Model.Rows)
            {
                var bgColor = rowIndex % 2 == 0 ? Colors.White : Colors.Grey.Lighten4;

                for (var i = 0; i < Model.Columns.Count; i++)
                {
                    var col = Model.Columns[i];
                    var cell = table.Cell()
                        .Background(bgColor)
                        .BorderBottom(0.5f)
                        .BorderColor(Colors.Grey.Lighten2)
                        .Padding(6);

                    if (col.Alignment == Alignment.Right)
                        cell = cell.AlignRight();
                    else if (col.Alignment == Alignment.Center)
                        cell = cell.AlignCenter();

                    cell.Text(row.Values[i]);
                }

                rowIndex++;
            }
        });
    }

    void ComposeFooter(IContainer container)
    {
        container.Row(row =>
        {
            row.RelativeItem().Text(Model.FooterNote ?? "").FontSize(8);
            row.AutoItem().Text(text =>
            {
                text.Span("Page ");
                text.CurrentPageNumber();
                text.Span(" of ");
                text.TotalPages();
            });
        });
    }
}
```

## Multi-Section Report

### Report with Cover, TOC, and Appendix

```csharp
public class ComprehensiveReport : IDocument
{
    public ReportModel Model { get; }

    public void Compose(IDocumentContainer container)
    {
        // Cover page
        ComposeCoverPage(container);

        // Table of contents
        ComposeTableOfContents(container);

        // Main content
        ComposeMainContent(container);

        // Appendix
        ComposeAppendix(container);
    }

    void ComposeCoverPage(IDocumentContainer container)
    {
        container.Page(page =>
        {
            page.Size(PageSizes.A4);
            page.Margin(50);

            page.Content().AlignCenter().AlignMiddle().Column(column =>
            {
                column.Item().Text(Model.Title).FontSize(36).Bold()
                    .FontColor(Colors.Blue.Darken3);
                column.Item().PaddingTop(20).Text(Model.Subtitle)
                    .FontSize(18).FontColor(Colors.Grey.Darken1);
                column.Item().PaddingTop(80).Text($"Prepared by: {Model.Author}");
                column.Item().Text($"Date: {Model.Date:D}");
                column.Item().PaddingTop(20).Text($"Version: {Model.Version}");
            });
        });
    }

    void ComposeTableOfContents(IDocumentContainer container)
    {
        container.Page(page =>
        {
            page.Size(PageSizes.A4);
            page.Margin(50);

            page.Content().Column(column =>
            {
                column.Spacing(10);

                column.Item().Text("Table of Contents")
                    .FontSize(24).Bold().FontColor(Colors.Blue.Darken2);

                column.Item().Height(20);

                foreach (var section in Model.Sections)
                {
                    column.Item().Row(row =>
                    {
                        row.RelativeItem()
                            .SectionLink(section.Id)
                            .Text(section.Title)
                            .FontColor(Colors.Blue.Medium);

                        row.AutoItem().Text(text =>
                        {
                            text.BeginPageNumberOfSection(section.Id);
                        });
                    });

                    // Subsections
                    foreach (var sub in section.Subsections)
                    {
                        column.Item().PaddingLeft(20).Row(row =>
                        {
                            row.RelativeItem()
                                .SectionLink(sub.Id)
                                .Text(sub.Title)
                                .FontColor(Colors.Blue.Lighten1);

                            row.AutoItem().Text(text =>
                            {
                                text.BeginPageNumberOfSection(sub.Id);
                            });
                        });
                    }
                }
            });
        });
    }

    void ComposeMainContent(IDocumentContainer container)
    {
        container.Page(page =>
        {
            page.Size(PageSizes.A4);
            page.Margin(50);
            page.DefaultTextStyle(x => x.FontSize(11));

            page.Header().Column(col =>
            {
                col.Item().ShowOnce().Element(ComposeFullHeader);
                col.Item().SkipOnce().Element(ComposeContinuationHeader);
            });

            page.Content().Column(column =>
            {
                column.Spacing(20);

                foreach (var section in Model.Sections)
                {
                    column.Item()
                        .Section(section.Id)
                        .Element(c => ComposeSection(c, section));
                }
            });

            page.Footer().Element(ComposeFooter);
        });
    }

    void ComposeSection(IContainer container, Section section)
    {
        container.Column(column =>
        {
            column.Spacing(10);

            column.Item()
                .BorderBottom(2)
                .BorderColor(Colors.Blue.Medium)
                .PaddingBottom(5)
                .Text(section.Title)
                .FontSize(18).Bold();

            column.Item().Text(section.Content);

            foreach (var sub in section.Subsections)
            {
                column.Item()
                    .PaddingTop(10)
                    .Section(sub.Id)
                    .Element(c => ComposeSubsection(c, sub));
            }
        });
    }

    void ComposeSubsection(IContainer container, Subsection sub)
    {
        container.Column(column =>
        {
            column.Spacing(5);
            column.Item().Text(sub.Title).FontSize(14).SemiBold();
            column.Item().Text(sub.Content);
        });
    }

    void ComposeAppendix(IDocumentContainer container)
    {
        container.Page(page =>
        {
            page.Size(PageSizes.A4.Landscape());
            page.Margin(40);

            page.Header()
                .Section("appendix")
                .Text("Appendix: Supporting Data")
                .FontSize(16).Bold();

            page.Content().Element(ComposeAppendixTables);

            page.Footer().Element(ComposeFooter);
        });
    }
}
```

## Extension Methods for Styling

```csharp
public static class ReportStyles
{
    public static IContainer SectionTitle(this IContainer container) =>
        container
            .BorderBottom(2)
            .BorderColor(Colors.Blue.Medium)
            .PaddingBottom(8);

    public static IContainer Card(this IContainer container) =>
        container
            .Background(Colors.White)
            .Border(1)
            .BorderColor(Colors.Grey.Lighten2)
            .Padding(15);

    public static IContainer HighlightBox(this IContainer container) =>
        container
            .Background(Colors.Yellow.Lighten4)
            .Border(1)
            .BorderColor(Colors.Yellow.Darken1)
            .Padding(10);

    public static IContainer TableHeader(this IContainer container) =>
        container
            .Background(Colors.Blue.Darken2)
            .Padding(8)
            .DefaultTextStyle(x => x.FontColor(Colors.White).Bold());

    public static IContainer TableCell(this IContainer container) =>
        container
            .BorderBottom(0.5f)
            .BorderColor(Colors.Grey.Lighten2)
            .Padding(8);

    public static IContainer AlternateRow(this IContainer container, int rowIndex) =>
        container.Background(rowIndex % 2 == 0 ? Colors.White : Colors.Grey.Lighten4);
}

// Usage
column.Item().SectionTitle().Text("Section Title").FontSize(18).Bold();
container.Card().Column(column => { /* card content */ });
table.Cell().TableHeader().Text("Header");
table.Cell().AlternateRow(rowIndex).TableCell().Text("Data");
```

## Typography Constants

```csharp
public static class ReportTypography
{
    public static TextStyle Title => TextStyle.Default
        .FontSize(28).Bold().FontColor(Colors.Blue.Darken3);

    public static TextStyle Heading1 => TextStyle.Default
        .FontSize(20).Bold();

    public static TextStyle Heading2 => TextStyle.Default
        .FontSize(16).SemiBold();

    public static TextStyle Heading3 => TextStyle.Default
        .FontSize(13).SemiBold();

    public static TextStyle Body => TextStyle.Default
        .FontSize(10);

    public static TextStyle Small => TextStyle.Default
        .FontSize(9).FontColor(Colors.Grey.Darken1);

    public static TextStyle TableHeader => TextStyle.Default
        .FontSize(10).Bold().FontColor(Colors.White);

    public static TextStyle Currency => TextStyle.Default
        .FontSize(10).FontFamily("Consolas");

    public static TextStyle Emphasis => TextStyle.Default
        .Italic();
}

// Usage
container.Text("Report Title").Style(ReportTypography.Title);
table.Cell().Text("$1,234.56").Style(ReportTypography.Currency);
```
