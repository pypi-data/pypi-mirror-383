"""Manage authentication flow for FastAPI endpoints with no-op auth and provided user token.

Intended for local/dev use only — do not use in production.

Behavior:
- Reads a user token from request headers via `authentication.utils.extract_user_token`.
- Reads `user_id` from query params (falls back to `DEFAULT_USER_UID`) and
  pairs it with `DEFAULT_USER_NAME`.
- Returns a tuple: (user_id, DEFAULT_USER_NAME, user_token).
"""

from fastapi import Request

from constants import (
    DEFAULT_USER_NAME,
    DEFAULT_USER_UID,
    DEFAULT_VIRTUAL_PATH,
)
from authentication.interface import AuthInterface
from authentication.utils import extract_user_token
from log import get_logger

logger = get_logger(__name__)


class NoopWithTokenAuthDependency(
    AuthInterface
):  # pylint: disable=too-few-public-methods
    """No-op AuthDependency class that bypasses authentication and authorization checks."""

    def __init__(self, virtual_path: str = DEFAULT_VIRTUAL_PATH) -> None:
        """Initialize the required allowed paths for authorization checks."""
        self.virtual_path = virtual_path
        self.skip_userid_check = True

    async def __call__(self, request: Request) -> tuple[str, str, bool, str]:
        """Validate FastAPI Requests for authentication and authorization.

        Args:
            request: The FastAPI request object.

        Returns:
            The user's UID and username if authentication and authorization succeed
            user_id check is skipped with noop auth to allow consumers provide user_id
        """
        logger.warning(
            "No-op with token authentication dependency is being used. "
            "The service is running in insecure mode intended solely for development purposes"
        )
        # try to extract user token from request
        user_token = extract_user_token(request.headers)
        # try to extract user ID from request
        user_id = request.query_params.get("user_id", DEFAULT_USER_UID)
        logger.debug("Retrieved user ID: %s", user_id)
        return user_id, DEFAULT_USER_NAME, self.skip_userid_check, user_token
