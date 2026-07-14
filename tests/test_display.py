import json
from pathlib import Path

from rich.console import Console

from neo_monitor.display import print_rich_bar_chart
from neo_monitor.summarize import extract_objects, rank_objects


FIXTURE = Path(__file__).parent / "fixtures" / "neo-feed-sample.json"


def test_rich_bar_chart_preserves_ranked_names_and_exact_values():
    objects = extract_objects(json.loads(FIXTURE.read_text()))
    ranked = rank_objects(objects, "fastest", top=2)
    console = Console(record=True, width=120, color_system=None)

    print_rich_bar_chart(console, ranked, "fastest")

    rendered = console.export_text()
    assert "Fastest Objects" in rendered
    assert "Example Asteroid Beta" in rendered
    assert "71,000 km/h" in rendered
    assert "Example Asteroid Alpha" in rendered
    assert "42,000 km/h" in rendered
