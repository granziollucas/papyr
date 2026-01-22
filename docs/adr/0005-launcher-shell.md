Title: Launcher shell mode for repeated CLI commands
Date: 2026-01-22
Status: Accepted

Context
- Users want to keep a terminal open and run multiple Papyr commands without relaunching.
- The Typer CLI is one-shot by design, so repeated usage requires re-running the command.

Decision
- Add a simple interactive shell mode in the platform launcher scripts when invoked with no arguments.
- The shell loops on user input and runs `python -m papyr <command>` for each line.

Alternatives considered
- Build a dedicated REPL command inside the Python CLI.
- Leave launchers as one-shot and rely on shell history.

Consequences / trade-offs
- Shell mode is implemented in platform scripts, not in the core CLI.
- Command parsing is minimal (simple whitespace splitting in shell).
