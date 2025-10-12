# DockAI - Ollama local analysis engine (engine-only)
# Provides analyze_with_ollama(log_text, meta=None, container_name=None, freshness_threshold_minutes=None)

from __future__ import annotations

import os
import re
import json
import requests
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
import subprocess

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_API_GENERATE = f"{OLLAMA_HOST}/api/generate"

# Türkçe için iyi sonuç: qwen2.5 instruct ailesi
OLLAMA_MODEL = os.getenv("DOCKAI_OLLAMA_MODEL", "qwen2.5:7b-instruct")

SHOW_UNCERTAIN_NOTES = os.getenv("DOCKAI_SHOW_UNCERTAIN_NOTES", "false").lower() in ("1", "true", "yes")
FRESHNESS_THRESHOLD_MIN = int(os.getenv("DOCKAI_FRESHNESS_THRESHOLD_MIN", "30"))
SHOW_LIVE_STATUS = os.getenv("DOCKAI_SHOW_LIVE_STATUS", "true").lower() in ("1", "true", "yes")

# -----------------------------------------------------------------------------
# Helpers: timestamps / freshness
# -----------------------------------------------------------------------------

TS_PATTERNS = [
    r"(?P<iso>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)",
    r"(?P<isooff>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:\d{2}))",
    r"(?P<plain>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})",
]

def _extract_last_timestamp(text: str) -> Optional[str]:
    last = None
    for pat in TS_PATTERNS:
        for m in re.finditer(pat, text or ""):
            last = m.group(0)
    return last


def _parse_ts(ts: str) -> Optional[datetime]:
    try:
        if ts.endswith("Z"):
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return datetime.fromisoformat(ts)
    except Exception:
        return None

# -----------------------------------------------------------------------------
# Helpers: docker live status
# -----------------------------------------------------------------------------

def _safe_run(cmd: List[str], timeout: int = 3) -> str:
    try:
        out = subprocess.check_output(cmd, timeout=timeout, stderr=subprocess.STDOUT)
        return out.decode(errors="ignore").strip()
    except Exception:
        return ""


def _docker_ok() -> bool:
    return bool(_safe_run(["docker", "version"], timeout=3))


def _live_status(container_name: str) -> Dict[str, Optional[str]]:
    if not container_name:
        return {}
    running = _safe_run(["docker", "inspect", "-f", "{{.State.Running}}", container_name])
    status  = _safe_run(["docker", "inspect", "-f", "{{.State.Status}}",  container_name])
    restarts = _safe_run(["docker", "inspect", "-f", "{{.RestartCount}}",  container_name])
    health  = _safe_run(["docker", "inspect", "-f", "{{if .State.Health}}{{.State.Health.Status}}{{end}}", container_name])
    return {
        "running": running,
        "status": status,
        "restart_count": restarts,
        "health": health or None,
    }

# -----------------------------------------------------------------------------
# Core API call
# -----------------------------------------------------------------------------

