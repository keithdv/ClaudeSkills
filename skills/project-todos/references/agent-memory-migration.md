# Agent Memory Migration Guide

**Skill version:** 2.1.0
**Breaking change from 1.x:** Yes — agents must write workflow state to memory files, not plan sections.
**Change from 2.0:** Non-breaking — agents must move memory file loading to REQUIRED FIRST STEP position in system prompt.

## What Changed

The plan template was split into two concerns:

| Before (v1) | After (v2) |
|-------------|------------|
| Plan file had design + workflow state (~376 lines) | Plan file has design only (~190 lines) |
| Agents wrote reviews, contracts, progress, evidence, verification to plan sections | Agents write workflow state to per-plan, per-agent memory files |
| Agents could read each other's work in the plan | Agents cannot read each other's memory files — orchestrator mediates |

### Memory File Structure

```
docs/plans/
├── feature-name-plan.md              # Design only — shared
└── feature-name-plan.memory/
    ├── architect.md                   # Architect's private notes
    ├── developer.md                   # Developer's private notes
    ├── requirements-reviewer.md       # Reviewer's private notes
    └── requirements-documenter.md     # Documenter's private notes
```

---

## What Each Agent Needs

Every project-specific agent that participates in the project-todos workflow needs two additions:

### 1. REQUIRED FIRST STEP Section (v2.1)

Add this section **immediately after the one-sentence role description** — before modes of work, expertise, context inheritance, or any other section. This is the agent's first operational instruction.

```markdown
## REQUIRED FIRST STEP

Before taking any other action, find your memory file:

1. Find the plan file path in your task context (e.g., `docs/plans/foo-bar-plan.md`)
2. Strip the `.md` extension, append `.memory/[your-agent-name].md`
   Example: plan at `docs/plans/foo-bar-plan.md` → memory at `docs/plans/foo-bar-plan.memory/architect.md`
3. Check if this file exists. If it does, read it completely before proceeding — it contains your prior work on this plan
4. If it does not exist, proceed with a fresh start

All workflow state goes in this memory file — not the plan. Create it with the Write tool the first time you need to write.

Do NOT read other agents' memory files. The orchestrator relays cross-agent information in your spawn prompt.
```

The Memory File Structure template can remain later in the agent file — only the operational "find and read" instruction needs to be at the top.

### 2. Updated References

Replace all references to writing plan sections with writing to memory files:

| Find (v1) | Replace with (v2) |
|-----------|-------------------|
| "Fill in the plan's [section]" | "Write [content] to your agent memory file" |
| "Write to the plan's [section]" | "Write to your agent memory file" |
| "Read the plan's Completion Evidence" | "Review the developer's completion evidence (relayed in your spawn prompt)" |
| "Update the plan's Documentation section" | "Write documentation tracking to your agent memory file" |
| "Read the plan's Requirements Verification" | Check spawn prompt or "read your agent memory file" |

---

## Agent-Specific Migration Checklist

### Developer Agent

**Memory file:** `developer.md`

**Sections to include in memory file structure:**
- Developer Review (status, assertion trace table, concerns)
- Implementation Contract (scope, gates, stop conditions, test scenario mapping)
- Implementation Progress (milestones)
- Completion Evidence (test results, contract status)

**Key updates:**
- [ ] Add Agent Memory File section with developer-specific structure
- [ ] Plan review verdict → write to memory file, not plan
- [ ] Implementation contract → write to memory file, not plan
- [ ] Implementation progress → write to memory file, not plan
- [ ] Completion evidence → write to memory file, not plan
- [ ] "Update the plan with your review" → "Write your review to your agent memory file"
- [ ] On resume: read own memory file for prior context (corrections, mistakes)

### Architect Agent

**Memory file:** `architect.md`

**Sections to include in memory file structure:**
- Architectural Verification (pre-handoff: scope table, evidence, breaking changes)
- Architect Verification (post-implementation: verdict, test results, design match)

**Key updates:**
- [ ] Add Agent Memory File section with architect-specific structure
- [ ] Pre-handoff verification → write to memory file, not plan
- [ ] Post-implementation verification → write to memory file, not plan
- [ ] "Read the plan's Completion Evidence" → "Review developer's evidence (relayed in spawn prompt)"
- [ ] Report verdict location: "Verdict in my memory file at [path]"

### Requirements Reviewer Agent

