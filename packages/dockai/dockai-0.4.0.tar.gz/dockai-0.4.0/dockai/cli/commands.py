import os
import time
import subprocess

import json
import click
from dotenv import load_dotenv

# plugins loader (fail-safe)
try:
    from dockai.plugins.loader import load_plugins
except Exception:  # if loader is missing or fails, keep CLI working
    def load_plugins():
        return []

from dockai.utils.docker_utils import get_logs as docker_get_logs
from dockai.core.openai_engine import analyze_with_openai
from dockai.core.ollama_engine import analyze_with_ollama
# from dockai.core.formatter import print_colored  # kullanılmıyor, şimdilik kapattım
# from dockai.core.config_manager import get_config  # isim çakışıyordu, kapattım

# .env otomatik yükle
load_dotenv()


CONFIG_FILE = os.path.expanduser("~/.dockai_config.json")

# --- Config helpers (config > env > default) ---

def _read_json_config() -> dict:
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f) or {}
    except Exception:
        pass
    return {}


def cfg_get(name: str, default=None):
    """Return value with priority: CONFIG > ENV > default."""
    cfg = _read_json_config()
    if name in cfg and cfg.get(name) not in (None, ""):
        return cfg.get(name)
    env_val = os.getenv(name)
    if env_val not in (None, ""):
        return env_val
    return default

# --- Live status (best-effort) ---
def _print_live_status(container_name: str) -> None:
    """Print a short live status block even when logs are empty."""
    def _safe(cmd):
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=3)
            return out.decode(errors="ignore").strip()
        except Exception:
            return ""
    running  = _safe(["docker", "inspect", "-f", "{{.State.Running}}", container_name])
    status   = _safe(["docker", "inspect", "-f", "{{.State.Status}}",  container_name])
    restarts = _safe(["docker", "inspect", "-f", "{{.RestartCount}}",  container_name])
    health   = _safe(["docker", "inspect", "-f", "{{if .State.Health}}{{.State.Health.Status}}{{end}}", container_name])

    lines = []
    lines.append("**Canlı Durum (özet):**")
    if running != "":
        lines.append(f"- Çalışıyor: {'Evet' if running.lower() in ('true','1') else 'Hayır'}")
    if status:
        lines.append(f"- Status: {status}")
    if restarts not in ("", None):
        lines.append(f"- Restart (toplam): {restarts}")
    if health:
        lines.append(f"- Health: {health}")
    click.echo("\n".join(lines))

# --- Performance sampling helpers ---
def _percent_to_float(s: str) -> float:
    try:
        return float(str(s).replace('%', '').strip())
    except Exception:
        return 0.0

def _sample_docker_stats(container: str, duration_sec: int = 60, interval_sec: float = 1.0) -> list[str]:
    """
    Sample `docker stats --no-stream` output at fixed intervals.
    Returns lines like: "12.34%|512MiB / 2GiB|25.6%|12|1.2MB / 800kB|0B / 0B"
    """
    series = []
    if duration_sec <= 0:
        return series
    end = time.time() + duration_sec
    fmt = "{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}|{{.PIDs}}|{{.NetIO}}|{{.BlockIO}}"
    while time.time() < end:
        try:
            out = subprocess.check_output(
                ["docker", "stats", container, "--no-stream", "--format", fmt],
                stderr=subprocess.STDOUT
            ).decode(errors="ignore").strip()
            if out:
                series.append(out)
        except Exception:
            pass
        time.sleep(max(0.1, interval_sec))
    return series

