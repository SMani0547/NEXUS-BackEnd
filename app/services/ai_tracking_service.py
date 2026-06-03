import csv
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any


class AITrackingService:
    _lock = Lock()
    _columns = [
        "timestamp_utc",
        "question",
        "answer",
        "suggested_questions",
        "ip_address",
        "user_agent",
        "device_type",
        "country",
        "city",
    ]

    def __init__(self, log_path: Path):
        self.log_path = log_path

    def record(self, question: str, response: dict[str, Any], client: dict[str, str]) -> None:
        row = {
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "question": question,
            "answer": response.get("answer", ""),
            "suggested_questions": " | ".join(response.get("suggested_questions", [])),
            "ip_address": client.get("ip_address", ""),
            "user_agent": client.get("user_agent", ""),
            "device_type": client.get("device_type", ""),
            "country": client.get("country", ""),
            "city": client.get("city", ""),
        }

        with self._lock:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            write_header = not self.log_path.exists() or self.log_path.stat().st_size == 0
            with self.log_path.open("a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self._columns)
                if write_header:
                    writer.writeheader()
                writer.writerow(row)
