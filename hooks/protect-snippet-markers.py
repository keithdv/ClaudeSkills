#!/usr/bin/env python3
"""
Hook to prevent snippet markers from being removed or modified in documentation.

Snippets are synced from docs/samples/ projects via extract-snippets.ps1.
Modifying snippet content directly in docs defeats the purpose of compiled samples.

Triggers on: Edit to files containing snippet markers
Action: BLOCK if snippet markers are being removed/modified without removing entire snippet
"""

import json
import sys
import re


def find_snippet_markers(content: str) -> list[tuple[str, int, int]]:
    """
    Find all snippet markers in content.
    Returns list of (snippet_id, start_pos, end_pos) for complete snippets.
    """
    snippets = []

    # Pattern for complete snippet blocks
    pattern = r'(<!-- snippet: ([^\s]+) -->.*?<!-- /snippet -->)'

    for match in re.finditer(pattern, content, re.DOTALL):
        snippet_id = match.group(2)
        snippets.append((snippet_id, match.start(), match.end()))

    return snippets


def find_orphaned_markers(content: str) -> list[str]:
    """
    Find snippet markers that don't have a matching closing tag.
    """
    orphaned = []

    # Find opening markers
    opening_pattern = r'<!-- snippet: ([^\s]+) -->'
    closing_pattern = r'<!-- /snippet -->'

    openings = list(re.finditer(opening_pattern, content))
    closings = list(re.finditer(closing_pattern, content))

    # Check for unmatched openings (more openings than closings, or opening after all closings)
    if len(openings) != len(closings):
        for match in openings:
            orphaned.append(match.group(1))

    return orphaned


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get('tool_name', '')
    tool_input = input_data.get('tool_input', {})

    # Only check Edit operations
    if tool_name != 'Edit':
        sys.exit(0)

    file_path = tool_input.get('file_path', '')
    old_string = tool_input.get('old_string', '')
    new_string = tool_input.get('new_string', '')

    if not old_string:
        sys.exit(0)

    # Check if old_string contains snippet markers
    old_has_opening = '<!-- snippet:' in old_string
    old_has_closing = '<!-- /snippet -->' in old_string
    new_has_opening = '<!-- snippet:' in new_string
    new_has_closing = '<!-- /snippet -->' in new_string

    # Case 1: Removing entire snippet (opening + closing) - ALLOW
    if old_has_opening and old_has_closing and not new_has_opening and not new_has_closing:
        # Entire snippet being removed - this is OK
        sys.exit(0)

    # Case 2: Removing just the opening marker - BLOCK
    if old_has_opening and not new_has_opening:
        # Extract snippet ID
        match = re.search(r'<!-- snippet: ([^\s]+) -->', old_string)
        snippet_id = match.group(1) if match else 'unknown'

        result = {
            "decision": "block",
            "reason": f"""
BLOCKED: Snippet marker removal detected

You are removing the snippet marker for '{snippet_id}' without removing
the entire snippet block.

Snippet markers sync code from docs/samples/ projects. To modify snippet content:

1. Update the corresponding code in docs/samples/ project
   - Find the #region {snippet_id} marker
   - Modify the code there (it must compile and have tests)

2. Run the sync script:
   .\\scripts\\extract-snippets.ps1 -Update

3. The documentation will be updated automatically

If you need to REMOVE a snippet entirely:
- Remove from opening marker through closing marker (<!-- /snippet -->)
- Also remove the corresponding #region from docs/samples/

Never modify snippet content directly in documentation files.
"""
        }
        print(json.dumps(result))
        sys.exit(0)

    # Case 3: Removing just the closing marker - BLOCK
    if old_has_closing and not new_has_closing and not old_has_opening:
        result = {
            "decision": "block",
            "reason": """
BLOCKED: Snippet closing marker removal detected

You are removing a snippet closing marker (<!-- /snippet -->) which will
break the snippet sync system.

To modify snippet content:
1. Update code in docs/samples/ project
2. Run: .\\scripts\\extract-snippets.ps1 -Update

To remove a snippet entirely:
- Remove from opening marker through closing marker
"""
        }
        print(json.dumps(result))
        sys.exit(0)

    # Case 4: Modifying content between markers - WARN but allow
    if old_has_opening and new_has_opening and old_has_closing and new_has_closing:
        # Check if content between markers changed
        old_content = re.search(r'<!-- snippet:[^>]+-->(.*?)<!-- /snippet -->', old_string, re.DOTALL)
        new_content = re.search(r'<!-- snippet:[^>]+-->(.*?)<!-- /snippet -->', new_string, re.DOTALL)

        if old_content and new_content and old_content.group(1) != new_content.group(1):
            print("""
WARNING: Modifying snippet content directly

You are modifying content inside a snippet block. This content is synced
from docs/samples/ and your changes may be overwritten.

Recommended workflow:
1. Update code in docs/samples/ project (so it compiles and has tests)
2. Run: .\\scripts\\extract-snippets.ps1 -Update

Proceeding with direct edit...
""", file=sys.stderr)

    # Allow the edit
    sys.exit(0)


if __name__ == '__main__':
    main()
