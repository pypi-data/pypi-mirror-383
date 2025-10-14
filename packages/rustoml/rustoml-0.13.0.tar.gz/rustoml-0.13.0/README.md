# rustoml

[![Actions Status](https://github.com/seanmozeik/rustoml/workflows/CI/badge.svg)](https://github.com/seanmozeik/rustoml/actions?query=event%3Apush+branch%3Amain+workflow%3ACI)
[![pypi](https://img.shields.io/pypi/v/rustoml.svg)](https://pypi.python.org/pypi/rustoml)
[![versions](https://img.shields.io/pypi/pyversions/rustoml.svg)](https://github.com/seanmozeik/rustoml)
[![license](https://img.shields.io/github/license/seanmozeik/rustoml.svg)](https://github.com/seanmozeik/rustoml/blob/main/LICENSE)

A modern, high-performance TOML library for Python implemented in Rust.

## About This Fork

This project is a maintained and enhanced fork of [samuelcolvin/rtoml](https://github.com/samuelcolvin/rtoml). The original project hasn't been updated in a while, and this fork continues development for the latest Python versions, with additional Rust tooling improvements.

### Key Improvements Over Original rtoml

- **Python 3.14 Support**: Full support for Python 3.14, including free-threaded mode (GIL-free)
- **Modern Dependencies**: Updated to latest Rust dependencies (PyO3 0.26, toml 0.9)
- **Enhanced Error Handling**: tomllib-compatible error messages with line/column information
- **Comprehensive Docstrings**: For improved developer experience and IDE support
- **Custom Float Parsing**: Support for `parse_float` parameter (e.g., for Decimal types)
- **Binary File Support**: Read TOML from binary file handles
- **Better Type Safety**: Comprehensive type stubs and full mypy strict compatibility
- **Modern Tooling**: Built with uv, maturin, and modern Python packaging standards

### Credits

Original project by [Samuel Colvin](https://github.com/samuelcolvin). This fork maintained by [Sean Lees](https://github.com/seanmozeik).

Both projects are MIT licensed.

## Why Use rustoml

- **Correctness**: Built on the widely-used and stable [toml-rs](https://github.com/toml-rs/toml) library. Passes all [standard TOML tests](https://github.com/BurntSushi/toml-test) with 100% test coverage on Python code.
- **Performance**: One of the fastest Python TOML libraries available.
- **Flexible None handling**: Configurable support for `None` values with custom serialization/deserialization.
- **Type safe**: Full type annotations with `py.typed` marker for excellent IDE support and type checking.

## Install

Requires `python>=3.10`, binaries are available from PyPI for Linux, macOS and Windows,
see [here](https://pypi.org/project/rustoml/#files).

```sh
uv add rustoml
# or
pip install rustoml
```

If no binary is available on PyPI for your system configuration, you'll need Rust stable
installed before you can install rustoml.

## Usage

#### load

```python
def load(toml: str | Path | TextIO, *, none_value: str | None = None) -> dict[str, Any]: ...
```

Parse TOML via a string or file and return a python dictionary.

- `toml`: a `str`, `Path` or file object from `open()`.
- `none_value`: controlling which value in `toml` is loaded as `None` in python. By default, `none_value` is `None`, which means nothing is loaded as `None`

#### loads

```python
def loads(toml: str, *, none_value: str | None = None) -> dict[str, Any]: ...
```

Parse a TOML string and return a python dictionary. (provided to match the interface of `json` and similar libraries)

- `toml`: a `str` containing TOML.
- `none_value`: controlling which value in `toml` is loaded as `None` in python. By default, `none_value` is `None`, which means nothing is loaded as `None`

#### dumps

```python
def dumps(obj: Any, *, pretty: bool = False, none_value: str | None = "null") -> str: ...
```

Serialize a python object to TOML.

- `obj`: a python object to be serialized.
- `pretty`: if `True` the output has a more "pretty" format.
- `none_value`: controlling how `None` values in `obj` are serialized. `none_value=None` means `None` values are ignored.

#### dump

```python
def dump(
    obj: Any, file: Path | TextIO, *, pretty: bool = False, none_value: str | None = "null"
) -> int: ...
```

Serialize a python object to TOML and write it to a file.

- `obj`: a python object to be serialized.
- `file`: a `Path` or file object from `open()`.
- `pretty`: if `True` the output has a more "pretty" format.
- `none_value`: controlling how `None` values in `obj` are serialized. `none_value=None` means `None` values are ignored.

### Examples

```python
from datetime import datetime, timezone, timedelta
import rustoml

obj = {
    'title': 'TOML Example',
    'owner': {
        'dob': datetime(1979, 5, 27, 7, 32, tzinfo=timezone(timedelta(hours=-8))),
        'name': 'Tom Preston-Werner',
    },
    'database': {
        'connection_max': 5000,
        'enabled': True,
        'ports': [8001, 8001, 8002],
        'server': '192.168.1.1',
    },
}

loaded_obj = rustoml.load("""\
# This is a TOML document.

title = "TOML Example"

[owner]
name = "Tom Preston-Werner"
dob = 1979-05-27T07:32:00-08:00 # First class dates

[database]
server = "192.168.1.1"
ports = [8001, 8001, 8002]
connection_max = 5000
enabled = true
""")

assert loaded_obj == obj

assert rustoml.dumps(obj) == """\
title = "TOML Example"

[owner]
dob = 1979-05-27T07:32:00-08:00
name = "Tom Preston-Werner"

[database]
connection_max = 5000
enabled = true
server = "192.168.1.1"
ports = [8001, 8001, 8002]
"""
```

An example of `None`-value handling:

```python
obj = {
    'a': None,
    'b': 1,
    'c': [1, 2, None, 3],
}

# Ignore None values
assert rustoml.dumps(obj, none_value=None) == """\
b = 1
c = [1, 2, 3]
"""

# Serialize None values as '@None'
assert rustoml.dumps(obj, none_value='@None') == """\
a = "@None"
b = 1
c = [1, 2, "@None", 3]
"""

# Deserialize '@None' back to None
assert rustoml.load("""\
a = "@None"
b = 1
c = [1, 2, "@None", 3]
""", none_value='@None') == obj
```
