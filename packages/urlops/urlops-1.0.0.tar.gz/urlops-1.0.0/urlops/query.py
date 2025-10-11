"""Query parameter handling - ordered multi-value support"""

from typing import Union, Optional, List, Tuple
from .exceptions import ValidationError, TypeError


def _validate_query_key(key: str) -> None:
    """Validate query parameter key."""
    if not isinstance(key, str):
        raise TypeError(
            f"Key must be a string, got {type(key).__name__}",
            expected_type="str",
            actual_type=type(key).__name__,
        )

    if not key:
        raise ValidationError("Query parameter key cannot be empty")


def _validate_query_value(value: str) -> None:
    """Validate query parameter value."""
    if not isinstance(value, str):
        raise TypeError(
            f"Value must be a string, got {type(value).__name__}",
            expected_type="str",
            actual_type=type(value).__name__,
        )


class QueryParams:
    """
    Immutable ordered multi-value query parameters.

    Handles URL query strings like "key1=value1&key2=value2&key1=value3"
    with support for multiple values per key and ordered parameter handling.
    """

    __slots__ = ("_items", "_str")

    def __init__(self, query: Union[str, dict, None] = None):
        """
        Initialize QueryParams from query string or dictionary.

        Args:
            query: Query parameters as:
                - str: Query string like "key1=value1&key2=value2"
                - dict: Dictionary like {"key1": "value1", "key2": ["value2a", "value2b"]}
                - None: Empty query parameters
        """
        if query is None:
            self._items: List[Tuple[str, str]] = []
            self._str = ""
        elif isinstance(query, str):
            self._parse_string(query)
        elif isinstance(query, dict):
            self._parse_dict(query)
        else:
            raise TypeError(
                f"Query parameters must be str, dict, or None, got {type(query).__name__}",
                expected_type="str, dict, or None",
                actual_type=type(query).__name__,
            )

    def _parse_string(self, query: str):
        """Parse query string into items."""
        if not query:
            self._items = []
            self._str = ""
            return

        # Parse query string
        self._items = []
        for pair in query.split("&"):
            if "=" in pair:
                # Check for multiple equals (invalid)
                if pair.count("=") > 1:
                    raise ValidationError(
                        f"Invalid query string: multiple '=' in '{pair}'"
                    )

                key, value = pair.split("=", 1)
                _validate_query_key(key)
                self._items.append((key, value))
            elif pair:  # Handle keys without values
                _validate_query_key(pair)
                self._items.append((pair, ""))

        self._str = query

    def _parse_dict(self, query: dict):
        """Parse dictionary into items."""
        self._items = []
        for key, value in query.items():
            _validate_query_key(key)

            # Handle different value types for multi-value support
            if isinstance(value, (list, tuple, set)):
                # Multi-value parameters: convert each value to string
                for v in value:
                    self._items.append((str(key), str(v)))
            else:
                # Single-value parameter: convert to string
                self._items.append((str(key), str(value)))

        # Build string representation: "key=value" or "key" for empty values
        self._str = "&".join(
            f"{key}={value}" if value else key for key, value in self._items
        )

    def __str__(self) -> str:
        """String representation of query parameters."""
        return self._str

    def __repr__(self) -> str:
        """Developer representation of query parameters."""
        return f"QueryParams('{self._str}')"

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get the first value for a key."""
        for k, v in self._items:
            if k == key:
                return v
        return default

    def get_all(self, key: str) -> List[str]:
        """Get all values for a key."""
        values = []
        for k, v in self._items:
            if k == key:
                values.append(v)
        return values

    def keys(self) -> List[str]:
        """Get all unique keys."""
        seen = set()
        keys = []
        for k, v in self._items:
            if k not in seen:
                seen.add(k)
                keys.append(k)
        return keys

    def values(self) -> List[str]:
        """Get all values."""
        return [v for k, v in self._items]

    def items(self) -> List[Tuple[str, str]]:
        """Get all key-value pairs."""
        return list(self._items)

    def __len__(self) -> int:
        """Number of key-value pairs."""
        return len(self._items)

    def __bool__(self) -> bool:
        """True if there are any parameters."""
        return len(self._items) > 0

    def add(self, key: str, value: str) -> "QueryParams":
        """Add a new key-value pair."""
        _validate_query_key(key)
        _validate_query_value(value)

        new_items = list(self._items)
        new_items.append((key, value))
        new_query = QueryParams()
        new_query._items = new_items
        new_query._str = "&".join(f"{k}={v}" if v else k for k, v in new_items)
        return new_query

    def set(self, key: str, value: str) -> "QueryParams":
        """Set a key to a single value (removes existing values)."""
        _validate_query_key(key)
        _validate_query_value(value)

        new_items = []
        for k, v in self._items:
            if k != key:
                new_items.append((k, v))
        new_items.append((key, value))
        new_query = QueryParams()
        new_query._items = new_items
        new_query._str = "&".join(f"{k}={v}" if v else k for k, v in new_items)
        return new_query

    def remove(self, key: str) -> "QueryParams":
        """Remove all values for a key."""
        _validate_query_key(key)

        new_items = [(k, v) for k, v in self._items if k != key]
        new_query = QueryParams()
        new_query._items = new_items
        new_query._str = "&".join(f"{k}={v}" if v else k for k, v in new_items)
        return new_query

    def with_(self, **kwargs) -> "QueryParams":
        """Create new QueryParams with additional parameters."""
        # Start with current items
        new_items = list(self._items)

        # Add new parameters (this adds to existing, doesn't replace)
        for key, value in kwargs.items():
            _validate_query_key(key)
            _validate_query_value(str(value))
            new_items.append((key, str(value)))

        # Create new QueryParams object
        new_query = QueryParams.__new__(QueryParams)
        new_query._items = new_items
        new_query._str = "&".join(
            f"{key}={value}" if value else key for key, value in new_items
        )
        return new_query
