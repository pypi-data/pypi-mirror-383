from fastapi import FastAPI, Depends
from dockai.server.auth import get_current_user
from dockai.core.openai_engine import analyze_with_openai

app = FastAPI(title="DockAI Cloud API")

@app.get("/")
def index():
    return {"status": "ok", "message": "DockAI Cloud API running"}

@app.post("/analyze")
def analyze_logs(payload: dict, user=Depends(get_current_user)):
    logs = payload.get("logs", "")
    result = analyze_with_openai(logs)
    return {"result": result, "user": user["email"]}
