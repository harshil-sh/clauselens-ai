import asyncio

from starlette.requests import Request

from app.core.config import Settings
from app.main import RateLimitMiddleware, create_app
from app.services.rate_limiting import RateLimitDecision, RequestRateLimiter


class RejectAllRateLimiter(RequestRateLimiter):
    def evaluate(self, request: Request) -> RateLimitDecision:
        return RateLimitDecision(
            allowed=False,
            headers={"X-RateLimit-Policy": "test"},
            retry_after_seconds=30,
        )


def test_create_app_adds_rate_limit_policy_header_for_api_requests() -> None:
    app = create_app(Settings(api_v1_prefix="/api/v1"))
    messages = _run_request(
        app,
        method="GET",
        path="/api/v1/unknown",
    )
    response_start = next(
        message for message in messages if message["type"] == "http.response.start"
    )
    response_headers = {
        key.decode("latin-1"): value.decode("latin-1")
        for key, value in response_start["headers"]
    }

    assert response_headers["x-ratelimit-policy"] == "disabled"


def test_rate_limit_middleware_returns_429_with_retry_after_when_strategy_blocks() -> None:
    app = create_app(Settings(api_v1_prefix="/api/v1"))
    app.add_middleware(
        RateLimitMiddleware,
        api_v1_prefix="/api/v1",
        limiter=RejectAllRateLimiter(),
    )

    messages = _run_request(
        app,
        method="GET",
        path="/api/v1/unknown",
    )
    response_start = next(
        message for message in messages if message["type"] == "http.response.start"
    )
    response_body = next(
        message for message in messages if message["type"] == "http.response.body"
    )
    response_headers = {
        key.decode("latin-1"): value.decode("latin-1")
        for key, value in response_start["headers"]
    }

    assert response_start["status"] == 429
    assert response_headers["retry-after"] == "30"
    assert response_headers["x-ratelimit-policy"] == "test"
    assert response_body["body"] == (
        b'{"error":{"code":"rate_limited","message":"Too many requests. Please retry later."}}'
    )


def _run_request(
    app,
    *,
    method: str,
    path: str,
    headers: list[tuple[bytes, bytes]] | None = None,
) -> list[dict[str, object]]:
    messages: list[dict[str, object]] = []

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": b"",
        "headers": headers or [],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }

    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict[str, object]) -> None:
        messages.append(message)

    asyncio.run(app(scope, receive, send))
    return messages
