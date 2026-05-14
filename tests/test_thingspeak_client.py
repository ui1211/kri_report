from datetime import UTC, datetime, timedelta
from urllib.error import HTTPError, URLError
from unittest.mock import Mock

import pytest

from src.thingspeak_client import (
    LIVE_CACHE_SAFE_RESULTS,
    MAX_RESULTS,
    SensorHealth,
    ThingSpeakAccessError,
    ThingSpeakClient,
    ThingSpeakError,
    ThingSpeakReadOptions,
    ThingSpeakResponseError,
    filter_rows_after_created_at,
    filter_rows_after_entry_id,
    normalize_feed_row,
)


class RecordingClient(ThingSpeakClient):
    def __init__(self, payloads=None, **kwargs):
        super().__init__(**kwargs)
        self.payloads = list(payloads or [])
        self.calls = []

    def _get_json(self, path, params):
        self.calls.append((path, params))
        if self.payloads:
            payload = self.payloads.pop(0)
            if isinstance(payload, Exception):
                raise payload
            return payload
        return {"feeds": []}


def test_client_requires_https_base_url():
    with pytest.raises(ValueError, match="HTTPS"):
        ThingSpeakClient(base_url="http://api.thingspeak.com")


def test_read_channel_builds_query_options_with_read_key():
    client = RecordingClient(read_api_key="read-key")
    start = datetime(2026, 5, 1, 12, 30, tzinfo=UTC)
    end = datetime(2026, 5, 2, 12, 30, tzinfo=UTC)

    client.read_channel(
        123,
        ThingSpeakReadOptions(
            results=25,
            start=start,
            end=end,
            timezone="Asia/Tokyo",
            include_status=True,
            include_metadata=True,
            include_location=True,
            min_value=1.5,
            max_value=9,
            round_digits=2,
            average_minutes=60,
        ),
    )

    assert client.calls == [
        (
            "channels/123/feeds.json",
            {
                "results": 25,
                "start": "2026-05-01 12:30:00",
                "end": "2026-05-02 12:30:00",
                "timezone": "Asia/Tokyo",
                "status": "true",
                "metadata": "true",
                "location": "true",
                "min": 1.5,
                "max": 9,
                "round": 2,
                "average": 60,
                "api_key": "read-key",
            },
        )
    ]


@pytest.mark.parametrize("field_id", [0, 9])
def test_read_field_rejects_out_of_range_field_id(field_id):
    client = RecordingClient()

    with pytest.raises(ValueError, match="field_id"):
        client.read_field(1, field_id)


@pytest.mark.parametrize("results", [0, MAX_RESULTS + 1])
def test_read_options_reject_invalid_results(results):
    client = RecordingClient()

    with pytest.raises(ValueError, match="results"):
        client.read_channel(1, ThingSpeakReadOptions(results=results))


def test_normalize_feed_row_converts_numeric_fields():
    row = {
        "entry_id": "10",
        "created_at": "2026-05-01T00:00:00Z",
        "field1": "42",
        "field2": "3.14",
        "field3": "",
        "status": "ok",
    }

    assert normalize_feed_row(row) == {
        "entry_id": 10,
        "created_at": "2026-05-01T00:00:00Z",
        "field1": 42,
        "field2": 3.14,
        "field3": None,
        "status": "ok",
    }


def test_filter_rows_after_entry_id_returns_newer_rows_only():
    rows = [{"entry_id": 1}, {"entry_id": "2"}, {"entry_id": 3}]

    assert filter_rows_after_entry_id(rows, 1) == [{"entry_id": "2"}, {"entry_id": 3}]
    assert filter_rows_after_entry_id(rows, None) == rows


def test_filter_rows_after_created_at_ignores_invalid_dates():
    rows = [
        {"entry_id": 1, "created_at": "2026-05-01T00:00:00Z"},
        {"entry_id": 2, "created_at": "invalid"},
        {"entry_id": 3, "created_at": "2026-05-03T00:00:00Z"},
    ]
    watermark = datetime(2026, 5, 2, tzinfo=UTC)

    assert filter_rows_after_created_at(rows, watermark) == [
        {"entry_id": 3, "created_at": "2026-05-03T00:00:00Z"}
    ]


