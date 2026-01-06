# Document Architecture

## Three-Layer Architecture

QuestPDF recommends separating concerns into three distinct layers:

| Layer | Responsibility |
|-------|----------------|
| **Document Models** | Data structures representing document content (no business logic) |
| **Data Source** | Data fetching, transformations, calculations |
| **Template** | Visual layout using the fluent API |

## IDocument Interface

```csharp
public interface IDocument
{
    DocumentMetadata GetMetadata();
    DocumentSettings GetSettings();
    void Compose(IDocumentContainer container);
}
```

## Basic IDocument Pattern

A minimal IDocument implementation with decomposed methods for header, content, and footer:

```csharp
public class ReportDocument : IDocument
{
    public ReportModel Model { get; }

    public ReportDocument(ReportModel model) => Model = model;

    public DocumentMetadata GetMetadata() => new DocumentMetadata
    {
        Title = "My Report",
        Author = "System",
        CreationDate = DateTimeOffset.Now
    };

    public DocumentSettings GetSettings() => DocumentSettings.Default;

    public void Compose(IDocumentContainer container)
    {
        container.Page(page =>
        {
            page.Size(PageSizes.A4);
            page.Margin(50);
            page.DefaultTextStyle(x => x.FontSize(11));

            page.Header().Element(ComposeHeader);
            page.Content().Element(ComposeContent);
            page.Footer().Element(ComposeFooter);
        });
    }

    void ComposeHeader(IContainer container) { /* ... */ }
    void ComposeContent(IContainer container) { /* ... */ }
    void ComposeFooter(IContainer container) { /* ... */ }
}

// Generate
var document = new ReportDocument(model);
document.GeneratePdf("report.pdf");
document.GeneratePdfAndShow();         // Opens in default viewer
byte[] bytes = document.GeneratePdf(); // Returns byte array
```

## Complete IDocument Implementation

```csharp
public class InvoiceDocument : IDocument
{
    public InvoiceModel Model { get; }

    public InvoiceDocument(InvoiceModel model)
    {
        Model = model;
    }

    public DocumentMetadata GetMetadata() => new DocumentMetadata
    {
        Title = $"Invoice #{Model.InvoiceNumber}",
        Author = "Acme Corp",
        Subject = "Invoice",
        Keywords = "invoice, billing, payment",
        Creator = "Invoice System v2.0",
        Producer = "QuestPDF",
        Language = "en-US",
        CreationDate = DateTimeOffset.Now,
        ModifiedDate = DateTimeOffset.Now
    };

    public DocumentSettings GetSettings() => new DocumentSettings
    {
        // Image compression (0.1 to 1.0)
        ImageCompressionQuality = ImageCompressionQuality.High,

        // DPI for raster images (default 72)
        ImageRasterDpi = 150,

        // PDF/A compliance (optional)
        PdfA = false,

        // Content direction
        ContentDirection = ContentDirection.LeftToRight
    };

    public void Compose(IDocumentContainer container)
    {
        container.Page(page =>
        {
            page.Size(PageSizes.A4);
            page.Margin(50);
            page.DefaultTextStyle(x => x.FontSize(11).FontFamily("Arial"));

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
                column.Item().Text("ACME CORPORATION")
                    .FontSize(20).Bold().FontColor(Colors.Blue.Darken2);
                column.Item().Text("123 Business Street");
                column.Item().Text("City, State 12345");
            });

            row.ConstantItem(150).AlignRight().Column(column =>
            {
                column.Item().Text("INVOICE").FontSize(24).Bold();
                column.Item().Text($"#{Model.InvoiceNumber}");
                column.Item().Text($"Date: {Model.Date:d}");
            });
        });
    }

    void ComposeContent(IContainer container)
    {
        container.Column(column =>
        {
            column.Spacing(20);
            column.Item().Element(ComposeAddresses);
            column.Item().Element(ComposeLineItems);
            column.Item().Element(ComposeTotals);
        });
    }

    void ComposeAddresses(IContainer container) { /* ... */ }
    void ComposeLineItems(IContainer container) { /* ... */ }
    void ComposeTotals(IContainer container) { /* ... */ }

    void ComposeFooter(IContainer container)
    {
        container.BorderTop(1).BorderColor(Colors.Grey.Lighten1)
            .PaddingTop(10)
            .Row(row =>
            {
                row.RelativeItem().Text($"Generated: {DateTime.Now:g}");
                row.RelativeItem().AlignRight().Text(text =>
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

## Document Generation Methods

```csharp
var document = new InvoiceDocument(model);

// Generate to file
document.GeneratePdf("invoice.pdf");

// Generate and open in default PDF viewer
document.GeneratePdfAndShow();

// Generate to byte array
byte[] pdfBytes = document.GeneratePdf();