def _parse_docker_stats(series: list[str]) -> dict:
    """Parse docker stats lines and compute aggregates for CPU% and Mem%."""
    cpu_vals, mem_perc_vals = [], []
    for line in series:
        parts = line.split("|")
        if len(parts) < 3:
            continue
        cpu_vals.append(_percent_to_float(parts[0]))
        mem_perc_vals.append(_percent_to_float(parts[2]))
    def _agg(xs):
        if not xs:
            return None
        xs_sorted = sorted(xs)
        p95_idx = max(0, int(0.95 * len(xs_sorted)) - 1)
        return {
            "avg": round(sum(xs_sorted) / len(xs_sorted), 2),
            "p95": round(xs_sorted[p95_idx], 2),
            "max": round(xs_sorted[-1], 2),
        }
    return {
        "cpu": _agg(cpu_vals),
        "mem_perc": _agg(mem_perc_vals),
    }
# --- end helpers ---

@click.group()
def cli():
    """DockAI: AI destekli Docker log analiz aracı"""
    pass



@cli.command()
@click.option(
    "--mode",
    type=click.Choice(["local", "cloud", "auto"], case_sensitive=False),
    default=None,
    help="AI mode: local, cloud veya auto. Boşsa önce config (DOCKAI_MODE), yoksa 'cloud'."
)
@click.option(
    "--since",
    default="15m",
    show_default=True,
    help="Log tazelik penceresi (örn: 15m, 2h, 1d). Varsayılan 15m."
)
@click.option(
    "--tail",
    type=int,
    default=3000,
    show_default=True,
    help="Son N satır. Varsayılan 3000."
)
@click.option(
    "--perf",
    type=int,
    default=0,
    show_default=True,
    help="Performans örnekleme süresi (saniye). 0=kapalı. Örn: --perf 60"
)
@click.option(
    "--instant-perf",
    is_flag=True,
    default=True,
    help="Anlık performans ölçümü (docker stats tek sefer). Varsayılan: açık, beklemeden sonuç döner."
)
@click.argument("container_name")
def analyze(mode, since, tail, perf, instant_perf, container_name):
    """Bir Docker container logunu analiz eder."""
    # --- Plugin lifecycle: on_start ---
    plugins = load_plugins()
    ctx = {
        "container_name": container_name,
        "since": since,
        "tail": tail,
    }
    for p, cfg in plugins:
        try:
            if hasattr(p, "on_start"):
                p.on_start(ctx)
        except Exception:
            pass
    # Mode resolution: CLI > CONFIG > ENV > default('cloud')
    def _norm(x):
        return x.strip().lower() if isinstance(x, str) else x

    env_mode = os.getenv("DOCKAI_MODE")
    cfg_mode = _read_json_config().get("DOCKAI_MODE")
    # Precedence: CLI > CONFIG > ENV > default('cloud')
    effective_mode = _norm(mode) or _norm(cfg_mode) or _norm(env_mode) or "cloud"

    if os.getenv("DOCKAI_DEBUG") in ("1", "true", "True"):
        click.echo(f"🔧 mode(cli)={mode} cfg={cfg_mode} env={env_mode} -> effective={effective_mode}")
    # Instant performance sampling
    if instant_perf:
        click.echo("⚡ Anlık performans ölçümü alınıyor...")
        try:
            out = subprocess.check_output(
                ["docker", "stats", container_name, "--no-stream", "--format",
                 "{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}|{{.PIDs}}|{{.NetIO}}|{{.BlockIO}}"],
                stderr=subprocess.STDOUT
            ).decode(errors="ignore").strip()
            meta = {"perf": _parse_docker_stats([out])}
        except Exception as e:
            click.secho(f"❌ Anlık performans ölçümü başarısız: {e}", fg="red")
            meta = {}
    else:
        meta = {}

    try:
        logs = docker_get_logs(container_name, since=since, tail=tail)
    except Exception as e:
        for p, cfg in plugins:
            try:
                if hasattr(p, "on_error"):
                    p.on_error(ctx, e)
            except Exception:
                pass
        click.secho(f"❌ Log okunamadı: {e}", fg="red")
        return

    for p, cfg in plugins:
        try:
            if hasattr(p, "on_logs_fetched"):
                p.on_logs_fetched({**ctx, "meta": {}}, logs or "")
        except Exception:
            pass

    click.echo(f"🕒 Pencere: since={since}  tail={tail}")

    if not instant_perf and perf and perf > 0:
        click.echo(f"⏱ Performans örnekleme başlıyor: {perf}s")
        series = _sample_docker_stats(container_name, duration_sec=perf, interval_sec=1.0)
        meta["perf"] = _parse_docker_stats(series)

    if not logs or not logs.strip():
        click.secho(f"⚠️  Son {since} penceresinde log bulunamadı veya log üretimi tespit edilemedi.", fg="yellow")
        click.echo("💡 İpucu: Container çalışıyor olabilir ancak bu zaman aralığında log üretmemiş.")
        click.echo("   Daha geniş bir aralıkla denemek için örnek:")
        click.echo(f"   dockai analyze {container_name} --since 1h --tail 10000")
        click.echo("   veya geçmiş tüm logları görmek için:")
        click.echo(f"   dockai analyze {container_name} --since 24h --tail 200000")
        _print_live_status(container_name)

        # Eğer performans verisi varsa, log yokken de AI analizi yap
        if meta.get("perf"):
            click.echo("ℹ️ Log yok; performans verilerine dayalı analiz yapılıyor...")
            click.echo(f"🔍 {effective_mode} modunda analiz ediliyor...")
            try:
                if effective_mode.lower() == "cloud":
                    response = analyze_with_openai(
                        "",
                        container_name=container_name,
                        meta=meta,
                    )
                elif effective_mode.lower() == "local":
                    response = analyze_with_ollama(
                        "",
                        container_name=container_name,
                        meta=meta,
                    )
                else:  # auto
                    try:
                        response = analyze_with_ollama(
                            "",
                            container_name=container_name,
                            meta=meta,
                        )
                    except Exception:
                        response = analyze_with_openai(
                            "",
                            container_name=container_name,
                            meta=meta,
                        )
                click.echo("\n")
                click.echo(response)
            except Exception as e:
                click.secho(f"❌ Analiz sırasında hata: {e}", fg="red")

            # Perf özetini yaz
            cpu = meta["perf"].get("cpu")
            mem = meta["perf"].get("mem_perc")
            lines = ["\n⚙️ Performans"]
            if perf and perf > 0:
                lines[0] += f" ({perf}s):"
            elif instant_perf:
                lines[0] += " (instant)"
            if cpu:
                lines.append(f"- CPU p95: {cpu.get('p95')}% | max: {cpu.get('max')}%")
            if mem:
                lines.append(f"- Mem p95: {mem.get('p95')}%")
            click.echo("\n".join(lines))
        return

    click.echo(f"🪶 Log alındı: {len(logs)} karakter.")
    click.echo(f"🔍 {effective_mode} modunda analiz ediliyor...")

    try:
        if effective_mode.lower() == "cloud":
            response = analyze_with_openai(
                logs,
                container_name=container_name,
                meta=meta,
            )
        elif effective_mode.lower() == "local":
            response = analyze_with_ollama(
                logs,
                container_name=container_name,
                meta=meta,
            )
        else:  # auto
            try:
                response = analyze_with_ollama(
                    logs,
                    container_name=container_name,
                    meta=meta,
                )
            except Exception:
                response = analyze_with_openai(
                    logs,
                    container_name=container_name,
                    meta=meta,
                )
    except Exception as e:
        for p, cfg in plugins:
            try:
                if hasattr(p, "on_error"):
                    p.on_error({**ctx, "meta": meta}, e)
            except Exception:
                pass
        click.secho(f"❌ Analiz sırasında hata: {e}", fg="red")
        return

    for p, cfg in plugins:
        try:
            if hasattr(p, "on_ai_response"):
                p.on_ai_response({**ctx, "meta": meta}, response, meta)
        except Exception:
            pass

    click.echo("\n")
    click.echo(response)
    if meta.get("perf"):
      cpu = meta["perf"].get("cpu")
      mem = meta["perf"].get("mem_perc")
      lines = ["\n⚙️ Performans"]
      if perf and perf > 0:
          lines[0] += f" ({perf}s):"
      if cpu:
          lines.append(f"- CPU p95: {cpu['p95']}% | max: {cpu['max']}%")
      if mem:
          lines.append(f"- Mem p95: {mem['p95']}%")
      click.echo("\n".join(lines))

    result = {"response": response}
    for p, cfg in plugins:
        try:
            if hasattr(p, "on_finish"):
                p.on_finish({**ctx, "meta": meta}, result)
        except Exception:
            pass


