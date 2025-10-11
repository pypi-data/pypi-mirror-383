"""Core URL class - main implementation"""

from typing import Union, Optional
from .exceptions import ParseError, ValidationError, TypeError
from .query import QueryParams
from .path import URLPath


def _validate_scheme(scheme: str) -> None:
    """Validate URL scheme format."""
    if not isinstance(scheme, str):
        raise TypeError(
            f"Scheme must be a string, got {type(scheme).__name__}",
            expected_type="str",
            actual_type=type(scheme).__name__,
        )

    if not scheme:
        return  # Empty scheme is valid

    if not scheme[0].isalpha():
        raise ValidationError(f"Invalid scheme: {scheme} (must start with letter)")

    if not all(c.isalnum() or c in "+-." for c in scheme):
        raise ValidationError(f"Invalid scheme: {scheme} (invalid characters)")


def _validate_host(host: str) -> None:
    """Validate URL host format."""
    if not isinstance(host, str):
        raise TypeError(
            f"Host must be a string, got {type(host).__name__}",
            expected_type="str",
            actual_type=type(host).__name__,
        )

    if not host:
        return  # Empty host is valid

    if not host.replace(".", "").replace("-", "").replace(":", "").isalnum():
        raise ValidationError(f"Invalid host: {host}")


def _validate_port(port: Union[int, None]) -> None:
    """Validate URL port number."""
    if port is not None and not isinstance(port, int):
        raise TypeError(
            f"Port must be an integer or None, got {type(port).__name__}",
            expected_type="int or None",
            actual_type=type(port).__name__,
        )

    if port is not None and (port < 0 or port > 65535):
        raise ValidationError(f"Invalid port number: {port}")


