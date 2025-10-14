import os
import json
from textwrap import dedent
from openai import OpenAI
from typing import Optional, Dict, Any


# Resolve DockAI config path with fallbacks
_DEF_PATHS = [
    os.path.expanduser("~/.dockai_config.json"),
    os.path.expanduser("~/.dockai/config.json"),
    os.path.join(os.getcwd(), ".dockai_config.json"),
]

def _resolve_config_path() -> str | None:
    # 1) explicit override
    override = os.getenv("DOCKAI_CONFIG_PATH")
    if override:
        p = os.path.expanduser(override)
        return p
    # 2) first existing default path
    for p in _DEF_PATHS:
        try:
            if os.path.exists(p):
                return p
        except Exception:
            continue
    # 3) fallback to primary default even if not exists
    return _DEF_PATHS[0]

CONFIG_PATH = _resolve_config_path()

def _read_config_key(name: str):
    try:
        path = _resolve_config_path()
        if not path or not os.path.exists(path):
            return None
        with open(path, "r") as f:
            data = json.load(f) or {}
        return data.get(name)
    except Exception:
        return None

def get_openai_api_key():
    # Prefer CONFIG first, then ENV
    cfg_val = _read_config_key("OPENAI_API_KEY")
    if cfg_val:
        if os.getenv("DOCKAI_DEBUG"):
            print("[DEBUG] OPENAI_API_KEY loaded from CONFIG (prefix=", cfg_val[:7], ") path=", _resolve_config_path())
        return cfg_val
    env_val = os.getenv("OPENAI_API_KEY")
    if env_val and os.getenv("DOCKAI_DEBUG"):
        print("[DEBUG] OPENAI_API_KEY loaded from ENV (prefix=", env_val[:7], ")")
    return env_val

def get_config_value(name: str, default=None):
    """Return value from ENV first, then ~/.dockai_config.json, else default."""
    val = os.getenv(name)
    if val is not None:
        return val
    return _read_config_key(name) or default

def _build_context_block(container_name: str | None, meta: dict | None) -> str:
    if not meta:
        return ""

    perf = meta.get("perf") or {}
    cpu = perf.get("cpu")
    mem = perf.get("mem_perc")
    counters = (meta.get("counters") or {})
    freshness = (meta.get("freshness") or {})
    last_log_time = freshness.get("last_log_time")
    has_ts = freshness.get("has_timestamp")
    is_stale = freshness.get("is_stale")
    freshness_note = freshness.get("note")

    lines: list[str] = []
    if container_name:
        lines.append(f"Container: {container_name}")

    # Perf summary
    if cpu or mem:
        lines.append("Perf (instant or window):")
        if cpu:
            lines.append(
                f" - CPU p95={cpu.get('p95')}% max={cpu.get('max')}% avg={cpu.get('avg')}%"
            )
        if mem:
            lines.append(
                f" - Mem p95={mem.get('p95')}% max={mem.get('max')}% avg={mem.get('avg')}%"
            )

    # Error/Warning counters (pre-triage)
    if counters:
        lines.append(
            f"Counters: ERROR={counters.get('errors', 0)} | WARN={counters.get('warnings', 0)}"
        )

    # Freshness info
    if last_log_time or has_ts is not None or is_stale is not None:
        lines.append("Freshness:")
        if last_log_time:
            lines.append(f" - Last log time: {last_log_time}")
        if has_ts is not None:
            lines.append(f" - Has timestamp: {'Yes' if has_ts else 'No'}")
        if is_stale is not None:
            lines.append(f" - Stale window: {'Yes' if is_stale else 'No'}")
        if freshness_note:
            lines.append(f" - Note: {freshness_note}")

    return "\n".join(lines)

def analyze_with_openai(
    log_text: str,
    *,
    container_name: str | None = None,
    meta: dict | None = None,
    strict_issue_mode: bool = True,
    lang: Optional[str] = None
) -> str:
    """
    OpenAI-based analysis.
    - Adds meta/perf context similar to Ollama.
    - strict_issue_mode: If True, produce a short 'OK' summary when no issues are found.
    """
    language = lang or get_config_value("DOCKAI_LANG", "English")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    api_key = get_openai_api_key()
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not found in environment or ~/.dockai_config.json. "
            "Set it with:\n  dockai config set OPENAI_API_KEY sk-..."
        )

    ctx = _build_context_block(container_name, meta)

    system_msg = dedent(f"""
        You are a senior DevOps assistant. Output in {language}.
        Your tasks:
        1) Extract real issues and warnings from the logs (ERROR/EXCEPTION/stacktrace/timeout/connection, etc.).
        2) List concrete root causes and actionable fix steps.
        3) When uncertain, use a **Notes**/**Uncertain** section to state what extra info is needed.
        4) If performance context is provided (CPU/Mem p95, max, avg), add a **short** "Performance Note" (e.g., "system stable" / "high CPU" / "high memory").
        5) If freshness info is provided (Last log time / Has timestamp / Stale), add a **short** "Freshness" section.
        6) If there is no issue, return a concise '✅ No issues detected (status=ok)' summary, and still include short Performance/Freshness.
        7) Produce sections with these headings:
           **Summary**, **Root Cause**, **Fix Steps**, **Confidence: low|medium|high**, **Performance Note**, **Freshness**.
    """)

    # Strict mod: hata/uyarı yoksa uzatmadan kısa "ok" üret.
    user_directive = "Report only issues/warnings; avoid long success descriptions." if strict_issue_mode else "Provide a general status summary."

    prompt = dedent(f"""\
        {user_directive}

        === Context ===
        {ctx or '(no context)'}

        === Raw Logs ===
        {log_text[:120000]}  # safe truncation
    """)

    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        temperature=0.1 if strict_issue_mode else 0.3,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt},
        ],
    )
    content = resp.choices[0].message.content or ""

    # Banner with source/model for transparency
    header = f"🤖 AI Analysis (source: OpenAI {model})\n\n"

    # Optionally append counters line for quick glance
    counters = ((meta or {}).get("counters") or {})
    counters_line = ""
    if counters:
        counters_line = f"\n\n📊 Counts: ERROR={counters.get('errors',0)} | WARN={counters.get('warnings',0)}"

    return header + content + counters_line