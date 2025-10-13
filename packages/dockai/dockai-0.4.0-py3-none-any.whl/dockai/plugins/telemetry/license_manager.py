import os
import hashlib

def _norm(s: str | None) -> str:
    return (s or "").strip()

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def verify_license(cfg: dict) -> tuple[bool, str]:
    """
    Offline lisans doğrulama iskeleti.
    Dönüş: (valid, plan)  -> plan: "pro" | "free"
    Kurallar:
      - ENV DOCKAI_LICENSE_KEY varsa onu kullan.
      - config.license_key doluysa onu kullan.
      - DEMO- ile başlayan anahtarlar: geçerli ama "free" (limitli) sayılır.
      - Basit salt'lı hash kontrolü için kanca bırakıldı (örn. daha sonra whitelist).
    """
    key = os.getenv("DOCKAI_LICENSE_KEY") or (cfg.get("license_key") if cfg else "")
    key = _norm(key)

    # Demo anahtar: sınırlı mod (free)
    demo_prefix = _norm((cfg or {}).get("accepted_demo_prefix") or "DEMO-")
    if key.startswith(demo_prefix) and len(key) > len(demo_prefix):
        return True, "free"  # geçerli ama limitli

    if not key:
        return False, "free"

    # Basit salt + hash kancası (ileride gerçek whitelist ile değiştir)
    salt = _norm((cfg or {}).get("product_salt") or "DOCKAI-TELEMETRY-SALT")
    signature = _sha256(f"{salt}:{key}")

    # Örnek: "PRO-" ile başlayan anahtarları kabul et (gösterim amaçlı)
    # Gerçek üretimde signature whitelist dosyası / online verify ile bağla.
    if key.startswith("PRO-") and len(key) > 4:
        return True, "pro"

    # Signature tabanlı "pro" doğrulama kancası (şimdilik devre dışı)
    # allowed = {...}  # file/remote kaynaktan yüklenebilir
    # if signature in allowed: return True, "pro"

    # Default: anahtar geçersiz → free
    return False, "free"