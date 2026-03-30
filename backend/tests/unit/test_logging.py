import json
import logging

from app.core.logging import JsonFormatter, RequestContextFilter, request_id_context


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


def test_request_context_filter_includes_request_id_from_context() -> None:
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=32,
        msg="Structured log message",
        args=(),
        exc_info=None,
    )
    request_id_token = request_id_context.set("req_test_123")

    try:
        RequestContextFilter().filter(record)
        payload = json.loads(formatter.format(record))
    finally:
        request_id_context.reset(request_id_token)

    assert payload["request_id"] == "req_test_123"
