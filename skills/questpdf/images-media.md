# Images & Media

## Loading Images

### From Different Sources

```csharp
// From file path
container.Image("path/to/image.png");

// From byte array
byte[] imageBytes = File.ReadAllBytes("image.png");
container.Image(imageBytes);

// From stream
using var stream = File.OpenRead("image.png");
container.Image(stream);

// From embedded resource
var assembly = Assembly.GetExecutingAssembly();
using var stream = assembly.GetManifestResourceStream("MyApp.Resources.logo.png");
container.Image(stream);
```

### SVG Support

```csharp
// From file
container.Image(SvgImage.FromFile("icon.svg"));

// From string content
var svgContent = "<svg>...</svg>";
container.Image(SvgImage.FromText(svgContent));

// From embedded resource
using var stream = assembly.GetManifestResourceStream("MyApp.Resources.icon.svg");
using var reader = new StreamReader(stream);
var svgText = reader.ReadToEnd();
container.Image(SvgImage.FromText(svgText));
```

## Scaling Modes

```csharp
// FitWidth (default): scales to fill container width, maintains aspect ratio
container.Image("photo.jpg").FitWidth();

// FitHeight: scales to fill container height, maintains aspect ratio
container.Image("photo.jpg").FitHeight();

// FitArea: scales to fit within the container (letterboxing)
container.Image("photo.jpg").FitArea();

// FitUnproportionally: stretches to fill (distorts image - avoid)
container.Image("photo.jpg").FitUnproportionally();
```

### Scaling Examples

```csharp
// Logo in header (fixed height, proportional width)
container.Row(row =>
{
    row.ConstantItem(100).Height(40).Image("logo.png").FitArea();
    row.RelativeItem().AlignRight().Text("Company Name").FontSize(18);
});

// Full-width banner image
container.Image("banner.jpg").FitWidth();

// Thumbnail in a fixed container
container.Width(100).Height(100).Image("product.jpg").FitArea();

// Product image with aspect ratio constraint
container.AspectRatio(4f / 3f).Image("product.jpg").FitArea();
```

## Performance Optimization

### Caching Repeated Images

```csharp
public class ProductCatalog : IDocument
{
    // Load once, reuse many times
    private readonly Image _logo;
    private readonly Image _watermark;

    public ProductCatalog(CatalogModel model)
    {
        Model = model;
        _logo = Image.FromFile("logo.png");
        _watermark = Image.FromFile("watermark.png");
    }

    public CatalogModel Model { get; }

    void ComposeProductCard(IContainer container, Product product)
    {
        container.Column(column =>
        {
            column.Item().Row(row =>
            {
                row.ConstantItem(50).Image(_logo);  // Reused logo
                row.RelativeItem().Text(product.Name);
            });
            // ...
        });
    }
}
```

### Lazy Loading for Large Datasets

```csharp
public class ProductCatalog : IDocument
{
    private readonly Dictionary<int, Image> _imageCache = new();

    private Image GetProductImage(int productId)
    {
        if (!_imageCache.TryGetValue(productId, out var image))
        {
            var bytes = _imageService.GetProductImage(productId);
            image = Image.FromBinaryData(bytes);
            _imageCache[productId] = image;
        }
        return image;
    }

    void ComposeProductGrid(IContainer container)
    {
        container.Table(table =>
        {
            // ...
            foreach (var product in Model.Products)
            {
                table.Cell()
                    .Height(100)
                    .Image(GetProductImage(product.Id))
                    .FitArea();
            }
        });
    }
}
```

## Quality Settings

### Per-Image Settings

```csharp
// Compression quality (affects file size)
container.Image("photo.jpg")
    .WithCompressionQuality(ImageCompressionQuality.Medium);

// DPI setting (default is 72)
container.Image("photo.jpg")
    .WithRasterDpi(150);

// Combined
container.Image("photo.jpg")
    .WithCompressionQuality(ImageCompressionQuality.High)
    .WithRasterDpi(300);
```

### Compression Quality Levels

| Level | Quality | Use Case |
|-------|---------|----------|
| `VeryLow` | 0.1 | Draft documents, quick previews |
| `Low` | 0.25 | Internal documents |
| `Medium` | 0.5 | Standard documents |
| `High` | 0.75 | Professional documents |
| `VeryHigh` | 0.9 | High-quality prints |
| `Best` | 1.0 | Maximum quality (largest file) |

### Global Document Settings

```csharp
public DocumentSettings GetSettings() => new DocumentSettings
{
    ImageCompressionQuality = ImageCompressionQuality.High,
    ImageRasterDpi = 150
};

// Or with Document.Create
Document.Create(container => { /* ... */ })
    .WithSettings(new DocumentSettings
    {
        ImageCompressionQuality = ImageCompressionQuality.High,
        ImageRasterDpi = 150
    })
    .GeneratePdf("output.pdf");
```

## Common Patterns

### Logo Header

