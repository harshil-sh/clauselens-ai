import json
import logging

from app.core.logging import JsonFormatter


def test_json_formatter_includes_structured_fields() -> None:
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=12,
        msg="Structured log message",
        args=(),
        exc_info=None,
    )
    record.path = "/health"
    record.method = "GET"
    record.status_code = 200

    payload = json.loads(formatter.format(record))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "app.test"
    assert payload["message"] == "Structured log message"
    assert payload["path"] == "/health"
    assert payload["method"] == "GET"
    assert payload["status_code"] == 200
    assert "timestamp" in payload