**Memory file:** `requirements-reviewer.md`

**Sections to include in memory file structure:**
- Requirements Verification (verdict, compliance table, side effects, issues)

**Key updates:**
- [ ] Add Agent Memory File section (Mode 2 only — Mode 1 still writes to todo)
- [ ] Post-implementation verification → write to memory file, not plan
- [ ] "Fill in the Requirements Verification section of the plan" → "Write verification findings to your agent memory file"
- [ ] Report verdict location: "Verdict in my memory file at [path]"

**Note:** Mode 1 (pre-design review) is unchanged — it writes to the todo's Requirements Review section, which is not a plan section.

### Requirements Documenter Agent

**Memory file:** `requirements-documenter.md`

**Sections to include in memory file structure:**
- Documentation Tracking (expected deliverables, developer deliverables, files updated)

**Key updates:**
- [ ] Add Agent Memory File section with documenter-specific structure
- [ ] "Record all work in the plan's Documentation section" → "Write documentation tracking to your agent memory file"
- [ ] "Read the plan's Completion Evidence" → "Review developer's evidence (relayed in spawn prompt)"
- [ ] "Read the plan's Requirements Verification" → receive verdict via spawn prompt
- [ ] Developer Deliverables → list in memory file for orchestrator to route

---

## Memory File Base Format

Every memory file starts with this base format. Agents add their role-specific sections after it.

```markdown
# [Agent Role] — [Plan Name]

Last updated: YYYY-MM-DD
Current step: [what this agent is doing or last did]

## Key Context
[Curated summary — decisions, corrections, discoveries
that matter for the next fresh run of THIS agent]

## Mistakes to Avoid
[Things this agent got wrong and was corrected on]

## User Corrections
[Direct quotes/paraphrases of user overrides]
```

**Format rules:**
- Curated summary, not append-only log — rewrite each run
- Keep only what's still relevant for future runs of THIS agent
- Include corrections and user overrides prominently

---

## Key Rules (for agent instructions)

Include these rules in each agent's memory file section:

1. **Plan = shared design.** All agents read it. Contains ONLY design.
2. **Memory = private notes.** Only this agent and the orchestrator read it.
3. **Never read other agents' memory files.** Orchestrator mediates.
4. **Create directory on first write.** The Write tool handles this automatically.
5. **Curated, not append-only.** Rewrite each run with only relevant content.

---

## v2.1 Migration: REQUIRED FIRST STEP Placement

**Problem:** In v2.0, the migration guide said to add the Agent Memory File section "after the agent's Context Inheritance or introductory section." This placed it after expertise lists, mode descriptions, and other content — often 50-70+ lines into the system prompt. Agents frequently ignored the memory file instructions because they had already committed to an approach by the time they reached them.

**Fix:** Move memory file loading to a `## REQUIRED FIRST STEP` section immediately after the one-line role description — before modes of work, expertise, context inheritance, or any other section.

### v2.1 Migration Checklist

For each project-specific agent that participates in the workflow:

- [ ] Find the `## Agent Memory File` section (wherever it currently lives)
- [ ] Delete it from its current location
- [ ] Add `## REQUIRED FIRST STEP` immediately after the agent's one-sentence role description
- [ ] Use the template from `~/.claude/skills/shared/references/agent-memory.md` (Agent System Prompt Placement section)
- [ ] Keep the Memory File Structure template where it was (or move it to a later section) — only the operational "check and read" instruction needs to be at the top
- [ ] Verify the agent's system prompt now reads: role → REQUIRED FIRST STEP → modes/expertise → everything else

### What Changed in Agent System Prompt Order

| Before (v2.0) | After (v2.1) |
|----------------|--------------|
| Role description | Role description |
| Modes of work | **REQUIRED FIRST STEP** (memory file check) |
| Core expertise (often 30+ lines) | Modes of work |
| Context inheritance | Core expertise |
| Agent Memory File section | Context inheritance |
| Memory File Structure | Memory File Structure |

---

## Compatibility

### Existing Plans

Plans created before v2.0.0 have workflow sections in the plan file. Agents should:
- Read workflow state from the plan if no memory file exists
- Write new workflow state to memory files going forward
- Do not migrate old plan sections to memory files — the plan is already in progress

### New Plans

Plans created after v2.0.0 use the slimmed template automatically. All workflow state goes to memory files from the start.
