"""Read-only ThingSpeak REST API wrapper.

The client is designed for sensor monitoring pipelines that backfill historical
records and then poll incrementally before loading into an upsert target such as
BigQuery.
"""

from __future__ import annotations

import json
import time
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

from loguru import logger
from tqdm.auto import tqdm


MAX_RESULTS = 8000
LIVE_CACHE_SAFE_RESULTS = 100
RETRYABLE_STATUS_CODES = {429, 500, 502, 503}


class ThingSpeakError(RuntimeError):
    """Base exception for ThingSpeak client errors."""


class ThingSpeakAccessError(ThingSpeakError):
    """Raised when a channel cannot be read with the supplied key."""


class ThingSpeakResponseError(ThingSpeakError):
    """Raised when ThingSpeak returns a non-success response."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(f"ThingSpeak API error {status_code}: {message}")
        self.status_code = status_code
        self.message = message


@dataclass(frozen=True)
class ThingSpeakReadOptions:
    """Query options supported by read feed and read field endpoints."""

    results: int | None = None
    days: int | None = None
    minutes: int | None = None
    start: datetime | str | None = None
    end: datetime | str | None = None
    timezone: str | None = None
    include_status: bool = False
    include_metadata: bool = False
    include_location: bool = False
    min_value: float | int | None = None
    max_value: float | int | None = None
    round_digits: int | None = None
    timescale: int | str | None = None
    sum_minutes: int | str | None = None
    average_minutes: int | str | None = None
    median_minutes: int | str | None = None


@dataclass(frozen=True)
class SensorHealth:
    """Latest observed sensor state derived from ThingSpeak."""

    channel_id: int
    alive: bool
    last_data_age_seconds: int | None
    max_age_seconds: int
    checked_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_entry: Mapping[str, Any] | None = None


@dataclass
class ThingSpeakClient:
    """Small read-only client for ThingSpeak REST API."""

    read_api_key: str | None = None
    user_api_key: str | None = None
    base_url: str = "https://api.thingspeak.com"
    timeout_seconds: float = 15.0
    max_retries: int = 3
    retry_backoff_seconds: float = 1.0
    user_agent: str = "kri-report-thingspeak-client/0.1"

    def __post_init__(self) -> None:
        if not self.base_url.startswith("https://"):
            raise ValueError("base_url must use HTTPS")
        if not self.base_url.endswith("/"):
            self.base_url = f"{self.base_url}/"

    def read_settings(self, channel_id: int) -> dict[str, Any]:
        """Read public channel settings, or private settings with user API key."""

        params = {"api_key": self.user_api_key} if self.user_api_key else {}
        return self._get_json(f"channels/{_positive_int(channel_id)}.json", params)

    def read_channel(
        self,
        channel_id: int,
        options: ThingSpeakReadOptions | None = None,
    ) -> dict[str, Any]:
        """Read all fields from a channel feed."""

        params = self._read_params(options)
        return self._get_json(f"channels/{_positive_int(channel_id)}/feeds.json", params)

    def read_field(
        self,
        channel_id: int,
        field_id: int,
        options: ThingSpeakReadOptions | None = None,
    ) -> dict[str, Any]:
        """Read one field from a channel feed."""

        params = self._read_params(options)
        path = f"channels/{_positive_int(channel_id)}/fields/{_field_id(field_id)}.json"
        return self._get_json(path, params)

    def read_last_entry(
        self,
        channel_id: int,
        *,
        timezone: str | None = None,
        include_status: bool = False,
        include_location: bool = False,
    ) -> dict[str, Any]:
        """Read the latest entry. This endpoint is not affected by feed caching."""

        params: dict[str, Any] = {}
        if timezone:
            params["timezone"] = timezone
        if include_status:
            params["status"] = "true"
        if include_location:
            params["location"] = "true"
        params = self._with_read_key(params)
        return self._get_json(f"channels/{_positive_int(channel_id)}/feeds/last.json", params)

    def read_last_entry_age(self, channel_id: int) -> int:
        """Return seconds since the latest entry."""

        payload = self._get_json(
            f"channels/{_positive_int(channel_id)}/feeds/last_data_age.json",
            {},
        )
        try:
            return int(payload["last_data_age"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ThingSpeakError("last_data_age response did not contain an integer age") from exc

    def check_sensor_alive(
        self,
        channel_id: int,
        *,
        max_age_seconds: int,
        include_last_entry: bool = True,
    ) -> SensorHealth:
        """Check sensor liveness from the age of the latest channel entry."""

        if max_age_seconds < 0:
            raise ValueError("max_age_seconds must be non-negative")

        age: int | None = None
        last_entry: Mapping[str, Any] | None = None
        try:
            age = self.read_last_entry_age(channel_id)
        except ThingSpeakAccessError:
            raise
        except ThingSpeakError as exc:
            logger.warning("last_data_age failed; falling back to last entry timestamp: {}", exc)

        if include_last_entry:
            last_entry = self.read_last_entry(channel_id)

        if age is None and last_entry:
            created_at = _parse_datetime(last_entry.get("created_at"))
            if created_at:
                age = int((datetime.now(UTC) - created_at).total_seconds())

        alive = age is not None and age <= max_age_seconds
        return SensorHealth(
            channel_id=channel_id,
            alive=alive,
            last_data_age_seconds=age,
            max_age_seconds=max_age_seconds,
            last_entry=last_entry,
        )

    def backfill_channel(
        self,
        channel_id: int,
        *,
        start: datetime,
        end: datetime,
        chunk: timedelta = timedelta(days=1),
        show_progress: bool = True,
    ) -> list[dict[str, Any]]:
        """Fetch historical feed data in time windows and de-duplicate by entry_id."""

        return list(
            self.iter_backfill_channel(
                channel_id,
                start=start,
                end=end,
                chunk=chunk,
                show_progress=show_progress,
            )
        )

    def iter_backfill_channel(
        self,
        channel_id: int,
        *,
        start: datetime,
        end: datetime,
        chunk: timedelta = timedelta(days=1),
        show_progress: bool = True,
    ) -> Iterator[dict[str, Any]]:
        """Yield historical feed records for BigQuery-style upsert loading.

        ThingSpeak returns at most 8000 rows for one feed request. If a chunk
        returns exactly 8000 rows the caller should rerun with a smaller chunk to
        avoid silently missing dense data.
        """

        _validate_window(start, end, chunk)
        windows = list(_iter_windows(start, end, chunk))
        iterator: Iterable[tuple[datetime, datetime]] = windows
        if show_progress:
            iterator = tqdm(windows, desc="ThingSpeak backfill", unit="window")

        seen_entry_ids: set[int] = set()
        for window_start, window_end in iterator:
            payload = self.read_channel(
                channel_id,
                ThingSpeakReadOptions(
                    start=window_start,
                    end=window_end,
                    results=MAX_RESULTS,
                ),
            )
            feeds = _feeds(payload)
            if len(feeds) >= MAX_RESULTS:
                logger.warning(
                    "ThingSpeak returned {} records for {} - {}; reduce chunk size",
                    len(feeds),
                    window_start.isoformat(),
                    window_end.isoformat(),
                )
            for row in feeds:
                entry_id = _entry_id(row)
                if entry_id in seen_entry_ids:
                    continue
                seen_entry_ids.add(entry_id)
                yield normalize_feed_row(row)

    def poll_new_entries(
        self,
        channel_id: int,
        *,
        since_entry_id: int | None = None,
        interval_seconds: float = 60.0,
        max_polls: int | None = None,
        results: int = LIVE_CACHE_SAFE_RESULTS,
    ) -> Iterator[dict[str, Any]]:
        """Poll recent entries and yield rows newer than since_entry_id."""

        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")
        if not 1 <= results <= LIVE_CACHE_SAFE_RESULTS:
            raise ValueError("results must be between 1 and 100 to avoid feed caching")

        last_seen = since_entry_id or 0
        polls = 0
        while max_polls is None or polls < max_polls:
            polls += 1
            payload = self.read_channel(channel_id, ThingSpeakReadOptions(results=results))
            rows = sorted((_feeds(payload)), key=_entry_id)
            for row in rows:
                entry_id = _entry_id(row)
                if entry_id <= last_seen:
                    continue
                last_seen = entry_id
                yield normalize_feed_row(row)
            if max_polls is None or polls < max_polls:
                time.sleep(interval_seconds)

    def _read_params(self, options: ThingSpeakReadOptions | None) -> dict[str, Any]:
        options = options or ThingSpeakReadOptions()
        params: dict[str, Any] = {}
        if options.results is not None:
            if not 1 <= options.results <= MAX_RESULTS:
                raise ValueError(f"results must be between 1 and {MAX_RESULTS}")
            params["results"] = options.results
        if options.days is not None:
            params["days"] = _non_negative_int(options.days, "days")
        if options.minutes is not None:
            params["minutes"] = _non_negative_int(options.minutes, "minutes")
        if options.start is not None:
            params["start"] = _format_datetime(options.start)
        if options.end is not None:
            params["end"] = _format_datetime(options.end)
        if options.timezone:
            params["timezone"] = options.timezone
        if options.include_status:
            params["status"] = "true"
        if options.include_metadata:
            params["metadata"] = "true"
        if options.include_location:
            params["location"] = "true"
        if options.min_value is not None:
            params["min"] = options.min_value
        if options.max_value is not None:
            params["max"] = options.max_value
        if options.round_digits is not None:
            params["round"] = _non_negative_int(options.round_digits, "round_digits")
        if options.timescale is not None:
            params["timescale"] = _aggregation_value(options.timescale)
        if options.sum_minutes is not None:
            params["sum"] = _aggregation_value(options.sum_minutes)
        if options.average_minutes is not None:
            params["average"] = _aggregation_value(options.average_minutes)
        if options.median_minutes is not None:
            params["median"] = _aggregation_value(options.median_minutes)
        return self._with_read_key(params)

    def _with_read_key(self, params: dict[str, Any]) -> dict[str, Any]:
        if self.read_api_key:
            return {**params, "api_key": self.read_api_key}
        return params

    def _get_json(self, path: str, params: Mapping[str, Any]) -> dict[str, Any]:
        body = self._request(path, params)
        if body.strip() == b"-1":
            raise ThingSpeakAccessError("ThingSpeak denied access to the channel")
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ThingSpeakError("ThingSpeak response was not valid JSON") from exc
        if isinstance(payload, dict) and "error" in payload:
            error = payload.get("error") or {}
            raise ThingSpeakResponseError(
                int(payload.get("status") or 0),
                str(error.get("message") or error.get("error_code") or "unknown error"),
            )
        if not isinstance(payload, dict):
            raise ThingSpeakError("ThingSpeak JSON response was not an object")
        return payload

    def _request(self, path: str, params: Mapping[str, Any]) -> bytes:
        query = urlencode({k: v for k, v in params.items() if v is not None})
        url = urljoin(self.base_url, path)
        full_url = f"{url}?{query}" if query else url
        safe_url = _redact_api_key(full_url)
        headers = {
            "Accept": "application/json",
            "Host": "api.thingspeak.com",
            "User-Agent": self.user_agent,
        }

        for attempt in range(self.max_retries + 1):
            try:
                logger.debug("GET {}", safe_url)
                request = Request(full_url, headers=headers, method="GET")
                with urlopen(request, timeout=self.timeout_seconds) as response:
                    return response.read()
            except HTTPError as exc:
                if exc.code not in RETRYABLE_STATUS_CODES or attempt >= self.max_retries:
                    message = _read_error_message(exc)
                    raise ThingSpeakResponseError(exc.code, message) from exc
                sleep_seconds = _retry_after(exc) or self.retry_backoff_seconds * (2**attempt)
                logger.warning(
                    "ThingSpeak returned {}; retrying in {:.1f}s",
                    exc.code,
                    sleep_seconds,
                )
                time.sleep(sleep_seconds)
            except URLError as exc:
                if attempt >= self.max_retries:
                    raise ThingSpeakError(f"ThingSpeak request failed: {exc.reason}") from exc
                sleep_seconds = self.retry_backoff_seconds * (2**attempt)
                logger.warning("ThingSpeak network error; retrying in {:.1f}s", sleep_seconds)
                time.sleep(sleep_seconds)

        raise ThingSpeakError("ThingSpeak request failed after retries")


def normalize_feed_row(row: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize a feed row for downstream statistics and BigQuery upsert."""

    normalized: dict[str, Any] = {
        "entry_id": _entry_id(row),
        "created_at": row.get("created_at"),
    }
    for key, value in row.items():
        if key.startswith("field"):
            normalized[key] = _to_number_or_none(value)
        elif key not in normalized:
            normalized[key] = value
    return normalized


