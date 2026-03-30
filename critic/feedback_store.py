# critic/feedback_store.py
import json
import os
from datetime import datetime, timezone

FEEDBACK_FILE = "./feedback_log.jsonl"


def log_feedback(
    question: str,
    chunks: list[dict],
    answer: str,
    scores: dict,
):
    """
    Appends one feedback record to the JSONL store.
    Each line is a self-contained JSON object.
    """
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question":  question,
        "answer":    answer,
        "scores":    scores,
        "sources": [
            {
                "file":  c["file_path"],
                "name":  c["name"],
                "lines": f"{c['start_line']}–{c['end_line']}",
                "score": c["score"],
            }
            for c in chunks
        ],
    }

    os.makedirs(os.path.dirname(FEEDBACK_FILE) if os.path.dirname(FEEDBACK_FILE) else ".", exist_ok=True)

    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def load_feedback() -> list[dict]:
    """Loads all feedback records for analysis."""
    if not os.path.exists(FEEDBACK_FILE):
        return []
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def average_scores() -> dict:
    """Returns average critic scores across all logged queries."""
    records = load_feedback()
    if not records:
        return {}

    keys = ["faithfulness", "relevance", "completeness", "overall"]
    totals = {k: 0.0 for k in keys}
    count = 0

    for r in records:
        s = r.get("scores", {})
        if s.get("overall", -1) >= 0:   # skip failed critic calls
            for k in keys:
                totals[k] += s.get(k, 0)
            count += 1

    if count == 0:
        return {}

    return {k: round(totals[k] / count, 2) for k in keys}