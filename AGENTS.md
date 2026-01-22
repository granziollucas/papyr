AGENT.md — Papyr Agent \& Repo Rules (en-US)



This file is the contract for any coding agent (codx/LLM) and for contributors working on this repository.

Follow these rules first. If there is a conflict:

1\) Safety/Compliance rules win.

2\) Output contracts (CSV/RIS/State) win.

3\) Architecture constraints win.

4\) Docs/ADRs must be updated whenever non-trivial decisions are made.

5\) Git is already initialized n he folder, so remembre to commit so we have backúps. Vor every major change, ask for permission before commiting.



──────────────────────────────────────────────────────────────────────────────

0\) NORTH STAR

──────────────────────────────────────────────────────────────────────────────

Project name: Papyr

Primary objective:

\- Build a Python CLI bot that searches academic works (papers, preprints, book chapters where possible) across sources and exports a single CSV with key metadata + official access links.

\- Optionally download available PDFs (only when explicitly requested by user). No piracy.



Success criteria:

\- CSV export works reliably and is resumable (pause/resume, incremental runs).

\- Downloads (when enabled) only happen for legitimately available PDFs.

\- Clean UX wizard with clear options and robust logs.

\- Works cross-platform (Windows/macOS/Linux) using Python 3.11+.



Non-goals for v1:

\- No frontend/UI.

\- No Docker.

\- No LLM features (but leave extension hooks).

\- No extra sources beyond Crossref, arXiv, SSRN (but architecture must be extensible).



Language:

\- All user-facing strings: en-US.

\- Docs: en-US.



──────────────────────────────────────────────────────────────────────────────

1\) USER EXPERIENCE (CLI) — MUST BE A WIZARD

──────────────────────────────────────────────────────────────────────────────

The CLI must provide:

A) First-run initialization wizard:

\- Guides the user through setting up required APIs/credentials ONE BY ONE.

\- For any provider requiring third-party account creation, show the official provider URL (do not embed unofficial guides).

\- Credentials are entered in-console, stored locally in an env file (never committed; must be gitignored).

\- After setup, print clear “next commands” for:

&nbsp; - starting a new search

&nbsp; - resuming a prior search



B) Main commands (short and easy to type; wizard-driven):

\- papyr init            -> credential setup wizard + doctor checks

\- papyr new             -> start new search wizard

\- papyr resume          -> resume a prior search (asks for params file path)

\- papyr config show     -> display current config (redact secrets)

\- papyr config init     -> create config template file

\- papyr doctor          -> validate environment, credentials, connectivity (best-effort)

\- papyr reset-cache     -> reset local cache/state for a run (ask for confirmation)

\- papyr export ris      -> generate RIS file from current run (CSV-driven)



C) Search wizard must ask (and print all possible options at each step):

\- keywords (simple keyword query)

\- publication year range (start\_year, end\_year)

\- publication types (user chooses from a displayed list; map to each provider capabilities)

\- keyword search fields (user chooses which metadata fields to apply the keyword against; implement best-effort by provider)

\- language filter: allow entering ISO code OR full language name (show examples)

\- access filter: Open Access only / Closed Access only / Both (default: Both)

\- sorting: date / relevance / citations / etc. (best-effort; provider dependent)

\- optional result limit: if user wants a limit, enforce integer; else run without limit

\- download PDFs? (yes/no)

\- output directory (user-provided)



D) Run folder layout (in the user-provided output directory):

\- <output\_dir>/

&nbsp; - search\_params.json               (or .toml; pick one and keep stable)

&nbsp; - results.csv                      (comma-separated, latin1 encoding for Excel friendliness)

&nbsp; - results.ris                      (optional if user runs export)

&nbsp; - state.sqlite                     (stores everything needed to resume/incremental)

&nbsp; - logs/

&nbsp;     - run\_<timestamp>.log          (DEBUG logs, text)

&nbsp;     - duplicates\_<timestamp>.csv   (or .log)

&nbsp;     - errors\_<timestamp>.jsonl     (structured error records)

