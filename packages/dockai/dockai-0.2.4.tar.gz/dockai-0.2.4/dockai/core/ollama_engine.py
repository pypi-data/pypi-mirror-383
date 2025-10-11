import json
import requests

def analyze_with_ollama(log_text, lang="tr"):
    """
    Ollama'yı kullanarak yerel (local) AI analizi yapar.
    Ollama sistemde 11434 portunda çalışıyor olmalıdır.
    Örn: ollama run mistral
    """
    try:
        # Dil yönergesi (sadece prompt'a enjekte edilir)
        if lang == "tr":
            lang_instr = "Lütfen YALNIZCA Türkçe yanıt ver."
        elif lang == "en":
            lang_instr = "Please respond ONLY in English."
        else:
            # bilinmeyen dil kodu gelirse İngilizceye düş
            lang_instr = "Please respond ONLY in English."

        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "llama3",
            "prompt": f"""
            You are an AI DevOps assistant. {lang_instr}
            Analyze these Docker logs and explain:
            1. What went wrong
            2. Possible cause
            3. Suggested fix
            Logs:
            {log_text[:4000]}
            """
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)

        if response.status_code != 200:
            return f"Ollama API hatası: {response.text}"

        # Ollama streaming output döner, bu yüzden 'response.text' satır satır işlenir
        output = ""
        for line in response.text.splitlines():
            try:
                data = json.loads(line)
                if "response" in data:
                    output += data["response"]
            except json.JSONDecodeError:
                continue

        return output.strip() if output else "Ollama'dan yanıt alınamadı."
    except Exception as e:
        return f"Ollama bağlantı hatası: {e}"
