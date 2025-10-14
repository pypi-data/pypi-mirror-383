import os
import time
import sqlite3
import sqlite3 as _sqlite
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from .license_manager import verify_license

def _expand(p: str) -> str:
    return os.path.expanduser(p)

def _ensure_dir(p: str):
    Path(_expand(p)).parent.mkdir(parents=True, exist_ok=True)

class TelemetryPlugin:
    name = "telemetry"
    version = "0.2.0"

    def __init__(self, cfg: dict | None = None):
        self.cfg = cfg or {}
        raw_path = (self.cfg.get("sqlite_path") or "~/.dockai/usage.db")
        self.sqlite_path = os.path.expanduser(raw_path)
        self.max_free_rows = int(self.cfg.get("max_free_rows") or 10)
        self.licensed = False
        self.plan = "free"
        self._t0 = None

        # findings caps (free plan defaults)
        self.max_findings_per_run = int(self.cfg.get("max_findings_per_run") or 20)
        self.max_findings_total = int(self.cfg.get("max_findings_total") or 200)

    # --- lifecycle hooks ---

    def on_start(self, ctx: dict):
        # lisans doğrula
        self.licensed, self.plan = verify_license(self.cfg)

        # DB bağlantısını hazırla
        _ensure_dir(self.sqlite_path)

        self._init_schema()
        self._verify_schema()
        # print(f"\n[telemetry] DB: {self.sqlite_path} | plan={self.plan} | licensed={self.licensed} | max_free_rows={self.max_free_rows}")

        # Debug: show DB file size after init
        try:
            dbp = self.sqlite_path
        except Exception:
            pass

        self._t0 = time.time()

        # if not self.licensed:
        #     print("\n⚠️ Telemetry: Free mode (limited). Lisans anahtarı girilirse sınırlar kalkar.\n")

    def on_logs_fetched(self, ctx: dict, logs: str):
        # İleri faz: secrets/PII redaction burada yapılabilir.
        pass

    def on_ai_response(self, ctx: dict, response: str, meta: dict):
        # İleri faz: meta['ai_usage'] içinden token & cost değerleri yakalanabilir.
        pass

    def on_finish(self, ctx: dict, result: dict):
        t1 = time.time()
        latency_ms = int((t1 - (self._t0 or t1)) * 1000)

        # print(f"\n[telemetry] on_finish: container={(ctx or {}).get('container_name')} mode={(ctx or {}).get('mode')} since={(ctx or {}).get('since')} tail={(ctx or {}).get('tail')}")

        meta = (ctx or {}).get("meta") or {}
        perf = meta.get("perf") or {}
        cpu = (perf.get("cpu") or {})
        mem = (perf.get("mem_perc") or {})
        usage = meta.get("ai_usage") or {}

        row = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "container": (ctx or {}).get("container_name", ""),
            "mode": (ctx or {}).get("mode", ""),        # commands.py içinde ctx["mode"]=effective_mode eklersen dolar
            "since": (ctx or {}).get("since", ""),
            "tail": (ctx or {}).get("tail", ""),
            "latency_ms": latency_ms,
            "cpu_p95": cpu.get("p95"),
            "cpu_max": cpu.get("max"),
            "mem_p95": mem.get("p95"),
            "model": usage.get("model"),
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "cost_usd": usage.get("cost_usd"),
            "status": "ok"
        }


        self._insert_row(row)
        
        # findings (optional): accept pre-parsed findings from pipeline if available
        # Expected formats:
        #  - ctx["meta"]["findings"]: List[dict] with keys: severity, kind, signature, message, component, file, line, count
        #  - or minimal counters: ctx["meta"]["counters"] = {"error": N, "warn": M} to create aggregate rows
        try:
            meta = (ctx or {}).get("meta") or {}
            findings: List[Dict[str, Any]] = meta.get("findings") or []
            counters = meta.get("counters") or {}
            run_id = self._last_inserted_run_id()
            if run_id:
                if findings:
                    self._insert_findings(run_id, row["container"], findings)
                else:
                    agg: List[Dict[str, Any]] = []
                    err = counters.get("error") or counters.get("errors")
                    wrn = counters.get("warn") or counters.get("warnings")
                    now_ts = row["ts"]
                    if err:
                        agg.append({
                            "ts": now_ts, "severity": "error", "kind": "aggregate",
                            "signature": "agg:error", "message": f"{int(err)} errors in window",
                            "component": None, "file": None, "line": None, "count": int(err)
                        })
                    if wrn:
                        agg.append({
                            "ts": now_ts, "severity": "warn", "kind": "aggregate",
                            "signature": "agg:warn", "message": f"{int(wrn)} warnings in window",
                            "component": None, "file": None, "line": None, "count": int(wrn)
                        })
                    if agg:
                        self._insert_findings(run_id, row["container"], agg)
        except Exception as e:
            print(f"[telemetry] findings insert skipped: {type(e).__name__}: {e}")

    # --- internal helpers ---

    def _connect(self):
        """Open sqlite connection with a sane timeout and optional SQL trace."""
        conn = sqlite3.connect(self.sqlite_path, timeout=10.0)
        if os.getenv("DOCKAI_SQL_TRACE") in ("1", "true", "True"):
            try:
                conn.set_trace_callback(lambda s: print(f"[sql] {s}"))
            except Exception as e:
                print(f"[telemetry] trace init failed: {e}")
        return conn

    def _retry(self, func, *, attempts=5, base_sleep=0.05):
        for i in range(attempts):
            try:
                return func()
            except sqlite3.OperationalError as e:
                msg = str(e).lower()
                if "database is locked" in msg or "database is busy" in msg:
                    # exponential backoff: 50ms, 100ms, 200ms, 400ms, 800ms
                    time.sleep(base_sleep * (2 ** i))
                    continue
                raise

    def _init_schema(self):
        FALLBACK_SQL = (
            "CREATE TABLE IF NOT EXISTS usage ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "ts TEXT NOT NULL,"
            "container TEXT,"
            "mode TEXT,"
            "since TEXT,"
            "tail INTEGER,"
            "latency_ms INTEGER,"
            "cpu_p95 REAL,"
            "cpu_max REAL,"
            "mem_p95 REAL,"
            "model TEXT,"
            "prompt_tokens INTEGER,"
            "completion_tokens INTEGER,"
            "cost_usd REAL,"
            "status TEXT);"
            "CREATE INDEX IF NOT EXISTS idx_usage_ts ON usage(ts);"
            "CREATE INDEX IF NOT EXISTS idx_usage_container ON usage(container);"
            "\n"
            "CREATE TABLE IF NOT EXISTS findings ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "run_id INTEGER NOT NULL,"
            "ts TEXT NOT NULL,"
            "container TEXT,"
            "severity TEXT,"
            "kind TEXT,"
            "signature TEXT,"
            "message TEXT,"
            "component TEXT,"
            "file TEXT,"
            "line INTEGER,"
            "count INTEGER DEFAULT 1,"
            "FOREIGN KEY(run_id) REFERENCES usage(id) ON DELETE CASCADE);"
            "CREATE INDEX IF NOT EXISTS idx_findings_ts ON findings(ts);"
            "CREATE INDEX IF NOT EXISTS idx_findings_container ON findings(container);"
            "CREATE INDEX IF NOT EXISTS idx_findings_sig ON findings(signature);"
        )

        schema_path = Path(__file__).resolve().parent / "schema.sql"
        sql = None
        try:
            if schema_path.exists():
                text = schema_path.read_text(encoding="utf-8")
                if text and text.strip():
                    sql = text
        except Exception as e:
            print(f"[telemetry] schema read error: {e}")
            sql = None

        if not sql:
            sql = FALLBACK_SQL

        try:
            _ensure_dir(self.sqlite_path)
            with self._connect() as conn:
                cur = conn.cursor()

                # If table already exists, skip init entirely (do not touch schema each run)
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usage'")
                if cur.fetchone():
                    return

                # Set stable PRAGMAs once at init (better concurrency on macOS/Linux)
                try:
                    cur.execute("PRAGMA journal_mode=WAL")
                except Exception:
                    pass
                try:
                    cur.execute("PRAGMA synchronous=NORMAL")
                except Exception:
                    pass
                try:
                    cur.execute("PRAGMA busy_timeout=10000")
                except Exception:
                    pass

                # Create schema atomically
                cur.execute("BEGIN IMMEDIATE")
                cur.executescript(sql)
                conn.commit()

                # Verify table exists; if not, apply fallback explicitly
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usage'")
                row = cur.fetchone()
                if not row:
                    cur.execute("BEGIN IMMEDIATE")
                    cur.executescript(FALLBACK_SQL)
                    conn.commit()

        except Exception as e:
            print(f"❌ [telemetry] schema init error: {e}")

    def _insert_row(self, row: dict):
        # print(f"[telemetry] _insert_row entered: ts={row.get('ts')} container={row.get('container')} mode={row.get('mode')} since={row.get('since')} tail={row.get('tail')}")
        try:
            _ensure_dir(self.sqlite_path)

            def _tx():
                with self._connect() as conn:
                    cur = conn.cursor()
                    # print("[telemetry] _tx: BEGIN IMMEDIATE; preparing INSERT…")

                    # Start an immediate transaction to avoid writer races
                    cur.execute("BEGIN IMMEDIATE")

                    # --- sanitize values to avoid datatype mismatch (e.g., "" into INTEGER) ---
                    def _to_int(v):
                        try:
                            if v is None:
                                return None
                            if isinstance(v, (int,)):
                                return v
                            s = str(v).strip()
                            if s == "":
                                return None
                            if "." in s:
                                return int(float(s))
                            return int(s)
                        except Exception:
                            return None

                    def _to_float(v):
                        try:
                            if v is None:
                                return None
                            if isinstance(v, (int, float)):
                                return float(v)
                            s = str(v).strip()
                            if s == "":
                                return None
                            return float(s)
                        except Exception:
                            return None

                    _tail          = _to_int(row.get("tail"))
                    _latency_ms    = _to_int(row.get("latency_ms"))
                    _cpu_p95       = _to_float(row.get("cpu_p95"))
                    _cpu_max       = _to_float(row.get("cpu_max"))
                    _mem_p95       = _to_float(row.get("mem_p95"))
                    _prompt_tokens = _to_int(row.get("prompt_tokens"))
                    _completion    = _to_int(row.get("completion_tokens"))
                    _cost_usd      = _to_float(row.get("cost_usd"))

                    # We always insert first, then prune to keep only the latest N rows (free plan)
                    # This is robust even if the table started with many old rows.

                    cur.execute(
                        """
                        INSERT INTO usage (
                          ts, container, mode, since, tail, latency_ms,
                          cpu_p95, cpu_max, mem_p95,
                          model, prompt_tokens, completion_tokens, cost_usd, status
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        """,
                        (
                            row.get("ts"), row.get("container"), row.get("mode"), row.get("since"), _tail, _latency_ms,
                            _cpu_p95, _cpu_max, _mem_p95,
                            row.get("model"), _prompt_tokens, _completion, _cost_usd, row.get("status")
                        )
                    )

                    # Robust prune after insert: delete only the oldest rows needed to keep cap
                    if (not self.licensed) and (self.max_free_rows and self.max_free_rows > 0):
                        cur.execute("SELECT COUNT(1) FROM usage")
                        (cnt_total,) = cur.fetchone() or (0,)
                        if cnt_total > self.max_free_rows:
                            over = cnt_total - self.max_free_rows
                            cur.execute(
                                "DELETE FROM usage WHERE id IN ("
                                "  SELECT id FROM usage ORDER BY id ASC LIMIT ?"
                                ")",
                                (over,)
                            )
                            cur.execute("SELECT changes()")
                            (deleted_changes,) = cur.fetchone() or (0,)
                            # print(f"[telemetry] prune after insert: over={over}, deleted={deleted_changes}, keep={self.max_free_rows}")

                    # Diagnostics: last row id and count after
                    last_id = cur.lastrowid
                    cur.execute("SELECT COUNT(1) FROM usage")
                    (count_after,) = cur.fetchone() or (0,)
                    # print(f"[telemetry] insert last_id={last_id} | final count={count_after}")
                    conn.commit()

            # retry on locking; if table is missing (fresh DB), re-init schema once and retry
            class _NeedsInit(Exception):
                pass

            def _tx_wrapper():
                try:
                    return _tx()
                except sqlite3.OperationalError as e:
                    msg = str(e).lower()
                    if "no such table: usage" in msg:
                        raise _NeedsInit()
                    raise

            try:
                self._retry(_tx_wrapper)
            except _NeedsInit:
                print("[telemetry] usage table missing; initializing schema and retrying once…")
                self._init_schema()
                self._retry(_tx)
        except Exception as e:
            print(f"❌ telemetry insert failed: {type(e).__name__}: {e}")

    def _last_inserted_run_id(self) -> int | None:
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id FROM usage ORDER BY id DESC LIMIT 1")
                r = cur.fetchone()
                return int(r[0]) if r else None
        except Exception:
            return None

    def _insert_findings(self, run_id: int, container: str, items: List[Dict[str, Any]]):
        """Insert a list of finding dicts for a given run_id. Honors free-plan caps.
        items keys: ts, severity, kind, signature, message, component, file, line, count
        """
        if not items:
            return

        def _norm_int(v):
            try:
                return int(v) if v is not None and str(v).strip() != "" else None
            except Exception:
                return None
        def _norm_str(v):
            return None if v is None else str(v)

        def _tx():
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute("BEGIN IMMEDIATE")

                # per-run cap (free): at most max_findings_per_run
                if (not self.licensed) and (self.max_findings_per_run and self.max_findings_per_run > 0):
                    cur.execute("SELECT COUNT(1) FROM findings WHERE run_id=?", (run_id,))
                    (cnt_run,) = cur.fetchone() or (0,)
                    remain = max(0, self.max_findings_per_run - int(cnt_run))
                    if remain <= 0:
                        # no room; keep older ones (do nothing) or replace oldest? For now, replace oldest one by one
                        cur.execute(
                            "DELETE FROM findings WHERE id IN (SELECT id FROM findings WHERE run_id=? ORDER BY id ASC LIMIT ?)",
                            (run_id, len(items))
                        )
                        remain = len(items)
                    # if too many items, trim input
                    if len(items) > remain:
                        del items[remain:]

                # total cap (free): keep last max_findings_total overall
                if (not self.licensed) and (self.max_findings_total and self.max_findings_total > 0):
                    cur.execute("SELECT COUNT(1) FROM findings")
                    (cnt_total,) = cur.fetchone() or (0,)
                    over = max(0, int(cnt_total) + len(items) - self.max_findings_total)
                    if over > 0:
                        cur.execute(
                            "DELETE FROM findings WHERE id IN (SELECT id FROM findings ORDER BY id ASC LIMIT ?)",
                            (over,)
                        )

                # bulk insert
                for it in items:
                    cur.execute(
                        """
                        INSERT INTO findings (
                          run_id, ts, container, severity, kind, signature, message,
                          component, file, line, count
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
                        """,
                        (
                            run_id,
                            _norm_str(it.get("ts")) or datetime.utcnow().isoformat()+"Z",
                            container,
                            _norm_str(it.get("severity")),
                            _norm_str(it.get("kind")),
                            _norm_str(it.get("signature")),
                            _norm_str(it.get("message")),
                            _norm_str(it.get("component")),
                            _norm_str(it.get("file")),
                            _norm_int(it.get("line")),
                            _norm_int(it.get("count")) or 1,
                        )
                    )
                conn.commit()
        try:
            self._retry(_tx)
        except Exception as e:
            print(f"❌ telemetry findings insert failed: {type(e).__name__}: {e}")

    def _verify_schema(self):
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA busy_timeout=5000")
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usage'")
                row = cur.fetchone()
                if row:
                    cur.execute("SELECT COUNT(1) FROM usage")
                    (cnt,) = cur.fetchone() or (0,)
                
                # ensure findings table exists as well
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='findings'")
                if not cur.fetchone():
                    cur.execute("BEGIN IMMEDIATE")
                    cur.executescript(
                        """
                        CREATE TABLE IF NOT EXISTS findings (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          run_id INTEGER NOT NULL,
                          ts TEXT NOT NULL,
                          container TEXT,
                          severity TEXT,
                          kind TEXT,
                          signature TEXT,
                          message TEXT,
                          component TEXT,
                          file TEXT,
                          line INTEGER,
                          count INTEGER DEFAULT 1,
                          FOREIGN KEY(run_id) REFERENCES usage(id) ON DELETE CASCADE
                        );
                        CREATE INDEX IF NOT EXISTS idx_findings_ts ON findings(ts);
                        CREATE INDEX IF NOT EXISTS idx_findings_container ON findings(container);
                        CREATE INDEX IF NOT EXISTS idx_findings_sig ON findings(signature);
                        """
                    )
                    conn.commit()

        except Exception as e:
            print(f"❌ [telemetry] schema verify error: {e}")

    def _has_free_capacity(self) -> bool:
        """
        Free modda kaç satır olduğuna bakar; max_free_rows'a ulaştıysa false döndürür.
        """
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA busy_timeout=5000")
                cur.execute("SELECT COUNT(1) FROM usage")
                (count,) = cur.fetchone() or (0,)
        except Exception as e:
            print(f"[telemetry] capacity check error (treating as empty): {e}")
            count = 0
        return count < self.max_free_rows