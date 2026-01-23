# CLI Reference

## Launcher shell (papyr.bat / papyr.sh / papyr.command)
If you run a launcher with no arguments, it starts a simple interactive shell:

- Prompt: `papyr>`
- Exit with `exit` or `quit`
- `help` prints example commands

Before the prompt, Papyr runs a credential check and offers to configure any missing providers. You can skip this step. It then shows a brief `new`/`resume` hint; each command prompts step-by-step.

You can also pass a command directly, e.g., `papyr.bat init`.

## papyr init
Runs the credential setup wizard and provider checks.

Steps:
- Crossref polite email
- SSRN opt-in (disabled by default)

## papyr new
Starts the interactive search wizard.

Prompts:
- Keywords (required)
- Year range (optional)
- Publication types (optional)
- Search fields (optional)
- Language codes or names (optional)
- Access filter: open / closed / both
- Sort order (best-effort)
- Result limit (optional)
- Download PDFs (yes/no)
- Output directory
- Dry-run (yes/no)
- Output format: csv / tsv
- Run providers in parallel (yes/no)
Tip: type `back` (or `b`) to return to the previous step.

During runs:
- Keyboard shortcuts: p=pause, r=resume, s=save+exit, q=stop.
- A `.papyr_control` file in the output folder can pause/resume/stop (fallback).
- A progress bar with ETA shows overall search progress (ETA is most accurate when a limit is set).

## papyr resume
Resumes a prior search. You can pass a run folder or the path to `search_params.json`.
During resume:
- Optionally edit search parameters
- Optionally download missing PDFs for records already saved

## papyr config show
Shows current config with secrets redacted.

## papyr config init
Creates a `.env` template.

## papyr doctor
Checks credentials and prints a brief step-by-step guide for `new` and `resume` if everything is configured.

## papyr reset-cache
Resets local cache/state for a run (asks for confirmation).

## papyr export ris
Generates `results.ris` from the current CSV.
