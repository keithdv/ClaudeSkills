#!/usr/bin/env python3
"""
Hook to warn about commented-out code that looks like a workaround.

Prevents the anti-pattern:
  Code doesn't compile → Comment it out → Leave commented code in place

Triggers on: Write/Edit to code files
Action: WARN (not block) when detecting commented-out code patterns
"""

import json
import sys
import re


def is_code_file(file_path: str) -> bool:
    """Check if this is a code file (not markdown/docs)."""
    code_extensions = ['.cs', '.py', '.ts', '.js', '.tsx', '.jsx', '.java', '.go', '.rs']
    return any(file_path.endswith(ext) for ext in code_extensions)


def check_commented_code(content: str) -> tuple[bool, str]:
    """
    Returns (should_warn, reason) if content has suspicious commented code.
    """

    # HIGH confidence patterns - these are almost always workarounds
    workaround_patterns = [
        (r"//\s*(can'?t|cannot|doesn'?t|won'?t)\s+(compile|work|build)", "Explicit 'can't compile' comment"),
        (r"//\s*TODO:?\s*(fix|uncomment|re-?enable)", "TODO to fix commented code"),
        (r"//\s*HACK:?", "HACK comment"),
        (r"//\s*commented\s+out\s+(because|since|due)", "Explicit 'commented out because'"),
        (r"//\s*disabled\s+(because|since|due|for now)", "Explicit 'disabled because'"),
        (r"//\s*temporarily\s+(removed|disabled|commented)", "Temporary removal"),
    ]

    for pattern, reason in workaround_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True, reason

    # MEDIUM confidence - commented code that looks like valid C#
    # Multiple consecutive lines of commented-out code
    consecutive_commented = re.findall(
        r'(?:^[ \t]*//[ \t]*(?:var|return|await|if|else|for|foreach|while|try|catch|throw|new|this\.|_\w+\.|[a-z]+\.[A-Z]).*$\n?){3,}',
        content,
        re.MULTILINE
    )
    if consecutive_commented:
        return True, f"Multiple lines of commented-out code ({len(consecutive_commented)} blocks)"

    # Commented method calls or assignments
    commented_statements = re.findall(
        r'^[ \t]*//[ \t]*(await\s+)?\w+\s*[.=]\s*\w+.*[;{][ \t]*$',
        content,
        re.MULTILINE
    )
    if len(commented_statements) >= 2:
        return True, f"Commented-out statements ({len(commented_statements)} found)"

    return False, ""


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = input_data.get('tool_input', {})
    file_path = tool_input.get('file_path', '')

    # Only check code files
    if not is_code_file(file_path):
        sys.exit(0)

    # Get the content being written/edited
    content = tool_input.get('content', '')  # For Write
    new_string = tool_input.get('new_string', '')  # For Edit

    check_content = content or new_string
    if not check_content:
        sys.exit(0)

    should_warn, reason = check_commented_code(check_content)

    if should_warn:
        # Exit 0 = allow but with warning
        print(f"""
┌──────────────────────────────────────────────────────────────────┐
│  WARNING: Possible commented-out code workaround                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Detected: {reason:<52}  │
│                                                                  │
│  Is this code commented out because it doesn't compile/work?     │
│                                                                  │
│  If YES - this is a workaround. STOP and consider:               │
│  - Fix the underlying issue                                      │
│  - Delete the code entirely if not needed                        │
│  - Ask for guidance if stuck                                     │
│                                                                  │
│  If NO - this is intentional pseudocode/documentation:           │
│  - Proceed (this warning is just a reminder)                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
""", file=sys.stderr)

    # Always allow (exit 0), this is just a warning
    sys.exit(0)


if __name__ == '__main__':
    main()
