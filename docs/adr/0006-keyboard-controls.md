# ADR 0006: Keyboard Controls With Control-File Fallback

## Context
- Runs show pause/resume/stop instructions, but the console is busy with the search loop.
- The existing control file works, but it is slow and not discoverable enough.
- The CLI must remain cross-platform and avoid fragile input handling.

## Decision
- Add a lightweight background keyboard listener that captures single-key commands:
  - p = pause
  - r = resume
  - s = save + exit
  - q = stop
- Keep the control-file mechanism as a reliable fallback when keyboard capture is unavailable.

## Alternatives Considered
- Use a third-party keyboard library (adds dependencies and elevated permissions on some systems).
- Use blocking input prompts (halts the search loop and conflicts with progress UI).

## Consequences
- Keyboard controls are best-effort and may be disabled when stdin is not a TTY.
- Control file remains the guaranteed method across environments.
