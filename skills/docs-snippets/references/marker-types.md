# Marker Types Reference

Detailed guidance for choosing the right code block marker in documentation.

## Decision Flowchart

```
Is this code intentionally broken/wrong?
├── YES → <!-- invalid:{id} -->
└── NO ↓

Is this showing actual source-generated output?
├── YES → <!-- generated:{path}#L{start}-L{end} -->
└── NO ↓

Is this a complete, compilable C# statement or block?
├── YES → snippet: {id} (add to docs/samples)
└── NO ↓

Is this just an API reference fragment or hypothetical feature?
├── YES → <!-- pseudo:{id} -->
└── NO → Reconsider - probably should be a snippet
```

## Marker Details

### `snippet: {id}` - Compiled and Tested

Code from `#region {id}` in the samples project, synced via MarkdownSnippets.

**Use for:**
- Real API usage examples
- Code users might copy and adapt
- Comparison examples (Moq vs NSubstitute, etc.)
- Any compilable C# demonstrating patterns

**Key principle:** If it compiles, compile it. Add package references to samples if needed (Moq, etc.).

### `<!-- invalid:{id} -->` - Intentionally Broken

Code that shows errors, wrong patterns, or diagnostic triggers.

**Use for:**
- "Don't do this" anti-pattern examples
- Code demonstrating compile errors
- Diagnostic documentation showing error triggers

**Format:**
```markdown
<!-- invalid:wrong-save-pattern -->
```csharp
// WRONG - discards the result
await factory.Save(entity);
```
<!-- /snippet -->
```

### `<!-- generated:{path}#L{start}-L{end} -->` - Source Generator Output

Actual output from a source generator, with path and line numbers for drift detection.

**Use for:**
- Showing what generators produce
- Documenting generated API shapes

**Format:**
```markdown
<!-- generated:Generated/Factory.g.cs#L15-L22 -->
```csharp
public interface IUserFactory { }
```
<!-- /snippet -->
```

Line numbers enable drift detection - when verification runs, mismatches signal the generator changed.

### `<!-- pseudo:{id} -->` - Illustrative Only

Code fragments NOT meant to compile because they are inherently incomplete.

**Use for (limited):**
- API signatures shown for reference
- Incomplete property fragments
- Hypothetical/future features not yet implemented

**NOT for:**
- Code from other libraries (compilable)
- Code "not in samples yet" (add it)
- Complete valid C# statements (compile them)

## Common Mistakes

### Marking Compilable Code as Pseudo

**Wrong:**
```markdown
<!-- pseudo:moq-example -->  # This code compiles!
```

**Correct:** Add Moq package to samples, use `snippet:`

### "Not in Samples Yet"

**Wrong:**
```markdown
<!-- pseudo:usage-pattern -->  # Lazy shortcut
```

**Correct:** Add to samples, then reference with `snippet:`

### "The Types Don't Exist"

**Wrong:** Using pseudo because supporting types aren't in samples.

**Correct:** Create placeholder types in samples:
```csharp
// Create what you need:
public interface IUserService { User GetUser(int id); }
public class User { public int Id { get; set; } }

#region user-service-example
var service = new UserServiceImpl();
var user = service.GetUser(42);
#endregion
```

The samples project exists to make documentation code real.

## No Commented Code in Snippets

Compiled snippets must not contain commented-out code:

**Wrong:**
```csharp
#region insert-operation
[Insert]
public async Task Insert()
{
    // In real code: db.Persons.Add(entity);
    // await db.SaveChangesAsync();
}
#endregion
```

**Acceptable comments:**
- Result annotations: `var total = x.Total; // 50.00`
- Anti-pattern labels: `// WRONG - don't do this`
- Brief explanations: `// Triggers validation`

**Unacceptable comments:**
- Database placeholders: `// await db.SaveChangesAsync();`
- "Real code" comments: `// In real implementation: ...`
- Hypothetical code: `// You could also do: ...`

If code can't be compiled, use `<!-- pseudo: -->` and be honest that it's illustrative.
