#!/usr/bin/env python3
"""
Hook to detect and block test doubles that copy production logic.

This prevents the anti-pattern:
  "Code isn't testable → Copy logic into test double → Test the copy"

Triggers on: Write/Edit to test files
Blocks when: Detects patterns indicating copied production logic
"""

import json
import sys
import re

def check_for_copied_logic(content: str, file_path: str) -> tuple[bool, str]:
    """
    Returns (should_block, reason) if the content appears to copy production logic.
    """

    # Pattern 1: Explicit "copied from" comments
    copied_patterns = [
        r'copied\s+from',
        r'copy\s+of',
        r'duplicated?\s+from',
        r'same\s+as\s+production',
        r'mirrors?\s+the\s+(real|actual|production)',
    ]

    for pattern in copied_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True, f"Contains comment indicating copied logic (pattern: '{pattern}')"

    # Pattern 2: Private class named *TestDouble* with method implementations
    # This catches: private class FooTestDouble { public bool Method() { return x != y; } }
    test_double_with_logic = re.search(
        r'private\s+class\s+\w*TestDouble\w*\s*\{[^}]*(?:public|private|protected)\s+\w+\s+\w+\s*\([^)]*\)\s*(?:=>|{)',
        content,
        re.IGNORECASE | re.DOTALL
    )
    if test_double_with_logic:
        return True, "Contains a TestDouble class with method implementations - this may be copying production logic"

    # Pattern 3: Test file creating a class that reimplements interface methods with actual logic
    # Look for: private class X { ... return ... != ... } patterns
    private_class_with_returns = re.search(
        r'private\s+class\s+\w+\s*\{[^}]*return\s+[^;]+\s*[!=<>]+\s*[^;]+;',
        content,
        re.DOTALL
    )
    if private_class_with_returns:
        return True, "Contains a private class with return statements that include comparison logic - may be copying production logic"

    return False, ""


def main():
    # Read tool input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # Can't parse input, allow the operation
        sys.exit(0)

    tool_input = input_data.get('tool_input', {})
    file_path = tool_input.get('file_path', '')

    # Only check test files
    if '/Unit/' not in file_path and '/Tests/' not in file_path and 'Test' not in file_path:
        sys.exit(0)

    # Get the content being written/edited
    content = tool_input.get('content', '')  # For Write
    new_string = tool_input.get('new_string', '')  # For Edit

    check_content = content or new_string
    if not check_content:
        sys.exit(0)

    should_block, reason = check_for_copied_logic(check_content, file_path)

    if should_block:
        # Exit code 2 = block the operation
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  BLOCKED: Possible copied production logic detected              ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  {reason[:60]:<60}  ║
║                                                                  ║
║  STOP! This may violate the testing principle:                   ║
║  "Test production code, not copies of it"                        ║
║                                                                  ║
║  Before proceeding, ask yourself:                                ║
║  - Am I testing the REAL production code?                        ║
║  - Or am I testing a copy that won't catch real bugs?            ║
║                                                                  ║
║  If you hit an obstacle (code isn't testable), STOP and ASK:     ║
║  1. Can the production code be refactored for testability?       ║
║  2. Should this be an integration test instead?                  ║
║  3. Is there a KnockOff pattern that works?                      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""", file=sys.stderr)
        sys.exit(2)

    # Exit 0 = allow the operation
    sys.exit(0)


if __name__ == '__main__':
    main()
