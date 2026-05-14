"""Offline smoke checks for the ThingSpeak client.

This script is intentionally network-free. It is useful when pytest is not
installed but a quick verification of the core transformation and polling paths
is needed.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.thingspeak_client import ThingSpeakClient, normalize_feed_row


class FakeThingSpeakClient(ThingSpeakClient):
    def __init__(self) -> None:
        super().__init__()
        self._payloads = [
            {
                "feeds": [
                    {"entry_id": 1, "created_at": "2026-05-01T00:00:00Z", "field1": "10"},
                    {"entry_id": 2, "created_at": "2026-05-01T00:01:00Z", "field1": "11"},
                ]
            },
            {
                "feeds": [
                    {"entry_id": 2, "created_at": "2026-05-01T00:01:00Z", "field1": "11"},
                    {"entry_id": 3, "created_at": "2026-05-02T00:00:00Z", "field1": "12"},
                ]
            },
        ]

    def _get_json(self, path, params):
        if not self._payloads:
            raise AssertionError(f"unexpected API call: {path} {params}")
        return self._payloads.pop(0)


def main() -> None:
    normalized = normalize_feed_row(
        {"entry_id": "7", "created_at": "2026-05-01T00:00:00Z", "field1": "12.5"}
    )
    assert normalized["entry_id"] == 7
    assert normalized["field1"] == 12.5

    client = FakeThingSpeakClient()
    rows = client.backfill_channel(
        1,
        start=datetime(2026, 5, 1, tzinfo=UTC),
        end=datetime(2026, 5, 3, tzinfo=UTC),
        chunk=timedelta(days=1),
        show_progress=False,
    )
    assert [row["entry_id"] for row in rows] == [1, 2, 3]

    print("ThingSpeak client smoke test passed")


if __name__ == "__main__":
    main()