&nbsp; - files/                           (PDF downloads only if requested)

&nbsp;     - <sanitized\_title>.pdf



File naming rules for PDFs:

\- Use paper Title as filename.

\- Replace spaces with underscores.

\- Remove/replace invalid filename characters (cross-platform safe).

\- Add a short suffix to avoid collisions when titles repeat (e.g., \_<shortid> derived from DOI/arXiv/SSRN id or stable hash).

\- Validate PDF (content-type and magic bytes) before saving.



E) Runtime control during search (cross-platform):

\- While running: show a progress bar with ETA and brief status.

\- Print keyboard commands (or minimal key controls) for:

&nbsp; - Pause

&nbsp; - Pause \& save \& exit (resume later)

&nbsp; - Cancel

\- While paused: print controls for:

&nbsp; - Save \& exit

&nbsp; - Continue

&nbsp; - Cancel



If true keyboard capture is not robust on some OS, implement a safe fallback:

\- Poll for a “control file” (e.g., .papyr\_control) in the run folder with commands: PAUSE/RESUME/STOP.

\- Still print instructions so user can pause reliably.



F) Console output policy:

\- Console should be quiet/minimal.

\- Detailed information goes to the DEBUG log.

\- On errors, console must say: “An error occurred. Please check the log at: <path>”.

\- End-of-run console summary must include:

&nbsp; - total works found

&nbsp; - how many Open Access

&nbsp; - how many PDFs downloaded

&nbsp; - how many duplicates

&nbsp; - how many failures

&nbsp; - how many preprints vs published works (best-effort categorization)



──────────────────────────────────────────────────────────────────────────────

2\) DATA SOURCES (ADAPTERS) — V1 MUST SUPPORT 3

──────────────────────────────────────────────────────────────────────────────

Sources in v1:

\- Crossref (mandatory)

\- arXiv (mandatory)

\- SSRN (mandatory), BUT:

&nbsp; - Prefer official API if available.

&nbsp; - If SSRN requires scraping, implement only if ToS permits and document the approach clearly.

&nbsp; - If ToS uncertainty exists, ship SSRN adapter in “disabled by default” state until user explicitly enables and accepts responsibility.

&nbsp; - Under no circumstance implement piracy or bypass paywalls.

Forbidden source:

\- Sci-Hub (explicitly excluded).



Metasearch behavior:

\- User can run without all credentials.

\- Before starting a search, detect missing credentials per provider.

\- Warn user and ask if they want to configure now.

&nbsp; - If yes: run the provider setup steps.

&nbsp; - If no: continue with remaining providers.



Rate limiting:

\- Be conservative and use ~80% of known provider limits (or conservative defaults if unknown).

\- No parallelism for API calls by default.

\- Implement per-adapter rate limiter + polite retry/backoff.



──────────────────────────────────────────────────────────────────────────────

3\) OUTPUT SCHEMA (CSV) — FIXED COLUMNS

──────────────────────────────────────────────────────────────────────────────

CSV must always include these columns (even if blank):

\- Authors                (format: "Surname, N.; Surname, N.; ...")

\- Title

\- Abstract               (preserve content; allow line breaks or normalize consistently)

\- Origin                 (source/provider name: Crossref/arXiv/SSRN)

\- Volume

\- Issue

\- Pages

\- Publisher

\- Month

\- Year

\- Type                   (paper/preprint/book\_chapter/etc. best-effort)

\- Keywords

\- Citations              (best-effort; blank if unavailable)

\- OA                     (true/false/unknown)

\- ID                     (DOI/arXiv/SSRN id; prefer DOI)

\- URL                    (official landing page; prefer DOI URL, then arXiv, then SSRN)



Additional columns:

\- License                (e.g., CC-BY, etc; blank if unavailable)

\- RetrievedAt            (ISO timestamp)

\- QueryHash              (stable hash of search\_params)

\- DuplicateOf            (if deduped; else blank)



Encoding \& delimiter:

