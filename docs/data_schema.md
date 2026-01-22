# Data Schema

Papyr exports a CSV with fixed columns (always present):

- Authors (format: "Surname, N.; Surname, N.; ...")
- Title
- Abstract
- Origin
- Volume
- Issue
- Pages
- Publisher
- Month
- Year
- Type
- Keywords
- Citations
- OA
- ID
- URL
- License
- RetrievedAt
- QueryHash
- DuplicateOf

Encoding
- CSV is comma-separated, latin1 encoded for Excel compatibility.

RIS mapping (best-effort)
- TY: record type derived from `Type`
- AU: Authors
- TI: Title
- PY: Year
- PB: Publisher
- UR: URL
- AB: Abstract
- DO: ID
