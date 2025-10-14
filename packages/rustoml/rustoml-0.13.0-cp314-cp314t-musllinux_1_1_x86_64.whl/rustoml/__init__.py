"""
rustoml - A high-performance TOML library for Python.

rustoml is a Python library for parsing and serializing TOML (Tom's Obvious, Minimal Language)
implemented in Rust for maximum performance. It provides a simple API similar to the standard
library's json module.

Key features:
- Fast: Built on rust's toml crate for high performance
- Correct: Passes all standard TOML tests
- Flexible: Supports custom None value handling
- Typed: Full type annotations and py.typed marker

Example:
    >>> import rustoml
    >>> data = rustoml.loads('[package]\\nname = "rustoml"')
    >>> print(data)
    {'package': {'name': 'rustoml'}}
    >>> rustoml.dumps(data)
    '[package]\\nname = "rustoml"\\n'
"""

import re
from collections.abc import Callable
from io import TextIOBase
from pathlib import Path
from typing import Any, BinaryIO, TextIO

from . import _rustoml

__all__ = (
    "__version__",
    "VERSION",
    "TomlParsingError",
    "TomlSerializationError",
    "load",
    "loads",
    "dumps",
    "dump",
)

# VERSION is set in Cargo.toml
VERSION: str = _rustoml.__version__
"""The version of the rustoml package (alias for __version__)."""

__version__: str = _rustoml.__version__
"""The version of the rustoml package."""


class TomlParsingError(_rustoml.TomlParsingError):
    """
    Exception raised when TOML parsing fails.

    This exception provides detailed information about parsing failures,
    similar to Python's tomllib.TOMLDecodeError.

    Attributes:
        msg: The error message describing what went wrong
        doc: The TOML document that failed to parse (if available)
        pos: The character position where parsing failed (0-indexed)
        lineno: The line number where parsing failed (1-indexed)
        colno: The column number where parsing failed (1-indexed)
    """

    def __init__(self, message: str, doc: str | None = None):
        super().__init__(message)
        self.msg = message
        self.doc = doc
        self.pos: int | None = None
        self.lineno: int | None = None
        self.colno: int | None = None

        # Parse error message to extract line and column info
        # Format: "TOML parse error at line X, column Y"
        match = re.search(r"at line (\d+), column (\d+)", message)
        if match:
            self.lineno = int(match.group(1))
            self.colno = int(match.group(2))

            # Calculate position if we have the document
            if doc is not None:
                self.pos = self._calculate_position(doc, self.lineno, self.colno)

    def _calculate_position(self, doc: str, lineno: int, colno: int) -> int:
        """Calculate the character position from line and column numbers."""
        lines = doc.splitlines(keepends=True)
        pos = 0
        for i, line in enumerate(lines, 1):
            if i == lineno:
                return pos + colno - 1
            pos += len(line)
        return pos

    def __str__(self) -> str:
        """Return a formatted error message with context."""
        if self.lineno is not None and self.colno is not None and self.doc is not None:
            lines = self.doc.splitlines()
            error_lines = [f"TOML parse error at line {self.lineno}, column {self.colno}"]

            # Show the problematic line with context
            if 0 < self.lineno <= len(lines):
                # Show previous line if available
                if self.lineno > 1:
                    error_lines.append(f"{self.lineno - 1:4d} | {lines[self.lineno - 2]}")

                # Show the error line
                error_line = lines[self.lineno - 1]
                error_lines.append(f"{self.lineno:4d} | {error_line}")

                # Show the error pointer
                pointer = " " * (7 + self.colno - 1) + "^"
                error_lines.append(pointer)

                # Show next line if available
                if self.lineno < len(lines):
                    error_lines.append(f"{self.lineno + 1:4d} | {lines[self.lineno]}")

            # Extract the actual error message
            msg_match = re.search(r"\n(.+)$", self.msg)
            if msg_match:
                error_lines.append("")
                error_lines.append(msg_match.group(1))

            return "\n".join(error_lines)
        return self.msg


class TomlSerializationError(_rustoml.TomlSerializationError):
    """Exception raised when TOML serialization fails."""

    pass


