"""Nox sessions for testing and linting."""

import nox

# Define Python versions to test
PYTHON_VERSIONS = ["3.11", "3.12", "3.13", "3.14"]


@nox.session(python=PYTHON_VERSIONS)
def tests(session):
    """Run tests with pytest for the data module."""
    # Install package with dev dependencies
    session.install("-e", ".[dev]")

    # Run pytest on tests/data/
    session.run("pytest", "tests/data/")


@nox.session(python="3.13")
def lint(session):
    """Run ruff linter on the source code and tests."""
    session.install("ruff")
    session.run("ruff", "check", "src/", "tests/")


@nox.session(python="3.13")
def format_check(session):
    """Check code formatting with ruff."""
    session.install("ruff")
    session.run("ruff", "format", "--check", "src/", "tests/")


@nox.session(python="3.13")
def format(session):
    """Format code with ruff."""
    session.install("ruff")
    session.run("ruff", "format", "src/", "tests/")