def test_backfill_channel_chunks_and_deduplicates_rows():
    client = RecordingClient(
        payloads=[
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
    )

    rows = client.backfill_channel(
        99,
        start=datetime(2026, 5, 1, tzinfo=UTC),
        end=datetime(2026, 5, 3, tzinfo=UTC),
        chunk=timedelta(days=1),
        show_progress=False,
    )

    assert [row["entry_id"] for row in rows] == [1, 2, 3]
    assert [call[1]["results"] for call in client.calls] == [MAX_RESULTS, MAX_RESULTS]


def test_poll_new_entries_yields_only_entries_after_watermark(monkeypatch):
    client = RecordingClient(
        payloads=[
            {
                "feeds": [
                    {"entry_id": 3, "created_at": "2026-05-01T00:03:00Z", "field1": "3"},
                    {"entry_id": 2, "created_at": "2026-05-01T00:02:00Z", "field1": "2"},
                    {"entry_id": 4, "created_at": "2026-05-01T00:04:00Z", "field1": "4"},
                ]
            }
        ]
    )
    sleep = Mock()
    monkeypatch.setattr("src.thingspeak_client.time.sleep", sleep)

    rows = list(client.poll_new_entries(1, since_entry_id=2, max_polls=1, results=3))

    assert [row["entry_id"] for row in rows] == [3, 4]
    sleep.assert_not_called()


@pytest.mark.parametrize("results", [0, LIVE_CACHE_SAFE_RESULTS + 1])
def test_poll_new_entries_rejects_cache_unsafe_result_counts(results):
    client = RecordingClient()

    with pytest.raises(ValueError, match="results"):
        list(client.poll_new_entries(1, max_polls=1, results=results))


def test_check_sensor_alive_uses_last_data_age():
    client = RecordingClient(
        payloads=[
            {"last_data_age": "30"},
            {"entry_id": 1, "created_at": "2026-05-01T00:00:00Z", "field1": "1"},
        ]
    )

    health = client.check_sensor_alive(5, max_age_seconds=60)

    assert isinstance(health, SensorHealth)
    assert health.channel_id == 5
    assert health.alive is True
    assert health.last_data_age_seconds == 30
    assert health.last_entry == {
        "entry_id": 1,
        "created_at": "2026-05-01T00:00:00Z",
        "field1": "1",
    }


def test_get_json_maps_access_denied_response(monkeypatch):
    client = ThingSpeakClient()
    monkeypatch.setattr(client, "_request", Mock(return_value=b"-1"))

    with pytest.raises(ThingSpeakAccessError):
        client.read_last_entry(1)


def test_get_json_rejects_non_object_json(monkeypatch):
    client = ThingSpeakClient()
    monkeypatch.setattr(client, "_request", Mock(return_value=b"[]"))

    with pytest.raises(ThingSpeakError, match="object"):
        client.read_last_entry(1)


def test_get_json_maps_error_payload(monkeypatch):
    client = ThingSpeakClient()
    monkeypatch.setattr(
        client,
        "_request",
        Mock(return_value=b'{"status": 404, "error": {"message": "not found"}}'),
    )

    with pytest.raises(ThingSpeakResponseError) as exc_info:
        client.read_last_entry(1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.message == "not found"


def test_request_retries_retryable_http_error_then_succeeds(monkeypatch):
    client = ThingSpeakClient(max_retries=1, retry_backoff_seconds=0)

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return b'{"ok": true}'

    error = HTTPError(
        url="https://api.thingspeak.com/channels/1/feeds.json",
        code=503,
        msg="unavailable",
        hdrs={},
        fp=None,
    )
    urlopen = Mock(side_effect=[error, Response()])
    sleep = Mock()
    monkeypatch.setattr("src.thingspeak_client.urlopen", urlopen)
    monkeypatch.setattr("src.thingspeak_client.time.sleep", sleep)

    assert client._request("channels/1/feeds.json", {}) == b'{"ok": true}'
    assert urlopen.call_count == 2
    sleep.assert_called_once_with(0)


def test_request_raises_after_url_error_retries(monkeypatch):
    client = ThingSpeakClient(max_retries=1, retry_backoff_seconds=0)
    monkeypatch.setattr("src.thingspeak_client.urlopen", Mock(side_effect=URLError("offline")))
    monkeypatch.setattr("src.thingspeak_client.time.sleep", Mock())

    with pytest.raises(ThingSpeakError, match="offline"):
        client._request("channels/1/feeds.json", {})
