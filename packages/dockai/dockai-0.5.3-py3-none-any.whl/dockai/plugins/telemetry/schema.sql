PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  container TEXT,
  mode TEXT,
  since TEXT,
  tail INTEGER,
  latency_ms INTEGER,
  cpu_p95 REAL,
  cpu_max REAL,
  mem_p95 REAL,
  model TEXT,
  prompt_tokens INTEGER,
  completion_tokens INTEGER,
  cost_usd REAL,
  status TEXT
);

CREATE INDEX IF NOT EXISTS idx_usage_ts ON usage(ts);
CREATE INDEX IF NOT EXISTS idx_usage_container ON usage(container);