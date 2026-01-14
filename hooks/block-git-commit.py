#!/usr/bin/env python3
"""
Hook to block git commit/push unless explicitly requested.

Prevents the anti-pattern:
  Claude commits changes without being asked

Triggers on: Bash commands containing git commit or git push
Action: BLOCK unless user explicitly requested commit/push in conversation
"""

import json
import sys
import re


# Patterns that indicate user explicitly requested commit/push
EXPLICIT_REQUEST_PATTERNS = [
    r'\bcommit\b',
    r'\bpush\b',
    r'\bgit\s+commit\b',
    r'\bgit\s+push\b',
    r'\bcreate\s+(a\s+)?pr\b',
    r'\bcreate\s+(a\s+)?pull\s*request\b',
    r'\bmerge\b',
]


def debug_log(msg):
    """Print debug info to stderr."""
    print(f"[DEBUG block-git-commit] {msg}", file=sys.stderr)


def check_user_requested_commit(transcript_path, debug=False):
    """Check if the user explicitly requested a commit/push in the conversation."""
    if not transcript_path:
        if debug:
            debug_log("transcript_path is empty or None")
        return False

    if debug:
        debug_log(f"transcript_path: {transcript_path}")

    try:
        with open(transcript_path, 'r') as f:
            lines = f.readlines()
            if debug:
                debug_log(f"Read {len(lines)} lines from transcript")

            message_types_seen = set()
            user_messages_found = 0

            for line in lines:
                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Track all message types for debugging
                msg_type = message.get('type', '<no type>')
                message_types_seen.add(msg_type)

                # Only check human/user messages
                if msg_type not in ('human', 'user', 'user_message'):
                    continue

                user_messages_found += 1

                # Get message content - handle nested message structure and both string and list formats
                # Transcript format: {"type":"user","message":{"role":"user","content":"..."}}
                inner_message = message.get('message', {})
                content = inner_message.get('content', '') if isinstance(inner_message, dict) else ''
                if isinstance(content, list):
                    # Extract text from content blocks
                    content = ' '.join(
                        block.get('text', '')
                        for block in content
                        if isinstance(block, dict)
                    )

                if not isinstance(content, str):
                    continue

                content_lower = content.lower()

                # Check for explicit request patterns
                for pattern in EXPLICIT_REQUEST_PATTERNS:
                    if re.search(pattern, content_lower):
                        if debug:
                            debug_log(f"MATCH found: pattern '{pattern}' in message")
                        return True

            if debug:
                debug_log(f"Message types seen: {message_types_seen}")
                debug_log(f"User messages found: {user_messages_found}")
                debug_log("No matching patterns found in user messages")

    except (FileNotFoundError, PermissionError, IOError) as e:
        if debug:
            debug_log(f"Error reading transcript: {type(e).__name__}: {e}")
        return False

    return False


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = input_data.get('tool_input', {})
    command = tool_input.get('command', '')

    # Check for git commit or push commands
    git_patterns = [
        r'\bgit\s+commit\b',
        r'\bgit\s+push\b',
        r'\bgit\s+.*--amend\b',
    ]

    is_git_commit_push = False
    for pattern in git_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            is_git_commit_push = True
            break

    if not is_git_commit_push:
        sys.exit(0)

    # Check if user explicitly requested commit/push
    transcript_path = input_data.get('transcript_path', '')

    # Enable debug mode to diagnose blocking issues
    debug_mode = True

    if debug_mode:
        debug_log(f"Command detected: {command}")

    if check_user_requested_commit(transcript_path, debug=debug_mode):
        sys.exit(0)  # Allow - user explicitly requested

    # Block - no explicit request found
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  BLOCKED: Git commit/push requires explicit user request         ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Command: {command[:50]:<50}  ║
║                                                                  ║
║  No explicit commit/push request found in conversation.          ║
║                                                                  ║
║  REMINDER: Do NOT commit or push unless explicitly requested.    ║
║                                                                  ║
║  - Each commit request is a ONE-TIME action                      ║
║  - Always let the user review changes first                      ║
║  - Never auto-commit subsequent changes                          ║
║                                                                  ║
║  ASK: "Would you like me to commit these changes?"               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""", file=sys.stderr)
    sys.exit(2)


if __name__ == '__main__':
    main()