```csharp
void ComposeHeader(IContainer container)
{
    container.Row(row =>
    {
        row.ConstantItem(120).Height(50).Image(_logo).FitArea();

        row.RelativeItem().Column(column =>
        {
            column.Item().AlignRight().Text("ACME Corporation").FontSize(16).Bold();
            column.Item().AlignRight().Text("123 Business St, City");
            column.Item().AlignRight().Text("(555) 123-4567");
        });
    });
}
```

### Image Gallery / Grid

```csharp
void ComposeImageGallery(IContainer container)
{
    var imagesPerRow = 3;
    var imageGroups = Model.Images
        .Select((img, idx) => new { img, idx })
        .GroupBy(x => x.idx / imagesPerRow)
        .Select(g => g.Select(x => x.img).ToList())
        .ToList();

    container.Column(column =>
    {
        column.Spacing(10);

        foreach (var rowImages in imageGroups)
        {
            column.Item().Row(row =>
            {
                row.Spacing(10);

                foreach (var image in rowImages)
                {
                    row.RelativeItem()
                        .AspectRatio(1)  // Square
                        .Border(1)
                        .BorderColor(Colors.Grey.Lighten2)
                        .Image(image.Bytes)
                        .FitArea();
                }

                // Fill empty slots with blank space
                for (var i = rowImages.Count; i < imagesPerRow; i++)
                {
                    row.RelativeItem();
                }
            });
        }
    });
}
```

### Product Card with Image

```csharp
void ComposeProductCard(IContainer container, Product product)
{
    container
        .Border(1)
        .BorderColor(Colors.Grey.Lighten2)
        .Column(column =>
        {
            // Product image
            column.Item()
                .Height(150)
                .Background(Colors.Grey.Lighten4)
                .Image(product.ImageBytes)
                .FitArea();

            // Product details
            column.Item().Padding(10).Column(details =>
            {
                details.Item().Text(product.Name).FontSize(12).Bold();
                details.Item().Text(product.Description).FontSize(10).ClampLines(2);
                details.Item().PaddingTop(5).Text($"${product.Price:F2}")
                    .FontSize(14).Bold().FontColor(Colors.Green.Darken2);
            });
        });
}
```

### Signature/Stamp Overlay

```csharp
void ComposeSignatureSection(IContainer container)
{
    container.Layers(layers =>
    {
        // Background: signature line
        layers.PrimaryLayer().Column(column =>
        {
            column.Item().Height(50);
            column.Item().BorderBottom(1).BorderColor(Colors.Grey.Medium);
            column.Item().Text("Authorized Signature").FontSize(8);
        });

        // Overlay: signature image (if signed)
        if (Model.SignatureImage != null)
        {
            layers.Layer()
                .AlignCenter()
                .AlignBottom()
                .PaddingBottom(15)
                .Height(40)
                .Image(Model.SignatureImage)
                .FitHeight();
        }
    });
}
```

### Watermark

```csharp
container.Page(page =>
{
    page.Size(PageSizes.A4);
    page.Margin(50);

    // Watermark behind content
    page.Background()
        .AlignCenter()
        .AlignMiddle()
        .Image("watermark.png")
        .FitArea();

    // Or text watermark
    page.Foreground()
        .AlignCenter()
        .AlignMiddle()
        .RotateLeft()
        .Text("DRAFT")
        .FontSize(72)
        .FontColor(Colors.Grey.Lighten2)
        .Bold();

    page.Content().Element(ComposeContent);
});
```

## Dynamic Images

### QR Codes (with library)

```csharp
// Using QRCoder library
using QRCoder;

byte[] GenerateQRCode(string content)
{
    using var qrGenerator = new QRCodeGenerator();
    var qrData = qrGenerator.CreateQrCode(content, QRCodeGenerator.ECCLevel.Q);
    using var qrCode = new PngByteQRCode(qrData);
    return qrCode.GetGraphic(10);
}

void ComposeQRCode(IContainer container)
{
    var qrBytes = GenerateQRCode($"INV-{Model.InvoiceNumber}");
    container.Width(80).Height(80).Image(qrBytes);
}
```

### Barcodes (with library)

```csharp
// Using ZXing.Net
using ZXing;
using ZXing.Common;

byte[] GenerateBarcode(string content)
{
    var writer = new BarcodeWriterPixelData
    {
        Format = BarcodeFormat.CODE_128,
        Options = new EncodingOptions
        {
            Width = 200,
            Height = 50,
            Margin = 0
        }
    };

    var pixelData = writer.Write(content);
    // Convert to PNG bytes...
    return ConvertToPng(pixelData);
}
```

## Error Handling

```csharp
void SafeComposeImage(IContainer container, string imagePath)
{
    try
    {
        if (File.Exists(imagePath))
        {
            container.Image(imagePath).FitArea();
        }
        else
        {
            ComposePlaceholder(container, "Image not found");
        }
    }
    catch (Exception ex)
    {
        ComposePlaceholder(container, $"Error: {ex.Message}");
    }
}

void ComposePlaceholder(IContainer container, string message)
{
    container
        .Background(Colors.Grey.Lighten4)
        .AlignCenter()
        .AlignMiddle()
        .Text(message)
        .FontSize(10)
        .FontColor(Colors.Grey.Medium);
}
```
