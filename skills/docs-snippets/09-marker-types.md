# Marker Types Reference

This guide provides detailed definitions for each code block marker type, helping you choose the right marker for any code in documentation.

## Core Principle

**If it compiles, it should be compiled.**

Code that could be pasted into a .cs file and compile (with appropriate usings/references) should be in the samples project, not marked as pseudo-code.

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
├── YES → <!-- pseudo:{description} -->
└── NO → Reconsider - probably should be a snippet
```

## Quick Reference

| Code Type | Marker | Action |
|-----------|--------|--------|
| Working example | `snippet:` | Add to docs/samples |
| Moq/other library comparison | `snippet:` | Add to docs/samples (with package reference) |
| Code that triggers diagnostic | `invalid:` | Use invalid marker |
| Anti-pattern example | `invalid:` | Use invalid marker |
| Source generator output | `generated:` | Use generated marker with path |
| Property name fragment | `pseudo:` | Use pseudo marker |
| Future/hypothetical feature | `pseudo:` | Use pseudo marker |
| "Not in samples yet" | `snippet:` | **Add to samples first** |

---

## `snippet: {id}` - Compiled and Tested

**Definition:** Code compiled and tested in the docs/samples project, synced via MarkdownSnippets.

**When to use:**
- ANY code demonstrating real API usage
- Code a user might copy and adapt
- Usage patterns and examples
- Comparison examples between libraries (Moq, NSubstitute, etc.)

**Key principle:** If the code is compilable, it should be compiled. This catches errors before they reach documentation.

**Examples of what belongs here:**
- Framework stub definitions and usage
- Moq setup/verify patterns (add Moq package reference to samples)
- Any C# that could be pasted into a real project

**How it works:**
1. Add `#region {snippet-id}` in docs/samples
2. Add `snippet: {snippet-id}` in markdown
3. Run `dotnet mdsnippets`

---

## `<!-- invalid:{id} -->` - Intentionally Broken

**Definition:** Code that intentionally shows errors, wrong patterns, or diagnostic triggers.

**When to use:**
- Diagnostic documentation showing error triggers
- "Don't do this" anti-pattern examples
- Code demonstrating compile errors
- Examples with intentional mistakes

**Key principle:** The code is meant to NOT work. It illustrates what to avoid.

**Examples:**
```csharp
<!-- invalid:struct-not-supported -->
```csharp
[KnockOff<MyStruct>]  // KO1001: Structs cannot be stubbed
public partial class MyTests { }
```
<!-- /snippet -->
```

---

## `<!-- generated:{path}#L{start}-L{end} -->` - Source Generator Output

**Definition:** Actual output from a source generator, referenced by file path and line numbers.

**When to use:**
- Showing what a generator produces
- Documenting generated API shapes
- Explaining generated code structure

**Key principle:** Line numbers enable drift detection - when verification runs, mismatches signal the generator changed.

**Example:**
```markdown
<!-- generated:Samples.DomainModel/Generated/PersonFactory.g.cs#L15-L22 -->
```csharp
public interface IPersonFactory
{
    IPerson Create();
    Task<IPerson> Fetch(int id);
}
```
<!-- /snippet -->
```

---

## `<!-- pseudo:{description} -->` - Truly Illustrative Only

**Definition:** Code fragments or conceptual illustrations NOT meant to compile because they are inherently incomplete.

**When to use - VERY LIMITED:**

1. **API signatures** - Interface definitions, method signatures shown for reference
   ```csharp
   Task WaitForTasks(CancellationToken? token = null);
   bool IsValid { get; }
   ```

2. **Incomplete fragments** - Property names without complete statements
   ```csharp
   knockOff.Indexer         // just showing the property exists
   knockOff.Indexer.Backing // just showing the property exists
   ```

3. **Hypothetical/future features** - Features not yet implemented
   ```csharp
   // Hypothetical - NOT YET IMPLEMENTED
   [KnockOff(Strict = true)]
   ```

