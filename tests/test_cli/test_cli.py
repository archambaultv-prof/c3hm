from click.testing import CliRunner

from c3hm.cli import cli


def test_help(runner: CliRunner):
    result = runner.invoke(cli, ["--help"], catch_exceptions=False)
    assert result.exit_code == 0

    for command in [
        "unpack",
        "template",
        "export",
        "gradebook",
        "feedback",
        "clean",
    ]:
        result = runner.invoke(cli, [command, "--help"], catch_exceptions=False)
        assert result.exit_code == 0
