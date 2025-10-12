from contextlib import suppress

from wcap.cli import main


def test_cli_help(capsys):
    with suppress(SystemExit):
        main(['-h'])
    output = capsys.readouterr().out
    assert '--dimension' in output
