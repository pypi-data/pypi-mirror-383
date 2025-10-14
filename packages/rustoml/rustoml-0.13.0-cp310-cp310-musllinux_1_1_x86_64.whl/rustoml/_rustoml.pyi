"""Type stubs for the rustoml Rust extension module."""

from typing import Any

__version__: str
"""The version of the rustoml package."""

def deserialize(toml: str, none_value: str | None = None) -> dict[str, Any]:
    """
    Deserialize a TOML string into a Python dictionary.

    Args:
        toml: A string containing valid TOML data.
        none_value: Optional string value to be converted to None. If specified,
            any string matching this value in the TOML will be deserialized as None.

    Returns:
        A dictionary representing the parsed TOML data.

    Raises:
        TomlParsingError: If the TOML string is invalid or cannot be parsed.
    """
    ...

def serialize(obj: Any, none_value: str | None = "null") -> str:
    """
    Serialize a Python object to a TOML string.

    Args:
        obj: A Python object to serialize (typically a dict).
        none_value: Optional string representation for None values. If None is passed,
            None values will be omitted from the output. Default is 'null'.

    Returns:
        A TOML string representation of the object.

    Raises:
        TomlSerializationError: If the object cannot be serialized to TOML.
    """
    ...

def serialize_pretty(obj: Any, none_value: str | None = "null") -> str:
    """
    Serialize a Python object to a pretty-formatted TOML string.

    Args:
        obj: A Python object to serialize (typically a dict).
        none_value: Optional string representation for None values. If None is passed,
            None values will be omitted from the output. Default is 'null'.

    Returns:
        A pretty-formatted TOML string representation of the object.

    Raises:
        TomlSerializationError: If the object cannot be serialized to TOML.
    """
    ...

class TomlParsingError(ValueError):
    """Exception raised when TOML parsing fails."""

    ...

class TomlSerializationError(ValueError):
    """Exception raised when TOML serialization fails."""

    ...
