import nox

nox.options.default_venv_backend = "uv|virtualenv"

@nox.session(python=['3.10', '3.11', '3.12', '3.13'])
def tests(session):
    session.install('pytest')
    session.install(".")
    session.run('pytest')


@nox.session()
def ruff(session):
    """Check code for linter warnings and formatting issues."""
    check_files = ['src', 'tests', 'noxfile.py']
    session.install('ruff')
    session.run('ruff', 'check', *check_files)
