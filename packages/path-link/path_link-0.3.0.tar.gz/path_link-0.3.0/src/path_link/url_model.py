"""URL validation models with lenient and strict modes.

This module provides Pydantic validators for URL strings with two validation modes:
- lenient: Allows localhost, private IPs, custom ports (for development)
- strict: RFC-aligned HTTP(S) only (for production)
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import AnyUrl, HttpUrl, field_validator, BaseModel, ConfigDict


class ValidationMode(str, Enum):
    """URL validation mode."""

    LENIENT = "lenient"
    STRICT = "strict"


class _ProjectUrlsBase(BaseModel):
    """
    Internal base class for ProjectUrls.
    Provides core functionality and should not be used directly by end-users.
    """

    model_config = ConfigDict(validate_assignment=True)

    def to_dict(self) -> dict[str, str]:
        """Returns a dictionary of all resolved URL attributes as strings."""
        return {k: str(v) for k, v in self.model_dump(include=set(self.__class__.model_fields.keys())).items()}  # type: ignore[no-any-return]

    def get_urls(self) -> list[str]:
        """Returns a list of all resolved URL strings."""
        return [str(v) for v in self.to_dict().values()]

    def __getitem__(self, key: str) -> str:
        """Enables dictionary-style access to URL attributes."""
        if key not in self.__class__.model_fields:
            raise KeyError(f"'{key}' is not a configured URL.")
        value = getattr(self, key)
        return str(value)  # type: ignore[no-any-return]


class LenientUrlModel(BaseModel):
    """
    Lenient URL validator that accepts localhost, private IPs, and custom ports.

    Suitable for development environments where URLs like http://localhost:8000
    are common.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    url: AnyUrl

    @field_validator("url", mode="before")
    @classmethod
    def validate_lenient_url(cls, v: Any) -> Any:
        """
        Lenient validation: accept any syntactically valid URL.

        This includes:
        - localhost and 127.0.0.1
        - Private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
        - Custom ports
        - http and https schemes
        """
        if not isinstance(v, str):
            v = str(v)

        # Basic checks for obviously invalid URLs
        if not v or v.isspace():
            raise ValueError("URL cannot be empty or whitespace")

        # Let Pydantic's AnyUrl handle the rest of the validation
        # It's permissive enough for development use cases
        return v


class StrictUrlModel(BaseModel):
    """
    Strict URL validator that only accepts RFC-compliant HTTP(S) URLs.

    Suitable for production environments where URLs must be publicly accessible
    and follow strict HTTP(S) standards.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    url: HttpUrl

    @field_validator("url", mode="after")
    @classmethod
    def validate_strict_url(cls, v: HttpUrl) -> HttpUrl:
        """
        Strict validation: only accept HTTP(S) URLs with proper hosts.

        This rejects:
        - localhost URLs
        - Private IP addresses
        - Non-HTTP(S) schemes
        - Malformed URLs
        """
        # Check for localhost
        host = v.host
        if host in ("localhost", "127.0.0.1", "::1"):
            raise ValueError("localhost URLs are not allowed in strict mode")

        # Check for private IP ranges
        if host:
            # Check IPv4 private ranges
            if host.startswith("10."):
                raise ValueError("Private IP addresses (10.0.0.0/8) are not allowed in strict mode")
            if host.startswith("172.") and len(host.split(".")) == 4:
                second_octet = int(host.split(".")[1])
                if 16 <= second_octet <= 31:
                    raise ValueError("Private IP addresses (172.16.0.0/12) are not allowed in strict mode")
            if host.startswith("192.168."):
                raise ValueError("Private IP addresses (192.168.0.0/16) are not allowed in strict mode")

        return v


def validate_url(url_string: str, mode: ValidationMode = ValidationMode.LENIENT) -> str:
    """
    Validate a URL string according to the specified mode.

    Args:
        url_string: The URL string to validate
        mode: Validation mode (lenient or strict)

    Returns:
        The validated URL as a string

    Raises:
        ValidationError: If the URL is invalid for the given mode

    Examples:
        >>> validate_url("http://localhost:8000", ValidationMode.LENIENT)
        'http://localhost:8000/'

        >>> validate_url("https://example.com/api", ValidationMode.STRICT)
        'https://example.com/api'
    """
    if mode == ValidationMode.LENIENT:
        lenient_model = LenientUrlModel(url=url_string)  # type: ignore[arg-type]
        return str(lenient_model.url)
    else:
        strict_model = StrictUrlModel(url=url_string)  # type: ignore[arg-type]
        return str(strict_model.url)
