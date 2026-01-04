# Text & Styling

## Basic Text

```csharp
// Simple text
container.Text("Hello World");

// Styled text
container.Text("Styled Text")
    .FontSize(24)
    .Bold()
    .FontColor(Colors.Blue.Medium);
```

## Text Blocks (Multiple Styles)

Use the text block overload for complex formatting within a single paragraph.

```csharp
container.Text(text =>
{
    text.Span("Normal text, ");
    text.Span("bold text, ").Bold();
    text.Span("italic text, ").Italic();
    text.Span("and colored text.").FontColor(Colors.Red.Medium);
});
```

### Text with Line Breaks

```csharp
container.Text(text =>
{
    text.Span("First paragraph of text.");
    text.EmptyLine();
    text.Span("Second paragraph after a blank line.");
});
```

### Page Numbers

```csharp
container.Text(text =>
{
    text.Span("Page ");
    text.CurrentPageNumber();
    text.Span(" of ");
    text.TotalPages();
});

// Formatted page numbers
container.Text(text =>
{
    text.Span("Document Page ");
    text.CurrentPageNumber().Bold();
    text.Span(" / ");
    text.TotalPages().Bold();
});
```

## Font Styling Methods

### Size and Family

```csharp
container.Text("Text")
    .FontSize(12)
    .FontFamily("Arial")
    .FontFamily("Helvetica", "Arial", "sans-serif");  // Fallback fonts
```

### Font Weight

```csharp
.Thin()
.ExtraLight()
.Light()
.NormalWeight()
.Medium()
.SemiBold()
.Bold()
.ExtraBold()
.Black()

// Or explicit weight value
.Weight(FontWeight.Bold)
```

### Font Style and Decoration

```csharp
.Italic()
.Underline()
.Strikethrough()
.Subscript()
.Superscript()
```

### Colors

```csharp
// Predefined colors
.FontColor(Colors.Blue.Medium)
.FontColor(Colors.Red.Darken2)
.BackgroundColor(Colors.Yellow.Lighten3)

// Hex colors
.FontColor("#0000FF")
.FontColor("#FF5733")

// Color shades available:
// - Lighten5, Lighten4, Lighten3, Lighten2, Lighten1
// - Medium
// - Darken1, Darken2, Darken3, Darken4
```

### Spacing

```csharp
.LineHeight(1.5f)              // Line height multiplier
.LetterSpacing(0.5f)           // Space between characters
.WordSpacing(2f)               // Space between words
.ParagraphSpacing(10)          // Space between paragraphs
.ParagraphFirstLineIndentation(20)  // First line indent
```

### Text Direction (RTL Support)

```csharp
.DirectionAuto()              // Auto-detect
.DirectionFromLeftToRight()   // LTR (default)
.DirectionFromRightToLeft()   // RTL for Arabic, Hebrew, etc.
```

## Text Alignment

**Note:** Alignment is applied to the container, not the text element.

```csharp
// Horizontal alignment
container.AlignLeft().Text("Left aligned");
container.AlignCenter().Text("Center aligned");
container.AlignRight().Text("Right aligned");

// Justify (stretch text to fill width)
container.Text("Justified text that fills the entire width...")
    .Justify();
```

## Line Clamping (Ellipsis)

Truncate long text with ellipsis after a specified number of lines.

```csharp
container.Text(veryLongText)
    .ClampLines(3);  // Truncates to 3 lines with "..."

container.Text(longDescription)
    .ClampLines(2)
    .FontSize(10);
```

## DefaultTextStyle

Apply consistent styling to all text within a container hierarchy.

```csharp
// At page level
page.DefaultTextStyle(x => x
    .FontSize(11)
    .FontFamily("Arial")
    .FontColor(Colors.Grey.Darken3));

// At container level
container.DefaultTextStyle(x => x.FontSize(10).Light())
    .Column(column =>
    {
        column.Item().Text("Uses default style (10pt light)");
        column.Item().Text("Also uses default style");
        column.Item().Text("Adds bold to default").Bold();  // 10pt light bold
    });
```

### Nested DefaultTextStyle

```csharp
container
    .DefaultTextStyle(x => x.FontSize(12).FontFamily("Times New Roman"))
    .Column(column =>
    {
        column.Item().Text("12pt Times New Roman");

        column.Item()
            .DefaultTextStyle(x => x.FontColor(Colors.Blue.Medium))
            .Column(inner =>
            {
                // Inherits 12pt Times, adds blue
                inner.Item().Text("12pt Times New Roman, Blue");
            });
    });
```

## Typography Pattern

Create a centralized typography system for consistent document styling.

