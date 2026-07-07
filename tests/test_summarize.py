import json
from pathlib import Path

from neo_monitor.output import write_objects_csv, write_raw_json
from neo_monitor.summarize import (
    extract_objects,
    filter_objects,
    format_object_listing,
    format_summary,
    summarize_feed,
)


FIXTURE = Path(__file__).parent / "fixtures" / "neo-feed-sample.json"


def load_fixture():
    return json.loads(FIXTURE.read_text())


def test_extract_objects_returns_selected_fields():
    objects = extract_objects(load_fixture())

    assert len(objects) == 3
    assert objects[0].name == "Example Asteroid Alpha"
    assert objects[0].diameter_meters == 200


def test_summarize_feed_identifies_key_objects():
    summary = summarize_feed(load_fixture())

    assert summary.total_objects == 3
    assert summary.hazardous_count == 1
    assert summary.closest is not None
    assert summary.closest.name == "Example Asteroid Beta"
    assert summary.fastest is not None
    assert summary.fastest.name == "Example Asteroid Beta"
    assert summary.largest is not None
    assert summary.largest.name == "Example Asteroid Gamma"


def test_format_summary_includes_report_values():
    summary = summarize_feed(load_fixture())

    report = format_summary(summary, "2026-07-02")

    assert "Near-Earth Object Summary" in report
    assert "Objects observed: 3" in report
    assert "Potentially hazardous: 1" in report
    assert "Example Asteroid Beta" in report


def test_format_object_listing_includes_extracted_rows():
    listing = format_object_listing(extract_objects(load_fixture()))

    assert "Near-Earth Object Listing" in listing
    assert "Approach Date | Name | Hazardous" in listing
    assert "2026-07-02 | Example Asteroid Beta | yes | 50 | 0.81 | 71000" in listing


def test_filter_objects_can_return_hazardous_only():
    filtered = filter_objects(extract_objects(load_fixture()), hazardous_only=True)

    assert [obj.name for obj in filtered] == ["Example Asteroid Beta"]


def test_filter_objects_can_apply_combined_numeric_filters():
    filtered = filter_objects(
        extract_objects(load_fixture()),
        min_diameter_meters=100,
        max_miss_distance_lunar=2,
    )

    assert [obj.name for obj in filtered] == ["Example Asteroid Alpha"]


def test_write_raw_json_creates_parent_directories(tmp_path):
    output_path = tmp_path / "data" / "raw" / "neo-feed.json"

    write_raw_json(load_fixture(), output_path)

    saved = json.loads(output_path.read_text())
    assert saved["element_count"] == 3


def test_write_objects_csv_creates_processed_rows(tmp_path):
    output_path = tmp_path / "data" / "processed" / "neo-objects.csv"

    write_objects_csv(extract_objects(load_fixture()), output_path)

    csv_text = output_path.read_text()
    assert "approach_date,name,hazardous,diameter_meters" in csv_text
    assert "2026-07-02,Example Asteroid Beta,true,50.000" in csv_text
