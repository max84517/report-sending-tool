import json
import os

DRAFT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "draft.json")


def load_draft() -> dict:
    if not os.path.exists(DRAFT_FILE):
        return {"subject": "", "body": ""}
    with open(DRAFT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_draft(subject: str, body: str) -> None:
    with open(DRAFT_FILE, "w", encoding="utf-8") as f:
        json.dump({"subject": subject, "body": body}, f, indent=2, ensure_ascii=False)
