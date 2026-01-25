from pathlib import Path
from datetime import datetime
import json

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "tickets.json"

VALID_STATUSES = {"Open", "In Progress", "Resolved", "Escalated"}
VALID_PRIORITIES = {"P1", "P2", "P3"}


def _utc_now_iso() -> str:
    # Example: 2026-01-25T02:13:44Z
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class TicketStore:
    def __init__(self, data_path: Path = DATA_PATH):
        self.data_path = data_path
        self._tickets: List[Dict[str, Any]] = self._load()

    def _load(self) -> List[Dict[str, Any]]:
        if not self.data_path.exists():
            return []
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            # If file is corrupted, fail safely instead of crashing the app
            return []

    def _atomic_write(self, data: List[Dict[str, Any]]) -> None:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)

        tmp_path = self.data_path.with_suffix(".json.tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Atomic replace on most OSes
        tmp_path.replace(self.data_path)

    def _save(self) -> None:
        self._atomic_write(self._tickets)

    def _reload(self) -> None:
        self._tickets = self._load()

    def list_tickets(self) -> List[Dict[str, Any]]:
        self._reload()
        return sorted(self._tickets, key=lambda x: x.get("id", ""))

    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        self._reload()
        return next((t for t in self._tickets if t.get("id") == ticket_id), None)

    def _next_id(self) -> str:
        # Robustly handle ids like "TKT-001"
        max_num = 0
        for t in self._tickets:
            tid = str(t.get("id", ""))
            if tid.startswith("TKT-"):
                suffix = tid.split("-", 1)[1]
                if suffix.isdigit():
                    max_num = max(max_num, int(suffix))
        return f"TKT-{max_num + 1:03d}"

    def create_ticket(
        self,
        title: str,
        user: str,
        category: str,
        priority: str,
        symptoms: str,
    ) -> Dict[str, Any]:
        self._reload()

        title = (title or "").strip()
        user = (user or "").strip()
        category = (category or "").strip()
        symptoms = (symptoms or "").strip()

        if not title:
            raise ValueError("title is required")
        if not user:
            raise ValueError("user is required")
        if not category:
            raise ValueError("category is required")

        if priority not in VALID_PRIORITIES:
            priority = "P3"

        now = _utc_now_iso()
        ticket = {
            "id": self._next_id(),
            "title": title,
            "status": "Open",
            "priority": priority,
            "user": user,
            "category": category,
            "created_at": now,
            "updated_at": now,
            "symptoms": symptoms,
            "work_notes": [],
        }

        self._tickets.append(ticket)
        self._save()
        return ticket

    def update_status(self, ticket_id: str, new_status: str) -> bool:
        if new_status not in VALID_STATUSES:
            return False

        self._reload()
        t = next((x for x in self._tickets if x.get("id") == ticket_id), None)
        if not t:
            return False

        t["status"] = new_status
        t["updated_at"] = _utc_now_iso()
        self._save()
        return True

    def add_work_note(self, ticket_id: str, note: str) -> bool:
        note = (note or "").strip()
        if not note:
            return False

        self._reload()
        t = next((x for x in self._tickets if x.get("id") == ticket_id), None)
        if not t:
            return False

        t.setdefault("work_notes", []).append({"at": _utc_now_iso(), "note": note})
        t["updated_at"] = _utc_now_iso()
        self._save()
        return True