// Generate to stream
using var stream = new MemoryStream();
document.GeneratePdf(stream);

// Generate XPS format
document.GenerateXps("invoice.xps");

// Generate images (one per page)
var images = document.GenerateImages();
foreach (var (pageNumber, image) in images)
{
    File.WriteAllBytes($"page-{pageNumber}.png", image);
}
```

## Document Model Patterns

### Simple Record-Based Models

```csharp
public record InvoiceModel(
    string InvoiceNumber,
    DateTime Date,
    DateTime DueDate,
    Address BillTo,
    Address ShipTo,
    IReadOnlyList<LineItem> Items,
    decimal Subtotal,
    decimal Tax,
    decimal Total
);

public record Address(
    string Name,
    string Line1,
    string? Line2,
    string City,
    string State,
    string PostalCode
);

public record LineItem(
    string Description,
    int Quantity,
    decimal UnitPrice,
    decimal Total
);
```

### Model with Computed Properties

```csharp
public class ReportModel
{
    public required string Title { get; init; }
    public required IReadOnlyList<DataRow> Rows { get; init; }
    public required DateTime GeneratedAt { get; init; }

    // Computed properties
    public decimal Total => Rows.Sum(r => r.Value);
    public int RowCount => Rows.Count;
    public decimal Average => RowCount > 0 ? Total / RowCount : 0;
}
```

## Data Source Pattern

Keep data fetching and transformation separate from the template:

```csharp
public class InvoiceDataSource
{
    private readonly IInvoiceRepository _repository;
    private readonly ITaxCalculator _taxCalculator;

    public InvoiceDataSource(
        IInvoiceRepository repository,
        ITaxCalculator taxCalculator)
    {
        _repository = repository;
        _taxCalculator = taxCalculator;
    }

    public async Task<InvoiceModel> GetInvoiceModel(int invoiceId)
    {
        var invoice = await _repository.GetByIdAsync(invoiceId);
        var lineItems = await _repository.GetLineItemsAsync(invoiceId);

        var items = lineItems.Select(li => new LineItem(
            li.Description,
            li.Quantity,
            li.UnitPrice,
            li.Quantity * li.UnitPrice
        )).ToList();

        var subtotal = items.Sum(i => i.Total);
        var tax = _taxCalculator.Calculate(subtotal, invoice.TaxRate);

        return new InvoiceModel(
            invoice.Number,
            invoice.Date,
            invoice.DueDate,
            MapAddress(invoice.BillToAddress),
            MapAddress(invoice.ShipToAddress),
            items,
            subtotal,
            tax,
            subtotal + tax
        );
    }

    private static Address MapAddress(AddressEntity entity) => new(
        entity.Name,
        entity.Line1,
        entity.Line2,
        entity.City,
        entity.State,
        entity.PostalCode
    );
}
```

## Multi-Page Documents

```csharp
public void Compose(IDocumentContainer container)
{
    // Cover page
    container.Page(page =>
    {
        page.Size(PageSizes.A4);
        page.Margin(50);

        page.Content().AlignCenter().AlignMiddle().Column(column =>
        {
            column.Item().Text(Model.Title).FontSize(36).Bold();
            column.Item().Text(Model.Subtitle).FontSize(18);
            column.Item().PaddingTop(50).Text($"Generated: {DateTime.Now:D}");
        });
    });

    // Content pages
    container.Page(page =>
    {
        page.Size(PageSizes.A4);
        page.Margin(50);

        page.Header().Text(Model.Title).FontSize(16).Bold();
        page.Content().Element(ComposeMainContent);
        page.Footer().AlignCenter().Text(text =>
        {
            text.CurrentPageNumber();
            text.Span(" / ");
            text.TotalPages();
        });
    });

    // Appendix with different orientation
    container.Page(page =>
    {
        page.Size(PageSizes.A4.Landscape());
        page.Margin(30);

        page.Header().Text("Appendix: Data Tables").FontSize(14).Bold();
        page.Content().Element(ComposeAppendix);
    });
}
```

## Dependency Injection Pattern

```csharp
// Register services
services.AddScoped<InvoiceDataSource>();
services.AddScoped<IInvoiceDocumentGenerator, InvoiceDocumentGenerator>();

// Implementation
public class InvoiceDocumentGenerator : IInvoiceDocumentGenerator
{
    private readonly InvoiceDataSource _dataSource;

    public InvoiceDocumentGenerator(InvoiceDataSource dataSource)
    {
        _dataSource = dataSource;
    }

    public async Task<byte[]> GenerateAsync(int invoiceId)
    {
        var model = await _dataSource.GetInvoiceModel(invoiceId);
        var document = new InvoiceDocument(model);
        return document.GeneratePdf();
    }
}
```
