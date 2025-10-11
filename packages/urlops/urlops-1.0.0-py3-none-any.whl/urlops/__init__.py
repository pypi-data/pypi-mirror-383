"""urlops - Clean URL handling made easy"""

# Version
__version__ = "1.0.0"

# Main classes
from .url import URL
from .query import QueryParams
from .path import URLPath
from .exceptions import URLParseError, ParseError, ValidationError, TypeError


# Factory functions
def parse(url: str) -> URL:
    """Parse a URL string and return a URL object."""
    return URL(url)


def join(base: URL, *components) -> URL:
    """Join a base URL with path components."""
    result = base
    for component in components:
        result = result / component
    return result


__all__ = [
    # Main classes
    "URL",
    "URLPath",
    "QueryParams",
    # Exceptions
    "URLParseError",
    "ParseError",
    "ValidationError",
    "TypeError",
    # Factory functions
    "parse",
    "join",
]
