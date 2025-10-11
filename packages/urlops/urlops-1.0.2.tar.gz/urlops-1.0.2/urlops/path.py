"""URLPath class for URL path manipulation"""

from typing import Union
from .exceptions import ValidationError, TypeError


def _validate_path_name(name: str) -> None:
    """Validate path name."""
    if not isinstance(name, str):
        raise TypeError(
            f"Name must be a string, got {type(name).__name__}",
            expected_type="str",
            actual_type=type(name).__name__,
        )

    if not name:
        raise ValidationError("Name cannot be empty")


def _validate_path_suffix(suffix: str) -> None:
    """Validate path suffix."""
    if not isinstance(suffix, str):
        raise TypeError(
            f"Suffix must be a string, got {type(suffix).__name__}",
            expected_type="str",
            actual_type=type(suffix).__name__,
        )

    if not suffix.startswith("."):
        raise ValidationError("Suffix must start with a dot")


class URLPath:
    """Path component handler for URL path manipulation"""

    __slots__ = ("_segments", "_is_absolute", "_str")

    def __init__(self, path: Union[str, "URLPath"]):
        """
        Initialize a URLPath object from a string or another URLPath.

        Args:
            path: Path string to parse or URLPath object to copy

        Raises:
            ValidationError: If the path contains double slashes
            TypeError: If path is not a string or URLPath
        """
        if isinstance(path, URLPath):
            # Copy from another URLPath
            self._segments = path._segments
            self._is_absolute = path._is_absolute
            self._str = path._str
        elif isinstance(path, str):
            # Parse from string
            self._parse_path(path)
        else:
            # Invalid type
            raise TypeError(
                f"Path must be a string or URLPath, got {type(path).__name__}",
                expected_type="str or URLPath",
                actual_type=type(path).__name__,
            )

    def _parse_path(self, path: str):
        """Parse a path string into segments."""
        if path == "":
            self._segments = []
            self._is_absolute = False
            self._str = ""
        else:

            # Parse path into segments
            self._is_absolute = path.startswith("/")

            # Handle double slashes in path (invalid)
            # Check for consecutive slashes anywhere in the path
            if "//" in path:
                raise ValidationError(
                    "Invalid path: consecutive slashes not allowed in path component"
                )

            # Split by '/' and filter out empty segments
            segments = [s for s in path.split("/") if s]
            self._segments = segments
            self._str = path

    @property
    def name(self) -> str:
        """The final path component."""
        if not self._segments:
            return ""
        return self._segments[-1]

    @property
    def stem(self) -> str:
        """The path without the final suffix."""
        name = self.name
        if not name:
            return ""

        # Handle hidden files (starting with dot)
        if name.startswith(".") and "." in name[1:]:
            # For hidden files like .hidden.txt, stem is .hidden
            return name.rsplit(".", 1)[0]
        elif name.startswith(".") and "." not in name[1:]:
            # For hidden files like .hidden (no extension), stem is the whole name
            return name
        elif "." in name:
            # For regular files, stem is name without extension
            return name.rsplit(".", 1)[0]
        else:
            # No extension
            return name

    @property
    def suffix(self) -> str:
        """The final suffix of the path."""
        name = self.name
        if not name:
            return ""

        # Handle hidden files (starting with dot)
        if name.startswith(".") and "." in name[1:]:
            # For hidden files like .hidden.txt, suffix is .txt
            return "." + name.rsplit(".", 1)[1]
        elif name.startswith(".") and "." not in name[1:]:
            # For hidden files like .hidden (no extension), no suffix
            return ""
        elif "." in name:
            # For regular files, suffix is the extension
            return "." + name.rsplit(".", 1)[1]
        else:
            # No extension
            return ""

    @property
    def parent(self) -> "URLPath":
        """The parent path."""
        if not self._segments:
            # For root path, parent is still root
            if self._is_absolute:
                return URLPath("/")
            else:
                return URLPath("")

        new_segments = self._segments[:-1]
        if self._is_absolute:
            new_path = "/" + "/".join(new_segments) if new_segments else "/"
        else:
            new_path = "/".join(new_segments)

        return URLPath(new_path)

    def __str__(self) -> str:
        """String representation of the path."""
        return self._str

    def __repr__(self) -> str:
        """Developer representation of the path."""
        return f"URLPath('{self._str}')"

    def __truediv__(self, other) -> "URLPath":
        """Join path with another path component."""
        if isinstance(other, str):
            other_path = URLPath(other)
        elif isinstance(other, URLPath):
            other_path = other
        else:
            other_path = URLPath(str(other))

        # Handle joining logic
        if other_path._is_absolute:
            # If other is absolute, return other
            return other_path

        # Join segments
        new_segments = self._segments + other_path._segments

        # Build new path
        if self._is_absolute:
            new_path = "/" + "/".join(new_segments)
        else:
            new_path = "/".join(new_segments)

        return URLPath(new_path)

    def with_name(self, name: str) -> "URLPath":
        """Return a new path with the given name."""
        _validate_path_name(name)

        if not self._segments:
            return URLPath(name)

        new_segments = self._segments[:-1] + [name]
        if self._is_absolute:
            new_path = "/" + "/".join(new_segments)
        else:
            new_path = "/".join(new_segments)

        return URLPath(new_path)

    def with_suffix(self, suffix: str) -> "URLPath":
        """Return a new path with the given suffix."""
        _validate_path_suffix(suffix)

        if not self._segments:
            return URLPath(suffix)

        # Get current name and modify it
        current_name = self._segments[-1]
        if "." in current_name:
            stem = current_name.rsplit(".", 1)[0]
        else:
            stem = current_name

        new_name = stem + suffix
        return self.with_name(new_name)

    def is_absolute(self) -> bool:
        """True if the path is absolute."""
        return self._is_absolute

    def is_relative(self) -> bool:
        """True if the path is relative."""
        return not self._is_absolute
