# Page Flow & Navigation

## Page Breaks

### Manual Page Breaks

```csharp
container.Column(column =>
{
    column.Item().Text("Content on first page");

    column.Item().PageBreak();

    column.Item().Text("Content on second page");
});
```

### Conditional Page Breaks

```csharp
// Break only if less than specified space remains
container.Column(column =>
{
    column.Item().Text("First section");

    // Insert page break if less than 200pt available
    column.Item().PageBreak().ConditionallyBreakIfNecessary();

    column.Item().Text("Second section");
});
```

## Keeping Content Together

### ShowEntire - Prevent Splitting

Keep content together as a unit (moves to next page if it doesn't fit).

```csharp
// Keep the entire block together - never split across pages
container.ShowEntire().Column(column =>
{
    column.Item().Text("Title").Bold();
    column.Item().Text("Subtitle");
    column.Item().Text("Description that should stay with the title");
});
```

### EnsureSpace - Minimum Space Requirement

Move to next page if less than specified space remains.

```csharp
// Move to next page if less than 100pt available
container.EnsureSpace(100).Column(column =>
{
    column.Item().Text("Section Title").Bold();
    column.Item().Text("Content that needs at least 100pt of space");
});
```

### Practical Pattern: Section Headers

```csharp
void ComposeSection(IContainer container, string title, Action<IContainer> content)
{
    container
        .EnsureSpace(100)  // Ensure header + some content stay together
        .Column(column =>
        {
            column.Item()
                .BorderBottom(2)
                .BorderColor(Colors.Blue.Medium)
                .PaddingBottom(5)
                .Text(title).FontSize(16).Bold();

            column.Item().PaddingTop(10).Element(content);
        });
}
```

### StopPaging - Single Page Only

Content that should not overflow to additional pages (may be cut off).

```csharp
// Content will be cut off if it exceeds page height
container.StopPaging().Column(column =>
{
    column.Item().Text("This content stays on one page only");
    // Additional content may be truncated
});
```

## Sections and Navigation

### Defining Sections

```csharp
container.Column(column =>
{
    column.Item()
        .Section("introduction")  // Define a section anchor
        .Text("Introduction").FontSize(18).Bold();

    column.Item().Text("Introduction content...");

    column.Item()
        .Section("chapter1")
        .Text("Chapter 1").FontSize(18).Bold();

    column.Item().Text("Chapter 1 content...");

    column.Item()
        .Section("chapter2")
        .Text("Chapter 2").FontSize(18).Bold();

    column.Item().Text("Chapter 2 content...");

    column.Item()
        .Section("appendix")
        .Text("Appendix").FontSize(18).Bold();
});
```

### Table of Contents with Links

```csharp
void ComposeTableOfContents(IContainer container)
{
    container.Column(column =>
    {
        column.Spacing(10);

        column.Item().Text("Table of Contents").FontSize(20).Bold();

        column.Item().Height(20);  // Spacing

        var entries = new[]
        {
            ("Introduction", "introduction"),
            ("Chapter 1: Getting Started", "chapter1"),
            ("Chapter 2: Advanced Topics", "chapter2"),
            ("Appendix", "appendix")
        };

        foreach (var (title, sectionId) in entries)
        {
            column.Item().Row(row =>
            {
                // Clickable link
                row.RelativeItem()
                    .SectionLink(sectionId)
                    .Text(title)
                    .FontColor(Colors.Blue.Medium)
                    .Underline();

                // Dotted leader
                row.ConstantItem(20);

                // Page number
                row.AutoItem().Text(text =>
                {
                    text.BeginPageNumberOfSection(sectionId);
                });
            });
        }
    });
}
```

### Section with Page Numbers in Footer

```csharp
void ComposeFooter(IContainer container)
{
    container.Row(row =>
    {
        // Current section name (if tracked separately)
        row.RelativeItem().Text($"Generated: {DateTime.Now:g}");

        // Page number with total
        row.RelativeItem().AlignRight().Text(text =>
        {
            text.Span("Page ");
            text.CurrentPageNumber();
            text.Span(" of ");
            text.TotalPages();
        });
    });
}
```

## Conditional Rendering

### ShowIf - Conditional Display

```csharp
// Show only if condition is true
container.ShowIf(Model.HasDiscount)
    .Background(Colors.Yellow.Lighten3)
    .Padding(10)
    .Text($"Discount Applied: {Model.DiscountPercent}%");

// Alternative: inline conditional
container.Column(column =>
{
    if (Model.HasDiscount)
    {
        column.Item()
            .Background(Colors.Yellow.Lighten3)
            .Padding(10)
            .Text($"Discount: {Model.DiscountPercent}%");
    }
});
```

### ShowOnce - First Page Only

```csharp
// Show only on the first page of the section
page.Header().ShowOnce()
    .Text("FIRST PAGE HEADER")
    .FontSize(24).Bold();
```

### SkipOnce - Skip First Page

```csharp
// Skip first page, show on all subsequent pages
page.Header().SkipOnce()
    .Text("CONTINUATION HEADER")
    .FontSize(14);
```

### Combined Header Pattern

```csharp
void ComposeHeader(IContainer container)
{
    container.Column(column =>
    {
        // Full header on first page
        column.Item().ShowOnce().Element(ComposeFullHeader);

        // Smaller header on subsequent pages
        column.Item().SkipOnce().Element(ComposeContinuationHeader);
    });
}

void ComposeFullHeader(IContainer container)
{
    container.Row(row =>
    {
        row.ConstantItem(120).Height(60).Image(_logo);
        row.RelativeItem().Column(col =>
        {
            col.Item().Text("COMPANY NAME").FontSize(20).Bold();
            col.Item().Text("Full Address and Contact Information");
        });
    });
}

void ComposeContinuationHeader(IContainer container)
{
    container.Row(row =>
    {
        row.ConstantItem(80).Height(30).Image(_logo).FitArea();
        row.RelativeItem().AlignRight().AlignMiddle()
            .Text(Model.DocumentTitle).FontSize(12);
    });
}
```

## Multi-Section Documents

### Document with Cover Page

```csharp
public void Compose(IDocumentContainer container)
{
    // Cover page (no header/footer)
    container.Page(page =>
    {
        page.Size(PageSizes.A4);
        page.Margin(50);

        page.Content().AlignCenter().AlignMiddle().Column(column =>
        {
            column.Item().Text(Model.Title).FontSize(36).Bold();
            column.Item().PaddingTop(20).Text(Model.Subtitle).FontSize(18);
            column.Item().PaddingTop(50).Text($"Prepared by: {Model.Author}");
            column.Item().Text($"Date: {Model.Date:D}");
        });
    });

    // Table of contents
    container.Page(page =>
    {
        page.Size(PageSizes.A4);
        page.Margin(50);
        page.Header().Text("Contents").FontSize(20).Bold();
        page.Content().Element(ComposeTableOfContents);
    });

    // Main content
    container.Page(page =>
    {
        page.Size(PageSizes.A4);
        page.Margin(50);

        page.Header().Element(ComposeHeader);
        page.Content().Element(ComposeMainContent);
        page.Footer().Element(ComposeFooter);
    });

    // Appendix (landscape for wide tables)
    container.Page(page =>
    {
        page.Size(PageSizes.A4.Landscape());
        page.Margin(30);

        page.Header().Section("appendix").Text("Appendix: Data Tables").Bold();
        page.Content().Element(ComposeAppendix);
        page.Footer().Element(ComposeFooter);
    });
}
```

### Dynamic Page Creation

```csharp
public void Compose(IDocumentContainer container)
{
    foreach (var chapter in Model.Chapters)
    {
        container.Page(page =>
        {
            page.Size(PageSizes.A4);
            page.Margin(50);

            page.Header()
                .Section($"chapter-{chapter.Number}")
                .Text($"Chapter {chapter.Number}: {chapter.Title}")
                .FontSize(16).Bold();

            page.Content().Column(column =>
            {
                column.Spacing(10);

                foreach (var section in chapter.Sections)
                {
                    column.Item().Element(c => ComposeSection(c, section));
                }
            });

            page.Footer().Element(ComposeFooter);
        });
    }
}
```

## Page Number Formatting

### Basic Page Numbers

```csharp
container.Text(text =>
{
    text.Span("Page ");
    text.CurrentPageNumber();
});

container.Text(text =>
{
    text.CurrentPageNumber();
    text.Span(" of ");
    text.TotalPages();
});
```

### Section-Relative Page Numbers

```csharp
// Page number where a section begins
container.Text(text =>
{
    text.Span("See page ");
    text.BeginPageNumberOfSection("appendix");
});

// Page number where a section ends
container.Text(text =>
{
    text.Span("Appendix ends on page ");
    text.EndPageNumberOfSection("appendix");
});
```

### Formatted Page Numbers

```csharp
// Roman numerals for front matter
container.Text(text =>
{
    text.CurrentPageNumber().Format(n => ToRomanNumerals(n));
});

// Custom formatting
container.Text(text =>
{
    text.CurrentPageNumber().Format(n => $"P{n:D3}");  // P001, P002, etc.
});
```

## Best Practices

### Preventing Orphaned Headers

```csharp
void ComposeContentWithHeaders(IContainer container)
{
    container.Column(column =>
    {
        column.Spacing(15);

        foreach (var section in Model.Sections)
        {
            // Keep header + first paragraph together
            column.Item()
                .EnsureSpace(100)  // At least 100pt for header + content
                .Column(sectionCol =>
                {
                    sectionCol.Item()
                        .Text(section.Title)
                        .FontSize(14)
                        .Bold();

                    sectionCol.Item()
                        .PaddingTop(5)
                        .Text(section.Content);
                });
        }
    });
}
```

### Table Row Grouping

```csharp
// Keep related rows together
foreach (var group in Model.ItemGroups)
{
    // Group header + first item stay together
    column.Item().ShowEntire().Column(groupCol =>
    {
        groupCol.Item()
            .Background(Colors.Grey.Lighten3)
            .Padding(5)
            .Text(group.Name).Bold();

        if (group.Items.Any())
        {
            groupCol.Item().Element(c => ComposeItemRow(c, group.Items.First()));
        }
    });

    // Remaining items can split normally
    foreach (var item in group.Items.Skip(1))
    {
        column.Item().Element(c => ComposeItemRow(c, item));
    }
}
```
