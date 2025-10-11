import click
from dockai.utils.docker_utils import get_logs
from dockai.core.openai_engine import analyze_with_openai
from dockai.core.ollama_engine import analyze_with_ollama
from dockai.core.formatter import print_colored
from dockai.core.config_manager import get_config

import os
import json

@click.group()
def cli():
    """DockAI: AI destekli Docker log analiz aracı"""
    pass

@cli.command()
@click.argument("container_name")
@click.option("--mode", default="local", help="AI mode: local veya cloud")
def analyze(container_name, mode):
    """Bir Docker container logunu analiz eder."""
    print_colored(f"🪶 Log alınıyor: {container_name}", "cyan")
    logs = get_logs(container_name)

    if not logs:
        print_colored("❌ Log alınamadı. Container adını kontrol et.", "red")
        return

    print_colored(f"🔍 {len(logs)} karakterlik log alındı.\n", "yellow")

    if mode == "cloud":
        cfg = get_config()
        print_colored("☁️ Cloud (OpenAI) modunda analiz ediliyor...", "magenta")
        result = analyze_with_openai(logs, cfg.get("OPENAI_API_KEY"))
    else:
        print_colored("💻 Local (Ollama) modunda analiz ediliyor...", "magenta")
        result = analyze_with_ollama(logs)

    print_colored("\n🤖 AI Analizi:\n", "green")
    print(result)

@cli.command()
def list():
    """Çalışan container'ları listeler."""
    import docker
    client = docker.from_env()
    containers = client.containers.list()
    if not containers:
        print("Hiç çalışan container yok.")
        return
    print("📦 Aktif container'lar:")
    for c in containers:
        print(f" - {c.name} ({c.image.tags[0] if c.image.tags else 'untagged'})")

CONFIG_FILE = os.path.expanduser("~/.dockai_config.json")

@cli.group()
def config():
    """Yapılandırma yönetimi (API key, model vs.)"""
    pass


@config.command("set")
@click.argument("key")
@click.argument("value")
def set_config(key, value):
    """Bir yapılandırma anahtarı ekle veya güncelle"""
    data = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                data = json.load(f)
            except Exception:
                data = {}

    data[key] = value
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

    click.echo(f"✅ {key} başarıyla kaydedildi.")


@config.command("get")
@click.argument("key")
def get_config(key):
    """Bir yapılandırma anahtarını görüntüle"""
    if not os.path.exists(CONFIG_FILE):
        click.echo("❌ Yapılandırma dosyası yok.")
        return
    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)
    value = data.get(key)
    if value:
        click.echo(f"{key} = {value}")
    else:
        click.echo(f"❌ {key} bulunamadı.")


@config.command("list")
def list_config():
    """Tüm yapılandırmaları listele"""
    if not os.path.exists(CONFIG_FILE):
        click.echo("❌ Yapılandırma dosyası yok.")
        return
    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)
    for k, v in data.items():
        click.echo(f"{k} = {v}")