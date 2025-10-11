import os
import json
import click
from dotenv import load_dotenv

from dockai.utils.docker_utils import get_logs
from dockai.core.openai_engine import analyze_with_openai
from dockai.core.ollama_engine import analyze_with_ollama
# from dockai.core.formatter import print_colored  # kullanılmıyor, şimdilik kapattım
# from dockai.core.config_manager import get_config  # isim çakışıyordu, kapattım

# .env otomatik yükle
load_dotenv()

CONFIG_FILE = os.path.expanduser("~/.dockai_config.json")

@click.group()
def cli():
    """DockAI: AI destekli Docker log analiz aracı"""
    pass



@cli.command()
@click.option(
    "--mode",
    type=click.Choice(["local", "cloud", "auto"], case_sensitive=False),
    default="local",
    help="AI mode: local, cloud veya auto"
)
@click.option("-i", "--interactive", is_flag=True, help="AI'nin önerilerini etkileşimli uygula")
@click.argument("container_name")
def analyze(mode, interactive, container_name):
    """Bir Docker container logunu analiz eder."""
    try:
        logs = get_logs(container_name)
    except Exception as e:
        click.secho(f"❌ Log okunamadı: {e}", fg="red")
        return

    if not logs or not logs.strip():
        click.secho("⚠️  Log boş görünüyor. Container adı doğru mu, log üretiyor mu?", fg="yellow")
        return

    click.echo(f"🪶 Log alındı: {len(logs)} karakter.")
    click.echo(f"🔍 {mode} modunda analiz ediliyor...")

    try:
        if mode.lower() == "cloud":
            response = analyze_with_openai(logs)
        elif mode.lower() == "local":
            response = analyze_with_ollama(logs)
        else:  # auto
            # Basit auto: önce local dene, olmazsa cloud
            try:
                response = analyze_with_ollama(logs)
            except Exception:
                response = analyze_with_openai(logs)
    except Exception as e:
        click.secho(f"❌ Analiz sırasında hata: {e}", fg="red")
        return

    click.echo("\n🤖 AI Analizi:\n")
    click.echo(response)

    if interactive:
        try:
            from dockai.core.fix_suggester import handle_interactive_fixes
            handle_interactive_fixes(response, container_name)
        except Exception as e:
            click.secho(f"⚠️  Interactive fix uygulanamadı: {e}", fg="yellow")


@cli.command()
def list():
    """Çalışan container'ları listeler."""
    try:
        import docker
        client = docker.from_env()
        containers = client.containers.list()
    except Exception as e:
        click.secho(f"❌ Docker'a bağlanılamadı: {e}", fg="red")
        return

    if not containers:
        click.echo("ℹ️  Hiç çalışan container yok.")
        return

    click.echo("📦 Aktif container'lar:")
    for c in containers:
        tag = (c.image.tags[0] if c.image.tags else "untagged")
        click.echo(f" - {c.name} ({tag})")


@cli.group()
def config():
    """Yapılandırma yönetimi (API key, model vs.)"""
    pass


@config.command("set")
@click.argument("key")
@click.argument("value")
def set_config(key, value):
    """Bir yapılandırma anahtarı ekle veya güncelle."""
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