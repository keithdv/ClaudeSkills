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

## Agent System Prompt Placement (v2.1)

The memory file check must be the agent's **first operational instruction** — immediately after the one-line role description and before any expertise, modes-of-work, or context-inheritance sections. Burying it later in the system prompt leads to agents ignoring it.

### Required Structure

```markdown
# [Agent Name]

[One-sentence role description.]

## REQUIRED FIRST STEP

Your memory file contains your prior work on this plan — decisions made, mistakes corrected, user overrides received. Without it you will repeat work, repeat mistakes, and contradict prior user decisions.

1. Find the plan file path in your task context (e.g., `docs/plans/foo-bar-plan.md`)
2. Derive your memory file path: strip `.md`, append `.memory/[your-agent-name].md`
   Example: `docs/plans/foo-bar-plan.md` → `docs/plans/foo-bar-plan.memory/architect.md`
3. Read this file. If it exists, it is as essential as the plan itself — read it completely before doing anything else
4. If it does not exist, this is your first run on this plan — proceed fresh and create the memory file when you first need to write workflow state

All workflow state goes in this memory file — not the plan. Do NOT read other agents' memory files.

## [Modes of Work / Core Expertise / etc.]
[Rest of system prompt...]
```

### Why This Placement Matters

- The agent knows *who it is* (role description) when it reads the instruction, giving it context
- The derivation is mechanical — no placeholder inference, just path manipulation from the plan path that's always in the spawn prompt
- The memory file is framed as essential (like the plan), not optional — skipping it has visible consequences (repeated work, repeated mistakes, contradicted user decisions)
- The instruction fires before the agent has committed to an approach
- This makes agents self-sufficient — they find their memory file regardless of what the orchestrator includes in the spawn prompt

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
