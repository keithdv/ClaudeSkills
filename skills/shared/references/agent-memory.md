# Agent Memory Files — Shared Pattern

Agent memory files store private working state for each agent participating in a workflow. This keeps plan files focused on design and prevents bloat from accumulating workflow artifacts.

## Directory Convention

Each plan has a companion memory directory named `{plan-name}.memory/` alongside the plan file. The specific agents vary by workflow — see the skill's SKILL.md for the agent list and content location table.

## Key Rules

1. **Plan = shared design document.** All agents read it. Contains ONLY the design — what to build and why.
2. **Memory = private notes for the agent's own future self.** Only that agent and the orchestrator read it.
3. **Agents must NOT read each other's memory files.** The orchestrator mediates all cross-agent communication.
4. **Orchestrator relays cross-agent information via spawn prompts.** When the developer raises concerns, the orchestrator reads `developer.md`, extracts the concerns, and includes them in the architect's spawn prompt. The architect never opens `developer.md`.
5. **Memory format: curated summary** — not an append-only log. The agent rewrites the file each run, keeping only what's still relevant.
6. **Agents create the memory directory and their file** the first time they write. Use the Write tool — the directory is created automatically.

## Memory File Base Format

Each memory file follows this base format, plus agent-specific sections:

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

## [Agent-Specific Sections]
[See the workflow skill for required sections per agent]
```

**Format rules:**
- Curated summary, not append-only log — rewrite each run
- Keep only what's still relevant for future runs of THIS agent
- Include corrections and user overrides prominently

## Orchestrator Responsibilities

When spawning agents, the orchestrator MUST:

1. **Include the memory file path** in the spawn prompt: "Write your findings to `docs/plans/{plan-name}.memory/{agent}.md`"
2. **Relay cross-agent context** when needed: Read the relevant memory file and include extracted information in the spawn prompt — agents never read each other's files
3. **Check memory files for routing decisions**: After an agent completes, read its memory file to determine the next workflow step (verdict, concerns, evidence)

When resuming mid-workflow:

1. Read the plan status to determine which step is current
2. Read the relevant agent memory file(s) to understand the details (what was the concern, what evidence was collected, what was the verdict)
3. Include relevant context from memory files in the fresh agent's spawn prompt
