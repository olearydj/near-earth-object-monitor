import pytest

from neo_monitor.cli import parse_args
from neo_monitor.metadata import package_version


def test_version_option_prints_version_and_exits(capsys):
    with pytest.raises(SystemExit) as exc_info:
        parse_args(["--version"])

    assert exc_info.value.code == 0
    assert capsys.readouterr().out == f"neo-monitor {package_version()}\n"
