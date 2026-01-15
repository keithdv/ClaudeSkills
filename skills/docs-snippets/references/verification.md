# Verification and CI Integration

How to verify documentation stays in sync with code.

## Verification Layers

```
[1] dotnet build docs/samples/     # Code compiles
        ↓
[2] dotnet test docs/samples/      # Tests pass
        ↓
[3] dotnet mdsnippets              # Snippets synced
        ↓
[4] git diff --exit-code docs/     # No uncommitted changes
        ↓
[5] verify-code-blocks.ps1         # All blocks have markers
```

## The Verification Script

`scripts/verify-code-blocks.ps1` checks that every C# code block has a marker.

See [../scripts/verify-code-blocks.ps1](../scripts/verify-code-blocks.ps1) for the full implementation.

**Usage:**
```powershell
# Basic check
pwsh scripts/verify-code-blocks.ps1

# With context for unmarked blocks
pwsh scripts/verify-code-blocks.ps1 -Verbose
```

**What it checks:**
- Compiled snippets (MarkdownSnippets-managed, have `<!-- endSnippet -->`)
- Pseudo-code blocks (`<!-- pseudo:{id} -->`)
- Invalid example blocks (`<!-- invalid:{id} -->`)
- Generated output blocks (`<!-- generated:{path} -->`)
- Unmarked blocks (any ` ```csharp ` not inside a managed snippet)

## CI Integration

### GitHub Actions

```yaml
# .github/workflows/build.yml

- name: Restore tools
  run: dotnet tool restore

- name: Build samples
  run: dotnet build docs/samples/

- name: Test samples
  run: dotnet test docs/samples/

- name: Run MarkdownSnippets
  run: dotnet mdsnippets

- name: Verify docs unchanged
  run: |
    if [ -n "$(git status --porcelain docs/)" ]; then
      echo "Documentation out of sync"
      git diff docs/
      exit 1
    fi

- name: Verify code block coverage
  run: pwsh scripts/verify-code-blocks.ps1
```

## Generated Snippet Drift Detection

For `<!-- generated:{path}#L{start}-L{end} -->` markers, create a drift detection script:

```powershell
# verify-generated-snippets.ps1
param(
    [string]$DocsPath = "docs",
    [string]$BasePath = "docs/samples"
)

$errors = @()

Get-ChildItem -Path $DocsPath -Recurse -Include "*.md" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $pattern = '<!-- generated:([^#]+)#L(\d+)-L(\d+)\s*-->'
    $matches = [regex]::Matches($content, $pattern)

    foreach ($match in $matches) {
        $sourcePath = Join-Path $BasePath $match.Groups[1].Value
        if (-not (Test-Path $sourcePath)) {
            $errors += "$($_.Name): generated marker - file not found: $sourcePath"
        }
    }
}

if ($errors) {
    Write-Host "Generated snippet issues:" -ForegroundColor Yellow
    $errors | ForEach-Object { Write-Host "  $_" }
    exit 1
}
```

When drift is detected, review the change and update the snippet content and line numbers.
