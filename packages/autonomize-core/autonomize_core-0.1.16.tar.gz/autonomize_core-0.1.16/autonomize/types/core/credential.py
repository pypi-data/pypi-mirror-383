"""Type definitions for credential authentication."""

from __future__ import annotations

from enum import Enum


class AuthType(Enum):
    """Authentication types supported by ModelhubCredential."""
    OAUTH = "oauth"
    API_KEY = "api_key"
    PERMANENT_TOKEN = "permanent_token"
