from dataclasses import dataclass, field

from starlette.requests import Request


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    headers: dict[str, str] = field(default_factory=dict)
    retry_after_seconds: int | None = None


class RequestRateLimiter:
    def evaluate(self, request: Request) -> RateLimitDecision:
        raise NotImplementedError


class NoOpRequestRateLimiter(RequestRateLimiter):
    def __init__(self, strategy_name: str = "disabled") -> None:
        self._strategy_name = strategy_name

    def evaluate(self, request: Request) -> RateLimitDecision:
        return RateLimitDecision(
            allowed=True,
            headers={"X-RateLimit-Policy": self._strategy_name},
        )
