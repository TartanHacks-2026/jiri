"""API security utilities.

Implements Zero-Trust patterns:
- API key authentication for service-to-service calls
- Request validation
- No secrets in responses or logs

Following CODE_PATTERNS.md: Secrets injected at proxy level only.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from jiri.core.config import get_settings

# API Key header scheme
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
    description="API key for service-to-service authentication",
)


async def verify_api_key(
    api_key: Annotated[str | None, Security(api_key_header)],
) -> str:
    """Verify API key from request header.

    Args:
        api_key: API key from X-API-Key header.

    Returns:
        The validated API key.

    Raises:
        HTTPException: If API key is missing or invalid.
    """
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    settings = get_settings()

    # In production, use constant-time comparison
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return api_key


# Type alias for dependency injection
APIKeyDep = Annotated[str, Depends(verify_api_key)]


def require_api_key() -> APIKeyDep:
    """FastAPI dependency that requires valid API key.

    Usage:
        @app.get("/protected")
        async def protected_endpoint(api_key: APIKeyDep):
            ...
    """
    return Depends(verify_api_key)  # type: ignore[return-value]


class SecureHeaders:
    """Security headers middleware helper.

    Adds security headers to responses following best practices.
    """

    HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Cache-Control": "no-store",
    }

    @classmethod
    def apply(cls, headers: dict[str, str]) -> dict[str, str]:
        """Apply security headers to response headers dict."""
        return {**headers, **cls.HEADERS}