def _apply_parse_float(obj: Any, parse_float: Callable[[str], Any]) -> Any:
    """Recursively apply parse_float to all float values in a data structure."""
    if isinstance(obj, float):
        # Convert float back to string and parse with custom function
        return parse_float(str(obj))
    elif isinstance(obj, dict):
        return {k: _apply_parse_float(v, parse_float) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_apply_parse_float(item, parse_float) for item in obj]
    return obj


def load(
    toml: str | Path | TextIO | BinaryIO,
    *,
    none_value: str | None = None,
    parse_float: Callable[[str], Any] = float,
) -> dict[str, Any]:
    """
    Parse TOML from a string, file path, or file object and return a Python dictionary.

    This function provides a convenient interface for loading TOML data from various sources.
    It automatically handles reading from files and delegates to `loads()` for parsing.

    Args:
        toml: The TOML source to parse. Can be:
            - A `str` containing TOML data
            - A `Path` object pointing to a TOML file
            - A file object opened in text or binary mode
        none_value: Optional string value to treat as Python `None`. When specified,
            any string matching this value in the TOML will be converted to `None`.
            By default, no values are converted to `None`.
        parse_float: A callable that will be called with the string representation
            of every TOML float to convert it to a Python object. Defaults to `float`.
            Can be used with `decimal.Decimal` for exact precision.

    Returns:
        A dictionary representing the parsed TOML data with string keys and
        values of various types (str, int, float, bool, list, dict, datetime).

    Raises:
        TomlParsingError: If the TOML data is malformed or invalid.
        TypeError: If `toml` is not a str, Path, or file object.
        OSError: If reading from a Path or file object fails.

    Example:
        >>> import rustoml
        >>> from pathlib import Path
        >>> from decimal import Decimal
        >>> # From string
        >>> data = rustoml.load('[package]\\nname = "example"')
        >>> # From Path
        >>> data = rustoml.load(Path('config.toml'))
        >>> # From binary file object
        >>> with open('config.toml', 'rb') as f:
        ...     data = rustoml.load(f)
        >>> # With custom float parsing
        >>> data = rustoml.load('[price]\\nvalue = 19.99', parse_float=Decimal)
    """
    if isinstance(toml, Path):
        toml_str = toml.read_text(encoding="UTF-8")
    elif isinstance(toml, str):
        toml_str = toml
    elif isinstance(toml, (TextIOBase, TextIO)):
        toml_str = toml.read()
    elif isinstance(toml, BinaryIO):
        # Binary file mode - decode as UTF-8
        content = toml.read()
        toml_str = content.decode("utf-8")
    else:
        # Try to handle file-like objects with a mode attribute
        if hasattr(toml, "read") and callable(getattr(toml, "read")):
            mode_attr = getattr(toml, "mode", None)
            if isinstance(mode_attr, str) and "b" in mode_attr:
                # Binary mode
                content = toml.read()  # type: ignore[attr-defined]
                toml_str = content.decode("utf-8") if isinstance(content, bytes) else str(content)
            else:
                # Text mode
                toml_str = str(toml.read())  # type: ignore[attr-defined]
        else:
            raise TypeError(f"invalid toml input type: {type(toml)}")

    return loads(toml_str, none_value=none_value, parse_float=parse_float)


def loads(
    toml: str,
    *,
    none_value: str | None = None,
    parse_float: Callable[[str], Any] = float,
) -> dict[str, Any]:
    """
    Parse a TOML string and return a Python dictionary.

    This function parses TOML data from a string. The interface matches that of
    `json.loads()` for consistency with Python's standard library.

    Args:
        toml: A string containing valid TOML data.
        none_value: Optional string value to treat as Python `None`. When specified,
            any string matching this value in the TOML will be converted to `None`.
            By default, no values are converted to `None`.
        parse_float: A callable that will be called with the string representation
            of every TOML float to convert it to a Python object. Defaults to `float`.
            Can be used with `decimal.Decimal` for exact precision.

    Returns:
        A dictionary representing the parsed TOML data with string keys and
        values of various types (str, int, float/custom, bool, list, dict, datetime).

    Raises:
        TomlParsingError: If the TOML string is malformed or invalid.
        TypeError: If `toml` is not a string.

    Example:
        >>> import rustoml
        >>> from decimal import Decimal
        >>> toml_str = '''
        ... [package]
        ... name = "rustoml"
        ... version = "0.12.0"
        ... '''
        >>> data = rustoml.loads(toml_str)
        >>> print(data['package']['name'])
        rustoml
        >>> # With Decimal for exact precision
        >>> data = rustoml.loads('price = 19.99', parse_float=Decimal)
        >>> isinstance(data['price'], Decimal)
        True
    """
    if not isinstance(toml, str):
        raise TypeError(f"invalid toml input, must be str not {type(toml)}")
    try:
        result = _rustoml.deserialize(toml, none_value=none_value)
        # Apply custom float parsing if not using default
        if parse_float is not float:
            result = _apply_parse_float(result, parse_float)
        return result
    except _rustoml.TomlParsingError as e:
        # Wrap the Rust error with our enhanced Python error
        raise TomlParsingError(str(e), doc=toml) from None


