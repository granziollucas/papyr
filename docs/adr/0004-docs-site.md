Title: MkDocs for documentation site
Date: 2026-01-22
Status: Accepted

Context
- GitHub Markdown pages are readable but lack navigation and search.
- A lightweight docs site is useful for users and contributors.

Decision
- Use MkDocs with the default theme.
- Source files live in `docs/` and are published via `mkdocs build`.

Alternatives considered
- Docusaurus (richer but heavier and React-based).
- Sphinx (powerful but more complex for this project).

Consequences / trade-offs
- Adds a documentation build dependency.
- Simple static site with minimal configuration.
