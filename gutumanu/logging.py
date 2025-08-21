import logging
import os
import re

try:  # optional dependency
    from opensearchpy import OpenSearch
except Exception:  # pragma: no cover - opensearch not installed
    OpenSearch = None  # type: ignore


class PIIFilter(logging.Filter):
    """Scrub basic PII such as email addresses from log records."""

    _email_regex = re.compile(r"[^\s]+@[^\s]+")

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - simple filter
        if isinstance(record.msg, str):
            record.msg = self._email_regex.sub("[REDACTED]", record.msg)
        return True


class OpenSearchHandler(logging.Handler):
    """Send log records to OpenSearch as JSON documents."""

    def __init__(self) -> None:
        super().__init__()
        self.client = None
        url = os.getenv("OPENSEARCH_URL")
        if OpenSearch and url:
            try:  # pragma: no cover - best effort connection
                self.client = OpenSearch(url)
            except Exception:
                self.client = None
        self.index = os.getenv("OPENSEARCH_LOG_INDEX", "app-logs")

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - network interaction
        if not self.client or record.name.startswith("opensearch"):
            return
        try:
            self.client.index(index=self.index, body=self.format(record))
        except Exception:
            pass
