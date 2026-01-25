from pathlib import Path
from datetime import datetime
import json

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "tickets.json"

VALID_STATUSES = {"Open", "In Progress", "Resolved", "Escalated"}
VALID_PRIORITIES = {"P1", "P2", "P3"}

class TicketStore:
    def __init__(self):
        self._tickets = self._load()

    def _load(self):
        if not DATA_PATH.exists():
            return []
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self):
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(self._tickets, f, indent=2)

    def _reload(self):
        self._tickets = self._load()

    def list_tickets(self):
        self._reload()
        return sorted(self._tickets, key=lambda x: x["id"])

    def get_ticket(self, ticket_id: str):
        self._reload()
        return next((t for t in self._tickets if t["id"] == ticket_id), None)

    def _next_id(self):
        nums = []
        for t in self._tickets:
            try:
                nums.append(int(t["id"].split("-")[1]))
            except Exception:
                pass
        nxt = (max(nums) + 1) if nums else 1
        return f"TKT-{nxt:03d}"

    def create_ticket(self, title, user, category, priority, symptoms):
        self._reload()
        if priority not in VALID_PRIORITIES:
            priority = "P3"

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ticket = {
            "id": self._next_id(),
            "title": title,
            "status": "Open",
            "priority": priority,
            "user": user,
            "category": category,
            "created_at": now,
            "updated_at": "",
            "symptoms": symptoms,
            "work_notes": []
        }

        self._tickets.append(ticket)
        self._save()
        return ticket

    def update_status(self, ticket_id, new_status):
        if new_status not in VALID_STATUSES:
            return False

        self._reload()
        t = next((x for x in self._tickets if x["id"] == ticket_id), None)
        if not t:
            return False

        t["status"] = new_status
        t["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save()
        return True

    def add_work_note(self, ticket_id, note):
        self._reload()
        t = next((x for x in self._tickets if x["id"] == ticket_id), None)
        if not t:
            return False

        t["work_notes"].append({
            "at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": note
        })
        t["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save()
        return True
