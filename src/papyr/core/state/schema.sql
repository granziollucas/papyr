-- Papyr state schema (SQLite)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_hash TEXT NOT NULL,
    params_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS provider_state (
    run_id INTEGER NOT NULL,
    provider TEXT NOT NULL,
    cursor TEXT,
    last_request_time REAL,
    extra_json TEXT,
    PRIMARY KEY (run_id, provider),
    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    provider TEXT NOT NULL,
    record_id TEXT,
    normalized_json TEXT NOT NULL,
    raw_json TEXT NOT NULL,
    is_duplicate INTEGER NOT NULL DEFAULT 0,
    duplicate_of TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_records_run_provider ON records(run_id, provider);
CREATE INDEX IF NOT EXISTS idx_records_record_id ON records(record_id);

CREATE TABLE IF NOT EXISTS downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    record_id TEXT,
    pdf_url TEXT,
    file_path TEXT,
    status TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS failures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    provider TEXT NOT NULL,
    stage TEXT NOT NULL,
    message TEXT NOT NULL,
    exception_type TEXT,
    stacktrace TEXT,
    record_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (run_id) REFERENCES runs(id) ON DELETE CASCADE
);
