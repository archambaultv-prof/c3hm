from c3hm.cli import cli
from click.testing import CliRunner


def test_help(runner: CliRunner):
    result = runner.invoke(cli, ["--help"], catch_exceptions=False)
    assert result.exit_code == 0

    for command in [
        "clean",
        "template",
        "rubric",
        "gradebook",
        "feedback",
    ]:
        result = runner.invoke(cli, [command, "--help"], catch_exceptions=False)
        assert result.exit_code == 0