```csharp
public static class Typography
{
    public static TextStyle Title => TextStyle.Default
        .FontSize(24)
        .Bold()
        .FontColor(Colors.Blue.Darken3);

    public static TextStyle Heading1 => TextStyle.Default
        .FontSize(18)
        .Bold()
        .FontColor(Colors.Grey.Darken3);

    public static TextStyle Heading2 => TextStyle.Default
        .FontSize(14)
        .SemiBold()
        .FontColor(Colors.Grey.Darken2);

    public static TextStyle Heading3 => TextStyle.Default
        .FontSize(12)
        .SemiBold();

    public static TextStyle Body => TextStyle.Default
        .FontSize(10)
        .FontColor(Colors.Grey.Darken3);

    public static TextStyle BodySmall => TextStyle.Default
        .FontSize(9)
        .FontColor(Colors.Grey.Darken1);

    public static TextStyle Caption => TextStyle.Default
        .FontSize(8)
        .FontColor(Colors.Grey.Medium);

    public static TextStyle Label => TextStyle.Default
        .FontSize(9)
        .SemiBold()
        .FontColor(Colors.Grey.Darken1);

    public static TextStyle TableHeader => TextStyle.Default
        .FontSize(10)
        .Bold()
        .FontColor(Colors.White);

    public static TextStyle Currency => TextStyle.Default
        .FontSize(10)
        .FontFamily("Consolas");

    public static TextStyle Emphasis => TextStyle.Default
        .Italic()
        .FontColor(Colors.Grey.Darken2);
}
```

### Using Typography

```csharp
container.Column(column =>
{
    column.Spacing(10);

    column.Item().Text("Document Title").Style(Typography.Title);
    column.Item().Text("Section Heading").Style(Typography.Heading1);
    column.Item().Text("This is body text with standard formatting.")
        .Style(Typography.Body);
    column.Item().Text("Small print and legal text").Style(Typography.Caption);
});

// In tables
table.Cell().Element(HeaderCell).Text("Amount").Style(Typography.TableHeader);
table.Cell().Element(DataCell).Text($"{amount:C}").Style(Typography.Currency);
```

## Special Text Elements

### Hyperlinks

```csharp
container.Text(text =>
{
    text.Span("Visit our website: ");
    text.Hyperlink("https://example.com", "Example.com")
        .FontColor(Colors.Blue.Medium)
        .Underline();
});
```

### Internal Links (to Sections)

```csharp
container.Text(text =>
{
    text.Span("See ");
    text.SectionLink("chapter1", "Chapter 1")
        .FontColor(Colors.Blue.Medium)
        .Underline();
    text.Span(" for more details.");
});
```

### Section Page Numbers

```csharp
container.Text(text =>
{
    text.Span("Appendix starts on page ");
    text.BeginPageNumberOfSection("appendix");
});
```

## Lists

QuestPDF doesn't have a dedicated list component, but you can create them easily.

### Bulleted List

```csharp
void ComposeBulletList(IContainer container, IEnumerable<string> items)
{
    container.Column(column =>
    {
        column.Spacing(5);

        foreach (var item in items)
        {
            column.Item().Row(row =>
            {
                row.ConstantItem(15).Text("•");
                row.RelativeItem().Text(item);
            });
        }
    });
}
```

### Numbered List

```csharp
void ComposeNumberedList(IContainer container, IEnumerable<string> items)
{
    container.Column(column =>
    {
        column.Spacing(5);

        var index = 1;
        foreach (var item in items)
        {
            column.Item().Row(row =>
            {
                row.ConstantItem(25).AlignRight().Text($"{index}.");
                row.ConstantItem(5); // Gap
                row.RelativeItem().Text(item);
            });
            index++;
        }
    });
}
```

### Nested List

```csharp
void ComposeNestedList(IContainer container)
{
    container.Column(column =>
    {
        column.Spacing(5);

        column.Item().Row(row =>
        {
            row.ConstantItem(15).Text("•");
            row.RelativeItem().Text("First level item");
        });

        // Nested items with indentation
        column.Item().PaddingLeft(20).Column(nested =>
        {
            nested.Spacing(3);
            nested.Item().Row(row =>
            {
                row.ConstantItem(15).Text("◦");
                row.RelativeItem().Text("Nested item 1");
            });
            nested.Item().Row(row =>
            {
                row.ConstantItem(15).Text("◦");
                row.RelativeItem().Text("Nested item 2");
            });
        });

        column.Item().Row(row =>
        {
            row.ConstantItem(15).Text("•");
            row.RelativeItem().Text("Second level item");
        });
    });
}
```

## Rich Text Formatting

### Terms and Definitions

```csharp
void ComposeDefinitionList(IContainer container)
{
    container.Column(column =>
    {
        column.Spacing(10);

        foreach (var (term, definition) in definitions)
        {
            column.Item().Column(item =>
            {
                item.Item().Text(term).Bold().FontSize(11);
                item.Item().PaddingLeft(15).Text(definition).FontSize(10);
            });
        }
    });
}
```

### Blockquote

```csharp
void ComposeBlockquote(IContainer container, string quote, string attribution)
{
    container
        .BorderLeft(3)
        .BorderColor(Colors.Grey.Medium)
        .PaddingLeft(15)
        .Column(column =>
        {
            column.Item().Text($"\"{quote}\"").Italic().FontSize(11);
            column.Item().PaddingTop(5).AlignRight().Text($"— {attribution}")
                .FontSize(10).FontColor(Colors.Grey.Darken1);
        });
}
```

### Code Block

```csharp
void ComposeCodeBlock(IContainer container, string code)
{
    container
        .Background(Colors.Grey.Lighten4)
        .Border(1)
        .BorderColor(Colors.Grey.Lighten2)
        .Padding(10)
        .Text(code)
        .FontFamily("Consolas", "Courier New", "monospace")
        .FontSize(9);
}
```
