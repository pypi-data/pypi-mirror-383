
import os
import subprocess

def get_logs(container_name: str, since: str | None = None, tail: int | None = None) -> str:
    """
    Docker loglarını toplar.
    Parametreler verilmezse varsayılanları kullanır:
      - since: 15m  (env: DOCKAI_LOG_SINCE ile değiştirilebilir)
      - tail : 3000 (env: DOCKAI_LOG_TAIL  ile değiştirilebilir)
    """
    default_since = os.getenv("DOCKAI_LOG_SINCE", "15m")
    default_tail  = int(os.getenv("DOCKAI_LOG_TAIL", "3000"))

    # Parametre verilmezse varsayılanları uygula
    s = since if (since is not None and str(since).strip()) else default_since
    t = tail if (tail is not None) else default_tail

    cmd = ["docker", "logs", container_name]
    if s:
        cmd += ["--since", str(s)]
    if t:
        cmd += ["--tail", str(int(t))]

    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return out.decode("utf-8", errors="ignore")
    except subprocess.CalledProcessError as e:
        return e.output.decode("utf-8", errors="ignore")
    except Exception as e:
        raise RuntimeError(f"docker logs çağrısı başarısız: {e}")

def docker_version_ok(timeout: int = 3) -> bool:
    """Docker CLI erişimi hızlıca doğrula."""
    try:
        subprocess.check_output(["docker", "version"], timeout=timeout, stderr=subprocess.STDOUT)
        return True
    except Exception:
        return False