@cli.command()
def list():
    """Çalışan container'ları listeler (CLI tabanlı)."""
    try:
        out = subprocess.check_output(
            ["docker", "ps", "--format", "{{json .}}"],
            stderr=subprocess.STDOUT,
            timeout=5
        ).decode("utf-8", errors="ignore").strip()
    except Exception as e:
        click.secho(f"❌ Docker CLI ile listelenemedi: {e}", fg="red")
        return

    if not out:
        click.echo("ℹ️  Hiç çalışan container yok.")
        return

    click.echo("📦 Aktif container'lar:")
    for line in out.splitlines():
        try:
            item = json.loads(line)
            name = item.get("Names") or item.get("Name") or "-"
            image = item.get("Image") or "untagged"
            click.echo(f" - {name} ({image})")
        except Exception:
            pass


@cli.group()
def config():
    """
    Yapılandırma yönetimi (API key, model vs.)

    \b
    🔹 Common keys:
      - OPENAI_API_KEY      → OpenAI API anahtarınızı ekler.
      - DOCKAI_LANG         → Çıktı dili (Turkish | English).
      - DOCKAI_OLLAMA_MODEL → Ollama modeli (örn. qwen2.5:7b-instruct).
      - DOCKAI_CONFIG_PATH  → Özel config dosya yolu belirtir.
      - DOCKAI_DEBUG        → 1 (veya true) ise debug loglarını gösterir.
      - DOCKAI_MODE         → AI modu (local | cloud)
    """
    pass


