from pathlib import Path
from .telemetry_plugin import TelemetryPlugin

# Defaults used when plugin.json is missing or incomplete
DEFAULT_CFG = {
    "sqlite_path": "~/.dockai/usage.db",
}


def _read_descriptor():
    """Read plugin.json if present; return dict or {}."""
    p = Path(__file__).resolve().parent / "plugin.json"
    try:
        if p.exists():
            import json
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[telemetry] plugin.json read error: {e}")
    return {}


def _build_plugin():
    data = _read_descriptor() or {}
    enabled = data.get("enabled", True)  # default: enabled
    cfg = data.get("config") or {}

    # fill defaults without overwriting explicit values
    for k, v in DEFAULT_CFG.items():
        cfg.setdefault(k, v)

    if not enabled:
        # Expose a no-op plugin with same surface so loader can keep going
        class _Disabled:
            name = "telemetry"
            version = data.get("version", "0.0.0")
            def on_start(self, ctx):
                print("[telemetry] disabled via plugin.json (enabled=false)")
            def on_logs_fetched(self, ctx, logs):
                pass
            def on_ai_response(self, ctx, response, meta):
                pass
            def on_finish(self, ctx, result):
                pass
        return _Disabled()

    # Normal plugin
    try:
        return TelemetryPlugin(cfg=cfg)
    except Exception as e:
        # Fail-safe: never break the host app on plugin construction
        print(f"[telemetry] init error, running disabled: {e}")
        class _Fallback:
            name = "telemetry"
            version = data.get("version", "0.0.0")
            def on_start(self, ctx):
                pass
            def on_logs_fetched(self, ctx, logs):
                pass
            def on_ai_response(self, ctx, response, meta):
                pass
            def on_finish(self, ctx, result):
                pass
        return _Fallback()


# Loader looks for a module-level symbol named `plugin`.
plugin = _build_plugin()