def filter_rows_after_entry_id(
    rows: Iterable[Mapping[str, Any]],
    last_entry_id: int | None,
) -> list[dict[str, Any]]:
    """Return rows with entry_id greater than the stored upsert watermark."""

    if last_entry_id is None:
        return [dict(row) for row in rows]
    return [dict(row) for row in rows if _entry_id(row) > last_entry_id]


def filter_rows_after_created_at(
    rows: Iterable[Mapping[str, Any]],
    last_created_at: datetime,
) -> list[dict[str, Any]]:
    """Return rows whose created_at is newer than the stored timestamp watermark."""

    return [
        dict(row)
        for row in rows
        if (created_at := _parse_datetime(row.get("created_at"))) is not None
        and created_at > last_created_at
    ]


def _feeds(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    feeds = payload.get("feeds")
    if not isinstance(feeds, list):
        raise ThingSpeakError("ThingSpeak response did not contain feeds")
    return [row for row in feeds if isinstance(row, Mapping)]


def _entry_id(row: Mapping[str, Any]) -> int:
    try:
        return int(row["entry_id"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ThingSpeakError("feed row did not contain an integer entry_id") from exc


def _positive_int(value: int) -> int:
    value = int(value)
    if value <= 0:
        raise ValueError("value must be positive")
    return value


def _field_id(value: int) -> int:
    value = int(value)
    if not 1 <= value <= 8:
        raise ValueError("ThingSpeak field_id must be between 1 and 8")
    return value


def _non_negative_int(value: int, name: str) -> int:
    value = int(value)
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
    return value


def _aggregation_value(value: int | str) -> int | str:
    allowed = {10, 15, 20, 30, 60, 240, 720, 1440}
    if isinstance(value, str):
        if value != "daily":
            raise ValueError("aggregation string value must be 'daily'")
        return value
    if int(value) not in allowed:
        raise ValueError(f"aggregation value must be one of {sorted(allowed)} or 'daily'")
    return int(value)


def _format_datetime(value: datetime | str) -> str:
    if isinstance(value, str):
        return value
    if value.tzinfo is not None:
        value = value.astimezone(UTC).replace(tzinfo=None)
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _validate_window(start: datetime, end: datetime, chunk: timedelta) -> None:
    if end <= start:
        raise ValueError("end must be later than start")
    if chunk.total_seconds() <= 0:
        raise ValueError("chunk must be positive")


def _iter_windows(
    start: datetime,
    end: datetime,
    chunk: timedelta,
) -> Iterator[tuple[datetime, datetime]]:
    cursor = start
    while cursor < end:
        next_cursor = min(cursor + chunk, end)
        yield cursor, next_cursor
        cursor = next_cursor


def _to_number_or_none(value: Any) -> float | int | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return value
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number.is_integer():
        return int(number)
    return number


def _redact_api_key(url: str) -> str:
    if "api_key=" not in url:
        return url
    prefix, _, suffix = url.partition("api_key=")
    tail = suffix.partition("&")[2]
    return f"{prefix}api_key=<redacted>{'&' + tail if tail else ''}"


def _read_error_message(exc: HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8", errors="replace")
    except Exception:
        return exc.reason
    if not body:
        return exc.reason
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return body[:300]
    error = payload.get("error") if isinstance(payload, dict) else None
    if isinstance(error, Mapping):
        return str(error.get("message") or error.get("error_code") or exc.reason)
    return str(payload)[:300]


def _retry_after(exc: HTTPError) -> float | None:
    retry_after = exc.headers.get("Retry-After")
    if not retry_after:
        return None
    try:
        return max(float(retry_after), 0.0)
    except ValueError:
        return None
