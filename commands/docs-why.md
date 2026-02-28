---
name: docs-why
description: Interactive documentation improvement - ask the domain expert "why" questions, then write prose from their answers
argument-hint: "<filepath> - e.g., docs/factory-operations.md"
allowed-tools: ["Glob", "Grep", "Read", "Edit", "Write", "AskUserQuestion"]
---

Improve documentation by extracting "why" knowledge from the domain expert (the user).

## The Problem This Solves

AI-generated documentation tends to be technically accurate but missing the *why* — the design motivations, trade-offs, and real-world reasoning that help readers understand and use the library. The domain expert knows this, but they're not documentation writers. This workflow bridges the gap: Claude asks targeted questions, the user answers from their knowledge, and Claude writes the prose.

## Process

### 1. Read the Target Document

Read the file specified in the argument. If no argument, ask the user which file to improve.

Read the full document and identify sections that:
- Jump straight to code without explaining the problem being solved
- Use vague descriptions like "supports X" without saying *why you'd want X*
- Describe *what* the code does without explaining the *design decision*
- Have disconnected code examples with no narrative connecting them

### 2. Ask "Why" Questions

For each section that needs improvement, ask the user **targeted questions** using AskUserQuestion. Questions should:
- Be specific, not open-ended ("Why does Fetch return bool instead of throwing?" not "Tell me about Fetch")
- Offer 2-3 concrete answer options to make it easy for the user to respond (they can always type their own)
- Group into batches of 2-3 questions at a time (not too many at once)
- Focus on design decisions, trade-offs, and real-world motivation

Good question patterns:
- "Why does X work this way instead of [obvious alternative]?"
- "When would a developer choose X over Y?"
- "What problem does X solve that [simpler approach] doesn't?"
- "What's the real-world scenario where this matters?"

### 3. Write Improved Prose

After each batch of answers, draft the improved prose for those sections. Keep these principles:

**Persistence routing framing (for RemoteFactory repos):**
- Frame around what the library *does for you*, not what it *generates*
- Lead with the problem being solved, then the solution
- "RemoteFactory routes/handles/manages X" not "The source generator produces X"

**General documentation principles:**
- One or two sentences of "why" before each code block
- Show first, explain second (but the "why" comes before the code)
- Each section should answer one question the reader has
- Be honest about advanced/optional features: "Most developers won't need this initially"
- Don't explain basic language concepts to expert developers
- Specific > vague: "tracks deleted items for server-side persistence" not "supports batch operations"

**What to preserve:**
- All MarkdownSnippets placeholder blocks (<!-- snippet: --> / <!-- endSnippet -->) — never modify these
- The existing code samples — only change the prose around them
- The overall page structure/ordering unless the user agrees to restructure

### 4. Show the Draft

After writing the improved prose, summarize what changed and let the user review. Be specific:
- "Added 'why' paragraph to the Fetch section explaining the two-step design"
- "Reframed intro from 'supports 7 operations' to 'persistence routing engine'"

### 5. Iterate

The user may:
- Correct something ("that's not quite right, the real reason is...")
- Want to go deeper ("ask me about the Collections section too")
- Be satisfied and want to move to the next page

Continue the ask-write-review cycle until the user is done.

## Key Insight

The user is the domain expert. They know *why* every design decision was made — they just haven't written it down. Claude's job is to ask the right questions to extract that knowledge, then structure it into clear prose. Don't guess at motivations; ask.