# Ensure `config` command group exists before attaching subcommands
try:
    config  # type: ignore[name-defined]
except NameError:
    @cli.group()
    def config():
        """Config management commands."""
        pass
@config.command("set")
@click.argument("key")
@click.argument("value")
def set_config(key, value):
    """
    Set a configuration key-value pair.

    \b
    🔹 Common keys:
      - OPENAI_API_KEY      → OpenAI API anahtarınızı ekler.
      - DOCKAI_LANG         → Çıktı dili (Turkish | English).
      - DOCKAI_OLLAMA_MODEL → Ollama modeli (örn. qwen2.5:7b-instruct).
      - DOCKAI_CONFIG_PATH  → Özel config dosya yolu belirtir.
      - DOCKAI_DEBUG        → 1 (veya true) ise debug loglarını gösterir.
    """
    data = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f) or {}
        except Exception:
            data = {}

    data[key] = value
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

    click.secho(f"✅ {key} başarıyla kaydedildi.", fg="green")


@config.command("get")
@click.argument("key")
def get_config_value(key):
    """Bir yapılandırma anahtarını görüntüle."""
    if not os.path.exists(CONFIG_FILE):
        click.secho("❌ Yapılandırma dosyası yok.", fg="red")
        return
    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)
    value = data.get(key)
    if value:
        click.echo(f"{key} = {value}")
    else:
        click.secho(f"❌ {key} bulunamadı.", fg="yellow")


@config.command("list")
def list_config():
    """Tüm yapılandırmaları listele."""
    if not os.path.exists(CONFIG_FILE):
        click.secho("❌ Yapılandırma dosyası yok.", fg="red")
        return
    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)
    if not data:
        click.echo("ℹ️  Kayıtlı yapılandırma yok.")
        return
    for k, v in data.items():
        click.echo(f"{k} = {v}")