class URL:
    """Main URL class for intuitive URL manipulation"""

    __slots__ = ("_scheme", "_host", "_port", "_path", "_query", "_fragment", "_str")

    def __init__(self, url: Union[str, "URL"]):
        """
        Initialize a URL object from a string or another URL.

        Args:
            url: URL string to parse or URL object to copy

        Raises:
            ParseError: If the URL string cannot be parsed
            ValidationError: If URL components are invalid
        """
        if isinstance(url, URL):
            # Copy from another URL
            self._scheme = url._scheme
            self._host = url._host
            self._port = url._port
            self._path = url._path
            self._query = url._query
            self._fragment = url._fragment
            self._str = url._str
        else:
            # Parse from string
            self._parse_url(url)

    def _parse_url(self, url: str):
        """Parse a URL string into components using WHATWG-style parsing."""
        if not url:
            raise ParseError("URL cannot be empty")

        if not isinstance(url, str):
            raise TypeError(
                f"URL must be a string, got {type(url).__name__}",
                expected_type="str",
                actual_type=type(url).__name__,
            )

        self._str = url

        # Find scheme separator (first colon that's not at start/end)
        scheme_end = url.find(":")
        if scheme_end > 0 and scheme_end < len(url) - 1:
            # Extract and validate scheme
            self._scheme = url[:scheme_end].lower()
            _validate_scheme(self._scheme)
            remaining = url[scheme_end + 1 :]  # Everything after ':'
        else:
            # No valid scheme found
            self._scheme = ""
            remaining = url

        # Check for authority (//) - protocol-relative URLs
        if remaining.startswith("//"):
            remaining = remaining[2:]  # Remove '//'
            # Find end of authority (before path, query, or fragment)
            auth_end = remaining.find("/")
            if auth_end == -1:
                auth_end = remaining.find("?")
            if auth_end == -1:
                auth_end = remaining.find("#")
            if auth_end == -1:
                auth_end = len(remaining)  # No path/query/fragment

            authority = remaining[:auth_end]
            remaining = remaining[auth_end:]

            # Parse host and port from authority
            if ":" in authority:
                # Split from right to handle IPv6 addresses
                self._host, port_str = authority.rsplit(":", 1)
                try:
                    self._port = int(port_str)
                    _validate_port(self._port)
                except ValueError:
                    raise ParseError(f"Invalid port format: {port_str}")
            else:
                self._host = authority
                self._port = None

            _validate_host(self._host)
        else:
            self._host = ""
            self._port = None

        # Find fragment
        fragment_start = remaining.find("#")
        if fragment_start >= 0:
            self._fragment = remaining[fragment_start + 1 :]
            remaining = remaining[:fragment_start]
        else:
            self._fragment = ""

        # Find query
        query_start = remaining.find("?")
        if query_start >= 0:
            query_str = remaining[query_start + 1 :]
            remaining = remaining[:query_start]
            self._query = QueryParams(query_str)
        else:
            self._query = QueryParams()

        # Remaining is the path
        self._path = URLPath(remaining)

    @property
    def scheme(self) -> str:
        """URL scheme (e.g., 'https', 'http')."""
        return self._scheme

    @property
    def host(self) -> str:
        """URL host (e.g., 'example.com')."""
        return self._host

    @property
    def port(self) -> Optional[int]:
        """URL port number, or None if not specified."""
        return self._port

    @property
    def path(self) -> URLPath:
        """URL path as URLPath object."""
        return self._path

    @property
    def query(self) -> QueryParams:
        """URL query parameters as QueryParams object."""
        return self._query

    @property
    def fragment(self) -> str:
        """URL fragment (e.g., '#section1')."""
        return self._fragment

    def __str__(self) -> str:
        """String representation of the URL."""
        if self._str is not None:
            return self._str

        # Reconstruct URL from components
        parts = []

        # Add scheme
        if self._scheme:
            parts.append(f"{self._scheme}:")

        # Add authority
        if self._host:
            parts.append("//")
            if self._port is not None:
                parts.append(f"{self._host}:{self._port}")
            else:
                parts.append(self._host)

        # Add path
        path_str = str(self._path)
        if path_str:
            parts.append(path_str)

        # Add query
        query_str = str(self._query)
        if query_str:
            parts.append(f"?{query_str}")

        # Add fragment
        if self._fragment:
            parts.append(f"#{self._fragment}")

        return "".join(parts)

    def __repr__(self) -> str:
        """Developer representation of the URL."""
        return f"URL('{self._str}')"

    def with_scheme(self, scheme: str) -> "URL":
        """Return a new URL with the given scheme."""
        _validate_scheme(scheme)

        new_url = URL(self)
        new_url._scheme = scheme.lower() if scheme else ""
        new_url._str = None  # Force reconstruction
        return new_url

    def with_host(self, host: str) -> "URL":
        """Return a new URL with the given host."""
        _validate_host(host)

        new_url = URL(self)
        new_url._host = host if host else ""
        new_url._str = None  # Force reconstruction
        return new_url

    def with_port(self, port: Union[int, None]) -> "URL":
        """Return a new URL with the given port."""
        _validate_port(port)

        new_url = URL(self)
        new_url._port = port
        new_url._str = None  # Force reconstruction
        return new_url

    def with_path(self, path: Union[str, URLPath]) -> "URL":
        """Return a new URL with the given path."""
        new_url = URL(self)
        if isinstance(path, str):
            new_url._path = URLPath(path)
        else:
            new_url._path = path
        new_url._str = None  # Force reconstruction
        return new_url

    def with_query(self, query: Union[str, dict, QueryParams, None]) -> "URL":
        """Return a new URL with the given query parameters."""
        new_url = URL(self)
        if isinstance(query, (str, dict)):
            new_url._query = QueryParams(query)
        else:
            new_url._query = query
        new_url._str = None  # Force reconstruction
        return new_url

    def with_fragment(self, fragment: str) -> "URL":
        """Return a new URL with the given fragment."""
        new_url = URL(self)
        new_url._fragment = fragment if fragment else ""
        new_url._str = None  # Force reconstruction
        return new_url

    def __truediv__(self, other) -> "URL":
        """Join URL with path component using / operator."""
        if isinstance(other, str):
            new_path = self._path / other
        elif isinstance(other, URLPath):
            new_path = self._path / other
        else:
            new_path = self._path / str(other)

        return self.with_path(new_path)

    def is_valid(self) -> bool:
        """Check if the URL is valid."""
        try:
            # Basic validation - check if we have at least one component
            if (
                not self._scheme
                and not self._host
                and not str(self._path)
                and not str(self._query)
                and not self._fragment
            ):
                return False

            # Validate components using our validation functions
            _validate_scheme(self._scheme)
            _validate_host(self._host)
            _validate_port(self._port)

            return True
        except (ValidationError, TypeError):
            return False

    def is_absolute(self) -> bool:
        """Check if the URL is absolute."""
        return bool(self._scheme and self._host)
