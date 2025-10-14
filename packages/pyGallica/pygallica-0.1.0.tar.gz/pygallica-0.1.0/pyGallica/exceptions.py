from __future__ import annotations


class GallicaError(Exception):
    """Base error for the Gallica wrapper."""


class GallicaHTTPError(GallicaError):
    """Raised when an HTTP error (4xx/5xx) occurs."""

    def __init__(self, status_code: int, url: str, message: str | None = None):
        self.status_code = status_code
        self.url = url
        super().__init__(message or f"HTTP {status_code} while calling {url}")


class GallicaAPIError(GallicaError):
    """Raised when Gallica/SRU returns a diagnostic or an invalid payload."""

    def __init__(self, message: str, diagnostics: dict | None = None):
        self.diagnostics = diagnostics or {}
        super().__init__(message)


class GallicaParseError(GallicaError):
    """Raised when the XML cannot be parsed or is missing required fields."""
