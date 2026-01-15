# verify-code-blocks.ps1
# Verifies all C# code blocks in documentation have appropriate markers
#
# Usage:
#   pwsh scripts/verify-code-blocks.ps1
#   pwsh scripts/verify-code-blocks.ps1 -DocsPath "docs" -Verbose

param(
    [string]$DocsPath = "docs",
    [switch]$Verbose
)

$errors = @()
$stats = @{
    Files = 0
    CompiledSnippets = 0
    PseudoSnippets = 0
    InvalidSnippets = 0
    GeneratedSnippets = 0
    Unmarked = 0
}

Get-ChildItem -Path $DocsPath -Recurse -Include "*.md" | ForEach-Object {
    $file = $_
    $stats.Files++
    $content = Get-Content $file.FullName -Raw
    $lines = Get-Content $file.FullName

    # Count MarkdownSnippets-managed blocks (look for endSnippet marker)
    $stats.CompiledSnippets += ([regex]'<!-- endSnippet -->').Matches($content).Count

    # Count manual pseudo/invalid/generated blocks
    $stats.PseudoSnippets += ([regex]'<!-- pseudo:').Matches($content).Count
    $stats.InvalidSnippets += ([regex]'<!-- invalid:').Matches($content).Count
    $stats.GeneratedSnippets += ([regex]'<!-- generated:').Matches($content).Count

    # Check for unclosed manual snippets
    $pseudoOpens = ([regex]'<!-- pseudo:').Matches($content).Count
    $invalidOpens = ([regex]'<!-- invalid:').Matches($content).Count
    $generatedOpens = ([regex]'<!-- generated:').Matches($content).Count
    $manualCloses = ([regex]'<!-- /snippet -->').Matches($content).Count

    if (($pseudoOpens + $invalidOpens + $generatedOpens) -ne $manualCloses) {
        $errors += "$($file.Name): Unclosed manual snippet (pseudo:$pseudoOpens + invalid:$invalidOpens + generated:$generatedOpens opens, $manualCloses closes)"
    }

    # Find unmarked code blocks
    $lineNum = 0
    $inManagedSnippet = $false

    foreach ($line in $lines) {
        $lineNum++

        # Track MarkdownSnippets-managed blocks
        if ($line -match '<!-- snippet:' -or $line -match '^snippet:\s+\S+') {
            $inManagedSnippet = $true
        }
        if ($line -match '<!-- endSnippet -->' -or $line -match '<!-- /snippet -->') {
            $inManagedSnippet = $false
        }

        # Find ```csharp blocks
        if ($line -match '^```csharp') {
            if (-not $inManagedSnippet) {
                $stats.Unmarked++
                $errors += "$($file.Name):$lineNum - Unmarked C# code block"
                if ($Verbose) {
                    # Show context
                    $contextStart = [Math]::Max(0, $lineNum - 3)
                    $contextEnd = [Math]::Min($lines.Count - 1, $lineNum + 2)
                    Write-Host "  Context:" -ForegroundColor Gray
                    for ($i = $contextStart; $i -le $contextEnd; $i++) {
                        $prefix = if ($i -eq $lineNum - 1) { ">>> " } else { "    " }
                        Write-Host "$prefix$($lines[$i])" -ForegroundColor Gray
                    }
                }
            }
        }
    }
}

# Output results
Write-Host "`n=== Code Block Verification ===" -ForegroundColor Cyan
Write-Host "Files scanned: $($stats.Files)"
Write-Host "Compiled snippets (MarkdownSnippets): $($stats.CompiledSnippets)" -ForegroundColor Green
Write-Host "Pseudo-code blocks: $($stats.PseudoSnippets)" -ForegroundColor Yellow
Write-Host "Invalid/anti-pattern blocks: $($stats.InvalidSnippets)" -ForegroundColor Yellow
Write-Host "Generated output blocks: $($stats.GeneratedSnippets)" -ForegroundColor Cyan
Write-Host "Unmarked blocks: $($stats.Unmarked)" -ForegroundColor $(if ($stats.Unmarked -gt 0) { 'Red' } else { 'Green' })

if ($errors) {
    Write-Host "`nErrors found:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    exit 1
} else {
    Write-Host "`nAll code blocks are properly marked" -ForegroundColor Green
    exit 0
}
