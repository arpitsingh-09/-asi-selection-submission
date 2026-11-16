"""Read-only OpenAlex and Semantic Scholar metadata adapters for E6.

The adapters preserve source-native records and do not resolve ambiguous title
matches automatically. Network access and disk caching are opt-in at call time.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from prepare_dataset import canonicalize_arxiv_id, canonicalize_records

OPENALEX_API_VERSION = "public REST API; unversioned endpoint"
SEMANTIC_SCHOLAR_API_VERSION = "Academic Graph API graph/v1"
OPENALEX_BASE = "https://api.openalex.org"
SEMANTIC_SCHOLAR_BASE = "https://api.semanticscholar.org/graph/v1"
OPENCITATIONS_API_VERSION = "Index REST API v2.2.0"
CROSSREF_API_VERSION = "REST API; unversioned endpoint"
OPENCITATIONS_BASE = "https://api.opencitations.net/index/v2"
CROSSREF_BASE = "https://api.crossref.org"
ARXIV_API_VERSION = "arXiv API; export.arxiv.org/api/query"
ARXIV_API_BASE = "https://export.arxiv.org/api/query"
S2_TARGET_FIELDS = (
    "paperId,title,abstract,year,publicationDate,externalIds"
)
OPENALEX_TARGET_FIELDS = (
    "id,doi,title,publication_date,referenced_works,ids,"
    "abstract_inverted_index,updated_date,locations"
)
OPENALEX_REFERENCE_FIELDS = (
    "id,doi,title,publication_date,ids,abstract_inverted_index,updated_date,locations"
)
MAX_HTTP_TIMEOUT_SECONDS = 30.0
MAX_HTTP_ATTEMPTS = 5
MAX_INLINE_RETRY_WAIT_SECONDS = 30.0


class CitationApiError(RuntimeError):
    def __init__(
        self, message: str, attempts: Sequence[Mapping[str, Any]] = (), *,
        request_url: str | None = None, retrieved_at_utc: str | None = None,
        http_status: int | None = None, raw_body: str | None = None,
    ):
        super().__init__(message)
        self.attempts = [dict(row) for row in attempts]
        last_attempt = self.attempts[-1] if self.attempts else {}
        self.request_url = request_url or last_attempt.get("request_url")
        self.retrieved_at_utc = retrieved_at_utc or last_attempt.get("retrieved_at_utc")
        self.http_status = http_status if http_status is not None else last_attempt.get("status_code")
        self.raw_body = raw_body if raw_body is not None else last_attempt.get("raw_body")
        self.retry_after_seconds = last_attempt.get("retry_after_seconds")


class CitationCacheMiss(CitationApiError):
    """Raised in offline mode when a required URL is absent from the cache."""


class CitationRetryDeferred(CitationApiError):
    """A server delay is too long to block inline; retry after its deadline."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def reconstruct_openalex_abstract(inverted_index: Any) -> str | None:
    """Reconstruct OpenAlex's indexed abstract without adding/changing text."""
    if not isinstance(inverted_index, Mapping):
        return None
    positions: dict[int, str] = {}
    for token, indexes in inverted_index.items():
        if not isinstance(token, str) or not isinstance(indexes, list):
            continue
        for index in indexes:
            if type(index) is int and index >= 0 and index not in positions:
                positions[index] = token
    if not positions:
        return None
    return " ".join(positions[index] for index in range(max(positions) + 1) if index in positions)


