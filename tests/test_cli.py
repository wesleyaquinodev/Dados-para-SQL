"""Testes da CLI."""

from pytest import CaptureFixture

from dados_para_sql import __version__
from dados_para_sql.cli import build_parser


def test_version_argument_returns_current_version(capsys: CaptureFixture[str]) -> None:
    parser = build_parser()

    try:
        parser.parse_args(["--version"])
    except SystemExit as error:
        assert error.code == 0

    captured = capsys.readouterr()
    assert __version__ in captured.out