**When NOT to use:**
- Code from other libraries (Moq, NSubstitute) - these ARE compilable
- Code that "just isn't in samples yet" - add it to samples
- Complete, valid C# statements - compile them
- Usage examples - compile them
- Database operation placeholders - see "No Commented Code in Snippets" below

**Key principle:** If you could paste it into a .cs file and it would compile (with appropriate usings/references), it's NOT pseudo-code.

---

## Common Mistakes

### Mistake 1: Marking Moq Code as Pseudo

**Wrong:** Treating Moq examples as pseudo-code because "it's a different library"
```markdown
<!-- pseudo:moq-example -->  ❌ WRONG
```

**Correct:** Add Moq package reference to samples, compile the code
```markdown
snippet: moq-setup-example  ✅ CORRECT
```

### Mistake 2: "Not in Samples Yet"

**Wrong:** Using pseudo-code as a shortcut for code not yet added to samples
```markdown
<!-- pseudo:usage-pattern -->  ❌ WRONG - it's compilable code
```

**Correct:** Add to samples first, then reference
```markdown
snippet: usage-pattern  ✅ CORRECT
```

### Mistake 3: Complete Statements as Pseudo

**Wrong:** Marking complete, compilable statements as pseudo
```markdown
<!-- pseudo:callback-example -->
var stub = new ServiceStub();
stub.Method.OnCall = (ko) => result;  ❌ This compiles!
```

**Correct:** If it compiles, it should be compiled
```markdown
snippet: callback-example  ✅ Add to samples
```

### Mistake 4: "The Types Don't Exist"

**Wrong:** Using pseudo because supporting types aren't in samples yet
```markdown
<!-- pseudo:user-service-example -->  ❌ WRONG
var stub = new UserServiceStub();
stub.GetUser.OnCall = (ko, id) => new User { Id = id };
```

**Correct:** Create placeholder types in samples, then compile
```csharp
// In samples project - create what you need:
public class User { public int Id { get; set; } }
public interface IUserService { User GetUser(int id); }
[KnockOff] public partial class UserServiceStub : IUserService { }

#region user-service-example
var stub = new UserServiceStub();
stub.GetUser.OnCall = (ko, id) => new User { Id = id };
#endregion
```

**The samples project exists to make documentation code real.** If your example needs `IUserService`, `EmailService`, or `ICalculator` - create them. Simple placeholder interfaces and classes are fine. The goal is compiled, tested examples.

---

## No Commented Code in Snippets

**Compiled snippets must not contain commented-out code.** Comments showing "what the real code would look like" completely defeat the purpose of having compiled, tested samples.

### The Problem

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

This snippet compiles, but the actual persistence code is hidden in comments. If the EF Core API changes, the comments become wrong and nobody notices.

### Acceptable Comments in Snippets

| Type | Example | Why OK |
|------|---------|--------|
| Result annotations | `var total = x.Total; // 50.00` | Shows expected value |
| Anti-pattern labels | `// WRONG - don't do this` | Explicit warning |
| Brief explanations | `// Triggers validation` | Clarifies non-obvious behavior |
| Section markers | `// Setup` / `// Act` / `// Assert` | Test organization |

### Unacceptable Comments in Snippets

| Type | Example | Why Bad |
|------|---------|---------|
| Database placeholders | `// await db.SaveChangesAsync();` | Not compiled/tested |
| "Real code" comments | `// In real implementation: ...` | Defeats the purpose |
| Behavior via comments | `// item.IsNew = true` | Should be an assertion |
| Hypothetical code | `// You could also do: ...` | Add it or don't |

### Solution: Write Real Code or Use Pseudo

If the code can't be compiled (e.g., requires a real database), you have two options:

1. **Create a testable abstraction** - Mock the database, use in-memory provider
2. **Use pseudo marker** - Be honest that it's illustrative, not tested

```markdown
<!-- pseudo:persistence-pattern -->
```csharp
[Insert]
public async Task Insert(PersonEntity entity)
{
    db.Persons.Add(entity);
    await db.SaveChangesAsync();
}
```
<!-- /snippet -->
```

The pseudo marker is honest: this code isn't compiled. Readers know to verify it themselves.
