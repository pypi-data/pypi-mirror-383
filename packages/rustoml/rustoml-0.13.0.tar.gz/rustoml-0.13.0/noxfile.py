"""Nox sessions for testing across Python versions."""

import nox

nox.options.default_venv_backend = "uv"

PYTHON_VERSIONS: list[str] = ["3.10", "3.11", "3.12", "3.13", "3.14"]


@nox.session(python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    """Run tests for a specific Python version."""
    # Install maturin and build the package
    session.install("maturin")
    session.run("maturin", "develop", "--release")

    # Install test dependencies
    session.install("pytest", "dirty-equals")

    # Run tests
    session.run("pytest", "tests/", "-v")


@nox.session(python=PYTHON_VERSIONS)
def quick_test(session: nox.Session) -> None:
    """Quick smoke test: build and import."""
    session.install("maturin")
    session.run("maturin", "develop", "--release")

    # Quick import test
    session.run(
        "python",
        "-c",
        "import rustoml; import sys; print(f'✅ Python {sys.version.split()[0]} - rustoml v{rustoml.__version__}')",
    )


@nox.session
def test_all(session: nox.Session) -> None:
    """Run quick tests on all Python versions."""
    for version in PYTHON_VERSIONS:
        session.log(f"Testing Python {version}...")
        session.run("nox", "-s", f"quick_test-{version}", external=True)