def dumps(obj: Any, *, pretty: bool = True, none_value: str | None = "null") -> str:
    """
    Serialize a Python object to a TOML string.

    This function converts a Python object (typically a dictionary) to TOML format.
    The interface matches that of `json.dumps()` for consistency with Python's standard library.

    Args:
        obj: A Python object to serialize. Typically a dict, but can also contain
            lists, strings, numbers, booleans, datetime objects, and None values.
        pretty: If `True`, the output uses a more readable "pretty" format with
            better spacing and organization. Default is `True`.
        none_value: Controls how `None` values are serialized. If a string is provided,
            `None` values will be serialized as that string. If `None` is passed,
            `None` values will be omitted from the output. Default is `'null'`.

    Returns:
        A TOML string representation of the object.

    Raises:
        TomlSerializationError: If the object cannot be serialized to TOML
            (e.g., unsupported types, circular references).

    Example:
        >>> import rustoml
        >>> data = {'package': {'name': 'rustoml', 'version': '0.13.0'}}
        >>> print(rustoml.dumps(data))
        [package]
        name = "rustoml"
        version = "0.13.0"
        <BLANKLINE>
        >>> # With None handling
        >>> data_with_none = {'key': None, 'other': 'value'}
        >>> rustoml.dumps(data_with_none, none_value=None)  # Omit None
        'other = "value"\\n'
        >>> rustoml.dumps(data_with_none, none_value='@null')  # Serialize as '@null'
        'key = "@null"\\nother = "value"\\n'
    """
    if pretty:
        serialize = _rustoml.serialize_pretty
    else:
        serialize = _rustoml.serialize

    return serialize(obj, none_value=none_value)


def dump(obj: Any, file: Path | TextIO, *, pretty: bool = False, none_value: str | None = "null") -> int:
    """
    Serialize a Python object to TOML and write it to a file.

    This function converts a Python object to TOML format and writes it directly to a file.
    The interface matches that of `json.dump()` for consistency with Python's standard library.

    Args:
        obj: A Python object to serialize. Typically a dict, but can also contain
            lists, strings, numbers, booleans, datetime objects, and None values.
        file: The destination for the TOML output. Can be:
            - A `Path` object pointing to the destination file
            - A file object opened in text write mode
        pretty: If `True`, the output uses a more readable "pretty" format with
            better spacing and organization. Default is `False`.
        none_value: Controls how `None` values are serialized. If a string is provided,
            `None` values will be serialized as that string. If `None` is passed,
            `None` values will be omitted from the output. Default is `'null'`.

    Returns:
        The number of characters written to the file.

    Raises:
        TomlSerializationError: If the object cannot be serialized to TOML.
        OSError: If writing to the file fails.
        TypeError: If `file` is not a Path or file object.

    Example:
        >>> import rustoml
        >>> from pathlib import Path
        >>> data = {'package': {'name': 'rustoml', 'version': '0.13.0'}}
        >>> # Write to Path
        >>> rustoml.dump(data, Path('config.toml'), pretty=True)
        >>> # Write to file object
        >>> with open('config.toml', 'w') as f:
        ...     rustoml.dump(data, f, pretty=True)
    """
    s = dumps(obj, pretty=pretty, none_value=none_value)
    if isinstance(file, Path):
        return file.write_text(s, encoding="UTF-8")
    else:
        return file.write(s)
