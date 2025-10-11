import re
import click
import os
import subprocess

def handle_interactive_fixes(ai_output: str, container_name: str):
    """
    AI'nin Suggested fix bölümünden komutları tespit eder, kullanıcıya sorar ve uygular.
    """
    # Suggested fix bölümünü bul
    match = re.search(r"\*\*Suggested fix\:\*\*(.*?)(\n\n|$)", ai_output, re.S)
    if not match:
        click.echo("⚠️  Suggested fix bulunamadı.")
        return

    fixes_text = match.group(1)
    click.echo("\n🧩 Algılanan öneriler:")
    items = [x.strip("-•* \n") for x in fixes_text.split("\n") if x.strip()]
    for i, item in enumerate(items, 1):
        click.echo(f"  {i}. {item}")

    for i, item in enumerate(items, 1):
        if any(cmd in item for cmd in ["echo", "systemctl", "docker", "chmod"]):
            # Uygulanabilir komut varsa sor
            confirm = click.confirm(f"💡 Bu komutu uygulamak ister misin?\n👉 {item}", default=False)
            if confirm:
                try:
                    if "docker exec" in item:
                        subprocess.run(item, shell=True, check=True)
                    elif item.startswith("echo "):
                        # root gerektiren komutlar için sudo iste
                        subprocess.run(f"sudo {item}", shell=True, check=True)
                    else:
                        subprocess.run(item, shell=True, check=True)
                    click.echo("✅ Komut başarıyla uygulandı.")
                except Exception as e:
                    click.echo(f"❌ Hata oluştu: {e}")
        else:
            click.echo(f"🟢 {i}. (Yalnızca bilgi: {item})")