def _call_ollama_generate(payload: Dict[str, Any]) -> str:
    resp = requests.post(OLLAMA_API_GENERATE, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data.get("response", "")

# -----------------------------------------------------------------------------
# Public function
# -----------------------------------------------------------------------------

def analyze_with_ollama(
    log_text: str,
    meta: Optional[Dict[str, Any]] = None,
    container_name: Optional[str] = None,
    freshness_threshold_minutes: Optional[int] = None,
) -> str:
    """
    Analyze Docker logs with a local Ollama model and return Markdown text.

    Usage:
        analyze_with_ollama(log_text, meta={"container":"web"})  |
        analyze_with_ollama(log_text, container_name="web")
    """
    meta = meta or {}

    # Freshness
    now_utc = datetime.now(timezone.utc)
    last_log_ts_str = _extract_last_timestamp(log_text or "")
    last_log_dt = _parse_ts(last_log_ts_str) if last_log_ts_str else None
    threshold_min = freshness_threshold_minutes if freshness_threshold_minutes is not None else FRESHNESS_THRESHOLD_MIN
    is_stale = False
    if last_log_dt:
        if last_log_dt.tzinfo is None:
            last_log_dt = last_log_dt.replace(tzinfo=timezone.utc)
        is_stale = (now_utc - last_log_dt) > timedelta(minutes=threshold_min)

    # Container name
    cn = (container_name or "").strip()
    if not cn and isinstance(meta, dict):
        cn = (meta.get("container") or meta.get("container_name") or "").strip()
    if not cn:
        cn = os.getenv("DOCKAI_CONTAINER", "").strip()

    docker_ok = _docker_ok()
    live = _live_status(cn) if (SHOW_LIVE_STATUS and cn and docker_ok) else {}

    # Meta to send
    meta_out = dict(meta)
    meta_out.update({
        "now": now_utc.isoformat(),
        "last_log_ts": last_log_ts_str,
        "freshness_threshold_min": threshold_min,
        "container": cn or meta.get("container") or meta.get("container_name"),
    })

    # Pre-triage (issue/ok hint)
    ERROR_SIGNS = [
        r"\b(ERROR|Exception|Unhandled|Traceback)\b",
        r"\b(ECONNREFUSED|ETIMEDOUT|EADDRINUSE)\b",
        r"\b(HTTP\/\d\.\d\" 5\d{2}| 5\d{2}\s+[A-Z]{3,6}\s)\b",
        r"\bOOMKilled\b",
        r"\bSegmentation fault\b",
    ]
    SUCCESS_SIGNS = [
        r"Ready on http://", r"compiled successfully", r"Started successfully",
        r"Listening on", r"server started", r"Next\.js.+ready",
    ]

    def _has_any(patterns: List[str], text: str) -> bool:
        for p in patterns:
            if re.search(p, text or "", flags=re.IGNORECASE):
                return True
        return False

    mode_hint = "neutral"
    if not _has_any(ERROR_SIGNS, log_text) and _has_any(SUCCESS_SIGNS, log_text):
        mode_hint = "ok"

    hint_line = ""
    if mode_hint == "ok":
        hint_line = "İpucu: Loglarda hata kanıtı yok, başarı sinyalleri var; büyük olasılıkla status='ok' olmalı.\n"

    prompt = (
        f"{hint_line}"
        "Aşağıdaki Docker logları için aşağıdaki ŞEMA ile UYUMLU TEK bir JSON döndür:\n"
        "{\n"
        '  "status": "ok" | "issue" | "unknown",\n'
        '  "summary": "<kısa özet>",\n'
        '  "root_cause": "<kök neden, yalnızca status=\'issue\' ise>",\n'
        '  "fix": ["<adım1>", "<adım2>"],\n'
        '  "commands": ["<güvenli_docker/uygulama_komutları>"],\n'
        '  "evidence": ["<logtan kanıt satırı veya anahtar bulgu>"],\n'
        '  "confidence": "<low|medium|high>",\n'
        '  "notes": "<belirsizlikler/ek veri isteği>",\n'
        '  "performans_yorumu": "<kısa yorum>"\n'
        "}\n"
        "Kurallar:\n"
        "- Eğer ciddi bir sorun işareti yoksa 'status'='ok' yaz ve 'fix' ile 'commands' BOŞ olsun.\n"
        "- 'status'='issue' ise mutlaka 'evidence' alanında somut kanıt ver. Kanıt; log satırı (örn. ERROR/Exception/5xx/OOMKilled) veya METAVERİ içindeki performans sayıları (örn. CPU p95=%92, Mem p95=%84) olabilir.\n"
        "- METAVERİ.'perf' mevcutsa bu sayıları mutlaka değerlendir; log yoksa yalnızca METAVERİ üzerinden yorum yap ve bu durumu 'notes' içinde belirt.\n"
        "- Docker ile ilgisiz ise 'unknown' yaz ve 'notes' alanında hangi ek veriye ihtiyaç olduğunu belirt.\n"
        "- Yanıt kesinlikle GEÇERLİ JSON olsun; açıklama metni ekleme.\n"
        "- Performans değerlendirmesi: METAVERİ.'perf' mevcutsa, CPU/mem değerlerini analiz et ve kısa bir 'performans_yorumu' alanı ekle (örn. 'CPU kullanımı düşük, sistem stabil' veya 'Bellek kullanımı yüksek, optimizasyon önerilir').\n"
        "- ŞEMA alanları: status, summary, root_cause, fix, commands, evidence, confidence, notes, performans_yorumu.\n\n"
        f"METAVERİ:\n{json.dumps(meta_out, ensure_ascii=False)}\n\n"
        f"LOGS:\n{(log_text or '')[:4000]}"
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.15, "top_p": 0.9},
        "format": "json",
    }

    try:
        output_text = _call_ollama_generate(payload)
    except requests.HTTPError as e:
        return f"❌ Ollama isteği başarısız: {e.response.status_code} {e.response.text}"
    except Exception as e:
        return f"❌ Ollama isteği başarısız: {e}"

    # Try to parse JSON
    try:
        parsed = json.loads(output_text)
    except json.JSONDecodeError:
        plain = output_text.strip()
        if SHOW_LIVE_STATUS:
            live = _live_status(cn) if cn and _docker_ok() else {}
            if live:
                lines = ["\n\n**Canlı Durum (özet):**"]
                if live.get("running") != "":
                    lines.append(f"- Çalışıyor: {'Evet' if str(live['running']).lower() in ('true','1') else 'Hayır'}")
                if live.get("status"):
                    lines.append(f"- Status: {live['status']}")
                if live.get("restart_count") not in (None, ""):
                    lines.append(f"- Restart (toplam): {live['restart_count']}")
                if live.get("health") is not None:
                    lines.append(f"- Health: {live['health']}")
                if last_log_ts_str:
                    lines.append(f"- Son log zamanı: {last_log_ts_str}")
                plain += "\n" + "\n".join(lines)
        return plain

    status = parsed.get("status", "unknown")
    summary = parsed.get("summary", "")
    root_cause = parsed.get("root_cause", "")
    fix = parsed.get("fix", []) or []
    commands = parsed.get("commands", []) or []
    evidence = parsed.get("evidence", []) or []
    confidence = parsed.get("confidence", "")
    notes = parsed.get("notes", "")
    perf_comment = parsed.get("performans_yorumu", "")
    if not perf_comment:
        try:
            perf = meta_out.get("perf") or meta.get("perf")
        except Exception:
            perf = None
        if perf:
            cpu_p95 = (perf.get("cpu") or {}).get("p95")
            mem_p95 = (perf.get("mem_perc") or {}).get("p95")
            try:
                cpu_p95 = float(cpu_p95) if cpu_p95 is not None else None
                mem_p95 = float(mem_p95) if mem_p95 is not None else None
            except Exception:
                cpu_p95 = mem_p95 = None
            if cpu_p95 is not None and mem_p95 is not None:
                if cpu_p95 < 10 and mem_p95 < 20:
                    perf_comment = "CPU ve bellek kullanımı düşük, sistem stabil."
                elif cpu_p95 >= 85 or mem_p95 >= 80:
                    perf_comment = f"Yüksek kaynak kullanımı: CPU p95={cpu_p95}%, Mem p95={mem_p95}%; ölçeklendirme/optimizasyon değerlendirilmeli."
                else:
                    perf_comment = f"Kaynak kullanımı orta seviyede (CPU p95={cpu_p95}%, Mem p95={mem_p95}%)."

    md: List[str] = []

    if last_log_ts_str:
        if is_stale:
            md.append(f"⚠️ Bu analiz eski loglara dayanıyor (son log: {last_log_ts_str}). Sorun şu anda tekrarlamıyor olabilir.")
    else:
        md.append("ℹ️ Loglarda zaman damgası bulunamadı; tazelik doğrulanamadı.")

    if status == "ok":
        md.append("✅ Sorun tespit edilmedi (status=ok).")
        if summary:
            md.append(f"**Özet:** {summary}")
    elif status == "issue":
        if summary:
            md.append(f"**Özet:** {summary}")
        if root_cause:
            md.append(f"**Kök Neden:** {root_cause}")
        if evidence:
            md.append("**Kanıt:**\n" + "\n".join([f"- {e}" for e in evidence[:5]]))
        if fix:
            md.append("**Çözüm Adımları:**\n" + "\n".join([f"- {step}" for step in fix]))
        if commands:
            md.append("**Komutlar:**\n" + "\n".join([f"`{cmd}`" for cmd in commands]))
    else:
        if summary:
            md.append(f"**Özet:** {summary}")
        if root_cause:
            md.append(f"**Kök Neden:** {root_cause}")
        if fix:
            md.append("**Çözüm Adımları:**\n" + "\n".join([f"- {step}" for step in fix]))
        if commands:
            md.append("**Komutlar:**\n" + "\n".join([f"`{cmd}`" for cmd in commands]))

    if confidence:
        md.append(f"**Güven:** {confidence}" if status == "ok" else f"**Güven:** {status} / {confidence}")

    if notes:
        normalized = str(notes).lower()
        if SHOW_UNCERTAIN_NOTES or ("belirsiz" not in normalized):
            md.append(f"**Notlar:** {notes}")
    if perf_comment:
        md.append(f"**Performans Yorumu:** {perf_comment}")

    if SHOW_LIVE_STATUS:
        live = _live_status(cn) if (cn and docker_ok) else {}
        if live:
            md.append("**Canlı Durum (özet):**")
            lines = []
            if live.get("running") != "":
                lines.append(f"- Çalışıyor: {'Evet' if str(live['running']).lower() in ('true','1') else 'Hayır'}")
            if live.get("status"):
                lines.append(f"- Status: {live['status']}")
            if live.get("restart_count") not in (None, ""):
                lines.append(f"- Restart (toplam): {live['restart_count']}")
            if live.get("health") is not None:
                lines.append(f"- Health: {live['health']}")
            if last_log_ts_str:
                lines.append(f"- Son log zamanı: {last_log_ts_str}")
            if lines:
                md.append("\n".join(lines))

    return "\n\n".join(md) if md else (output_text.strip() or "Analiz tamamlandı.")