def _normalize_title(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join("".join(ch.lower() if ch.isalnum() else " " for ch in value).split())


def _normalize_doi(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    value = value.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if value.startswith(prefix):
            value = value[len(prefix):]
    return value if re.match(r"^10\.\d{4,9}/\S+$", value) else None


def _identifier_keys(record: Mapping[str, Any]) -> set[str]:
    keys: set[str] = set()
    doi = _normalize_doi(record.get("doi"))
    if doi:
        keys.add("doi:" + doi)
    ids = record.get("ids")
    if isinstance(ids, Mapping):
        doi = _normalize_doi(ids.get("doi"))
        if doi:
            keys.add("doi:" + doi)
        arxiv = ids.get("arxiv") or ids.get("ArXiv")
        if isinstance(arxiv, str) and arxiv.strip():
            keys.add("arxiv:" + arxiv.strip().lower().removeprefix("arxiv:"))
    external = record.get("externalIds")
    if isinstance(external, Mapping):
        doi = _normalize_doi(external.get("DOI"))
        if doi:
            keys.add("doi:" + doi)
        arxiv = external.get("ArXiv") or external.get("arXiv")
        if isinstance(arxiv, str) and arxiv.strip():
            keys.add("arxiv:" + arxiv.strip().lower().removeprefix("arxiv:"))
    return keys


def openalex_arxiv_identifiers(record: Mapping[str, Any]) -> set[str]:
    """Extract exact arXiv IDs explicitly represented in an OpenAlex work.

    OpenAlex often omits ``ids.arxiv`` while exposing the same identifier as
    an ``arxiv.org/abs`` location or as its registered
    ``10.48550/arxiv.<id>`` DOI. No title or abstract matching is performed.
    """
    if not isinstance(record, Mapping):
        return set()
    found: set[str] = set()

    def add_id(value: Any) -> None:
        if not isinstance(value, str) or not value.strip():
            return
        try:
            found.add(canonicalize_arxiv_id(value))
        except (TypeError, ValueError):
            return

    ids = record.get("ids")
    if isinstance(ids, Mapping):
        add_id(ids.get("arxiv") or ids.get("ArXiv"))
        for doi_value in (ids.get("doi"), record.get("doi")):
            doi = _normalize_doi(doi_value)
            if doi and doi.startswith("10.48550/arxiv."):
                add_id(doi[len("10.48550/arxiv."):])

    locations = record.get("locations")
    if isinstance(locations, list):
        for location in locations:
            if not isinstance(location, Mapping):
                continue
            for url_value in (location.get("landing_page_url"), location.get("pdf_url")):
                if not isinstance(url_value, str):
                    continue
                parsed = urllib.parse.urlparse(url_value)
                host = (parsed.hostname or "").lower()
                if host not in {"arxiv.org", "www.arxiv.org", "export.arxiv.org"}:
                    continue
                parts = [part for part in parsed.path.split("/") if part]
                if len(parts) == 2 and parts[0] in {"abs", "pdf"}:
                    add_id(parts[1].removesuffix(".pdf"))
    return found


def openalex_record_matches_arxiv_id(record: Mapping[str, Any], arxiv_id: str) -> bool:
    """Return true only for a single, exact canonical ID in the source record."""
    try:
        requested = canonicalize_arxiv_id(arxiv_id)
    except (TypeError, ValueError):
        return False
    identities = openalex_arxiv_identifiers(record)
    return identities == {requested}


def compare_reference_sets(
    openalex_references: Sequence[Mapping[str, Any]],
    semantic_scholar_references: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Crosswalk refs only by shared DOI/arXiv ID; titles are not proof of identity."""
    oa_index: dict[str, Mapping[str, Any]] = {}
    for record in openalex_references:
        for key in _identifier_keys(record):
            oa_index.setdefault(key, record)
    s2_index: dict[str, Mapping[str, Any]] = {}
    for record in semantic_scholar_references:
        cited = record.get("citedPaper") if isinstance(record.get("citedPaper"), Mapping) else record
        for key in _identifier_keys(cited):
            s2_index.setdefault(key, cited)
    shared = sorted(set(oa_index) & set(s2_index))
    title_only_pairs = []
    s2_title_index: dict[str, list[Mapping[str, Any]]] = {}
    for record in semantic_scholar_references:
        cited = record.get("citedPaper") if isinstance(record.get("citedPaper"), Mapping) else record
        title = _normalize_title(cited.get("title"))
        if title:
            s2_title_index.setdefault(title, []).append(cited)
    for record in openalex_references:
        title = _normalize_title(record.get("title"))
        if title and title in s2_title_index and not (_identifier_keys(record) & set(s2_index)):
            title_only_pairs.append(title)
    return {
        "shared_stable_identifier_count": len(shared),
        "shared_stable_identifiers": shared,
        "title_only_candidate_match_count": len(set(title_only_pairs)),
        "title_only_matches_are_verified": False,
    }


class JsonFileCache:
    """Optional append-only per-URL JSON cache; never replaces an existing entry."""

    def __init__(self, directory: str | Path):
        self.directory = Path(directory)

    def _path(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.directory / (digest + ".json")

    def get(self, key: str) -> Mapping[str, Any] | None:
        path = self._path(key)
        if not path.is_file():
            return None
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
        if not isinstance(value, dict):
            raise CitationApiError("cache entry must contain a JSON object")
        return value

    def put(self, key: str, value: Mapping[str, Any]) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self._path(key)
        payload = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
        try:
            descriptor = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            return
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(payload)
        except Exception:
            try:
                os.close(descriptor)
            except OSError:
                pass
            raise


class MemoryCache:
    def __init__(self):
        self._values: dict[str, dict[str, Any]] = {}

    def get(self, key: str) -> Mapping[str, Any] | None:
        value = self._values.get(key)
        return dict(value) if value is not None else None

    def put(self, key: str, value: Mapping[str, Any]) -> None:
        self._values.setdefault(key, dict(value))


class UrllibTransport:
    """Small stdlib transport; the response body remains available verbatim."""

    def get(self, url: str, headers: Mapping[str, str], timeout: float) -> dict[str, Any]:
        request = urllib.request.Request(url, headers=dict(headers), method="GET")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read().decode("utf-8")
                try:
                    parsed = json.loads(body)
                except json.JSONDecodeError:
                    parsed = None
                return {"status_code": response.status, "headers": dict(response.headers.items()),
                        "body": body, "json": parsed}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            return {"status_code": exc.code, "headers": dict(exc.headers.items()) if exc.headers else {},
                    "body": body, "json": None}


class _BaseAdapter:
    source = ""
    api_version = ""

    def __init__(
        self, *, transport: Any | None = None, cache: Any | None = None,
        max_attempts: int = 3, backoff_seconds: float = 1.0,
        timeout_seconds: float = 15.0, sleep: Callable[[float], None] = time.sleep,
        min_request_interval_seconds: float = 0.0,
        monotonic: Callable[[], float] = time.monotonic,
        user_agent: str = "ASI-Lab-E6-citation-audit/0.1",
        cache_only: bool = False,
        max_inline_retry_wait_seconds: float = MAX_INLINE_RETRY_WAIT_SECONDS,
        progress_callback: Callable[[Mapping[str, Any]], None] | None = None,
    ):
        if type(max_attempts) is not int or not 1 <= max_attempts <= MAX_HTTP_ATTEMPTS:
            raise ValueError(f"max_attempts must be between 1 and {MAX_HTTP_ATTEMPTS}")
        if not isinstance(timeout_seconds, (int, float)) or not 0 < timeout_seconds <= MAX_HTTP_TIMEOUT_SECONDS:
            raise ValueError(f"timeout_seconds must be in (0, {MAX_HTTP_TIMEOUT_SECONDS}]")
        if not isinstance(max_inline_retry_wait_seconds, (int, float)) or max_inline_retry_wait_seconds < 0:
            raise ValueError("max_inline_retry_wait_seconds must be nonnegative")
        self.transport = transport or UrllibTransport()
        self.cache = cache
        self.max_attempts = max_attempts
        self.backoff_seconds = backoff_seconds
        self.timeout_seconds = timeout_seconds
        self.sleep = sleep
        self.min_request_interval_seconds = max(0.0, float(min_request_interval_seconds))
        self.monotonic = monotonic
        self._last_request_at: float | None = None
        self.user_agent = user_agent
        self.cache_only = bool(cache_only)
        self.max_inline_retry_wait_seconds = float(max_inline_retry_wait_seconds)
        self.progress_callback = progress_callback

    def _emit_progress(self, event: Mapping[str, Any]) -> None:
        if self.progress_callback is not None:
            self.progress_callback(dict(event))

    @staticmethod
    def _retry_wait_seconds(headers: Mapping[str, Any]) -> float | None:
        lowered = {str(key).lower(): value for key, value in headers.items()}
        waits = []
        retry_after = lowered.get("retry-after")
        if retry_after is not None:
            try:
                waits.append(max(0.0, float(retry_after)))
            except (TypeError, ValueError):
                try:
                    deadline = parsedate_to_datetime(str(retry_after))
                    if deadline.tzinfo is None:
                        deadline = deadline.replace(tzinfo=timezone.utc)
                    waits.append(max(0.0, (deadline - datetime.now(timezone.utc)).total_seconds()))
                except (TypeError, ValueError, OverflowError):
                    pass
        for key in ("ratelimit-reset", "x-ratelimit-reset", "x-rate-limit-reset"):
            value = lowered.get(key)
            if value is None:
                continue
            try:
                reset = float(value)
            except (TypeError, ValueError):
                continue
            # X-RateLimit-Reset commonly carries Unix time; RateLimit-Reset
            # commonly carries seconds until reset.
            if reset > 1_000_000_000:
                reset = max(0.0, reset - time.time())
            waits.append(max(0.0, reset))
        return max(waits) if waits else None

    def _get(self, url: str, *, headers: Mapping[str, str] | None = None) -> dict[str, Any]:
        cache_key = self.source + ":" + url
        cached = self.cache.get(cache_key) if self.cache is not None else None
        if cached is not None:
            result = dict(cached)
            result["cache_hit"] = True
            self._emit_progress({"event": "cache_hit", "source": self.source,
                                 "request_url": url, "http_status": result.get("http_status")})
            return result
        if self.cache_only:
            self._emit_progress({"event": "cache_miss", "source": self.source, "request_url": url})
            raise CitationCacheMiss(f"{self.source} cache miss in offline mode", request_url=url)
        call_headers = {"User-Agent": self.user_agent, "Accept": "application/json"}
        call_headers.update(dict(headers or {}))
        attempts: list[dict[str, Any]] = []
        for number in range(1, self.max_attempts + 1):
            try:
                now = self.monotonic()
                if self._last_request_at is not None:
                    remaining = self.min_request_interval_seconds - (now - self._last_request_at)
                    if remaining > 0:
                        self.sleep(remaining)
                self._last_request_at = self.monotonic()
                self._emit_progress({"event": "request", "source": self.source,
                                     "attempt": number, "max_attempts": self.max_attempts,
                                     "request_url": url})
                response = self.transport.get(url, call_headers, self.timeout_seconds)
                status = int(response.get("status_code", 0))
                retrieved_at_utc = utc_now()
                response_headers = dict(response.get("headers") or {})
                raw_body = response.get("body")
                attempt = {
                    "attempt": number, "status_code": status, "request_url": url,
                    "retrieved_at_utc": retrieved_at_utc, "raw_body": raw_body,
                    "response_headers": response_headers,
                }
                attempts.append(attempt)
                if status == 429 or status >= 500:
                    attempt["status"] = "retryable_http_error"
                    headers_received = response_headers
                    attempt["retry_after"] = next((value for key, value in headers_received.items()
                                                    if key.lower() == "retry-after"), None)
                    wait = self._retry_wait_seconds(headers_received)
                    if wait is None:
                        wait = min(self.backoff_seconds * (2 ** (number - 1)),
                                   self.max_inline_retry_wait_seconds)
                    attempt["retry_after_seconds"] = wait
                    attempt["response_headers"] = {
                        key: value for key, value in headers_received.items()
                        if key.lower() in ("date", "retry-after", "ratelimit-reset",
                                           "ratelimit-limit", "ratelimit-remaining",
                                           "x-ratelimit-reset", "x-rate-limit-reset",
                                           "x-ratelimit-limit", "x-ratelimit-remaining")
                    }
                    attempt["error_body"] = raw_body
                    self._emit_progress({"event": "retryable_response", "source": self.source,
                                         "http_status": status, "attempt": number,
                                         "retry_after_seconds": wait, "request_url": url})
                    if wait > self.max_inline_retry_wait_seconds:
                        attempt["status"] = "retry_deferred"
                        raise CitationRetryDeferred(
                            f"{self.source} HTTP {status}; retry deferred for {wait:.1f} seconds",
                            attempts, request_url=url, retrieved_at_utc=retrieved_at_utc,
                            http_status=status, raw_body=raw_body,
                        )
                    if number < self.max_attempts:
                        self.sleep(max(0.0, wait))
                        continue
                    raise CitationApiError(
                        f"{self.source} HTTP {status} after retries", attempts,
                        request_url=url, retrieved_at_utc=retrieved_at_utc,
                        http_status=status, raw_body=raw_body,
                    )
                if status < 200 or status >= 300:
                    attempt["status"] = "non_retryable_http_error"
                    raise CitationApiError(
                        f"{self.source} HTTP {status}", attempts,
                        request_url=url, retrieved_at_utc=retrieved_at_utc,
                        http_status=status, raw_body=raw_body,
                    )
                body = response.get("json")
                if not isinstance(body, (Mapping, list)) and not (self.source == "arXiv API" and isinstance(response.get("body"), str)):
                    attempt["status"] = "invalid_json_or_response"
                    raise CitationApiError(
                        f"{self.source} returned non-object JSON", attempts,
                        request_url=url, retrieved_at_utc=retrieved_at_utc,
                        http_status=status, raw_body=raw_body,
                    )
                attempt["status"] = "ok"
                result = {
                    "source": self.source,
                    "api_version": self.api_version,
                    "request_url": url,
                    "retrieved_at_utc": retrieved_at_utc,
                    "http_status": status,
                    "response_headers": {
                        key: value for key, value in (response.get("headers") or {}).items()
                        if key.lower() in ("date", "etag", "last-modified", "retry-after", "x-ratelimit-limit", "x-ratelimit-remaining")
                    },
                    "raw_body": response.get("body"),
                    "raw_response": (dict(body) if isinstance(body, Mapping) else
                                     {"_list_response": body} if isinstance(body, list) else
                                     {"_xml_body": response.get("body")}),
                    "raw_json": body,
                    "attempt_history": attempts,
                    "cache_hit": False,
                }
                if self.cache is not None:
                    self.cache.put(cache_key, result)
                self._emit_progress({"event": "response", "source": self.source,
                                     "http_status": status, "request_url": url})
                return result
            except CitationApiError:
                raise
            except Exception as exc:
                attempts.append({"attempt": number, "status": "transport_error", "error": str(exc),
                                 "request_url": url, "retrieved_at_utc": utc_now()})
                if number == self.max_attempts:
                    raise CitationApiError(f"{self.source} transport failed after retries: {exc}", attempts,
                                           request_url=url) from exc
                self.sleep(min(self.backoff_seconds * (2 ** (number - 1)),
                               self.max_inline_retry_wait_seconds))
        raise CitationApiError(f"{self.source} request failed", attempts)


class OpenAlexAdapter(_BaseAdapter):
    source = "OpenAlex"
    api_version = OPENALEX_API_VERSION

    def __init__(self, **kwargs):
        kwargs.setdefault("min_request_interval_seconds", 0.1)
        super().__init__(**kwargs)

    def resolve_by_arxiv_id(self, arxiv_id: str) -> dict[str, Any]:
        """Look for an arXiv location; return candidates without auto-selecting."""
        original = arxiv_id.strip() if isinstance(arxiv_id, str) else ""
        if not original:
            raise ValueError("arXiv ID is required")
        value = canonicalize_arxiv_id(original)
        landing_id = original
        if "://" in landing_id:
            landing_id = landing_id.rstrip("/").rsplit("/", 1)[-1]
        landing_id = re.sub(r"^arxiv\s*:\s*", "", landing_id, flags=re.IGNORECASE)
        landing_id = landing_id.removesuffix(".pdf")
        landing_page = "https://arxiv.org/abs/" + landing_id
        params = urllib.parse.urlencode({
            "filter": "locations.landing_page_url:" + landing_page,
            "per_page": 5, "select": OPENALEX_TARGET_FIELDS,
        })
        response = self._get(OPENALEX_BASE + "/works?" + params)
        response["original_arxiv_id"] = original
        response["canonical_arxiv_id"] = value
        response["match_method"] = "arxiv_landing_page_filter"
        response["automatic_match_selected"] = False
        results = response["raw_response"].get("results", [])
        response["candidate_matches"] = [dict(row) for row in results if isinstance(row, Mapping)]
        return response

    def resolve_by_arxiv_external_id(self, arxiv_id: str) -> dict[str, Any]:
        """Query by OpenAlex's filterable arXiv landing-page URL.

        OpenAlex returns arXiv identifiers in ``ids.arxiv`` but does not accept
        that response field as a Works API filter. Use the documented,
        filterable location URL for candidate retrieval; downstream callers
        must still confirm the canonical arXiv ID from each candidate before
        accepting a match.
        """
        original = arxiv_id.strip() if isinstance(arxiv_id, str) else ""
        if not original:
            raise ValueError("arXiv ID is required")
        canonical = canonicalize_arxiv_id(original)
        landing_page = "https://arxiv.org/abs/" + canonical
        params = urllib.parse.urlencode({"filter": "locations.landing_page_url:" + landing_page,
                                         "per_page": 5, "select": OPENALEX_TARGET_FIELDS})
        result = self._get(OPENALEX_BASE + "/works?" + params)
        result.update({"original_arxiv_id": original, "canonical_arxiv_id": canonical,
                       "match_method": "arxiv_landing_page_filter_exact_id_confirmed_by_caller",
                       "automatic_match_selected": False})
        rows = result["raw_response"].get("results", [])
        result["candidate_matches"] = [dict(row) for row in rows if isinstance(row, Mapping)]
        return result

    def search_by_title(self, title: str, *, per_page: int = 5) -> dict[str, Any]:
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title is required for OpenAlex matching")
        if type(per_page) is not int or not 1 <= per_page <= 100:
            raise ValueError("per_page must be between 1 and 100")
        params = urllib.parse.urlencode({"search": title, "per_page": per_page,
                                        "select": OPENALEX_TARGET_FIELDS})
        response = self._get(OPENALEX_BASE + "/works?" + params)
        query = _normalize_title(title)
        candidates = response["raw_response"].get("results", [])
        if not isinstance(candidates, list):
            candidates = []
        response["candidate_matches"] = [
            {"record": row,
             "normalized_title_exact_match": _normalize_title(row.get("title")) == query,
             "automatic_match_selected": False}
            for row in candidates if isinstance(row, Mapping)
        ]
        return response

    def search_by_doi(self, doi: str, *, per_page: int = 5) -> dict[str, Any]:
        normalized = _normalize_doi(doi)
        if not normalized:
            raise ValueError("DOI is required for OpenAlex matching")
        if type(per_page) is not int or not 1 <= per_page <= 100:
            raise ValueError("per_page must be between 1 and 100")
        params = urllib.parse.urlencode({"filter": "doi:" + normalized,
                                        "per_page": per_page, "select": OPENALEX_TARGET_FIELDS})
        response = self._get(OPENALEX_BASE + "/works?" + params)
        response["match_method"] = "doi_filter"
        response["automatic_match_selected"] = False
        return response

    def get_work(self, openalex_id: str) -> dict[str, Any]:
        if not isinstance(openalex_id, str) or not openalex_id.strip():
            raise ValueError("OpenAlex work ID is required")
        identifier = openalex_id.rsplit("/", 1)[-1]
        query = urllib.parse.urlencode({"select": OPENALEX_TARGET_FIELDS})
        return self._get(OPENALEX_BASE + "/works/" + urllib.parse.quote(identifier, safe="") + "?" + query)

    def get_works(self, openalex_ids: Sequence[str], *, per_page: int = 100) -> dict[str, Any]:
        identifiers = [value.rsplit("/", 1)[-1] for value in openalex_ids]
        if not identifiers:
            raise ValueError("at least one OpenAlex ID is required")
        if len(identifiers) > 100:
            raise ValueError("OpenAlex OR lookups are limited to 100 IDs per request")
        filter_value = "openalex:" + "|".join(identifiers)
        params = urllib.parse.urlencode({"filter": filter_value, "per_page": per_page,
                                        "select": OPENALEX_REFERENCE_FIELDS})
        return self._get(OPENALEX_BASE + "/works?" + params)


class SemanticScholarAdapter(_BaseAdapter):
    source = "Semantic Scholar Academic Graph"
    api_version = SEMANTIC_SCHOLAR_API_VERSION

    def __init__(self, *, api_key: str | None = None, **kwargs):
        # Use the API's documented introductory keyed rate as a conservative
        # default even for unauthenticated calls, whose public pool is shared.
        kwargs.setdefault("min_request_interval_seconds", 1.0)
        super().__init__(**kwargs)
        self.api_key = api_key

    def _headers(self):
        return {"x-api-key": self.api_key} if self.api_key else {}

    def get_paper_by_arxiv(self, arxiv_id: str) -> dict[str, Any]:
        if not isinstance(arxiv_id, str) or not arxiv_id.strip():
            raise ValueError("arXiv ID is required")
        canonical_id = canonicalize_arxiv_id(arxiv_id)
        paper_id = "ARXIV:" + canonical_id
        url = (SEMANTIC_SCHOLAR_BASE + "/paper/" + urllib.parse.quote(paper_id, safe="")
               + "?" + urllib.parse.urlencode({"fields": S2_TARGET_FIELDS}))
        response = self._get(url, headers=self._headers())
        response["original_arxiv_id"] = arxiv_id
        response["canonical_arxiv_id"] = canonical_id
        return response

    def get_paper_references(
        self, semantic_scholar_id: str, *, limit: int = 1000, offset: int = 0,
    ) -> dict[str, Any]:
        if not semantic_scholar_id:
            raise ValueError("Semantic Scholar paperId is required")
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError("reference limit must be between 1 and 1000")
        if type(offset) is not int or offset < 0:
            raise ValueError("reference offset must be a nonnegative integer")
        params = urllib.parse.urlencode({
            "limit": limit,
            "offset": offset,
            "fields": "citedPaper.paperId,citedPaper.title,citedPaper.abstract,"
                      "citedPaper.year,citedPaper.publicationDate,citedPaper.externalIds",
        })
        url = (SEMANTIC_SCHOLAR_BASE + "/paper/" + urllib.parse.quote(semantic_scholar_id, safe="")
               + "/references?" + params)
        return self._get(url, headers=self._headers())

    def get_all_paper_references(self, semantic_scholar_id: str, *, page_size: int = 1000) -> dict[str, Any]:
        """Follow the API offset until exhausted; retain every page envelope."""
        pages: list[dict[str, Any]] = []
        offset = 0
        all_rows: list[Any] = []
        while True:
            page = self.get_paper_references(semantic_scholar_id, limit=page_size, offset=offset)
            pages.append(page)
            body = page["raw_response"]
            rows = body.get("data") if isinstance(body.get("data"), list) else []
            all_rows.extend(rows)
            next_offset = body.get("next")
            if not rows or next_offset in (None, 0, False) or next_offset == offset:
                break
            if type(next_offset) is int:
                offset = next_offset
            else:
                offset += len(rows)
        return {"source": self.source, "api_version": self.api_version,
                "retrieved_at_utc": utc_now(), "paper_id": semantic_scholar_id,
                "reference_count": len(all_rows), "references": all_rows, "pages": pages}


class OpenCitationsAdapter(_BaseAdapter):
    """Read outgoing citation edges from OpenCitations Index, using a DOI PID."""
    source = "OpenCitations Index"
    api_version = OPENCITATIONS_API_VERSION

    def __init__(self, *, access_token: str | None = None, **kwargs):
        kwargs.setdefault("min_request_interval_seconds", 1.0)
        super().__init__(**kwargs)
        self.access_token = access_token

    def get_references(self, doi: str) -> dict[str, Any]:
        normalized = _normalize_doi(doi)
        if not normalized:
            raise ValueError("DOI is required; OpenCitations does not accept arXiv IDs")
        url = OPENCITATIONS_BASE + "/references/doi:" + urllib.parse.quote(normalized, safe="")
        headers = {"authorization": self.access_token} if self.access_token else {}
        result = self._get(url, headers=headers)
        result["query_doi"] = normalized
        result["edge_records"] = result.get("raw_json", [])
        if not isinstance(result["edge_records"], list):
            result["edge_records"] = []
        return result


class CrossrefAdapter(_BaseAdapter):
    """Read Crossref-deposited DOI reference metadata; absence is not a negative edge."""
    source = "Crossref"
    api_version = CROSSREF_API_VERSION

    def __init__(self, *, mailto: str | None = None, **kwargs):
        kwargs.setdefault("min_request_interval_seconds", 1.0)
        super().__init__(**kwargs)
        self.mailto = mailto

    def get_work(self, doi: str) -> dict[str, Any]:
        normalized = _normalize_doi(doi)
        if not normalized:
            raise ValueError("DOI is required; Crossref work lookup requires a DOI")
        suffix = "/works/" + urllib.parse.quote(normalized, safe="")
        if self.mailto:
            suffix += "?" + urllib.parse.urlencode({"mailto": self.mailto})
        result = self._get(CROSSREF_BASE + suffix)
        message = result["raw_response"].get("message") if isinstance(result["raw_response"], Mapping) else None
        result["work_record"] = dict(message) if isinstance(message, Mapping) else None
        refs = message.get("reference", []) if isinstance(message, Mapping) else []
        result["reference_records"] = [dict(row) for row in refs if isinstance(row, Mapping)]
        return result


class ArxivApiAdapter(_BaseAdapter):
    """Resolve one exact arXiv identifier via the source's Atom API."""
    source = "arXiv API"
    api_version = ARXIV_API_VERSION

    def get_paper(self, arxiv_id: str) -> dict[str, Any]:
        if not isinstance(arxiv_id, str) or not arxiv_id.strip():
            raise ValueError("arXiv ID is required")
        original = arxiv_id.strip()
        canonical = canonicalize_arxiv_id(original)
        url = ARXIV_API_BASE + "?" + urllib.parse.urlencode({"id_list": canonical})
        result = self._get(url, headers={"Accept": "application/atom+xml"})
        body = result.get("raw_body") or ""
        try:
            root = ET.fromstring(body)
        except ET.ParseError as exc:
            raise CitationApiError("arXiv API returned invalid Atom XML", result.get("attempt_history", [])) from exc
        ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
        entries = []
        for entry in root.findall("a:entry", ns):
            def val(path):
                node = entry.find(path, ns)
                return node.text if node is not None else None
            identifier = val("a:id")
            entries.append({"id": identifier, "versioned_arxiv_id": identifier.rsplit("/", 1)[-1] if identifier else None,
                            "title": val("a:title"), "published": val("a:published"),
                            "updated": val("a:updated"), "doi": val("arxiv:doi"),
                            "raw_entry_xml": ET.tostring(entry, encoding="unicode")})
        result.update({"original_arxiv_id": original, "canonical_arxiv_id": canonical,
                       "entries": entries, "exact_identity_match_count": sum(
                           1 for entry in entries if entry["versioned_arxiv_id"] and
                           entry["versioned_arxiv_id"].split("v", 1)[0] == canonical)})
        return result


def openalex_reference_records(target_response: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return reference IDs from a target record without inventing metadata."""
    target = target_response.get("raw_response", target_response)
    references = target.get("referenced_works") if isinstance(target, Mapping) else None
    if not isinstance(references, list):
        return []
    target_id = target.get("id") if isinstance(target, Mapping) else None
    return [{"openalex_id": identifier, "paper_id": identifier,
             "source": "OpenAlex", "title": None, "abstract": None,
             "publication_date": None, "metadata_status": "identifier_only",
             "citing_target_openalex_id": target_id,
             "citation_edge_source_field": "referenced_works"}
            for identifier in references]


def fetch_openalex_works_batched(
    adapter: OpenAlexAdapter, openalex_ids: Sequence[str], *, batch_size: int = 100,
) -> dict[str, Any]:
    """Fetch cited-work records in API-sized batches without dropping missing IDs."""
    if type(batch_size) is not int or not 1 <= batch_size <= 100:
        raise ValueError("batch_size must be between 1 and 100")
    normalized = [value.rsplit("/", 1)[-1] for value in openalex_ids]
    responses = []
    records: dict[str, Mapping[str, Any]] = {}
    for start in range(0, len(normalized), batch_size):
        page = adapter.get_works(normalized[start:start + batch_size], per_page=batch_size)
        responses.append(page)
        results = page["raw_response"].get("results", [])
        if isinstance(results, list):
            for row in results:
                if isinstance(row, Mapping) and isinstance(row.get("id"), str):
                    records[row["id"].rsplit("/", 1)[-1]] = row
    missing = [identifier for identifier in normalized if identifier not in records]
    return {"records_by_openalex_id": records, "missing_openalex_ids": missing,
            "request_count": len(responses), "responses": responses}


def select_diagnostic_sample(
    raw_rows: Sequence[Mapping[str, Any]], excluded_ids: Sequence[str], *, size: int = 5,
    namespace: str = "e6-lit-api-diagnostic-v1",
) -> list[dict[str, Any]]:
    """Choose reproducible feasibility-only IDs; never an E6 confirmatory sample."""
    if type(size) is not int or size < 1:
        raise ValueError("diagnostic sample size must be a positive integer")
    papers = canonicalize_records(raw_rows)["papers"]
    exclusions = {canonicalize_arxiv_id(value) for value in excluded_ids}
    eligible = [paper_id for paper_id, record in papers.items()
                if paper_id not in exclusions and record.get("canonical_record") is not None]
    ordered = sorted(eligible, key=lambda paper_id: hashlib.sha256(
        (namespace + ":" + paper_id).encode("utf-8")
    ).hexdigest())
    result = []
    for paper_id in ordered[:size]:
        source = dict(papers[paper_id]["canonical_record"])
        result.append({
            "canonical_paper_id": paper_id,
            "original_arxiv_id": source.get("paper_id"),
            "diagnostic_only": True,
            "selection_namespace": namespace,
            "selection_sha256": hashlib.sha256((namespace + ":" + paper_id).encode("utf-8")).hexdigest(),
            "source_record": source,
        })
    return result


def metadata_coverage(records: Sequence[Mapping[str, Any]], *, source: str) -> dict[str, Any]:
    """Count resolvable ID, title, abstract, and exact-date coverage by source."""
    counts = {"identifier_present": 0, "resolvable_identifier": 0,
              "title": 0, "abstract": 0, "publication_date": 0}
    for row in records:
        record = row.get("citedPaper") if isinstance(row.get("citedPaper"), Mapping) else row
        if source == "OpenAlex":
            counts["identifier_present"] += bool(record.get("id") or record.get("openalex_id"))
            counts["resolvable_identifier"] += bool(record.get("id"))
            counts["abstract"] += bool(reconstruct_openalex_abstract(record.get("abstract_inverted_index"))
                                        or record.get("abstract"))
            date_value = record.get("publication_date") or record.get("publication_date_value")
        elif source == "Semantic Scholar Academic Graph":
            counts["identifier_present"] += bool(record.get("paperId"))
            counts["resolvable_identifier"] += bool(record.get("paperId"))
            counts["abstract"] += bool(isinstance(record.get("abstract"), str) and record["abstract"].strip())
            date_value = record.get("publicationDate")
        else:
            raise ValueError("source must be OpenAlex or Semantic Scholar Academic Graph")
        counts["title"] += bool(isinstance(record.get("title"), str) and record["title"].strip())
        counts["publication_date"] += bool(isinstance(date_value, str) and date_value.strip())
    return {"source": source, "reference_record_count": len(records), **counts}


def _arxiv_identifier(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    value = value.strip().lower().removeprefix("arxiv:")
    if "arxiv.org/abs/" in value:
        value = value.rsplit("/", 1)[-1]
    return value.split("v", 1)[0]


def verify_cross_source_reference_edges(
    requested_arxiv_id: str, openalex_target: Mapping[str, Any],
    semantic_scholar_target: Mapping[str, Any],
    openalex_references: Sequence[Mapping[str, Any]],
    semantic_scholar_references: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Conservatively cross-check target and citation edges using stable IDs."""
    requested = _arxiv_identifier(requested_arxiv_id)
    oa = openalex_target.get("raw_response", openalex_target)
    s2 = semantic_scholar_target.get("raw_response", semantic_scholar_target)
    oa_ids = set()
    if isinstance(oa, Mapping):
        ids = oa.get("ids") if isinstance(oa.get("ids"), Mapping) else {}
        found = _arxiv_identifier(ids.get("arxiv") or ids.get("ArXiv"))
        if found:
            oa_ids.add(found)
        locations = oa.get("locations")
        if isinstance(locations, list):
            for location in locations:
                landing = location.get("landing_page_url") if isinstance(location, Mapping) else None
                found = _arxiv_identifier(landing)
                if found:
                    oa_ids.add(found)
    s2_ids = set()
    if isinstance(s2, Mapping):
        external = s2.get("externalIds") if isinstance(s2.get("externalIds"), Mapping) else {}
        found = _arxiv_identifier(external.get("ArXiv") or external.get("arXiv"))
        if found:
            s2_ids.add(found)
    s2_record = s2 if isinstance(s2, Mapping) else {}
    oa_record = oa if isinstance(oa, Mapping) else {}
    shared_target_identifiers = sorted(_identifier_keys(oa_record) & _identifier_keys(s2_record))
    arxiv_match = bool(requested and requested in oa_ids and requested in s2_ids)
    doi_match = bool(shared_target_identifiers and requested and requested in s2_ids)
    target_matched_in_both = arxiv_match or doi_match
    ref_crosswalk = compare_reference_sets(openalex_references, semantic_scholar_references)
    return {
        "requested_arxiv_id": requested_arxiv_id,
        "openalex_target_contains_arxiv_id": requested in oa_ids if requested else False,
        "semantic_scholar_target_contains_arxiv_id": requested in s2_ids if requested else False,
        "target_identity_cross_checked_by_arxiv_id": arxiv_match,
        "target_identity_cross_checked_by_shared_doi": doi_match,
        "shared_target_identifiers": shared_target_identifiers,
        "reference_crosswalk": ref_crosswalk,
        "independently_verified_shared_reference_edge_count": (
            ref_crosswalk["shared_stable_identifier_count"] if target_matched_in_both else 0
        ),
        "independent_edge_verification_possible": target_matched_in_both,
        "title_similarity_alone_is_not_verification": True,
    }


def normalize_openalex_work(record: Mapping[str, Any]) -> dict[str, Any]:
    """Expose comparable metadata while preserving every source-native field."""
    return {
        "source": "OpenAlex",
        "source_record_id": record.get("id"),
        "source_identifiers": dict(record.get("ids") or {}),
        "arxiv_id": next(iter(openalex_arxiv_identifiers(record)))
        if len(openalex_arxiv_identifiers(record)) == 1 else None,
        "title": record.get("title"),
        "abstract": reconstruct_openalex_abstract(record.get("abstract_inverted_index")),
        "publication_date": record.get("publication_date"),
        "source_record": dict(record),
    }


def normalize_semantic_scholar_paper(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source": "Semantic Scholar Academic Graph",
        "source_record_id": record.get("paperId"),
        "source_identifiers": dict(record.get("externalIds") or {}),
        "title": record.get("title"),
        "abstract": record.get("abstract"),
        "publication_date": record.get("publicationDate"),
        "publication_year": record.get("year"),
        "source_record": dict(record),
    }
