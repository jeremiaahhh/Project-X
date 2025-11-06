class RateLimitError(RuntimeError):
    """Raised when upstream data providers throttle requests."""

    def __init__(self, provider: str = "Yahoo Finance", message: str | None = None) -> None:
        detail = message or "Rate limit exceeded"
        super().__init__(f"{provider}: {detail}")
        self.provider = provider
        self.detail = detail