\- Comma-separated (",")

\- latin1 encoding (for Excel friendliness)

\- Ensure proper escaping/quoting for commas and newlines.



──────────────────────────────────────────────────────────────────────────────

4\) DEDUPLICATION RULES

──────────────────────────────────────────────────────────────────────────────

Dedup logic:

1\) Group by normalized Title (casefold, collapse whitespace, strip punctuation).

2\) If two or more titles match, compare IDs (DOI/arXiv/SSRN):

&nbsp;  - Mark as duplicate ONLY if BOTH normalized title AND ID match.

3\) Do NOT merge metadata across duplicates in v1.

4\) Keep one canonical row (prefer Crossref as canonical) and log duplicates separately:

&nbsp;  - duplicates\_<timestamp>.csv with both records and reason.



──────────────────────────────────────────────────────────────────────────────

5\) RESUMABILITY, INCREMENTAL, STATE

──────────────────────────────────────────────────────────────────────────────

State persistence:

\- Use SQLite (state.sqlite in the run folder).

\- Store:

&nbsp; - search parameters (normalized)

&nbsp; - per-provider cursor/pagination token if applicable

&nbsp; - each harvested record (raw + normalized) with stable IDs

&nbsp; - download status for PDFs

&nbsp; - failures with error types and timestamps

&nbsp; - last processed position so resume is accurate



Resume behavior:

\- papyr resume asks for path to search\_params file.

\- Load run folder based on that path.

\- Quick check the CSV and SQLite to determine already harvested works.

\- Continue from the last stored cursor/offset, avoiding redundancy.



Incremental behavior:

\- If the same search is run again into the same folder, it should:

&nbsp; - detect prior QueryHash

&nbsp; - only fetch items not already present (best-effort)

&nbsp; - append to state + regenerate results.csv deterministically



Dry-run:

\- Implement a dry-run mode (wizard toggle or flag) that does not download PDFs and can optionally stop after N results.



──────────────────────────────────────────────────────────────────────────────

6\) PDF DOWNLOAD POLICY

──────────────────────────────────────────────────────────────────────────────

Downloads happen ONLY if user explicitly enabled it in the wizard.

Only download if:

\- The record provides an official, legitimate PDF URL or an OA link.

\- Validate response indicates a PDF (headers + magic bytes).

Retry policy:

\- Up to 3 attempts with exponential backoff; then record failure and continue.

No maximum size enforcement in v1 (but code should be ready to add it later).

No supplementary materials download.



──────────────────────────────────────────────────────────────────────────────

7\) ARCHITECTURE (MUST BE EXTENSIBLE)

──────────────────────────────────────────────────────────────────────────────

Use a clean layered design: adapters + domain core.



Recommended structure (src layout):

\- pyproject.toml

\- README.md

\- docs/

&nbsp;   - index.md

&nbsp;   - quickstart.md

&nbsp;   - cli\_reference.md

&nbsp;   - providers.md

&nbsp;   - data\_schema.md

&nbsp;   - resumability.md

&nbsp;   - troubleshooting.md

&nbsp;   - adr/

&nbsp;       - 0001-architecture.md

&nbsp;       - 0002-state-sqlite.md

&nbsp;       - ... (add as decisions happen)

\- src/papyr/

&nbsp;   - \_\_init\_\_.py

&nbsp;   - \_\_main\_\_.py

&nbsp;   - cli/

&nbsp;       - app.py              (Typer main app)

&nbsp;       - wizard.py           (interactive flows)

&nbsp;       - prompts.py          (all strings centralized, en-US)

&nbsp;   - core/

&nbsp;       - models.py           (dataclasses/pydantic models)

&nbsp;       - normalize.py        (field normalization)

&nbsp;       - dedup.py

&nbsp;       - pipeline.py         (search -> normalize -> dedup -> persist -> export)

&nbsp;       - export\_csv.py

&nbsp;       - export\_ris.py

&nbsp;       - downloader.py

&nbsp;       - rate\_limit.py

&nbsp;       - state/

