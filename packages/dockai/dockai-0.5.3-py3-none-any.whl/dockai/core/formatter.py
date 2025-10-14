from termcolor import colored

def print_colored(text, color="white", attrs=None):
    """
    CLI çıktısını renkli yazdırmak için yardımcı fonksiyon.
    Örn: print_colored("Başarılı", "green", ["bold"])
    """
    try:
        print(colored(text, color, attrs=attrs or []))
    except Exception:
        # Eğer termcolor yoksa düz yazdır
        print(text)
