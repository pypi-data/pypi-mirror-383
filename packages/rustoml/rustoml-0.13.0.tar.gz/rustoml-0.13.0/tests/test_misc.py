from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import ModuleType

import pytest

import rustoml


def test_example():
    loader = SourceFileLoader("example", str(Path(__file__).parent / "../example.py"))
    module = ModuleType(loader.name)
    loader.exec_module(module)
    # check it looks about right
    assert isinstance(module.obj, dict)
    assert module.obj["title"] == "TOML Example"


def test_version():
    assert isinstance(rustoml.__version__, str)
    print("rustoml __version__:", rustoml.__version__)


@pytest.mark.parametrize(
    "dt",
    [
        # passes, for 6 significant subsecond digits
        "2020-05-25T12:00:01.123456",
        # previously failed because last subsecond digit is not dumped to string
        # and load parsing fails with only 5 fractional digits
        "2020-05-25T12:00:01.123450",
    ],
)
def test_datetime_precision(dt):
    assert rustoml.loads(rustoml.dumps({"a": dt})) == {"a": dt}