&nbsp;           - db.py           (sqlite access layer)

&nbsp;           - schema.sql

&nbsp;           - repo.py         (repositories/queries)

&nbsp;   - adapters/

&nbsp;       - base.py             (Provider interface)

&nbsp;       - crossref.py

&nbsp;       - arxiv.py

&nbsp;       - ssrn.py

&nbsp;   - util/

&nbsp;       - fs.py               (safe filenames, paths)

&nbsp;       - hashing.py

&nbsp;       - logging.py

&nbsp;       - time.py

&nbsp;       - config.py           (load env/config)

\- tests/

&nbsp;   - test\_normalize.py

&nbsp;   - test\_dedup.py

&nbsp;   - test\_safe\_filename.py

&nbsp;   - test\_state\_resume.py

&nbsp;   - adapters/

&nbsp;       - test\_crossref\_smoke.py (network tests marked optional)

\- .gitignore (must include .env, run folders, logs)

\- environment.yml (prod)

\- environment.dev.yml (dev)

\- CONTRIBUTING.md

\- CHANGELOG.md

\- LICENSE

\- SECURITY.md (policy: no piracy, responsible disclosure)



CLI framework:

\- Use Typer for commands and overall CLI.

\- For yes/no prompts, you may use Click prompt utilities internally or Typer’s prompting features.

\- Use Rich for progress bars and nicer console rendering (but keep output minimal).

\- Ensure dependency list remains reasonable.



──────────────────────────────────────────────────────────────────────────────

8\) PROVIDER INTERFACE CONTRACT (IMPORTANT)

──────────────────────────────────────────────────────────────────────────────

Define a Provider protocol / abstract base with at least:

\- name: str

\- requires\_credentials: bool

\- credential\_fields: list\[str]  (for wizard prompts)

\- is\_configured(config) -> bool

\- setup\_instructions() -> list\[str]  (include official links if needed)

\- search(query: SearchQuery, state: ProviderState) -> Iterator\[RawRecord]

&nbsp; - Must support continuation via state/cursor.

\- normalize(raw: RawRecord) -> PaperRecord  (or shared normalize pipeline)

\- get\_official\_urls(record) -> {landing\_url, pdf\_url?}

\- rate\_limit\_policy() -> RateLimitPolicy



SearchQuery model must include:

\- keywords

\- year\_start/year\_end

\- types

\- language(s)

\- fields\_to\_search

\- access\_filter

\- sort\_order

\- limit (optional)

\- download\_pdfs (bool)

\- output\_dir



ProviderState must include:

\- cursor/offset tokens

\- last\_request\_time

\- any provider-specific continuation info



──────────────────────────────────────────────────────────────────────────────

9\) LOGGING + ERROR HANDLING

──────────────────────────────────────────────────────────────────────────────

Logging:

\- DEBUG level to a text log file in logs/

\- Minimal console output (status + summary + error pointers)

\- Structured errors file in JSONL with fields:

&nbsp; - timestamp, provider, stage, message, exception\_type, stacktrace (in debug), record\_id if relevant



Failures must never crash the entire run unless:

\- state.sqlite cannot be opened/written

\- output directory is invalid/unwritable

In other cases: log and continue.



──────────────────────────────────────────────────────────────────────────────

10\) DOCUMENTATION REQUIREMENTS (HUMANS + MODEL CONTEXT)

──────────────────────────────────────────────────────────────────────────────

You must continuously write/update documentation as you implement.



Human docs:

\- README.md: quick intro, what it does, what it does NOT do, install, quickstart, key commands.

\- docs/: very detailed documentation (separate from README), including:

&nbsp; - CLI reference with examples

&nbsp; - Provider behaviors, limitations, credentials setup

&nbsp; - Data schema (CSV + RIS mapping)

&nbsp; - Resuming and incremental runs

&nbsp; - Troubleshooting (common errors + where to find logs)

&nbsp; - Legal/ethical stance: no piracy, respect ToS, OA only downloads



