import json
import sys
from pathlib import Path

import pytest

from neo_monitor import cli
from neo_monitor.cli import parse_args
from neo_monitor.metadata import package_version


def test_version_option_prints_version_and_exits(capsys):
    with pytest.raises(SystemExit) as exc_info:
        parse_args(["--version"])

    assert exc_info.value.code == 0
    assert capsys.readouterr().out == f"neo-monitor {package_version()}\n"


def test_help_includes_examples_defaults_and_configuration(capsys):
    with pytest.raises(SystemExit) as exc_info:
        parse_args(["--help"])

    assert exc_info.value.code == 0
    help_text = " ".join(capsys.readouterr().out.split())
    assert "examples:" in help_text
    assert "--start-date 2026-07-01" in help_text
    assert "default: today" in help_text
    assert "NASA_API_KEY" in help_text


def test_parse_args_rejects_a_date_range_that_ends_before_it_starts(capsys):
    with pytest.raises(SystemExit) as exc_info:
        parse_args(["--start-date", "2026-07-03", "--end-date", "2026-07-02"])

    assert exc_info.value.code == 2
    assert "--end-date cannot be before --start-date" in capsys.readouterr().err


def test_parse_args_requires_a_ranking_for_a_bar_chart(capsys):
    with pytest.raises(SystemExit) as exc_info:
        parse_args(["--bar-chart"])

    assert exc_info.value.code == 2
    assert "--bar-chart requires --sort-by" in capsys.readouterr().err


def test_project_info_is_a_no_network_smoke_test(monkeypatch, capsys):
    def unexpected_network_call(**kwargs):
        raise AssertionError(f"unexpected network call: {kwargs}")

    monkeypatch.setattr(cli, "fetch_monitor_feed", unexpected_network_call)
    monkeypatch.setattr(sys, "argv", ["neo-monitor", "--project-info"])

    cli.main()

    assert "Near-Earth Object Monitor Project Info" in capsys.readouterr().out


def test_cli_runs_several_parts_together_with_controlled_data(
    monkeypatch, capsys, tmp_path
):
    fixture_path = Path(__file__).parent / "fixtures" / "neo-feed-sample.json"
    fixture_data = json.loads(fixture_path.read_text())
    raw_path = tmp_path / "raw" / "neo-feed.json"
    csv_path = tmp_path / "processed" / "neo-objects.csv"

    monkeypatch.setenv("NASA_API_KEY", "test-key")
    monkeypatch.setattr(cli, "fetch_monitor_feed", lambda *_args: fixture_data)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "neo-monitor",
            "--start-date",
            "2026-07-02",
            "--end-date",
            "2026-07-02",
            "--plain",
            "--sort-by",
            "closest",
            "--top",
            "1",
            "--save-raw",
            str(raw_path),
            "--save-processed-csv",
            str(csv_path),
        ],
    )

    cli.main()

    assert "Near-Earth Object Summary" in capsys.readouterr().out
    assert json.loads(raw_path.read_text())["element_count"] == 3
    csv_text = csv_path.read_text()
    assert "Example Asteroid Beta" in csv_text
    assert "Example Asteroid Alpha" not in csv_text


def test_cli_can_render_a_rich_bar_chart_with_controlled_data(monkeypatch, capsys):
    fixture_path = Path(__file__).parent / "fixtures" / "neo-feed-sample.json"
    fixture_data = json.loads(fixture_path.read_text())

    monkeypatch.setenv("NASA_API_KEY", "test-key")
    monkeypatch.setattr(cli, "fetch_monitor_feed", lambda *_args: fixture_data)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "neo-monitor",
            "--bar-chart",
            "--sort-by",
            "fastest",
            "--top",
            "2",
        ],
    )

    cli.main()

    output = capsys.readouterr().out
    assert "Fastest Objects" in output
    assert "Example Asteroid Beta" in output
    assert "71,000 km/h" in output


def test_cli_saves_raw_evidence_before_reporting_bad_external_data(
    monkeypatch, tmp_path
):
    fixture_path = Path(__file__).parent / "fixtures" / "neo-feed-invalid.json"
    invalid_data = json.loads(fixture_path.read_text())
    raw_path = tmp_path / "raw" / "bad-neo-feed.json"

    monkeypatch.setenv("NASA_API_KEY", "test-key")
    monkeypatch.setattr(cli, "fetch_monitor_feed", lambda *_args: invalid_data)
    monkeypatch.setattr(
        sys,
        "argv",
        ["neo-monitor", "--save-raw", str(raw_path)],
    )

    with pytest.raises(SystemExit, match="NASA data could not be used"):
        cli.main()

    assert json.loads(raw_path.read_text()) == invalid_data
