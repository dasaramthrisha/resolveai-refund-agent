import json
import os
from datetime import datetime

LOG_FILE = os.path.join("logs", "decisions.log")


def log_decision(message, analysis, reply, result):
    os.makedirs("logs", exist_ok=True)
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message,
        "reason": analysis.get("reason"),
        "final": result["final"],
        "note": result["note"],
        "agent_reply": reply,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def read_logs(limit=10):
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, encoding="utf-8") as f:
        lines = f.readlines()
    return [json.loads(line) for line in lines[-limit:]][::-1]