Model-context docs (internal developer notes):

\- docs/dev\_notes.md:

&nbsp; - current architecture summary

&nbsp; - key modules and responsibilities

&nbsp; - how to add a new provider adapter

&nbsp; - assumptions and known limitations



ADR (Architecture Decision Records):

\- Create an ADR whenever you make a non-trivial decision (e.g., SQLite schema, pause mechanism).

\- Each ADR must include:

&nbsp; - context

&nbsp; - decision

&nbsp; - alternatives considered

&nbsp; - consequences/trade-offs



──────────────────────────────────────────────────────────────────────────────

11\) TESTING + QUALITY BAR

──────────────────────────────────────────────────────────────────────────────

Testing:

\- Use pytest.

\- Unit tests must cover:

&nbsp; - filename sanitization

&nbsp; - normalization (authors formatting, ids)

&nbsp; - dedup rule correctness

&nbsp; - state persistence + resume logic (SQLite)

\- Adapter tests:

&nbsp; - Provide “smoke tests” that are skipped by default unless user enables (to avoid CI flakiness and API bans).

&nbsp; - Use clear markers like @pytest.mark.network.



Code quality:

\- Type hints throughout.

\- Docstrings in Google style.

\- Keep functions small and readable.

\- No heavy frameworks.



Environments:

\- Provide environment.yml (prod) and environment.dev.yml (dev) for conda.

\- Include python=3.11+ and dependencies.



──────────────────────────────────────────────────────────────────────────────

12\) IMPLEMENTATION PLAN (DO THIS IN ORDER)

──────────────────────────────────────────────────────────────────────────────

Phase 1 — Skeleton \& CLI

1\) Create repo structure + pyproject + packaging.

2\) Implement Typer CLI scaffolding: init/new/resume/config/doctor/reset-cache/export ris.

3\) Implement logging setup and minimal console UI with Rich.



Phase 2 — Core models \& state

4\) Implement SearchQuery, PaperRecord, RawRecord models.

5\) Implement SQLite state layer with schema + repository helpers.

6\) Implement export\_csv and export\_ris.



Phase 3 — Providers

7\) Implement Crossref adapter.

8\) Implement arXiv adapter.

9\) Implement SSRN adapter with safe/ethical defaults (document limitations and ToS concerns).

10\) Implement metasearch pipeline (sequential calls; rate-limited; resumable).



Phase 4 — Downloads, pause/resume controls

11\) Implement downloader with validation + retries.

12\) Implement pause/resume/cancel controls (keyboard or control-file fallback).

13\) Implement incremental behavior via QueryHash + SQLite.



Phase 5 — Docs \& tests

14\) Write full docs in docs/ + ADRs + dev\_notes.

15\) Add tests and ensure basic local run success.



──────────────────────────────────────────────────────────────────────────────

13\) OUTPUT EXPECTATIONS (WHAT YOU MUST DELIVER)

──────────────────────────────────────────────────────────────────────────────

You must:

\- Create all required files, modules, and documentation.

\- Ensure CLI runs end-to-end for at least one provider with a sample query.

\- Provide example commands in docs.

\- Ensure secrets are never printed or stored in tracked files.

\- Ensure the project never facilitates piracy.



When uncertain about a provider capability:

\- Implement best-effort and document clearly in providers.md.

\- Provide graceful degradation (blank fields).

\- Never invent metadata; leave blank if unknown.



──────────────────────────────────────────────────────────────────────────────

14\) DEFAULTS (USE THESE UNLESS USER OVERRIDES)

──────────────────────────────────────────────────────────────────────────────

\- access\_filter default: Both

\- download\_pdfs default: No

\- limit default: None (unbounded)

\- parallelism: off

\- logs: DEBUG to file; minimal console

\- canonical provider for duplicates: Crossref

\- rate limiting: conservative (80% of known limits; else safe default delay)



Now implement Papyr according to this spec. As you implement, keep docs and ADRs updated.

Do not ask the user follow-up questions unless absolutely required to proceed.

