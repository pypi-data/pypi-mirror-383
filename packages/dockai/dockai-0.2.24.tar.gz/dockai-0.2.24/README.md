# 🐳 DockAI – AI-powered Docker Log Analysis Tool (CLI + Cloud)

DockAI is an intelligent CLI tool that analyzes Docker container logs using **Large Language Models (LLMs)**.
It helps developers, DevOps engineers, and system administrators quickly identify issues, summarize logs, and provide actionable insights.

---

## 🚀 Features

* **AI Log Analysis**
  Understands and summarizes logs using LLMs, identifying possible root causes and suggesting solutions.

* **Performance Monitoring (CPU & Memory)**
  Measure container performance in real-time or over a time window using `--perf` or `--instant-perf`.

* **Local & Cloud AI Modes (Ollama + OpenAI)**
  Analyze with a local model (e.g., `llama3`) or cloud-based OpenAI API:

  ```bash
  dockai analyze my-container --mode local
  dockai analyze my-container --mode cloud
  ```

* **Live Container Status**
  Even when no logs are generated, DockAI provides a live summary including container status, restart count, and health.

* **Simple CLI Usage**

  ```bash
  dockai analyze <container-name> --since 15m --tail 3000
  ```

---

## 📊 Example Output

```
🤖 AI Analysis:
**Summary:** Database connection failed.
**Root Cause:** TCP/IP connection refused.
**Solution:** 
- Restart the database service inside the Docker container.
- Check port accessibility and network configuration.

⚙️ Performance
- CPU p95: 0.3% | max: 1.1%
- Mem p95: 12.7%
```

---

## 🧠 Supported Models

* Local: `Ollama` (e.g., `llama3`, `mistral`, `gemma`)
* Cloud: `OpenAI GPT-4`, `GPT-4o-mini`

### 🔧 Default Model

By default, DockAI uses:

```bash
DOCKAI_OLLAMA_MODEL = "qwen2.5:7b-instruct"
```

This model offers excellent multilingual support (including Turkish 🇹🇷) and strong technical reasoning for analyzing Docker logs.

To override the model, set an environment variable:

```bash
export DOCKAI_OLLAMA_MODEL="aya:23b"
```

---

## ⚙️ Installation

```bash
pip install dockai
```

### 🧩 Ollama Installation (All Platforms)

#### macOS

```bash
brew install ollama
ollama pull qwen2.5:7b-instruct
```

#### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:7b-instruct
```

#### Windows (PowerShell)

```powershell
winget install Ollama.Ollama
ollama pull qwen2.5:7b-instruct
```

> 💡 **Tip:** DockAI automatically uses the model defined in the environment variable `DOCKAI_OLLAMA_MODEL` (default: `qwen2.5:7b-instruct`).

---

## 🧩 Developer Commands

```bash
make build       # build the package
make publish     # publish to PyPI
make testpublish # publish to TestPyPI
```

---

## 🧾 License

Apache License 2.0
Copyright (c) 2025 Ahmet Atakan
