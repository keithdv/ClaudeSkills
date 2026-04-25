# Framework-Correctness Rubric — zTreatment

Project-specific check list loaded by the code-reviewer in addition to `rubric.md` Section 5 when the active project is zTreatment. The base rubric stays framework-agnostic; the zTreatment idioms live here so other projects don't inherit them.

## Idioms to verify

### Neatoo

- `EntityBase` / `ValidateBase` / `ValidateListBase` / `EntityListBase` used correctly per aggregate
- State flag names: `IsModified` (NOT `IsDirty`), `IsValid`, `IsSelfValid`, `IsSavable`, `IsNew`, `IsDeleted`
- Validation and reactive logic via `AddValidation` / `AddValidationAsync` / `AddAction` / `AddActionAsync` / class-based rules — never `if/else` in `.razor` driving business outcomes
- Computed properties live in the domain model, not in code-behind
- Lazy load via `EntityLazyLoad` / `IEntityLazyLoadFactory` when crossing the deferred-load boundary

### RemoteFactory

- `[Factory]` on the factory class, `[Create]` / `[Fetch]` / `[Remote]` / `[Execute]` / `[Service]` / `[AuthorizeFactory]` / `[AspAuthorize]` placed correctly
- `ServerOnly` and `RaiseOptions` set appropriately for factory events
- Save routing respects the 3-tier client/server boundary; no client-side reach into server-only services

### KnockOff

- Strict mode on factories, services, repositories
- Loose on entities (so partial-property tracking works)
- `Return` / `ThenReturn` / `Call` / `ThenCall` for setup; `Verify` / `VerifyAll` for assertions
- Existing stubs reused before creating new inline stubs (per `knockoff` skill)

### EF Core + PostgreSQL

- `.ToUtcForDb()` on every `DateTime` saved to the database
- `IRepositoryTransaction` for transactions — no raw `BeginTransaction()`
- Repository `Include` patterns match the aggregate's read needs; no N+1 in hot paths
- Migrations explicit, not implicit

### Exception handling

- Every `catch` logs `ex` (not just a message)
- Razor pages do NOT catch RemoteFactory exceptions — the centralized handler does
- No silent swallows

### Forbidden patterns

- No `System.Reflection` / `Type.GetMethod()` / `MethodInfo.Invoke()` (no reflection rule, per CLAUDE.md)
- No casting an interface to its concrete type (interface-completeness rule)

### NuGet

- Versions checked against `nuget.org` registration endpoints only — never `flatcontainer`, never inferred from local builds or sibling repos

## Grade calibration for this project

A single material violation of any item above is automatic C in Framework Correctness (per base rubric §5). One minor deviation (a missing XML comment, a non-load-bearing attribute omitted on code that works anyway) is B. Clean across all items is A.

If `docs/code-review-calibration.md` overrides any specific item (e.g., flags it as out-of-scope for the team's current iteration), the calibration wins.
