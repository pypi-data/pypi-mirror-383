import importlib, importlib.util, json, os, sys
from pathlib import Path
from typing import List, Tuple, Any
import pkgutil

DEBUG = os.getenv("DOCKAI_DEBUG") in ("1", "true", "True")

def _dbg(msg: str):
    if DEBUG:
        print(f"[plugins] {msg}")

USER_PLUGIN_ROOT = Path(os.path.expanduser("~/.dockai/plugins"))


def load_plugins() -> List[Tuple[Any, dict]]:
    """Deterministic loader (Option B):
    1) Discover built-in plugins via package scanning: dockai.plugins.<name>.plugin
    2) Overlay user plugins from ~/.dockai/plugins/<name>/plugin.py (user takes precedence)
    """
    plugins: List[Tuple[Any, dict]] = []
    seen = {}  # name -> index in plugins

    # Ensure user root exists (do not fail if missing)
    try:
        USER_PLUGIN_ROOT.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    # --- 1) PACKAGE-INTERNAL DISCOVERY (DETERMINISTIC) ---
    try:
        import dockai.plugins as pkg
        _dbg(f"pkg scan root: {pkg.__path__}")
        for modinfo in pkgutil.iter_modules(pkg.__path__):
            name = modinfo.name  # e.g., telemetry, hello, ...
            mod_path = f"dockai.plugins.{name}.plugin"
            try:
                # Respect built-in plugin.json (enabled flag)
                try:
                    base_mod = importlib.import_module(f"dockai.plugins.{name}")
                    from pathlib import Path as _P
                    desc_path = _P(base_mod.__file__).resolve().parent / "plugin.json"
                    if desc_path.exists():
                        try:
                            with open(desc_path, "r", encoding="utf-8") as _f:
                                _desc = json.load(_f) or {}
                            if _desc.get("enabled", True) is False:
                                _dbg(f"skip built-in {name} (disabled via plugin.json)")
                                continue
                        except Exception as e:
                            _dbg(f"descriptor read error for {desc_path}: {e}")
                except Exception as e:
                    _dbg(f"base package import failed for {name}: {e}")

                mod = importlib.import_module(mod_path)
                plugin = getattr(mod, "plugin", None)
                if plugin is None:
                    _dbg(f"skip {mod_path} (no 'plugin' symbol)")
                    continue
                idx = len(plugins)
                plugins.append((plugin, {}))
                seen[name] = idx
                _dbg(f"loaded built-in: {name} from {mod_path}")
            except Exception as e:
                _dbg(f"built-in load failed for {mod_path}: {e}")
                continue

        # If nothing loaded via pkgutil (editable/namespace/zipped cases), fallback to direct FS scan
        if not any(k for k in seen.keys()):
            try:
                import inspect
                pkg_file = inspect.getfile(pkg)
                pkg_root = Path(pkg_file).resolve().parent
                _dbg(f"pkg FS scan root: {pkg_root}")
                for child in pkg_root.iterdir():
                    try:
                        if not child.is_dir():
                            continue
                        if not (child / "plugin.py").exists():
                            continue
                        name = child.name
                        # Respect built-in plugin.json enabled flag
                        desc_path = child / "plugin.json"
                        if desc_path.exists():
                            try:
                                _desc = json.loads(desc_path.read_text(encoding="utf-8")) or {}
                                if _desc.get("enabled", True) is False:
                                    _dbg(f"skip built-in (fs) {name} (disabled via plugin.json)")
                                    continue
                            except Exception as e:
                                _dbg(f"descriptor read error for {desc_path}: {e}")
                        mod_path = f"dockai.plugins.{name}.plugin"
                        mod = importlib.import_module(mod_path)
                        plugin = getattr(mod, "plugin", None)
                        if plugin is None:
                            _dbg(f"skip {mod_path} (no 'plugin' symbol)")
                            continue
                        idx = len(plugins)
                        plugins.append((plugin, {}))
                        seen[name] = idx
                        _dbg(f"loaded built-in (fs): {name} from {mod_path}")
                    except Exception as e:
                        _dbg(f"built-in fs load failed for {child}: {e}")
                        continue
            except Exception as e:
                _dbg(f"pkg FS scan failed: {e}")
    except Exception as e:
        _dbg(f"package discovery error: {e}")

    # --- 2) USER DIRECTORY OVERLAY (~/.dockai/plugins) ---
    if USER_PLUGIN_ROOT.exists():
        _dbg(f"user scan root: {USER_PLUGIN_ROOT}")
        for item in USER_PLUGIN_ROOT.iterdir():
            try:
                if not item.is_dir():
                    _dbg(f"skip (not dir): {item}")
                    continue
                py = item / "plugin.py"
                if not py.exists():
                    _dbg(f"skip (no plugin.py): {py}")
                    continue

                # Read optional config/descriptor
                cfg: dict = {}
                cfg_path = item / "plugin.json"
                if cfg_path.exists():
                    try:
                        cfg = json.loads(cfg_path.read_text()) or {}
                    except Exception as e:
                        _dbg(f"cfg read error for {cfg_path}: {e}")
                        cfg = {}
                if cfg.get("enabled", True) is False:
                    _dbg(f"skip (disabled): {item}")
                    continue

                plug_name = (cfg.get("name") or item.name).strip()
                # Import user plugin with a unique, namespaced module name
                mod_name = f"user_plugins.{item.name}.plugin_{id(py)}"
                spec = importlib.util.spec_from_file_location(mod_name, str(py))
                if not spec or not spec.loader:
                    _dbg(f"spec load failed for {py}")
                    continue
                mod = importlib.util.module_from_spec(spec)
                sys.modules[mod_name] = mod
                spec.loader.exec_module(mod)  # type: ignore
                plugin = getattr(mod, "plugin", None)
                if plugin is None:
                    _dbg(f"skip user {item} (no 'plugin' symbol)")
                    continue

                # User precedence: replace built-in with the same name if exists
                if plug_name in seen:
                    idx = seen[plug_name]
                    plugins[idx] = (plugin, cfg)
                    _dbg(f"override built-in with user plugin: {plug_name} from {item}")
                else:
                    seen[plug_name] = len(plugins)
                    plugins.append((plugin, cfg))
                    _dbg(f"loaded user plugin: {plug_name} from {item}")
            except Exception as e:
                _dbg(f"user load failed for {item}: {e}")
                continue

    _dbg("loaded: " + ", ".join(getattr(p, "name", type(p).__name__) for p, _ in plugins))
    return plugins