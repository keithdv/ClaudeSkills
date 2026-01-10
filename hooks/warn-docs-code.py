#!/usr/bin/env python3
"""
Hook to warn about writing code directly in documentation files.

Prevents the anti-pattern:
  Writing code examples directly in docs instead of docs/samples/

Triggers on: Write/Edit to docs/*.md files
Action: WARN (not block) when detecting code blocks in documentation
"""

import json
import sys
import re


def is_docs_markdown(file_path: str) -> bool:
    """Check if this is a markdown file in a docs directory."""
    return '/docs/' in file_path and file_path.endswith('.md')


def check_for_code_blocks(content: str) -> tuple[bool, str]:
    """
    Returns (should_warn, reason) if content has substantial code blocks.
    """

    # Find code blocks with language specifiers
    code_blocks = re.findall(
        r'```(?:csharp|cs|python|py|typescript|ts|javascript|js|java|go|rust)\n(.*?)```',
        content,
        re.DOTALL | re.IGNORECASE
    )

    if not code_blocks:
        return False, ""

    # Check if code blocks contain substantial code (not just 1-2 lines of pseudocode)
    substantial_blocks = []
    for block in code_blocks:
        lines = [l for l in block.strip().split('\n') if l.strip() and not l.strip().startswith('//')]
        if len(lines) >= 3:
            substantial_blocks.append(block)

    if substantial_blocks:
        return True, f"Found {len(substantial_blocks)} code block(s) with 3+ lines"

    return False, ""


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = input_data.get('tool_input', {})
    file_path = tool_input.get('file_path', '')

    # Only check docs markdown files
    if not is_docs_markdown(file_path):
        sys.exit(0)

    # Get the content being written/edited
    content = tool_input.get('content', '')  # For Write
    new_string = tool_input.get('new_string', '')  # For Edit

    check_content = content or new_string
    if not check_content:
        sys.exit(0)

    should_warn, reason = check_for_code_blocks(check_content)

    if should_warn:
        # Exit 0 = allow but with warning
        print(f"""
┌──────────────────────────────────────────────────────────────────┐
│  WARNING: Code blocks in documentation file                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  {reason:<60}  │
│                                                                  │
│  REMINDER: Documentation Code Examples workflow:                 │
│                                                                  │
│  1. Add code to docs/samples/ projects first (so it compiles)    │
│  2. Mark with #region docs:{{target}}:{{id}}                         │
│  3. Run extract-snippets script to sync to docs                  │
│                                                                  │
│  Never write code directly in documentation - always source      │
│  from compiled samples to ensure examples actually work.         │
│                                                                  │
│  If this is pseudocode/illustration, proceed.                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
""", file=sys.stderr)

    # Always allow (exit 0), this is just a warning
    sys.exit(0)


if __name__ == '__main__':
    main()
