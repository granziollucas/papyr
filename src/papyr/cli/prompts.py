"""Centralized user-facing strings (en-US)."""

APP_NAME = "Papyr"

INIT_TITLE = "Papyr init"
NEW_TITLE = "Papyr new search"
RESUME_TITLE = "Papyr resume"
DOCTOR_TITLE = "Papyr doctor"
BOOTSTRAP_TITLE = "Papyr setup check"

NOT_IMPLEMENTED = "This step is not implemented yet."


GUIDE_TITLE = "Quick guide"
GUIDE_COMMANDS = [
    "Main commands:",
    "  papyr init       Set up credentials. Example: papyr init",
    "  papyr new        Start a new search. Example: papyr new",
    "  papyr resume     Resume a search. Example: papyr resume C:\\path\\search_params.json",
    "  papyr config show  Show current config (redacted). Example: papyr config show",
    "  papyr config init  Create a .env template. Example: papyr config init",
    "  papyr doctor     Check credentials and guidance. Example: papyr doctor",
    "  papyr reset-cache  Reset run cache. Example: papyr reset-cache",
    "  papyr export ris  Export RIS from CSV. Example: papyr export ris",
]
GUIDE_CHOICE = [
    "Choose one: new or resume.",
]

GUIDE_NEW_STEPS = [
    "New search (step-by-step):",
    "  1) Run: papyr new (example: papyr new)",
    "  2) Keywords (required). Example: climate policy",
    "  3) Year range (optional). Example: 2019 to 2024",
    "  4) Access filter values: open (OA only), closed (non-OA only), both (default).",
    "  5) Sort order values: relevance, date, citations.",
    "  6) Download PDFs? values: yes or no.",
    "  7) Dry run? values: yes or no.",
    "  8) Output directory (required). Example: C:\\Papyr\\runs\\climate",
]

GUIDE_RESUME_STEPS = [
    "Resume (step-by-step):",
    "  1) Find search_params.json in the run folder.",
    "  2) Run: papyr resume <path>. Example: papyr resume C:\\Papyr\\runs\\climate\\search_params.json",
    "  3) Papyr continues from the last saved state.sqlite.",
]

BOOTSTRAP_CHOICES = [
    "Type 'new' for a new search (example: new) or 'resume' to pick up from another search (example: resume).",
]
SHELL_HINT = 'Papyr shell. Type "help" for commands, "exit" to quit.'
BOOTSTRAP_SKIP_PROMPT = "Skip credential setup and continue?"

NEW_WIZARD_INTRO = "Configure your search. Press Enter to accept defaults."

PROMPT_KEYWORDS = "Step 1/12: Keywords (required). Example: climate policy"
PROMPT_YEAR_START = "Step 2/12: Start year (optional). Example: 2019"
PROMPT_YEAR_END = "Step 3/12: End year (optional). Example: 2024"
PROMPT_TYPES = "Step 4/12: Publication types (comma-separated, optional). Example: journal-article, preprint"
PROMPT_FIELDS = "Step 5/12: Search fields (comma-separated, optional). Example: title, abstract"
PROMPT_LANG = "Step 6/12: Language codes or names (comma-separated, optional). Example: en, Spanish"
PROMPT_ACCESS = "Step 7/12: Access filter values: open (OA only), closed (non-OA only), both (default)"
PROMPT_SORT = "Step 8/12: Sort order values: relevance (default), date (newest), citations (best-effort)"
PROMPT_LIMIT = "Step 9/12: Result limit (optional). Example: 200"
PROMPT_DOWNLOAD = "Step 10/12: Download PDFs? values: yes or no"
PROMPT_OUTPUT = "Step 11/12: Output directory (required). Example: C:\\Papyr\\runs\\climate"
PROMPT_DRY_RUN = "Step 12/12: Dry run? values: yes or no"
PROMPT_OUTPUT_FORMAT = "Step 13/13: Output format: csv (default) or tsv"
