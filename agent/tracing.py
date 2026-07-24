import json
import os
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "trace.jsonl")

def reset_log() -> None:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")

def log_step(step: int, tool_name: str, args: dict, result: any, error: str = None) -> None:
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "step": step,
        "tool": tool_name,
        "args": args,
        "result": result,
        "error": error
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")