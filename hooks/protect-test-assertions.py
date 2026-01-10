#!/usr/bin/env python3
"""
Hook to protect test assertions from being removed or gutted.

Prevents the anti-pattern:
  Tests fail → Remove/comment assertions → Tests "pass"

Triggers on: Edit to test files
Action: BLOCK when removing assertions or test attributes
"""

import json
import sys
import re


def is_test_file(file_path: str) -> bool:
    """Check if this is a test file."""
    test_indicators = [
        '/Unit/',
        '/Tests/',
        '/Test/',
        'Test.cs',
        'Tests.cs',
        '_test.py',
        '_tests.py',
        '.test.ts',
        '.test.js',
        '.spec.ts',
        '.spec.js',
    ]
    return any(indicator in file_path for indicator in test_indicators)


def check_assertion_removal(old_string: str, new_string: str) -> tuple[bool, str]:
    """
    Returns (should_block, reason) if assertions are being removed.
    """

    # Patterns that indicate test assertions or test structure
    assertion_patterns = [
        r'\bAssert\.\w+',           # Assert.Equal, Assert.True, etc.
        r'\b\.Should\w*\(',         # FluentAssertions
        r'\bExpect\(',              # Jest/JS
        r'\bassert\s+',             # Python assert
        r'\[Fact\]',                # xUnit
        r'\[Theory\]',              # xUnit
        r'\[Test\]',                # NUnit
        r'\[TestMethod\]',          # MSTest
        r'@Test\b',                 # Java JUnit
        r'\bit\(',                  # Jest/Mocha
        r'\bdescribe\(',            # Jest/Mocha
    ]

    old_lower = old_string.lower()
    new_lower = new_string.lower()

    for pattern in assertion_patterns:
        old_matches = len(re.findall(pattern, old_string, re.IGNORECASE))
        new_matches = len(re.findall(pattern, new_string, re.IGNORECASE))

        if old_matches > new_matches:
            return True, f"Removing {pattern} ({old_matches} → {new_matches})"

    # Check for commenting out test code
    # If old has code and new has that code commented out
    if '//' + old_string.strip() in new_string or '// ' + old_string.strip() in new_string:
        return True, "Commenting out test code instead of fixing it"

    # Check for removing entire test methods
    test_method_pattern = r'public\s+(async\s+)?Task\s+\w+\s*\('
    old_methods = len(re.findall(test_method_pattern, old_string))
    new_methods = len(re.findall(test_method_pattern, new_string))
    if old_methods > 0 and new_methods < old_methods:
        return True, f"Removing test methods ({old_methods} → {new_methods})"

    return False, ""


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = input_data.get('tool_input', {})
    file_path = tool_input.get('file_path', '')

    # Only check test files
    if not is_test_file(file_path):
        sys.exit(0)

    # For Edit tool, check old_string vs new_string
    old_string = tool_input.get('old_string', '')
    new_string = tool_input.get('new_string', '')

    if not old_string:
        sys.exit(0)

    should_block, reason = check_assertion_removal(old_string, new_string)

    if should_block:
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  BLOCKED: Test assertion removal detected                        ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  {reason[:60]:<60}  ║
║                                                                  ║
║  EXISTING TESTS ARE SACRED!                                      ║
║                                                                  ║
║  What counts as "gutting" a test (NEVER do these):               ║
║  - Removing or commenting out assertions                         ║
║  - Removing test cases or edge cases                             ║
║  - Changing expected values to match broken behavior             ║
║  - Commenting out or deleting tests                              ║
║                                                                  ║
║  If a test is failing, STOP and ASK:                             ║
║  1. Should I fix the underlying issue?                           ║
║  2. Add this to the bug list?                                    ║
║  3. Is this expected breakage from my changes?                   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""", file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == '__main__':
    main()
