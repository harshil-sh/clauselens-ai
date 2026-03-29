import asyncio
import json

from fastapi import FastAPI

from app.core.errors import ApiError, register_exception_handlers


def create_test_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/api-error")
    async def api_error() -> None:
        raise ApiError(code="bad_input", message="Bad input.", status_code=400)

    @app.get("/unhandled-error")
    async def unhandled_error() -> None:
        raise RuntimeError("boom")

    @app.get("/items/{item_id}")
    async def get_item(item_id: int) -> dict[str, int]:
        return {"item_id": item_id}

    return app


def call_app(path: str) -> tuple[int, dict[str, object]]:
    app = create_test_app()
    messages: list[dict[str, object]] = []

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }

    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict[str, object]) -> None:
        messages.append(message)

    try:
        asyncio.run(app(scope, receive, send))
    except Exception:
        pass

    response_start = next(
        message for message in messages if message["type"] == "http.response.start"
    )
    response_body = next(
        message for message in messages if message["type"] == "http.response.body"
    )
    return response_start["status"], json.loads(response_body["body"])


def test_api_error_returns_standardized_payload() -> None:
    status_code, body = call_app("/api-error")

    assert status_code == 400
    assert body == {
        "error": {
            "code": "bad_input",
            "message": "Bad input.",
        }
    }


def test_validation_error_returns_standardized_payload() -> None:
    status_code, body = call_app("/items/not-an-int")

    assert status_code == 422
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["message"] == "Request validation failed."
    assert body["error"]["details"]


def test_unhandled_error_returns_internal_server_error_payload() -> None:
    status_code, body = call_app("/unhandled-error")

    assert status_code == 500
    assert body == {
        "error": {
            "code": "internal_server_error",
            "message": "An unexpected error occurred.",
        }
    }
