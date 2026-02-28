# [Plan Title]

**Date:** YYYY-MM-DD
**Related Todo:** [Link to todo file]
**Status:** Draft | Under Review | Approved | In Progress | Awaiting Verification | Sent Back | Complete
**Last Updated:** YYYY-MM-DD

---

## Overview

[What this plan accomplishes visually. Reference the todo's visual description.]

---

## Component Strategy

[Which MudBlazor components to use and why. Layout approach (MudGrid, MudStack, MudContainer, etc.).]

### New Components

- [Component name and purpose]

### Modified Components

- [Component name and what changes]

---

## CSS Strategy

[CSS approach following project priorities: MudBlazor utilities first, scoped CSS second, global CSS last.]

- **MudBlazor classes:** [List any MudBlazor utility classes planned]
- **Scoped CSS:** [Any component-specific styles needed]
- **Global CSS:** [Only if truly global changes are needed — justify why]

---

## Layout & Responsive Considerations

[Spacing, alignment, breakpoint behavior. How the layout adapts at different sizes if relevant.]

---

## Implementation Steps

1. [ ] Step description
   - Files: `path/to/file.razor`
   - Details: ...

2. [ ] Step description
   - Files: `path/to/file.razor.css`
   - Details: ...

---

## Visual Acceptance Criteria

- [ ] [Specific visual check — what the user should see]
- [ ] [Layout/spacing requirement]
- [ ] [Component behavior requirement]
- [ ] [Matches legacy screen (if applicable) — with noted divergences]

---

## Testing

- [ ] `dotnet build` passes
- [ ] Visual inspection matches acceptance criteria
- [ ] No regressions in related pages
- [ ] E2E tests (if applicable): [list specific tests or "N/A"]

---

## Backend Prerequisites (Optional)

[List any backend changes needed before UI implementation can proceed. Remove this section if none are needed.]

[If the changes involve more than 2-3 entities or require new aggregates or complex business rules, this UI todo is too large — use project-todos for the backend portion instead.]

- [ ] [Change description — e.g., "Add MiddleName property to IPatient interface and implementation"]
  - Files: [expected files to change]
  - Tests: [expected test changes]

**Developer Agent Results:**
- **Completed:** [date or "Pending"]
- **Files Changed:** [list]
- **Tests Added:** [list]
- **Test Results:** [all passing / failures]

---

## Dependencies

[Other components or data requirements. Note any dependencies on the Backend Prerequisites above.]

---

## Risks / Considerations

[MudBlazor version constraints, browser compatibility, performance concerns, etc.]

---

## Implementation Progress

**Started:** [date]
**Agent:** [UI agent]

### Milestone: [Name]
- Status: Not Started | In Progress | Complete
- Files changed:
  - `path/to/file`
- Notes:

---

## Completion Evidence

[Implementation agent fills this section, then sets status to "Awaiting Verification".]

**Reported:** [date]

- **Build:** [dotnet build output or summary]
- **Files Changed:** [List all files created or modified]
- **Visual State:** [Description of what the UI looks like now]
- **All Plan Steps:** [Confirmed complete]

---

## Verification

[Fresh UI agent fills this section after independent review.]

**Verified:** [date]
**Verdict:** VERIFIED | SENT BACK

### Review Findings

- **Visual correctness:** [Does the UI match the acceptance criteria?]
- **MudBlazor usage:** [Follows project patterns?]
- **CSS quality:** [Follows priority order? No unnecessary global styles?]
- **Component patterns:** [Clean, idiomatic Blazor?]
- **Build:** [Independent build result]
- **Regressions:** [Any issues in related pages?]

### Issues

[List specific issues if SENT BACK, or "None" if VERIFIED]
